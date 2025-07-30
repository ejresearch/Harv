#!/usr/bin/env python3
"""
HARV CLI - Socratic AI Tutoring Command Line Interface
AI-Assisted Mass Communication Education System
"""

import os
import sqlite3
import sys
import json
import shutil
import hashlib
import secrets
import re
import base64
import hmac
from datetime import datetime, timedelta
from openai import OpenAI
from typing import Dict, List, Optional, Any

# Platform-specific imports for keyboard handling
try:
    import termios
    import tty
    HAS_TERMIOS = True
except ImportError:
    HAS_TERMIOS = False

# JWT implementation without external dependencies
class JWTHandler:
    """Simple JWT implementation for CLI authentication"""
    
    @staticmethod  
    def base64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')
    
    @staticmethod
    def base64url_decode(data: str) -> bytes:
        # Add padding if necessary
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += '=' * padding
        return base64.urlsafe_b64decode(data)
    
    @staticmethod
    def create_token(payload: Dict[str, Any], secret: str, expires_hours: int = 24) -> str:
        """Create a JWT token with expiration"""
        header = {"alg": "HS256", "typ": "JWT"}
        
        # Add timestamps
        now = datetime.utcnow()
        payload.update({
            "iat": int(now.timestamp()),  # issued at
            "exp": int((now + timedelta(hours=expires_hours)).timestamp()),  # expires
            "jti": secrets.token_hex(16)  # JWT ID for uniqueness
        })
        
        # Encode header and payload
        header_encoded = JWTHandler.base64url_encode(json.dumps(header).encode())
        payload_encoded = JWTHandler.base64url_encode(json.dumps(payload).encode())
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            secret.encode(), 
            message.encode(), 
            hashlib.sha256
        ).digest()
        signature_encoded = JWTHandler.base64url_encode(signature)
        
        return f"{message}.{signature_encoded}"
    
    @staticmethod
    def verify_token(token: str, secret: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            header_encoded, payload_encoded, signature_encoded = token.split('.')
            
            # Verify signature
            message = f"{header_encoded}.{payload_encoded}"
            expected_signature = hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
            
            received_signature = JWTHandler.base64url_decode(signature_encoded)
            
            if not hmac.compare_digest(expected_signature, received_signature):
                return None
            
            # Decode payload
            payload = json.loads(JWTHandler.base64url_decode(payload_encoded))
            
            # Check expiration
            if 'exp' in payload:
                if datetime.utcnow().timestamp() > payload['exp']:
                    return None
            
            return payload
            
        except Exception:
            return None

# Enhanced Security Module
class SecurityManager:
    """Handles authentication, password validation, and secure storage"""
    
    def __init__(self):
        self.secret_key = self._get_or_create_secret()
        self.failed_attempts = {}
        self.max_attempts = 3
        self.lockout_time = 300  # 5 minutes
    
    def _get_or_create_secret(self) -> str:
        """Get or create application secret key"""
        secret_path = os.path.expanduser("~/.harv_secret")
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as f:
                return f.read().strip()
        else:
            secret = secrets.token_hex(32)
            with open(secret_path, 'w') as f:
                f.write(secret)
            os.chmod(secret_path, 0o600)  # Read/write for owner only
            return secret
    
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_bytes(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return base64.b64encode(salt + password_hash).decode()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            decoded = base64.b64decode(password_hash)
            salt = decoded[:32]
            stored_hash = decoded[32:]
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            return hmac.compare_digest(stored_hash, new_hash)
        except Exception:
            return False
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common patterns
        common_patterns = ['123', 'abc', 'password', 'qwerty', '111', '000']
        for pattern in common_patterns:
            if pattern in password.lower():
                return False, f"Password cannot contain common pattern: {pattern}"
        
        return True, "Password meets security requirements"
    
    def create_session_token(self, student_name: str) -> str:
        """Create session token for authenticated student"""
        payload = {
            "student": student_name,
            "type": "session"
        }
        return JWTHandler.create_token(payload, self.secret_key, expires_hours=24)
    
    def verify_session_token(self, token: str) -> Optional[str]:
        """Verify session token and return student name"""
        payload = JWTHandler.verify_token(token, self.secret_key)
        if payload and payload.get("type") == "session":
            return payload.get("student")
        return None
    
    def is_locked_out(self, identifier: str) -> bool:
        """Check if identifier is locked out due to failed attempts"""
        if identifier in self.failed_attempts:
            attempts, last_attempt = self.failed_attempts[identifier]
            if attempts >= self.max_attempts:
                if datetime.now().timestamp() - last_attempt < self.lockout_time:
                    return True
                else:
                    # Reset after lockout period
                    del self.failed_attempts[identifier]
        return False
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed login attempt"""
        now = datetime.now().timestamp()
        if identifier in self.failed_attempts:
            attempts, _ = self.failed_attempts[identifier]
            self.failed_attempts[identifier] = (attempts + 1, now)
        else:
            self.failed_attempts[identifier] = (1, now)
    
    def clear_failed_attempts(self, identifier: str):
        """Clear failed attempts after successful login"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]

# Enhanced Memory System Integration
class EnhancedMemorySystem:
    """Advanced memory management with learning pattern analysis"""
    
    def __init__(self, student_name: str):
        self.student_name = student_name
        self.db_path = f"students/{student_name}/{student_name}_harv.sqlite"
        
    def analyze_learning_patterns(self) -> Dict[str, Any]:
        """Analyze student learning patterns from conversation history"""
        if not os.path.exists(self.db_path):
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze conversation patterns
        cursor.execute("""
            SELECT module_id, COUNT(*) as interactions,
                   AVG(LENGTH(content)) as avg_response_length,
                   COUNT(CASE WHEN message_type = 'user' THEN 1 END) as questions_asked
            FROM conversations 
            GROUP BY module_id
        """)
        
        module_patterns = {}
        for row in cursor.fetchall():
            module_id, interactions, avg_length, questions = row
            module_patterns[module_id] = {
                'engagement_level': min(interactions / 10.0, 1.0),  # Normalize to 0-1
                'depth_of_responses': min(avg_length / 100.0, 1.0),  # Normalize
                'curiosity_level': min(questions / 5.0, 1.0)  # Normalize
            }
        
        # Analyze learning progression
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as daily_interactions
            FROM conversations 
            WHERE message_type = 'user'
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        """)
        
        daily_engagement = cursor.fetchall()
        conn.close()
        
        return {
            'module_patterns': module_patterns,
            'daily_engagement': daily_engagement,
            'total_modules_engaged': len(module_patterns),
            'avg_engagement': sum(p['engagement_level'] for p in module_patterns.values()) / max(len(module_patterns), 1)
        }
    
    def get_adaptive_context(self, module_id: int) -> str:
        """Generate adaptive context based on learning patterns"""
        patterns = self.analyze_learning_patterns()
        
        if module_id in patterns.get('module_patterns', {}):
            module_pattern = patterns['module_patterns'][module_id]
            
            # Adjust teaching approach based on patterns
            if module_pattern['engagement_level'] < 0.3:
                return "The student shows low engagement. Use more interactive questions and real-world examples."
            elif module_pattern['curiosity_level'] > 0.7:
                return "The student is highly curious. Provide deeper explanations and encourage exploration."
            elif module_pattern['depth_of_responses'] < 0.3:
                return "The student gives brief responses. Use prompts that encourage elaboration."
        
        return "Maintain standard Socratic questioning approach."
    
    def save_learning_insight(self, module_id: int, insight: str):
        """Save learning insights for future reference"""
        if not os.path.exists(self.db_path):
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO learning_insights 
            (module_id, insight_text, created_at)
            VALUES (?, ?, ?)
        """, (module_id, insight, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

# Global instances
security_manager = SecurityManager()
enhanced_memory = None

# Terminal colors for retro aesthetic
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ASCII Art Header
HARV_HEADER = f"""{Colors.GREEN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ██╗  ██╗ █████╗ ██████╗ ██╗   ██╗                        ║
║                    ██║  ██║██╔══██╗██╔══██╗██║   ██║                        ║
║                    ███████║███████║██████╔╝██║   ██║                        ║
║                    ██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝                        ║
║                    ██║  ██║██║  ██║██║  ██║ ╚████╔╝                         ║
║                    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝                          ║
║                                                                              ║
║              {Colors.YELLOW}🎓 SOCRATIC AI TUTORING SYSTEM 🎓{Colors.GREEN}                     ║
║                          {Colors.CYAN}~ Question • Reflect • Discover ~{Colors.GREEN}                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.END}"""

# Initialize OpenAI client
client = None

# Global session state
class Session:
    def __init__(self):
        self.current_student = None
        self.db_conn = None
        self.api_key_set = False
        self.menu_stack = []
        self.backend_url = "http://localhost:8000"
        self.session_token = None
        self.is_authenticated = False
        self.last_activity = datetime.now()
        self.session_timeout = 3600  # 1 hour
    
    def authenticate_student(self, student_name: str, password: str) -> bool:
        """Authenticate student with password"""
        if security_manager.is_locked_out(student_name):
            return False
        
        db_path = f"students/{student_name}/{student_name}_harv.sqlite"
        if not os.path.exists(db_path):
            security_manager.record_failed_attempt(student_name)
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT password_hash FROM student_auth WHERE student_name = ?", (student_name,))
            result = cursor.fetchone()
            
            if result and security_manager.verify_password(password, result[0]):
                self.current_student = student_name
                self.db_conn = conn
                self.is_authenticated = True
                self.session_token = security_manager.create_session_token(student_name)
                self.last_activity = datetime.now()
                security_manager.clear_failed_attempts(student_name)
                
                global enhanced_memory
                enhanced_memory = EnhancedMemorySystem(student_name)
                return True
            else:
                security_manager.record_failed_attempt(student_name)
                conn.close()
                return False
                
        except sqlite3.Error:
            conn.close()
            security_manager.record_failed_attempt(student_name)
            return False
    
    def set_student(self, student_name):
        """Legacy method - now requires authentication"""
        if not self.is_authenticated or self.current_student != student_name:
            return False
        return True
    
    def check_session_timeout(self) -> bool:
        """Check if session has timed out"""
        if not self.is_authenticated:
            return True
        
        if (datetime.now() - self.last_activity).seconds > self.session_timeout:
            self.logout()
            return True
        
        return False
    
    def refresh_activity(self):
        """Update last activity timestamp"""
        if self.is_authenticated:
            self.last_activity = datetime.now()
    
    def logout(self):
        """Logout current student"""
        self.current_student = None
        self.is_authenticated = False
        self.session_token = None
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None
    
    def close(self):
        if self.db_conn:
            self.db_conn.close()

session = Session()

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the HARV header"""
    clear_screen()
    print(HARV_HEADER)

def print_separator(char="═", length=80):
    """Print a separator line"""
    print(f"{Colors.CYAN}{char * length}{Colors.END}")

def print_status():
    """Print current session status"""
    api_status = f"{Colors.GREEN}✓ Connected{Colors.END}" if session.api_key_set else f"{Colors.RED}✗ Not Set{Colors.END}"
    student_status = f"{Colors.GREEN}{session.current_student}{Colors.END}" if session.current_student else f"{Colors.YELLOW}None Selected{Colors.END}"
    
    print(f"{Colors.BLUE}API Key: {api_status} │ Current Student: {student_status}{Colors.END}")
    print_separator("─")

def setup_api_key():
    """Enhanced secure API key setup"""
    global client, session
    
    print(f"\n{Colors.YELLOW}🔑 SECURE API KEY SETUP{Colors.END}")
    print_separator()
    
    # Check environment first
    current_key = os.getenv('OPENAI_API_KEY')
    if current_key:
        print(f"{Colors.GREEN}✓ API key found in environment{Colors.END}")
        try:
            client = OpenAI(api_key=current_key)
            # Test the key with a simple request
            client.models.list()
            session.api_key_set = True
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Invalid environment API key: {e}{Colors.END}")
    
    # Check secure storage
    secure_key_path = os.path.expanduser("~/.harv_api_key")
    if os.path.exists(secure_key_path):
        try:
            with open(secure_key_path, 'r') as f:
                stored_key = f.read().strip()
                if stored_key:
                    client = OpenAI(api_key=stored_key)
                    client.models.list()  # Test the key
                    session.api_key_set = True
                    print(f"{Colors.GREEN}✓ API key loaded from secure storage{Colors.END}")
                    return True
        except Exception as e:
            print(f"{Colors.RED}❌ Stored API key invalid: {e}{Colors.END}")
            os.remove(secure_key_path)  # Remove invalid key
    
    print(f"{Colors.CYAN}Enter your OpenAI API key:{Colors.END}")
    print(f"{Colors.YELLOW}⚠️  Key will be securely stored locally{Colors.END}")
    
    try:
        import getpass
        api_key = getpass.getpass(f"{Colors.BOLD}🔑 API Key: {Colors.END}")
    except (ImportError, OSError):
        api_key = input(f"{Colors.BOLD}🔑 API Key: {Colors.END}").strip()
    
    if api_key:
        # Validate API key format
        if not api_key.startswith('sk-') or len(api_key) < 20:
            print(f"{Colors.RED}❌ Invalid API key format{Colors.END}")
            return False
        
        try:
            client = OpenAI(api_key=api_key)
            # Test the key
            client.models.list()
            
            # Store securely
            with open(secure_key_path, 'w') as f:
                f.write(api_key)
            os.chmod(secure_key_path, 0o600)  # Read/write for owner only
            
            os.environ['OPENAI_API_KEY'] = api_key
            session.api_key_set = True
            print(f"{Colors.GREEN}✓ API key configured and securely stored!{Colors.END}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ Invalid API key: {e}{Colors.END}")
    
    return False

def list_students():
    """List all student profiles"""
    students_dir = "students"
    if not os.path.exists(students_dir):
        return []
    
    students = []
    for entry in os.scandir(students_dir):
        if entry.is_dir():
            db_path = os.path.join(entry.path, f"{entry.name}_harv.sqlite")
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT value FROM student_metadata WHERE key = 'created_date'")
                    result = cursor.fetchone()
                    created = result[0] if result else "Unknown"
                    conn.close()
                    students.append((entry.name, created))
                except:
                    students.append((entry.name, "Unknown"))
    
    return sorted(students, key=lambda x: x[1], reverse=True)

def create_student_profile():
    """Create a new student profile"""
    print(f"\n{Colors.YELLOW}🎓 CREATE STUDENT PROFILE{Colors.END}")
    print_separator()
    
    # Show existing students
    existing_students = [s[0] for s in list_students()]
    if existing_students:
        print(f"{Colors.BLUE}📚 Existing Students:{Colors.END}")
        for i, student in enumerate(existing_students[:5], 1):
            print(f"   {i}. {student}")
        if len(existing_students) > 5:
            print(f"   ... and {len(existing_students) - 5} more")
        print()
    
    while True:
        student_name = input(f"{Colors.BOLD}💭 Enter student name (or 'back' to return): {Colors.END}").strip()
        
        if student_name.lower() == 'back':
            return False
        
        if not student_name:
            print(f"{Colors.RED}❌ Student name cannot be empty!{Colors.END}")
            continue
        
        # Sanitize student name
        import re
        sanitized_name = re.sub(r'[^\w\-_]', '_', student_name)
        if sanitized_name != student_name:
            print(f"{Colors.YELLOW}📝 Student name sanitized to: {sanitized_name}{Colors.END}")
            student_name = sanitized_name
        
        if student_name in existing_students:
            print(f"{Colors.RED}❌ Student '{student_name}' already exists!{Colors.END}")
            continue
        
        break
    
    # Get student information
    print(f"\n{Colors.CYAN}📋 Student Registration Form{Colors.END}")
    print_separator("─", 40)
    
    email = input(f"{Colors.BOLD}Email: {Colors.END}").strip()
    reason = input(f"{Colors.BOLD}Why are you taking this course? {Colors.END}").strip()
    familiarity = input(f"{Colors.BOLD}Familiarity with mass communication (1-10): {Colors.END}").strip()
    learning_style = input(f"{Colors.BOLD}Preferred learning style: {Colors.END}").strip()
    goals = input(f"{Colors.BOLD}Learning goals: {Colors.END}").strip()
    background = input(f"{Colors.BOLD}Relevant background: {Colors.END}").strip()
    
    # Set up password with validation
    print(f"\n{Colors.YELLOW}🔐 Security Setup{Colors.END}")
    print_separator("─", 40)
    print(f"{Colors.CYAN}Password Requirements:{Colors.END}")
    print("  • At least 8 characters long")
    print("  • Contains uppercase and lowercase letters")
    print("  • Contains at least one number")
    print("  • Contains at least one special character (!@#$%^&*(),.?\":{}|<>)")
    print("  • Cannot contain common patterns (123, abc, password, etc.)")
    print()
    
    while True:
        try:
            import getpass
            password = getpass.getpass(f"{Colors.BOLD}🔑 Enter password: {Colors.END}")
        except (ImportError, OSError):
            # Fallback for systems without getpass
            password = input(f"{Colors.BOLD}🔑 Enter password: {Colors.END}")
        
        if not password:
            print(f"{Colors.RED}❌ Password cannot be empty!{Colors.END}")
            continue
        
        valid, message = security_manager.validate_password_strength(password)
        if not valid:
            print(f"{Colors.RED}❌ {message}{Colors.END}")
            continue
        
        try:
            password_confirm = getpass.getpass(f"{Colors.BOLD}🔑 Confirm password: {Colors.END}")
        except (ImportError, OSError):
            password_confirm = input(f"{Colors.BOLD}🔑 Confirm password: {Colors.END}")
        
        if password != password_confirm:
            print(f"{Colors.RED}❌ Passwords do not match!{Colors.END}")
            continue
        
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        break
    
    # Hash the password
    password_hash = security_manager.hash_password(password)
    
    # Create student profile
    if create_student_database(student_name, email, reason, familiarity, learning_style, goals, background, password_hash):
        # Authenticate the new student
        if session.authenticate_student(student_name, password):
            print(f"\n{Colors.GREEN}🎉 Student profile '{student_name}' created and authenticated!{Colors.END}")
            input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
            return True
        else:
            print(f"\n{Colors.RED}❌ Profile created but authentication failed!{Colors.END}")
    
    return False

def create_student_database(student_name, email, reason, familiarity, learning_style, goals, background, password_hash):
    """Create student database with all tables including authentication"""
    students_dir = "students"
    if not os.path.exists(students_dir):
        os.makedirs(students_dir)
    
    student_dir = os.path.join(students_dir, student_name)
    if os.path.exists(student_dir):
        return False
    
    os.makedirs(student_dir)
    db_path = os.path.join(student_dir, f"{student_name}_harv.sqlite")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create all tables
    tables = [
        """CREATE TABLE student_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        )""",
        """CREATE TABLE conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            message_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            session_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE module_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            questions_asked INTEGER DEFAULT 0,
            insights_gained TEXT,
            reflection_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE learning_reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            reflection_type TEXT,
            prompt TEXT,
            student_response TEXT,
            ai_followup TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE student_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept TEXT NOT NULL,
            understanding_level INTEGER,
            personal_connection TEXT,
            questions_remaining TEXT,
            discovered_at TEXT DEFAULT (datetime('now')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE learning_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            insight_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE exported_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER,
            export_format TEXT,
            filename TEXT,
            content TEXT,
            exported_at TEXT DEFAULT (datetime('now')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        """CREATE TABLE student_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    # Insert authentication record
    cursor.execute("""
        INSERT INTO student_auth (student_name, password_hash) 
        VALUES (?, ?)
    """, (student_name, password_hash))
    
    # Insert metadata
    cursor.execute("""
        INSERT INTO student_metadata (key, value) VALUES 
        ('student_name', ?),
        ('email', ?),
        ('reason', ?),
        ('familiarity', ?),
        ('learning_style', ?),
        ('goals', ?),
        ('background', ?),
        ('created_date', ?)
    """, (student_name, email, reason, familiarity, learning_style, goals, background, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True

def select_student():
    """Select and authenticate an existing student profile"""
    print(f"\n{Colors.YELLOW}👤 STUDENT LOGIN{Colors.END}")
    print_separator()
    
    students = list_students()
    if not students:
        print(f"{Colors.RED}❌ No student profiles found!{Colors.END}")
        print(f"{Colors.CYAN}💡 Create a new student profile first{Colors.END}")
        input(f"\nPress Enter to continue...")
        return False
    
    print(f"{Colors.BLUE}📚 Available Students:{Colors.END}")
    for i, (name, created) in enumerate(students, 1):
        date_str = created.split('T')[0] if 'T' in created else created
        print(f"   {Colors.BOLD}{i:2d}.{Colors.END} {name} {Colors.CYAN}(created: {date_str}){Colors.END}")
    
    while True:
        choice = input(f"\n{Colors.BOLD}Select student number (or 'back' to return): {Colors.END}").strip()
        
        if choice.lower() == 'back':
            return False
        
        try:
            student_idx = int(choice) - 1
            if 0 <= student_idx < len(students):
                student_name = students[student_idx][0]
                
                # Check if student is locked out
                if security_manager.is_locked_out(student_name):
                    print(f"{Colors.RED}🔒 Account locked due to failed attempts. Try again in 5 minutes.{Colors.END}")
                    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
                    return False
                
                # Get password
                print(f"\n{Colors.CYAN}🔐 Authentication Required{Colors.END}")
                try:
                    import getpass
                    password = getpass.getpass(f"{Colors.BOLD}🔑 Enter password for {student_name}: {Colors.END}")
                except (ImportError, OSError):
                    password = input(f"{Colors.BOLD}🔑 Enter password for {student_name}: {Colors.END}")
                
                if session.authenticate_student(student_name, password):
                    print(f"\n{Colors.GREEN}✅ Welcome back, {student_name}!{Colors.END}")
                    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
                    return True
                else:
                    if security_manager.is_locked_out(student_name):
                        print(f"{Colors.RED}🔒 Too many failed attempts. Account locked for 5 minutes.{Colors.END}")
                    else:
                        remaining = security_manager.max_attempts - security_manager.failed_attempts.get(student_name, (0, 0))[0]
                        print(f"{Colors.RED}❌ Invalid password. {remaining} attempts remaining.{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}❌ Please enter a number{Colors.END}")

def wait_for_key(prompt="Press any key to continue..."):
    """Wait for any key press"""
    print(f"\n{Colors.CYAN}{prompt}{Colors.END}")
    input()

def main_menu():
    """Enhanced main navigation menu with security features"""
    while True:
        try:
            print_header()
            
            # Check for session timeout if user is logged in
            if session.is_authenticated and session.check_session_timeout():
                print(f"\n{Colors.YELLOW}⏰ Session expired for security. Please log in again.{Colors.END}")
                input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
                continue
            
            if not session.api_key_set:
                print(f"\n{Colors.RED}⚠️  OpenAI API key required to continue{Colors.END}")
                if not setup_api_key():
                    print(f"{Colors.RED}❌ API key setup failed{Colors.END}")
                continue
            
            print(f"\n{Colors.BOLD}HARV CLI - Enhanced Security Edition{Colors.END}")
            print_separator()
            
            # Show current session status
            if session.is_authenticated:
                remaining_time = session.session_timeout - (datetime.now() - session.last_activity).seconds
                print(f"{Colors.GREEN}🔒 Logged in as: {session.current_student} (Session: {remaining_time//60}m remaining){Colors.END}")
                print()
            
            print(f"   {Colors.BOLD}1.{Colors.END} 🎓 New Student Profile")
            print(f"   {Colors.BOLD}2.{Colors.END} 👤 Student Login")
            if session.is_authenticated:
                print(f"   {Colors.BOLD}3.{Colors.END} 🏠 Student Dashboard")
                print(f"   {Colors.BOLD}4.{Colors.END} 🔓 Logout")
                print(f"   {Colors.BOLD}5.{Colors.END} 🌐 Connect to Backend")
                print(f"   {Colors.BOLD}6.{Colors.END} 📖 Getting Started")
                print(f"   {Colors.BOLD}7.{Colors.END} 🚪 Exit")
            else:
                print(f"   {Colors.BOLD}3.{Colors.END} 🌐 Connect to Backend")
                print(f"   {Colors.BOLD}4.{Colors.END} 📖 Getting Started")
                print(f"   {Colors.BOLD}5.{Colors.END} 🚪 Exit")
            
            choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
            
            if choice == "1":
                if create_student_profile():
                    student_menu()
            elif choice == "2":
                if select_student():
                    student_menu()
            elif choice == "3":
                if session.is_authenticated:
                    student_menu()
                else:
                    connect_backend()
            elif choice == "4":
                if session.is_authenticated:
                    session.logout()
                    print(f"{Colors.GREEN}✅ Successfully logged out{Colors.END}")
                    input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
                else:
                    show_getting_started()
            elif choice == "5":
                if session.is_authenticated:
                    connect_backend()
                else:
                    break
            elif choice == "6" and session.is_authenticated:
                show_getting_started()
            elif choice == "7" and session.is_authenticated:
                break
            elif choice == "5" and not session.is_authenticated:
                break
            else:
                print(f"{Colors.RED}❌ Invalid option{Colors.END}")
                
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}👋 Thank you for using HARV!{Colors.END}")
            print(f"{Colors.YELLOW}   Happy learning! 🎓✨{Colors.END}\n")
            break
            
        except Exception as e:
            print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
            input(f"{Colors.CYAN}Press Enter to continue...{Colors.END}")
            session.close()
            sys.exit(0)

def student_menu():
    """Student-specific menu"""
    while True:
        print_header()
        print_status()
        
        print(f"\n{Colors.BOLD}STUDENT DASHBOARD{Colors.END}")
        print_separator()
        
        print(f"   {Colors.BOLD}1.{Colors.END} 🎯 Browse Modules")
        print(f"   {Colors.BOLD}2.{Colors.END} 💬 Continue Conversation")
        print(f"   {Colors.BOLD}3.{Colors.END} 📊 View Progress")
        print(f"   {Colors.BOLD}4.{Colors.END} 🤔 Reflection Journal")
        print(f"   {Colors.BOLD}5.{Colors.END} 📤 Export Conversations")
        print(f"   {Colors.BOLD}6.{Colors.END} ⚙️  Settings")
        print(f"   {Colors.BOLD}0.{Colors.END} 🏠 Back to Main Menu")
        
        choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            browse_modules()
        elif choice == "2":
            continue_conversation()
        elif choice == "3":
            view_progress()
        elif choice == "4":
            reflection_journal()
        elif choice == "5":
            export_conversations()
        elif choice == "6":
            student_settings()

def browse_modules():
    """Browse available communication modules"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}📚 COMMUNICATION MEDIA MODULES{Colors.END}")
    print_separator()
    
    modules = [
        {"id": 1, "title": "Your Four Worlds", "description": "Communication models, perception, and reality"},
        {"id": 2, "title": "Media Uses & Effects", "description": "Functions vs effects, cultivation theory, agenda-setting"},
        {"id": 3, "title": "Shared Characteristics of Media", "description": "Common patterns across all media types"},
        {"id": 4, "title": "Communication Infrastructure", "description": "Telegraph, telephone, internet evolution"},
        {"id": 5, "title": "Books: Birth of Mass Communication", "description": "Publishing industry and cultural impact"},
        {"id": 6, "title": "News & Newspapers", "description": "News values, gatekeeping, journalism norms"},
        {"id": 7, "title": "Magazines: Special Interest Medium", "description": "Specialization and audience targeting"},
        {"id": 8, "title": "Comic Books: Small Business, Big Impact", "description": "Cultural influence and artistic expression"},
        {"id": 9, "title": "Photography: Fixing a Shadow", "description": "Visual communication and technology"},
        {"id": 10, "title": "Recordings: Bach to Rock & Rap", "description": "Music industry and cultural reflection"},
        {"id": 11, "title": "Motion Pictures: Mass Entertainment", "description": "Film industry and storytelling"},
        {"id": 12, "title": "Radio: The Pervasive Medium", "description": "Broadcasting and social role"},
        {"id": 13, "title": "Television: Center of Attention", "description": "TV dominance and cultural transformation"},
        {"id": 14, "title": "Video Games: Newest Mass Medium", "description": "Interactive entertainment and gaming culture"},
        {"id": 15, "title": "Economic Influencers", "description": "Advertising, PR, and media ownership"}
    ]
    
    for module in modules:
        progress = get_module_progress(module["id"])
        status_icon = "✅" if progress["completed"] else "🔄" if progress["started"] else "📖"
        
        print(f"   {Colors.BOLD}{module['id']:2d}. {status_icon} {module['title']}{Colors.END}")
        print(f"       {Colors.CYAN}{module['description']}{Colors.END}")
        if progress["started"]:
            print(f"       {Colors.YELLOW}Progress: {progress['questions_asked']} questions asked{Colors.END}")
        print()
    
    print(f"   {Colors.BOLD}0.{Colors.END} 🔙 Back")
    
    choice = input(f"\n{Colors.BOLD}Select module (1-15) or 0 to go back: {Colors.END}").strip()
    
    try:
        module_id = int(choice)
        if 1 <= module_id <= 15:
            start_module_conversation(module_id, modules[module_id-1])
        elif module_id == 0:
            return
    except ValueError:
        print(f"{Colors.RED}❌ Please enter a valid number{Colors.END}")
        wait_for_key()

def get_module_progress(module_id):
    """Get progress for a specific module"""
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT started_at, completed_at, questions_asked 
        FROM module_progress 
        WHERE module_id = ?
    """, (module_id,))
    
    result = cursor.fetchone()
    if result:
        started_at, completed_at, questions_asked = result
        return {
            "started": bool(started_at),
            "completed": bool(completed_at),
            "questions_asked": questions_asked or 0
        }
    
    return {"started": False, "completed": False, "questions_asked": 0}

def start_module_conversation(module_id, module_info):
    """Start or continue a Socratic conversation for a module with enhanced security"""
    # Check session timeout
    if session.check_session_timeout():
        print(f"{Colors.RED}🔒 Session expired. Please log in again.{Colors.END}")
        return
    
    session.refresh_activity()
    
    print_header()
    print(f"\n{Colors.BOLD}📖 MODULE {module_id}: {module_info['title'].upper()}{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}{module_info['description']}{Colors.END}")
    print()
    
    # Check if module already started
    try:
        progress = get_module_progress(module_id)
        if progress["started"]:
            print(f"{Colors.YELLOW}📚 Continuing your exploration of {module_info['title']}...{Colors.END}")
            print(f"{Colors.CYAN}Questions asked so far: {progress['questions_asked']}{Colors.END}")
        else:
            print(f"{Colors.GREEN}🎯 Starting your Socratic journey with {module_info['title']}...{Colors.END}")
            # Mark as started
            cursor = session.db_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO module_progress (module_id, started_at, questions_asked)
                VALUES (?, ?, 0)
            """, (module_id, datetime.now().isoformat()))
            session.db_conn.commit()
            
            # Save learning insight
            if enhanced_memory:
                enhanced_memory.save_learning_insight(module_id, f"Started module: {module_info['title']}")
                
    except Exception as e:
        print(f"{Colors.RED}❌ Error accessing module progress: {e}{Colors.END}")
        return
    
    print(f"\n{Colors.BOLD}💭 Remember: I won't give you direct answers.{Colors.END}")
    print(f"{Colors.BOLD}💭 I'll guide you to discover insights through questions.{Colors.END}")
    print()
    
    # Start conversation loop
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Get recent conversation context
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT message_type, content 
        FROM conversations 
        WHERE module_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    """, (module_id,))
    
    recent_context = cursor.fetchall()
    
    # Generate initial Socratic question if no recent context
    if not recent_context:
        initial_question = generate_socratic_question(module_id, module_info, None)
        save_conversation(module_id, "assistant", initial_question, session_id)
        print(f"{Colors.GREEN}🎓 HARV: {initial_question}{Colors.END}")
    else:
        print(f"{Colors.YELLOW}📜 Recent conversation context:{Colors.END}")
        for msg_type, content in reversed(recent_context[-4:]):  # Show last 4 messages
            if msg_type == "user":
                print(f"{Colors.BLUE}   You: {content}{Colors.END}")
            else:
                print(f"{Colors.GREEN}   HARV: {content}{Colors.END}")
    
    print(f"\n{Colors.CYAN}Type your response, 'help' for guidance, or 'exit' to leave:{Colors.END}")
    
    while True:
        user_input = input(f"\n{Colors.BOLD}You: {Colors.END}").strip()
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'help':
            show_conversation_help()
            continue
        elif not user_input:
            continue
        
        # Save user message
        save_conversation(module_id, "user", user_input, session_id)
        
        # Generate Socratic response
        print(f"{Colors.CYAN}🤔 HARV is thinking...{Colors.END}")
        
        response = generate_socratic_response(module_id, module_info, user_input)
        save_conversation(module_id, "assistant", response, session_id)
        
        # Update progress
        update_module_progress(module_id)
        
        print(f"\n{Colors.GREEN}🎓 HARV: {response}{Colors.END}")
    
    print(f"\n{Colors.YELLOW}📚 Great exploration! Your insights have been saved.{Colors.END}")
    wait_for_key()

def generate_socratic_question(module_id, module_info, context=None):
    """Generate an initial Socratic question for a module"""
    if not session.api_key_set:
        return f"Let's explore {module_info['title']}. What comes to mind when you think about {module_info['title'].lower()}?"
    
    system_prompts = {
        1: "You are Harv, a Socratic tutor for communication theory. Guide students to discover the four worlds of communication through strategic questioning about perception, reality, and media influence. Never give direct answers - only ask questions that lead to discovery.",
        2: "Guide students to discover the difference between media functions and effects through Socratic questioning about cultivation theory, agenda-setting, and media influence. Focus on questioning rather than explaining.",
        3: "Use Socratic questioning to help students identify universal patterns and characteristics that exist across all forms of media. Lead them to discover through questions.",
        4: "Lead students to understand the evolution of communication infrastructure through strategic questions about technological development and social impact.",
        5: "Guide students to discover how books became the first mass medium and their transformative cultural impact through Socratic inquiry.",
        6: "Use Socratic questioning to help students understand how news is constructed, what makes something 'newsworthy,' and the role of gatekeepers.",
        7: "Guide students to understand how magazines evolved from general interest to specialized publications through strategic questioning.",
        8: "Use Socratic questioning to explore how comic books, despite being a small industry, have had significant cultural impact.",
        9: "Lead students to understand how photography changed human communication and perception through strategic questioning.",
        10: "Guide students to understand how recorded music reflects and shapes culture through Socratic questioning about music industry evolution.",
        11: "Use strategic questioning to help students understand how motion pictures became the first mass entertainment medium.",
        12: "Guide students to discover why radio became the most pervasive medium and its unique social role through Socratic questioning.",
        13: "Use Socratic questioning to help students understand why television became the dominant medium and its cultural impact.",
        14: "Guide students to understand how video games represent a new form of mass communication through strategic questioning.",
        15: "Use Socratic questioning to help students understand how economic forces shape media content and industry practices."
    }
    
    try:
        prompt = f"""
        {system_prompts.get(module_id, "You are a Socratic tutor. Ask questions to guide learning, never give direct answers.")}
        
        Module: {module_info['title']}
        Description: {module_info['description']}
        
        Generate an engaging opening question that will start the student thinking about this topic. 
        The question should be thought-provoking and encourage personal reflection.
        Keep it under 2 sentences.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Harv, a Socratic AI tutor. You guide learning through questions, never direct answers."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"{Colors.RED}❌ API Error: {e}{Colors.END}")
        return f"Let's explore {module_info['title']}. What's your first thought when you hear about {module_info['title'].lower()}?"

def generate_socratic_response(module_id, module_info, user_input):
    """Generate enhanced Socratic response with adaptive context"""
    if not session.api_key_set:
        return "That's interesting. What makes you think that? Can you tell me more about your reasoning?"
    
    # Get conversation context
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT message_type, content 
        FROM conversations 
        WHERE module_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 6
    """, (module_id,))
    
    context_messages = []
    for msg_type, content in reversed(cursor.fetchall()):
        role = "user" if msg_type == "user" else "assistant"
        context_messages.append({"role": role, "content": content})
    
    # Get adaptive context from enhanced memory system
    adaptive_context = ""
    if enhanced_memory:
        adaptive_context = enhanced_memory.get_adaptive_context(module_id)
        
        # Analyze learning patterns for insights
        patterns = enhanced_memory.analyze_learning_patterns()
        if patterns and module_id in patterns.get('module_patterns', {}):
            pattern = patterns['module_patterns'][module_id]
            if pattern['engagement_level'] < 0.5:
                adaptive_context += " Focus on engaging the student with interactive examples."
            if pattern['curiosity_level'] > 0.8:
                adaptive_context += " The student is highly curious - provide deeper explanations."
    
    system_prompts = {
        1: "You are Harv, a Socratic tutor for communication theory. Guide students to discover the four worlds of communication through strategic questioning about perception, reality, and media influence.",
        2: "Guide students to discover the difference between media functions and effects through Socratic questioning about cultivation theory, agenda-setting, and media influence.",
        3: "Use Socratic questioning to help students identify universal patterns and characteristics that exist across all forms of media.",
        4: "Lead students to understand the evolution of communication infrastructure through strategic questions about technological development and social impact.",
        5: "Guide students to discover how books became the first mass medium and their transformative cultural impact through Socratic inquiry.",
        6: "Use Socratic questioning to help students understand how news is constructed, what makes something 'newsworthy,' and the role of gatekeepers.",
        7: "Guide students to understand how magazines evolved from general interest to specialized publications through strategic questioning.",
        8: "Use Socratic questioning to explore how comic books, despite being a small industry, have had significant cultural impact.",
        9: "Lead students to understand how photography changed human communication and perception through strategic questioning.",
        10: "Guide students to understand how recorded music reflects and shapes culture through Socratic questioning about music industry evolution.",
        11: "Use strategic questioning to help students understand how motion pictures became the first mass entertainment medium.",
        12: "Guide students to discover why radio became the most pervasive medium and its unique social role through Socratic questioning.",
        13: "Use Socratic questioning to help students understand why television became the dominant medium and its cultural impact.",
        14: "Guide students to understand how video games represent a new form of mass communication through strategic questioning.",
        15: "Use Socratic questioning to help students understand how economic forces shape media content and industry practices."
    }
    
    try:
        base_prompt = system_prompts.get(module_id, "You are a Socratic tutor. Ask questions to guide learning, never give direct answers.")
        
        # Integrate adaptive context
        if adaptive_context:
            base_prompt += f"\n\nAdaptive Teaching Context: {adaptive_context}"
        
        messages = [
            {"role": "system", "content": f"""
            {base_prompt}
            
            IMPORTANT RULES:
            1. NEVER give direct answers or explanations
            2. ALWAYS respond with thoughtful questions
            3. Build on the student's response to guide deeper thinking
            4. Encourage personal connections and examples
            5. Keep responses to 1-2 sentences maximum
            6. Be encouraging and supportive
            
            Module: {module_info['title']}
            Topic: {module_info['description']}
            """}
        ]
        
        # Add conversation context
        messages.extend(context_messages[-4:])  # Last 4 messages for context
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"{Colors.RED}❌ API Error: {e}{Colors.END}")
        return "That's a thoughtful response. What led you to that conclusion? Can you think of a specific example?"

def save_conversation(module_id, message_type, content, session_id):
    """Save conversation message to database"""
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO conversations (module_id, message_type, content, session_id, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (module_id, message_type, content, session_id, datetime.now().isoformat()))
    session.db_conn.commit()

def update_module_progress(module_id):
    """Update module progress"""
    cursor = session.db_conn.cursor()
    cursor.execute("""
        UPDATE module_progress 
        SET questions_asked = questions_asked + 1
        WHERE module_id = ?
    """, (module_id,))
    session.db_conn.commit()

def show_conversation_help():
    """Show help during conversation"""
    print(f"\n{Colors.YELLOW}💡 CONVERSATION TIPS{Colors.END}")
    print_separator("─", 40)
    print(f"{Colors.CYAN}• Share your thoughts and reasoning{Colors.END}")
    print(f"{Colors.CYAN}• Give specific examples when possible{Colors.END}")
    print(f"{Colors.CYAN}• Don't worry about being 'right' - explore ideas{Colors.END}")
    print(f"{Colors.CYAN}• Connect concepts to your own experience{Colors.END}")
    print(f"{Colors.CYAN}• Ask for clarification if you're confused{Colors.END}")
    print(f"{Colors.CYAN}• Type 'exit' when you're ready to leave{Colors.END}")

def continue_conversation():
    """Continue the most recent conversation"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}💬 CONTINUE CONVERSATION{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT DISTINCT module_id, MAX(timestamp) as last_time
        FROM conversations 
        GROUP BY module_id 
        ORDER BY last_time DESC 
        LIMIT 5
    """)
    
    recent_modules = cursor.fetchall()
    
    if not recent_modules:
        print(f"{Colors.YELLOW}📚 No recent conversations found.{Colors.END}")
        print(f"{Colors.CYAN}💡 Start by browsing modules.{Colors.END}")
        wait_for_key()
        return
    
    print(f"{Colors.BLUE}Recent Conversations:{Colors.END}")
    
    modules_info = {
        1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
        4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
        7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
        10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
        13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
    }
    
    for i, (module_id, last_time) in enumerate(recent_modules, 1):
        module_title = modules_info.get(module_id, f"Module {module_id}")
        time_str = last_time.split('T')[0] if 'T' in last_time else last_time
        print(f"   {Colors.BOLD}{i}.{Colors.END} {module_title} {Colors.CYAN}({time_str}){Colors.END}")
    
    print(f"   {Colors.BOLD}0.{Colors.END} 🔙 Back")
    
    choice = input(f"\n{Colors.BOLD}Select conversation to continue: {Colors.END}").strip()
    
    try:
        conv_idx = int(choice)
        if conv_idx == 0:
            return
        elif 1 <= conv_idx <= len(recent_modules):
            module_id = recent_modules[conv_idx-1][0]
            module_info = {
                "id": module_id,
                "title": modules_info.get(module_id, f"Module {module_id}"),
                "description": "Continuing your exploration..."
            }
            start_module_conversation(module_id, module_info)
    except ValueError:
        print(f"{Colors.RED}❌ Please enter a valid number{Colors.END}")
        wait_for_key()

def view_progress():
    """View student progress across all modules"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}📊 LEARNING PROGRESS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT module_id, started_at, completed_at, questions_asked 
        FROM module_progress 
        ORDER BY module_id
    """)
    
    progress_data = cursor.fetchall()
    
    if not progress_data:
        print(f"{Colors.YELLOW}📚 No modules started yet.{Colors.END}")
        print(f"{Colors.CYAN}💡 Visit 'Browse Modules' to begin your learning journey.{Colors.END}")
        wait_for_key()
        return
    
    modules_info = {
        1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
        4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
        7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
        10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
        13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
    }
    
    completed_count = 0
    total_questions = 0
    
    print(f"{Colors.BLUE}Module Progress:{Colors.END}\n")
    
    for module_id, started_at, completed_at, questions_asked in progress_data:
        module_title = modules_info.get(module_id, f"Module {module_id}")
        status = "✅ Completed" if completed_at else "🔄 In Progress"
        
        if completed_at:
            completed_count += 1
        
        total_questions += questions_asked or 0
        
        print(f"   {Colors.BOLD}{module_id:2d}. {module_title}{Colors.END}")
        print(f"       Status: {Colors.GREEN if completed_at else Colors.YELLOW}{status}{Colors.END}")
        print(f"       Questions: {Colors.CYAN}{questions_asked or 0}{Colors.END}")
        
        if started_at:
            start_date = started_at.split('T')[0] if 'T' in started_at else started_at
            print(f"       Started: {Colors.CYAN}{start_date}{Colors.END}")
        
        print()
    
    print(f"{Colors.BOLD}📈 Summary:{Colors.END}")
    print(f"   Modules Started: {Colors.GREEN}{len(progress_data)}/15{Colors.END}")
    print(f"   Modules Completed: {Colors.GREEN}{completed_count}/15{Colors.END}")
    print(f"   Total Questions Asked: {Colors.CYAN}{total_questions}{Colors.END}")
    
    # Progress bar
    progress_percent = (len(progress_data) / 15) * 100
    progress_bar = "█" * int(progress_percent // 5) + "░" * (20 - int(progress_percent // 5))
    print(f"   Progress: {Colors.GREEN}[{progress_bar}] {progress_percent:.0f}%{Colors.END}")
    
    wait_for_key()

def reflection_journal():
    """Personal reflection journal"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}🤔 REFLECTION JOURNAL{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} ✍️  New Reflection")
    print(f"   {Colors.BOLD}2.{Colors.END} 📖 View Reflections")
    print(f"   {Colors.BOLD}3.{Colors.END} 💡 Insights Tracker")
    print(f"   {Colors.BOLD}0.{Colors.END} 🔙 Back")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    if choice == "1":
        new_reflection()
    elif choice == "2":
        view_reflections()
    elif choice == "3":
        insights_tracker()
    elif choice == "0":
        return

def new_reflection():
    """Create a new reflection entry"""
    print(f"\n{Colors.YELLOW}✍️  NEW REFLECTION{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}What would you like to reflect on?{Colors.END}")
    print(f"   {Colors.BOLD}1.{Colors.END} Specific module concept")
    print(f"   {Colors.BOLD}2.{Colors.END} Personal insight or connection")
    print(f"   {Colors.BOLD}3.{Colors.END} Question that emerged")
    print(f"   {Colors.BOLD}4.{Colors.END} General learning reflection")
    
    reflection_type = input(f"\n{Colors.BOLD}Select type: {Colors.END}").strip()
    
    type_mapping = {
        "1": "concept_reflection",
        "2": "personal_connection", 
        "3": "emerging_question",
        "4": "general_reflection"
    }
    
    reflection_category = type_mapping.get(reflection_type, "general_reflection")
    
    # Get module context if relevant
    module_id = None
    if reflection_type in ["1", "3"]:
        module_input = input(f"{Colors.BOLD}Which module (1-15, or press Enter to skip): {Colors.END}").strip()
        try:
            module_id = int(module_input) if module_input else None
        except ValueError:
            pass
    
    print(f"\n{Colors.CYAN}Write your reflection (press Enter twice when finished):{Colors.END}")
    
    reflection_lines = []
    empty_lines = 0
    
    while empty_lines < 2:
        line = input()
        if line.strip():
            reflection_lines.append(line)
            empty_lines = 0
        else:
            empty_lines += 1
            if empty_lines == 1:
                reflection_lines.append("")
    
    reflection_text = "\n".join(reflection_lines).strip()
    
    if reflection_text:
        cursor = session.db_conn.cursor()
        cursor.execute("""
            INSERT INTO learning_reflections (module_id, reflection_type, student_response)
            VALUES (?, ?, ?)
        """, (module_id, reflection_category, reflection_text))
        session.db_conn.commit()
        
        print(f"\n{Colors.GREEN}✅ Reflection saved!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}No reflection entered.{Colors.END}")
    
    wait_for_key()

def view_reflections():
    """View saved reflections"""
    print(f"\n{Colors.YELLOW}📖 YOUR REFLECTIONS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT module_id, reflection_type, student_response, timestamp 
        FROM learning_reflections 
        ORDER BY timestamp DESC
    """)
    
    reflections = cursor.fetchall()
    
    if not reflections:
        print(f"{Colors.CYAN}No reflections yet. Start by creating one!{Colors.END}")
        wait_for_key()
        return
    
    modules_info = {
        1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
        4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
        7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
        10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
        13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
    }
    
    type_names = {
        "concept_reflection": "💭 Concept Reflection",
        "personal_connection": "🔗 Personal Connection",
        "emerging_question": "❓ Emerging Question",
        "general_reflection": "📝 General Reflection"
    }
    
    for i, (module_id, reflection_type, response, timestamp) in enumerate(reflections, 1):
        module_name = modules_info.get(module_id, "General") if module_id else "General"
        type_name = type_names.get(reflection_type, "📝 Reflection")
        date_str = timestamp.split('T')[0] if 'T' in timestamp else timestamp.split()[0]
        
        print(f"{Colors.BOLD}{i}. {type_name}{Colors.END}")
        print(f"   Module: {Colors.CYAN}{module_name}{Colors.END}")
        print(f"   Date: {Colors.YELLOW}{date_str}{Colors.END}")
        print(f"   {Colors.GREEN}{response[:100]}{'...' if len(response) > 100 else ''}{Colors.END}")
        print()
    
    wait_for_key()

def insights_tracker():
    """Track key insights and understanding"""
    print(f"\n{Colors.YELLOW}💡 INSIGHTS TRACKER{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} 📝 Record New Insight")
    print(f"   {Colors.BOLD}2.{Colors.END} 📊 View All Insights")
    print(f"   {Colors.BOLD}3.{Colors.END} 🎯 Update Understanding Level")
    print(f"   {Colors.BOLD}0.{Colors.END} 🔙 Back")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    if choice == "1":
        record_insight()
    elif choice == "2":
        view_insights()
    elif choice == "3":
        update_understanding()
    elif choice == "0":
        return

def record_insight():
    """Record a new insight"""
    print(f"\n{Colors.YELLOW}📝 RECORD NEW INSIGHT{Colors.END}")
    print_separator()
    
    concept = input(f"{Colors.BOLD}What concept or idea did you gain insight about? {Colors.END}").strip()
    if not concept:
        return
    
    print(f"\n{Colors.CYAN}Understanding Level (1-10):{Colors.END}")
    print(f"1-3: Just starting to grasp it")
    print(f"4-6: Developing understanding")
    print(f"7-9: Strong comprehension")
    print(f"10: Can teach it to others")
    
    try:
        level = int(input(f"{Colors.BOLD}Level: {Colors.END}").strip())
        level = max(1, min(10, level))  # Clamp between 1-10
    except ValueError:
        level = 5
    
    connection = input(f"{Colors.BOLD}Personal connection or example: {Colors.END}").strip()
    questions = input(f"{Colors.BOLD}Questions you still have: {Colors.END}").strip()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        INSERT INTO student_insights (concept, understanding_level, personal_connection, questions_remaining)
        VALUES (?, ?, ?, ?)
    """, (concept, level, connection, questions))
    session.db_conn.commit()
    
    print(f"\n{Colors.GREEN}✅ Insight recorded!{Colors.END}")
    wait_for_key()

def view_insights():
    """View all recorded insights"""
    print(f"\n{Colors.YELLOW}📊 YOUR INSIGHTS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT concept, understanding_level, personal_connection, questions_remaining, discovered_at
        FROM student_insights 
        ORDER BY discovered_at DESC
    """)
    
    insights = cursor.fetchall()
    
    if not insights:
        print(f"{Colors.CYAN}No insights recorded yet. Capture your learning moments!{Colors.END}")
        wait_for_key()
        return
    
    for i, (concept, level, connection, questions, date) in enumerate(insights, 1):
        level_bar = "█" * level + "░" * (10 - level)
        date_str = date.split('T')[0] if 'T' in date else date.split()[0]
        
        print(f"{Colors.BOLD}{i}. {concept}{Colors.END}")
        print(f"   Understanding: {Colors.GREEN}[{level_bar}] {level}/10{Colors.END}")
        print(f"   Date: {Colors.YELLOW}{date_str}{Colors.END}")
        
        if connection:
            print(f"   Connection: {Colors.CYAN}{connection}{Colors.END}")
        
        if questions:
            print(f"   Questions: {Colors.YELLOW}{questions}{Colors.END}")
        
        print()
    
    wait_for_key()

def update_understanding():
    """Update understanding level for an existing insight"""
    print(f"\n{Colors.YELLOW}🎯 UPDATE UNDERSTANDING{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT id, concept, understanding_level FROM student_insights ORDER BY discovered_at DESC")
    insights = cursor.fetchall()
    
    if not insights:
        print(f"{Colors.CYAN}No insights to update yet.{Colors.END}")
        wait_for_key()
        return
    
    print(f"{Colors.BLUE}Select insight to update:{Colors.END}")
    for i, (insight_id, concept, level) in enumerate(insights, 1):
        print(f"   {Colors.BOLD}{i}.{Colors.END} {concept} (Level {level})")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select insight: {Colors.END}").strip())
        if 1 <= choice <= len(insights):
            insight_id, concept, current_level = insights[choice-1]
            
            print(f"\n{Colors.CYAN}Current understanding level for '{concept}': {current_level}/10{Colors.END}")
            new_level = int(input(f"{Colors.BOLD}New level (1-10): {Colors.END}").strip())
            new_level = max(1, min(10, new_level))
            
            cursor.execute("""
                UPDATE student_insights 
                SET understanding_level = ?, discovered_at = datetime('now')
                WHERE id = ?
            """, (new_level, insight_id))
            session.db_conn.commit()
            
            print(f"\n{Colors.GREEN}✅ Understanding level updated to {new_level}/10!{Colors.END}")
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
    
    wait_for_key()

def export_conversations():
    """Export conversations for submission or review"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}📤 EXPORT CONVERSATIONS{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} 📄 Export Single Module")
    print(f"   {Colors.BOLD}2.{Colors.END} 📚 Export All Conversations")
    print(f"   {Colors.BOLD}3.{Colors.END} 📋 Export Progress Summary")
    print(f"   {Colors.BOLD}0.{Colors.END} 🔙 Back")
    
    choice = input(f"\n{Colors.BOLD}Select export option: {Colors.END}").strip()
    
    if choice == "1":
        export_single_module()
    elif choice == "2":
        export_all_conversations()
    elif choice == "3":
        export_progress_summary()
    elif choice == "0":
        return

def export_single_module():
    """Export conversations for a single module"""
    print(f"\n{Colors.YELLOW}📄 EXPORT SINGLE MODULE{Colors.END}")
    print_separator()
    
    # Get modules with conversations
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT DISTINCT module_id, COUNT(*) as message_count
        FROM conversations 
        GROUP BY module_id 
        ORDER BY module_id
    """)
    
    modules_with_convs = cursor.fetchall()
    
    if not modules_with_convs:
        print(f"{Colors.YELLOW}No conversations to export yet.{Colors.END}")
        wait_for_key()
        return
    
    modules_info = {
        1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
        4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
        7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
        10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
        13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
    }
    
    print(f"{Colors.BLUE}Modules with conversations:{Colors.END}")
    for i, (module_id, count) in enumerate(modules_with_convs, 1):
        module_title = modules_info.get(module_id, f"Module {module_id}")
        print(f"   {Colors.BOLD}{i}.{Colors.END} {module_title} ({count} messages)")
    
    try:
        choice = int(input(f"\n{Colors.BOLD}Select module: {Colors.END}").strip())
        if 1 <= choice <= len(modules_with_convs):
            module_id = modules_with_convs[choice-1][0]
            module_title = modules_info.get(module_id, f"Module {module_id}")
            
            # Export format choice
            print(f"\n{Colors.CYAN}Export format:{Colors.END}")
            print(f"   {Colors.BOLD}1.{Colors.END} TXT (Plain text)")
            print(f"   {Colors.BOLD}2.{Colors.END} PDF (Formatted)")
            
            format_choice = input(f"\n{Colors.BOLD}Select format: {Colors.END}").strip()
            export_format = "pdf" if format_choice == "2" else "txt"
            
            export_module_conversation(module_id, module_title, export_format)
            
    except (ValueError, IndexError):
        print(f"{Colors.RED}❌ Invalid selection{Colors.END}")
        wait_for_key()

def export_module_conversation(module_id, module_title, format_type):
    """Export a specific module's conversation"""
    cursor = session.db_conn.cursor()
    cursor.execute("""
        SELECT message_type, content, timestamp 
        FROM conversations 
        WHERE module_id = ? 
        ORDER BY timestamp
    """, (module_id,))
    
    messages = cursor.fetchall()
    
    if not messages:
        print(f"{Colors.YELLOW}No messages found for this module.{Colors.END}")
        wait_for_key()
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session.current_student}_Module{module_id}_{timestamp}.{format_type}"
    
    # Create exports directory
    export_dir = f"students/{session.current_student}/exports"
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"HARV CONVERSATION EXPORT\n")
            f.write(f"Student: {session.current_student}\n")
            f.write(f"Module: {module_title}\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for message_type, content, timestamp in messages:
                speaker = "You" if message_type == "user" else "HARV"
                time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp.split()[1][:8]
                
                f.write(f"[{time_str}] {speaker}: {content}\n\n")
        
        # Save export record
        cursor.execute("""
            INSERT INTO exported_conversations (module_id, export_format, filename, content)
            VALUES (?, ?, ?, ?)
        """, (module_id, format_type, filename, f"Exported {len(messages)} messages"))
        session.db_conn.commit()
        
        print(f"\n{Colors.GREEN}✅ Conversation exported to: {filepath}{Colors.END}")
        print(f"{Colors.CYAN}📄 {len(messages)} messages exported{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Export failed: {e}{Colors.END}")
    
    wait_for_key()

def export_all_conversations():
    """Export all conversations"""
    print(f"\n{Colors.YELLOW}📚 EXPORT ALL CONVERSATIONS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_messages = cursor.fetchone()[0]
    
    if total_messages == 0:
        print(f"{Colors.YELLOW}No conversations to export yet.{Colors.END}")
        wait_for_key()
        return
    
    print(f"{Colors.CYAN}This will export {total_messages} total messages across all modules.{Colors.END}")
    confirm = input(f"{Colors.BOLD}Continue? (y/n): {Colors.END}").strip().lower()
    
    if confirm != 'y':
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session.current_student}_AllConversations_{timestamp}.txt"
    
    export_dir = f"students/{session.current_student}/exports"
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)
    
    modules_info = {
        1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
        4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
        7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
        10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
        13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"HARV COMPLETE CONVERSATION EXPORT\n")
            f.write(f"Student: {session.current_student}\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Export by module
            cursor.execute("""
                SELECT DISTINCT module_id 
                FROM conversations 
                ORDER BY module_id
            """)
            
            modules = [row[0] for row in cursor.fetchall()]
            
            for module_id in modules:
                module_title = modules_info.get(module_id, f"Module {module_id}")
                f.write(f"\nMODULE {module_id}: {module_title.upper()}\n")
                f.write("-" * 50 + "\n\n")
                
                cursor.execute("""
                    SELECT message_type, content, timestamp 
                    FROM conversations 
                    WHERE module_id = ? 
                    ORDER BY timestamp
                """, (module_id,))
                
                messages = cursor.fetchall()
                for message_type, content, timestamp in messages:
                    speaker = "You" if message_type == "user" else "HARV"
                    time_str = timestamp.split('T')[1][:8] if 'T' in timestamp else timestamp.split()[1][:8]
                    f.write(f"[{time_str}] {speaker}: {content}\n\n")
        
        print(f"\n{Colors.GREEN}✅ All conversations exported to: {filepath}{Colors.END}")
        print(f"{Colors.CYAN}📄 {total_messages} messages across {len(modules)} modules{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Export failed: {e}{Colors.END}")
    
    wait_for_key()

def export_progress_summary():
    """Export learning progress summary"""
    print(f"\n{Colors.YELLOW}📋 EXPORT PROGRESS SUMMARY{Colors.END}")
    print_separator()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session.current_student}_ProgressSummary_{timestamp}.txt"
    
    export_dir = f"students/{session.current_student}/exports"
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)
    
    try:
        cursor = session.db_conn.cursor()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"HARV LEARNING PROGRESS SUMMARY\n")
            f.write(f"Student: {session.current_student}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Student metadata
            cursor.execute("SELECT key, value FROM student_metadata")
            metadata = dict(cursor.fetchall())
            
            f.write("STUDENT PROFILE\n")
            f.write("-" * 20 + "\n")
            f.write(f"Name: {metadata.get('student_name', 'Unknown')}\n")
            f.write(f"Email: {metadata.get('email', 'Not provided')}\n")
            f.write(f"Course reason: {metadata.get('reason', 'Not provided')}\n")
            f.write(f"Familiarity level: {metadata.get('familiarity', 'Not provided')}\n")
            f.write(f"Learning style: {metadata.get('learning_style', 'Not provided')}\n")
            f.write(f"Goals: {metadata.get('goals', 'Not provided')}\n")
            f.write(f"Background: {metadata.get('background', 'Not provided')}\n\n")
            
            # Module progress
            cursor.execute("""
                SELECT module_id, started_at, completed_at, questions_asked 
                FROM module_progress 
                ORDER BY module_id
            """)
            progress_data = cursor.fetchall()
            
            f.write("MODULE PROGRESS\n")
            f.write("-" * 20 + "\n")
            
            modules_info = {
                1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
                4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
                7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
                10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
                13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
            }
            
            completed_count = 0
            total_questions = 0
            
            for module_id, started_at, completed_at, questions_asked in progress_data:
                module_title = modules_info.get(module_id, f"Module {module_id}")
                status = "Completed" if completed_at else "In Progress"
                
                if completed_at:
                    completed_count += 1
                total_questions += questions_asked or 0
                
                f.write(f"Module {module_id}: {module_title}\n")
                f.write(f"  Status: {status}\n")
                f.write(f"  Questions Asked: {questions_asked or 0}\n")
                if started_at:
                    f.write(f"  Started: {started_at.split('T')[0]}\n")
                if completed_at:
                    f.write(f"  Completed: {completed_at.split('T')[0]}\n")
                f.write("\n")
            
            f.write(f"SUMMARY STATISTICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Modules Started: {len(progress_data)}/15\n")
            f.write(f"Modules Completed: {completed_count}/15\n")
            f.write(f"Total Questions Asked: {total_questions}\n")
            f.write(f"Progress: {(len(progress_data)/15)*100:.0f}%\n\n")
            
            # Recent insights
            cursor.execute("""
                SELECT concept, understanding_level, personal_connection 
                FROM student_insights 
                ORDER BY discovered_at DESC 
                LIMIT 10
            """)
            insights = cursor.fetchall()
            
            if insights:
                f.write("RECENT INSIGHTS\n")
                f.write("-" * 20 + "\n")
                for concept, level, connection in insights:
                    f.write(f"• {concept} (Understanding: {level}/10)\n")
                    if connection:
                        f.write(f"  Connection: {connection}\n")
                    f.write("\n")
        
        print(f"\n{Colors.GREEN}✅ Progress summary exported to: {filepath}{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Export failed: {e}{Colors.END}")
    
    wait_for_key()

def student_settings():
    """Student settings and preferences"""
    print_header()
    print_status()
    
    print(f"\n{Colors.BOLD}⚙️  STUDENT SETTINGS{Colors.END}")
    print_separator()
    
    print(f"   {Colors.BOLD}1.{Colors.END} 👤 Update Profile")
    print(f"   {Colors.BOLD}2.{Colors.END} 🎯 Learning Preferences") 
    print(f"   {Colors.BOLD}3.{Colors.END} 📊 View Statistics")
    print(f"   {Colors.BOLD}4.{Colors.END} 🗑️  Clear Data")
    print(f"   {Colors.BOLD}0.{Colors.END} 🔙 Back")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    if choice == "1":
        update_profile()
    elif choice == "2":
        learning_preferences()
    elif choice == "3":
        view_statistics()
    elif choice == "4":
        clear_data()
    elif choice == "0":
        return

def update_profile():
    """Update student profile information"""
    print(f"\n{Colors.YELLOW}👤 UPDATE PROFILE{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    cursor.execute("SELECT key, value FROM student_metadata")
    current_data = dict(cursor.fetchall())
    
    print(f"{Colors.BLUE}Current Profile (press Enter to keep current value):{Colors.END}")
    
    fields = [
        ('email', 'Email'),
        ('reason', 'Course reason'),
        ('familiarity', 'Familiarity level (1-10)'),
        ('learning_style', 'Learning style'),
        ('goals', 'Learning goals'),
        ('background', 'Background')
    ]
    
    updates = {}
    
    for key, label in fields:
        current_value = current_data.get(key, 'Not set')
        new_value = input(f"{Colors.BOLD}{label} [{current_value}]: {Colors.END}").strip()
        
        if new_value:
            updates[key] = new_value
    
    if updates:
        for key, value in updates.items():
            cursor.execute("""
                UPDATE student_metadata 
                SET value = ?, updated_at = datetime('now') 
                WHERE key = ?
            """, (value, key))
        
        session.db_conn.commit()
        print(f"\n{Colors.GREEN}✅ Profile updated!{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}No changes made.{Colors.END}")
    
    wait_for_key()

def learning_preferences():
    """Manage learning preferences"""
    print(f"\n{Colors.YELLOW}🎯 LEARNING PREFERENCES{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}This feature will be available in a future update.{Colors.END}")
    print(f"Planned features:")
    print(f"• Adjust question difficulty")
    print(f"• Set conversation pace")
    print(f"• Choose feedback style")
    print(f"• Configure export formats")
    
    wait_for_key()

def view_statistics():
    """View detailed learning statistics"""
    print(f"\n{Colors.YELLOW}📊 LEARNING STATISTICS{Colors.END}")
    print_separator()
    
    cursor = session.db_conn.cursor()
    
    # Basic stats
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversations WHERE message_type = 'user'")
    user_messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT module_id) FROM conversations")
    modules_engaged = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM learning_reflections")
    reflections_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM student_insights")
    insights_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM exported_conversations")
    exports_count = cursor.fetchone()[0]
    
    # Time-based stats
    cursor.execute("""
        SELECT MIN(timestamp), MAX(timestamp) 
        FROM conversations
    """)
    time_range = cursor.fetchone()
    
    print(f"{Colors.BLUE}Learning Activity Summary:{Colors.END}\n")
    
    print(f"   📝 Total Messages: {Colors.GREEN}{total_messages}{Colors.END}")
    print(f"   💬 Your Messages: {Colors.GREEN}{user_messages}{Colors.END}")
    print(f"   📚 Modules Engaged: {Colors.GREEN}{modules_engaged}/15{Colors.END}")
    print(f"   🤔 Reflections: {Colors.GREEN}{reflections_count}{Colors.END}")
    print(f"   💡 Insights Recorded: {Colors.GREEN}{insights_count}{Colors.END}")
    print(f"   📤 Exports Created: {Colors.GREEN}{exports_count}{Colors.END}")
    
    if time_range[0] and time_range[1]:
        first_date = time_range[0].split('T')[0]
        last_date = time_range[1].split('T')[0]
        print(f"   📅 Learning Period: {Colors.CYAN}{first_date} to {last_date}{Colors.END}")
    
    # Most active modules
    cursor.execute("""
        SELECT module_id, COUNT(*) as activity 
        FROM conversations 
        GROUP BY module_id 
        ORDER BY activity DESC 
        LIMIT 3
    """)
    
    top_modules = cursor.fetchall()
    
    if top_modules:
        print(f"\n{Colors.BLUE}Most Active Modules:{Colors.END}")
        modules_info = {
            1: "Your Four Worlds", 2: "Media Uses & Effects", 3: "Shared Characteristics of Media",
            4: "Communication Infrastructure", 5: "Books: Birth of Mass Communication", 6: "News & Newspapers",
            7: "Magazines: Special Interest Medium", 8: "Comic Books: Small Business, Big Impact", 9: "Photography: Fixing a Shadow",
            10: "Recordings: Bach to Rock & Rap", 11: "Motion Pictures: Mass Entertainment", 12: "Radio: The Pervasive Medium",
            13: "Television: Center of Attention", 14: "Video Games: Newest Mass Medium", 15: "Economic Influencers"
        }
        
        for i, (module_id, activity) in enumerate(top_modules, 1):
            module_title = modules_info.get(module_id, f"Module {module_id}")
            print(f"   {i}. {module_title}: {Colors.GREEN}{activity} messages{Colors.END}")
    
    wait_for_key()

def clear_data():
    """Clear student data with confirmation"""
    print(f"\n{Colors.YELLOW}🗑️  CLEAR STUDENT DATA{Colors.END}")
    print_separator()
    
    print(f"{Colors.RED}⚠️  WARNING: This will permanently delete data!{Colors.END}")
    print(f"\nOptions:")
    print(f"   {Colors.BOLD}1.{Colors.END} Clear conversations only")
    print(f"   {Colors.BOLD}2.{Colors.END} Clear reflections and insights")
    print(f"   {Colors.BOLD}3.{Colors.END} Clear all learning data (keep profile)")
    print(f"   {Colors.BOLD}4.{Colors.END} Delete entire student profile")
    print(f"   {Colors.BOLD}0.{Colors.END} Cancel")
    
    choice = input(f"\n{Colors.BOLD}Select option: {Colors.END}").strip()
    
    if choice == "0":
        return
    
    # Double confirmation
    confirm1 = input(f"\n{Colors.RED}Are you sure? Type 'DELETE' to confirm: {Colors.END}").strip()
    if confirm1 != "DELETE":
        print(f"{Colors.YELLOW}Operation cancelled.{Colors.END}")
        wait_for_key()
        return
    
    confirm2 = input(f"{Colors.RED}Final confirmation - type your student name: {Colors.END}").strip()
    if confirm2 != session.current_student:
        print(f"{Colors.YELLOW}Operation cancelled - name mismatch.{Colors.END}")
        wait_for_key()
        return
    
    cursor = session.db_conn.cursor()
    
    try:
        if choice == "1":
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM module_progress")
            print(f"{Colors.GREEN}✅ Conversations cleared.{Colors.END}")
            
        elif choice == "2":
            cursor.execute("DELETE FROM learning_reflections")
            cursor.execute("DELETE FROM student_insights")
            print(f"{Colors.GREEN}✅ Reflections and insights cleared.{Colors.END}")
            
        elif choice == "3":
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM module_progress")
            cursor.execute("DELETE FROM learning_reflections")
            cursor.execute("DELETE FROM student_insights")
            cursor.execute("DELETE FROM exported_conversations")
            print(f"{Colors.GREEN}✅ All learning data cleared.{Colors.END}")
            
        elif choice == "4":
            session.db_conn.close()
            student_dir = f"students/{session.current_student}"
            shutil.rmtree(student_dir)
            session.current_student = None
            session.db_conn = None
            print(f"{Colors.GREEN}✅ Student profile completely deleted.{Colors.END}")
            wait_for_key()
            return
        
        session.db_conn.commit()
        
    except Exception as e:
        print(f"{Colors.RED}❌ Clear operation failed: {e}{Colors.END}")
    
    wait_for_key()

def connect_backend():
    """Connect to HARV backend system"""
    print_header()
    
    print(f"\n{Colors.BOLD}🌐 CONNECT TO HARV BACKEND{Colors.END}")
    print_separator()
    
    print(f"{Colors.CYAN}Backend URL: {session.backend_url}{Colors.END}")
    
    try:
        import requests
        response = requests.get(f"{session.backend_url}/health", timeout=5)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"\n{Colors.GREEN}✅ Backend Connected!{Colors.END}")
            print(f"   Status: {Colors.GREEN}{health_data.get('status', 'unknown')}{Colors.END}")
            print(f"   Version: {Colors.CYAN}{health_data.get('version', 'unknown')}{Colors.END}")
            print(f"   Course: {Colors.YELLOW}{health_data.get('course', 'unknown')}{Colors.END}")
            
            if 'database' in health_data:
                db_info = health_data['database']
                print(f"   Modules: {Colors.GREEN}{db_info.get('modules', 0)}{Colors.END}")
                print(f"   Users: {Colors.GREEN}{db_info.get('users', 0)}{Colors.END}")
                print(f"   Conversations: {Colors.GREEN}{db_info.get('conversations', 0)}{Colors.END}")
            
            print(f"\n{Colors.BLUE}Available Features:{Colors.END}")
            print(f"   • 🌐 Web interface at http://localhost:5173")
            print(f"   • 📚 15 Communication Media modules")
            print(f"   • 🤖 Enhanced AI tutoring")
            print(f"   • 💾 Cloud data sync")
            
        else:
            print(f"\n{Colors.RED}❌ Backend responded with error: {response.status_code}{Colors.END}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}❌ Cannot connect to backend{Colors.END}")
        print(f"{Colors.YELLOW}💡 Make sure the HARV backend is running:{Colors.END}")
        print(f"   cd backend && uvicorn app.main:app --reload")
        
    except requests.exceptions.Timeout:
        print(f"\n{Colors.RED}❌ Connection timeout{Colors.END}")
        
    except ImportError:
        print(f"\n{Colors.RED}❌ Requests library not available{Colors.END}")
        print(f"{Colors.YELLOW}Install with: pip install requests{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Connection error: {e}{Colors.END}")
    
    wait_for_key()

def show_getting_started():
    """Show getting started guide"""
    print_header()
    
    print(f"\n{Colors.BOLD}📖 GETTING STARTED WITH HARV CLI{Colors.END}")
    print_separator()
    
    guide_text = f"""{Colors.CYAN}
🎓 Welcome to HARV - Your Socratic AI Tutor!

{Colors.BOLD}🚀 QUICK START:{Colors.END}{Colors.CYAN}
1. {Colors.BOLD}Create Student Profile{Colors.END}{Colors.CYAN} - Tell us about yourself and your goals
2. {Colors.BOLD}Browse Modules{Colors.END}{Colors.CYAN} - Explore 15 Communication Media topics
3. {Colors.BOLD}Start Conversations{Colors.END}{Colors.CYAN} - Engage in Socratic dialogue
4. {Colors.BOLD}Reflect & Record{Colors.END}{Colors.CYAN} - Capture insights in your journal
5. {Colors.BOLD}Export Progress{Colors.END}{Colors.CYAN} - Share conversations with instructors

{Colors.BOLD}💡 HOW SOCRATIC LEARNING WORKS:{Colors.END}{Colors.CYAN}
• HARV asks questions to guide your thinking
• You explore ideas through dialogue, not lectures
• Discover concepts through your own reasoning
• Build deeper understanding through reflection
• Connect learning to your personal experience

{Colors.BOLD}📚 THE 15 MODULES:{Colors.END}{Colors.CYAN}
1. Your Four Worlds - Communication models & perception
2. Media Uses & Effects - Functions vs effects theory
3. Shared Media Characteristics - Universal patterns
4. Communication Infrastructure - Technology evolution
5. Books - Birth of mass communication
6. News & Newspapers - Gatekeeping & journalism
7. Magazines - Specialization & targeting
8. Comic Books - Cultural impact & art
9. Photography - Visual communication
10. Recordings - Music industry & culture
11. Motion Pictures - Mass entertainment
12. Radio - Pervasive medium
13. Television - Cultural transformation
14. Video Games - Interactive entertainment
15. Economic Influencers - Advertising & ownership

{Colors.BOLD}🛠️ CLI FEATURES:{Colors.END}{Colors.CYAN}
• 💬 Natural conversation flow
• 📊 Progress tracking across modules
• 🤔 Personal reflection journal
• 💡 Insights tracker with understanding levels
• 📤 Export conversations for submission
• ⚙️  Customizable learning preferences

{Colors.BOLD}💭 LEARNING TIPS:{Colors.END}{Colors.CYAN}
• Be curious and ask follow-up questions
• Share personal examples and connections
• Don't worry about being "right" - explore ideas
• Reflect on what surprises or challenges you
• Export conversations to review later
• Use the insight tracker to measure growth

{Colors.BOLD}🆘 NEED HELP?{Colors.END}{Colors.CYAN}
• Type 'help' during any conversation
• Check your progress regularly
• Use reflection tools to process learning
• Export data to share with instructors
• Backend connection provides web interface
{Colors.END}"""
    
    print(guide_text)
    wait_for_key()

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.CYAN}👋 Thank you for using HARV CLI!{Colors.END}")
        session.close()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ An error occurred: {e}{Colors.END}")
        session.close()
        sys.exit(1)