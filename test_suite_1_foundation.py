#!/usr/bin/env python3
"""
Test Suite 1: Foundation Layer
Tests: Database, Backend Health, Basic API
Prerequisites: None
"""

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_backend_health():
    """Test 1.1: Backend server health"""
    print("🔍 Test 1.1: Backend Health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend health: PASS")
            return True
        else:
            print(f"   ❌ Backend health: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Backend health: ERROR - {e}")
        print("   💡 Start backend: cd backend && uvicorn app.main:app --reload")
        return False

def test_database_connection():
    """Test 1.2: Database connectivity"""
    print("\n🔍 Test 1.2: Database Connection")
    try:
        response = requests.get(f"{BASE_URL}/modules", timeout=5)
        if response.status_code == 200:
            modules = response.json()
            print(f"   ✅ Database connection: PASS ({len(modules)} modules)")
            return True, len(modules)
        else:
            print(f"   ❌ Database connection: FAIL ({response.status_code})")
            return False, 0
    except Exception as e:
        print(f"   ❌ Database connection: ERROR - {e}")
        return False, 0

def test_module_structure():
    """Test 1.3: Module data structure"""
    print("\n🔍 Test 1.3: Module Structure")
    try:
        response = requests.get(f"{BASE_URL}/modules/1", timeout=5)
        if response.status_code == 200:
            module = response.json()
            required_fields = ['id', 'title', 'description']
            missing = [f for f in required_fields if f not in module]
            
            if not missing:
                print("   ✅ Module structure: PASS")
                return True
            else:
                print(f"   ❌ Module structure: Missing fields {missing}")
                return False
        else:
            print(f"   ❌ Module structure: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Module structure: ERROR - {e}")
        return False

def main():
    print("🧪 TEST SUITE 1: FOUNDATION LAYER")
    print("=" * 40)
    print("Testing: Database, Backend Health, Basic API")
    print("")
    
    results = []
    
    # Test 1.1: Backend Health
    health_ok = test_backend_health()
    results.append(health_ok)
    
    if not health_ok:
        print("\n❌ FOUNDATION FAILURE: Backend not running")
        print("Cannot proceed to next test suite")
        return False
    
    # Test 1.2: Database Connection
    db_ok, module_count = test_database_connection()
    results.append(db_ok)
    
    # Test 1.3: Module Structure
    structure_ok = test_module_structure()
    results.append(structure_ok)
    
    # Summary
    passed = sum(results)
    print(f"\n📊 Suite 1 Results: {passed}/3 tests passed")
    
    if passed == 3:
        print("✅ FOUNDATION LAYER: SOLID")
        print("🚀 Ready for Suite 2: Configuration Layer")
        return True
    else:
        print("❌ FOUNDATION LAYER: NEEDS FIXES")
        print("Fix foundation issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
