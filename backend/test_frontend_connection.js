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
