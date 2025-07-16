#!/bin/bash
# Progressive Test Suite Runner
# Runs all test suites in order, stopping if any fail

echo "🧪 HARV PLATFORM PROGRESSIVE TEST RUNNER"
echo "========================================"
echo ""

# Track overall progress
SUITES_PASSED=0
TOTAL_SUITES=5

# Suite 1: Foundation
echo "🏗️  RUNNING SUITE 1: FOUNDATION"
echo "=" * 50
python3 test_suite_1_foundation.py
if [ $? -eq 0 ]; then
    SUITES_PASSED=$((SUITES_PASSED + 1))
    echo "✅ Suite 1 PASSED - Foundation solid"
    echo ""
else
    echo "❌ Suite 1 FAILED - Fix foundation issues"
    exit 1
fi

# Suite 2: Configuration
echo "⚙️  RUNNING SUITE 2: CONFIGURATION"
echo "=" * 50
python3 test_suite_2_configuration.py
if [ $? -eq 0 ]; then
    SUITES_PASSED=$((SUITES_PASSED + 1))
    echo "✅ Suite 2 PASSED - Configuration working"
    echo ""
else
    echo "❌ Suite 2 FAILED - Fix configuration issues"
    exit 1
fi

# Suite 3: Authentication
echo "🔐 RUNNING SUITE 3: AUTHENTICATION"
echo "=" * 50
python3 test_suite_3_authentication.py
if [ $? -eq 0 ]; then
    SUITES_PASSED=$((SUITES_PASSED + 1))
    echo "✅ Suite 3 PASSED - Authentication working"
    echo ""
else
    echo "❌ Suite 3 FAILED - Fix authentication issues"
    exit 1
fi

# Suite 4: Chat & AI
echo "💬 RUNNING SUITE 4: CHAT & AI"
echo "=" * 50
python3 test_suite_4_chat_ai.py
if [ $? -eq 0 ]; then
    SUITES_PASSED=$((SUITES_PASSED + 1))
    echo "✅ Suite 4 PASSED - Chat & AI working"
    echo ""
else
    echo "❌ Suite 4 FAILED - Fix chat/AI issues"
    exit 1
fi

# Suite 5: Frontend
echo "⚛️  RUNNING SUITE 5: FRONTEND"
echo "=" * 50
python3 test_suite_5_frontend.py
if [ $? -eq 0 ]; then
    SUITES_PASSED=$((SUITES_PASSED + 1))
    echo "✅ Suite 5 PASSED - Frontend integration working"
    echo ""
else
    echo "❌ Suite 5 FAILED - Fix frontend issues"
    exit 1
fi

# Final summary
echo "🎉 ALL PROGRESSIVE TESTS COMPLETED!"
echo "=" * 50
echo "✅ Suites Passed: $SUITES_PASSED/$TOTAL_SUITES"
echo ""
echo "🚀 YOUR HARV PLATFORM IS PRODUCTION READY!"
echo ""
echo "📋 Manual Testing URLs:"
echo "   • Backend: http://127.0.0.1:8000"
echo "   • GUI: http://localhost:3000/dev-gui.html"
echo "   • Frontend: http://localhost:5173"
echo ""
echo "🎯 All layers validated and working together!"

# Cleanup
rm -f .test_token
