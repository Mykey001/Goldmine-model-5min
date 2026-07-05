"""
Test API terminal discovery endpoint
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_discover():
    print("=" * 60)
    print("TESTING /api/terminals/discover ENDPOINT")
    print("=" * 60)
    
    try:
        print(f"\nCalling: {API_URL}/api/terminals/discover")
        response = requests.get(f"{API_URL}/api/terminals/discover", timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse Headers:")
        print(f"  Content-Type: {response.headers.get('content-type')}")
        
        print(f"\nResponse Body:")
        data = response.json()
        print(json.dumps(data, indent=2))
        
        if 'terminals' in data:
            terminals = data['terminals']
            print(f"\n✅ Found {len(terminals)} terminal(s)")
            
            for i, terminal in enumerate(terminals, 1):
                print(f"\nTerminal {i}:")
                print(f"  ID: {terminal.get('id')}")
                print(f"  Name: {terminal.get('name')}")
                print(f"  Broker: {terminal.get('broker')}")
                print(f"  Path: {terminal.get('path')}")
        else:
            print("\n❌ No 'terminals' key in response")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("   Make sure the backend is running on port 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_discover()
