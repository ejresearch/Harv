#!/bin/bash
# Backend Connection Fix
# Fixes the connection between demo frontend and backend

echo "🔧 BACKEND CONNECTION FIX"
echo "========================="

# Check if backend is running on port 8000
echo "🔍 Checking backend connection..."
if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "✅ Backend is running on port 8000"
    
    # Test modules endpoint
    echo "🔍 Testing modules endpoint..."
    MODULES_RESPONSE=$(curl -s http://127.0.0.1:8000/modules)
    if [[ $MODULES_RESPONSE == *"[{"* ]]; then
        MODULE_COUNT=$(echo $MODULES_RESPONSE | grep -o '"id"' | wc -l)
        echo "✅ Modules endpoint working - found $MODULE_COUNT modules"
    else
        echo "❌ Modules endpoint not returning data"
        echo "Response: $MODULES_RESPONSE"
    fi
    
else
    echo "❌ Backend not accessible on port 8000"
    echo "💡 Starting backend..."
    
    # Navigate to backend and start it
    cd backend
    uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
    BACKEND_PID=$!
    echo "🚀 Backend started with PID: $BACKEND_PID"
    
    # Wait for backend to start
    echo "⏳ Waiting for backend to start..."
    sleep 5
    
    # Test again
    if curl -s http://127.0.0.1:8000/health > /dev/null; then
        echo "✅ Backend now accessible"
    else
        echo "❌ Backend still not accessible"
    fi
fi

echo ""
echo "🌐 CORS & Connection Check"
echo "=========================="

# Test CORS headers
echo "🔍 Testing CORS headers..."
CORS_TEST=$(curl -s -H "Origin: http://localhost:3001" -H "Access-Control-Request-Method: GET" -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS http://127.0.0.1:8000/modules)

if [[ $CORS_TEST == *"Access-Control-Allow-Origin"* ]]; then
    echo "✅ CORS headers present"
else
    echo "⚠️  CORS headers may need configuration"
    echo "💡 Backend should allow origin: http://localhost:3001"
fi

echo ""
echo "🔧 Frontend Connection Test"
echo "==========================="

# Create a test script to verify frontend can reach backend
cat > test_frontend_connection.js << 'EOF'
// Test frontend connection to backend
async function testConnection() {
    console.log('🔍 Testing frontend connection to backend...');
    
    try {
        console.log('Testing health endpoint...');
        const healthResponse = await fetch('http://127.0.0.1:8000/health');
        console.log('Health status:', healthResponse.status);
        
        if (healthResponse.ok) {
            const healthData = await healthResponse.text();
            console.log('✅ Health response:', healthData);
        }
        
        console.log('Testing modules endpoint...');
        const modulesResponse = await fetch('http://127.0.0.1:8000/modules');
        console.log('Modules status:', modulesResponse.status);
        
        if (modulesResponse.ok) {
            const modulesData = await modulesResponse.json();
            console.log(`✅ Found ${modulesData.length} modules`);
            console.log('Sample module:', modulesData[0]);
        } else {
            console.log('❌ Modules endpoint failed');
        }
        
    } catch (error) {
        console.error('❌ Connection error:', error);
        console.log('💡 Possible issues:');
        console.log('   - Backend not running on port 8000');
        console.log('   - CORS not configured for localhost:3001');
        console.log('   - Network/firewall blocking connection');
    }
}

// Run the test
testConnection();
EOF

echo "📝 Created connection test script"
echo "💡 To run manually: node test_frontend_connection.js"

echo ""
echo "🚀 Quick Fixes to Try"
echo "===================="
echo ""
echo "1. Open browser developer console on your demo page"
echo "   (F12 → Console tab)"
echo "   Look for any red error messages"
echo ""
echo "2. Try manually visiting backend in browser:"
echo "   http://127.0.0.1:8000/health"
echo "   http://127.0.0.1:8000/modules"
echo ""
echo "3. If backend endpoints work in browser but not in demo:"
echo "   → CORS issue - backend needs to allow localhost:3001"
echo ""
echo "4. Restart demo frontend:"
echo "   cd demo_frontend"
echo "   npm start"
echo ""
echo "5. Force refresh demo page:"
echo "   Ctrl+F5 (or Cmd+Shift+R on Mac)"
echo ""
echo "🎯 Expected Result:"
echo "   Demo shows '✅ Backend Connected' and lists 15 modules"
