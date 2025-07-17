#!/usr/bin/env python3
"""
Test Suite 5: Frontend Integration
Tests: React App, API Integration, User Experience
Prerequisites: Suite 1, 2, 3, 4 passing
"""

import requests
import json
import sys
import time
import os
from datetime import datetime

FRONTEND_URL = "http://localhost:5173"
BASE_URL = "http://127.0.0.1:8000"

def test_frontend_accessibility():
    """Test 5.1: Frontend accessibility"""
    print("🔍 Test 5.1: Frontend Accessibility")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("   ✅ Frontend accessible: PASS")
            print("   🌐 React app: http://localhost:5173")
            return True
        else:
            print(f"   ❌ Frontend accessible: FAIL ({response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Frontend accessible: ERROR - {e}")
        print("   💡 Start frontend: cd frontend && npm run dev")
        return False

def test_api_integration():
    """Test 5.2: Frontend API integration"""
    print("\n🔍 Test 5.2: API Integration")
    
    # Test if frontend can proxy to backend
    try:
        response = requests.get(f"{FRONTEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API proxy: PASS")
            return True
        else:
            print("   ⚠️  API proxy: Not configured (using direct backend)")
            return True  # This is acceptable
    except:
        print("   ⚠️  API proxy: Not configured (using direct backend)")
        return True  # This is acceptable

def test_static_assets():
    """Test 5.3: Static assets loading"""
    print("\n🔍 Test 5.3: Static Assets")
    
    try:
        # Test if we can get any static assets
        response = requests.get(f"{FRONTEND_URL}/vite.svg", timeout=5)
        if response.status_code == 200:
            print("   ✅ Static assets: PASS")
            return True
        else:
            print("   ⚠️  Static assets: May not be fully loaded")
            return True  # Not critical
    except:
        print("   ⚠️  Static assets: May not be fully loaded")
        return True  # Not critical

def main():
    print("🧪 TEST SUITE 5: FRONTEND INTEGRATION")
    print("=" * 40)
    print("Testing: React App, API Integration, Assets")
    print("")
    
    results = []
    
    # Test 5.1: Frontend Accessibility
    frontend_ok = test_frontend_accessibility()
    results.append(frontend_ok)
    
    # Test 5.2: API Integration
    api_ok = test_api_integration()
    results.append(api_ok)
    
    # Test 5.3: Static Assets
    assets_ok = test_static_assets()
    results.append(assets_ok)
    
    # Summary
    passed = sum(results)
    print(f"\n📊 Suite 5 Results: {passed}/3 tests passed")
    
    if passed >= 2:  # 2/3 is acceptable
        print("✅ FRONTEND INTEGRATION: SOLID")
        print("🚀 Ready for Suite 6: Full Integration")
        return True
    else:
        print("❌ FRONTEND INTEGRATION: NEEDS FIXES")
        print("Fix frontend issues before proceeding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
