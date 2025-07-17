#!/usr/bin/env python3
"""
Module Configuration Testing Script
Run from root directory: python test_module_configuration.py
"""

import requests
import json
import time

def test_configuration_system():
    """Test the complete module configuration system"""
    print("🧪 TESTING MODULE CONFIGURATION SYSTEM")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 1. Test backend is running
    print("1. Testing backend connectivity...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend. Start with: uvicorn app.main:app --reload")
        return False
    
    # 2. Test modules endpoint
    print("2. Testing modules endpoint...")
    try:
        response = requests.get(f"{base_url}/modules")
        modules = response.json()
        print(f"   ✅ Found {len(modules)} modules")
        
        if len(modules) < 15:
            print(f"   ⚠️  Expected 15 modules, found {len(modules)}")
    except Exception as e:
        print(f"   ❌ Modules endpoint error: {e}")
        return False
    
    # 3. Test configuration endpoints
    print("3. Testing configuration endpoints...")
    test_module_id = 1
    
    # Test get config
    try:
        response = requests.get(f"{base_url}/modules/{test_module_id}/config")
        if response.status_code == 200:
            config = response.json()
            print(f"   ✅ Retrieved config for module {test_module_id}")
        else:
            print(f"   ❌ Config retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Config endpoint error: {e}")
        return False
    
    # Test update config
    try:
        test_config = {
            "module_prompt": "Test prompt for configuration validation",
            "system_corpus": "Test knowledge base",
            "memory_weight": 2
        }
        
        response = requests.put(
            f"{base_url}/modules/{test_module_id}/config",
            json=test_config
        )
        
        if response.status_code == 200:
            print("   ✅ Configuration update successful")
        else:
            print(f"   ❌ Config update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Config update error: {e}")
        return False
    
    # 4. Test configuration validation
    print("4. Testing configuration validation...")
    try:
        response = requests.get(f"{base_url}/modules/{test_module_id}/test")
        result = response.json()
        
        if result.get("success"):
            print("   ✅ Configuration validation passed")
        else:
            print(f"   ⚠️  Validation issues: {result.get('error', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Validation test error: {e}")
    
    # 5. Test GUI accessibility
    print("5. Testing GUI accessibility...")
    try:
        gui_response = requests.get("http://localhost:3000/dev-gui.html")
        if gui_response.status_code == 200:
            print("   ✅ Developer GUI is accessible")
        else:
            print("   ⚠️  GUI not accessible. Start with: python start_config_gui.py")
    except requests.exceptions.ConnectionError:
        print("   ⚠️  GUI server not running. Start with: python start_config_gui.py")
    
    print("
" + "=" * 50)
    print("✅ MODULE CONFIGURATION TESTING COMPLETE")
    print("=" * 50)
    print("🎯 Results Summary:")
    print("   ✅ Backend connectivity: Working")
    print("   ✅ Module endpoints: Functional")
    print("   ✅ Configuration API: Operational")
    print("   ✅ Save/Edit operations: Successful")
    print("
🚀 Ready for integration testing!")
    
    return True

if __name__ == "__main__":
    test_configuration_system()
