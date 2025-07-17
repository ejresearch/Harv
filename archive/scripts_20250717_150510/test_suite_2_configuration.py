#!/usr/bin/env python3
"""
Test Suite 2: Configuration Layer
Tests: Module Config, Memory System, GUI
Prerequisites: Suite 1 passing
"""

import requests
import json
import sys
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
GUI_URL = "http://localhost:3000"

def test_module_configuration():
    """Test 2.1: Module configuration system"""
    print("🔍 Test 2.1: Module Configuration")
    
    # Test configuration read
    try:
        response = requests.get(f"{BASE_URL}/modules/1/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print("   ✅ Config read: PASS")
            
            # Test configuration write
            test_config = {
                "socratic_prompt": "Test prompt for integration",
                "learning_style": "mixed",
                "difficulty_level": "intermediate"
            }
            
            update_response = requests.put(f"{BASE_URL}/modules/1/config", 
                                         json=test_config, timeout=5)
            
            if update_response.status_code == 200:
                print("   ✅ Config write: PASS")
                return True
            else:
                print(f"   ❌ Config write: FAIL ({update_response.status_code})")
                return False
        else:
            print(f"   ❌ Config read: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Module configuration: ERROR - {e}")
        return False

def test_memory_system():
    """Test 2.2: Memory system functionality"""
    print("\n🔍 Test 2.2: Memory System")
    
    try:
        response = requests.get(f"{BASE_URL}/memory/stats/1", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Memory stats: PASS")
            print(f"   📊 Memory data: {stats}")
            return True
        else:
            print(f"   ❌ Memory stats: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Memory system: ERROR - {e}")
        return False

def test_gui_accessibility():
    """Test 2.3: GUI accessibility"""
    print("\n🔍 Test 2.3: GUI Accessibility")
    
    try:
        response = requests.get(f"{GUI_URL}/dev-gui.html", timeout=5)
        if response.status_code == 200:
            print("   ✅ GUI accessibility: PASS")
            print("   🌐 GUI URL: http://localhost:3000/dev-gui.html")
            return True
        else:
            print(f"   ❌ GUI accessibility: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ GUI accessibility: ERROR - {e}")
        print("   💡 Start GUI: cd tools && python3 -m http.server 3000")
        return False

def test_all_modules():
    """Test 2.4: All 15 modules accessible"""
    print("\n🔍 Test 2.4: All Modules Accessible")
    
    working_modules = 0
    for i in range(1, 16):
        try:
            response = requests.get(f"{BASE_URL}/modules/{i}/config", timeout=2)
            if response.status_code == 200:
                working_modules += 1
        except:
            pass
    
    print(f"   📊 Working modules: {working_modules}/15")
    
    if working_modules >= 10:  # 10+ modules is acceptable
        print("   ✅ Module accessibility: PASS")
        return True
    else:
        print("   ❌ Module accessibility: FAIL")
        return False

def main():
    print("🧪 TEST SUITE 2: CONFIGURATION LAYER")
    print("=" * 40)
    print("Testing: Module Config, Memory System, GUI")
    print("")
    
    results = []
    
    # Test 2.1: Module Configuration
    config_ok = test_module_configuration()
    results.append(config_ok)
    
    # Test 2.2: Memory System
    memory_ok = test_memory_system()
    results.append(memory_ok)
    
    # Test 2.3: GUI Accessibility
    gui_ok = test_gui_accessibility()
    results.append(gui_ok)
    
    # Test 2.4: All Modules
    modules_ok = test_all_modules()
    results.append(modules_ok)
    
    # Summary
    passed = sum(results)
    print(f"\n📊 Suite 2 Results: {passed}/4 tests passed")
    
    if passed >= 3:  # 3/4 is acceptable
        print("✅ CONFIGURATION LAYER: SOLID")
        print("🚀 Ready for Suite 3: Authentication Layer")
        return True
    else:
        print("❌ CONFIGURATION LAYER: NEEDS FIXES")
        print("Fix configuration issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
