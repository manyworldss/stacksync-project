import requests
import json

def test_health():
    try:
        response = requests.get('http://localhost:8080/health')
        print(f"Health check status: {response.status_code}")
        print(f"Health check response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_execute():
    try:
        test_script = '''
def main():
    print("Hello from executed script!")
    return {"message": "Script executed successfully", "value": 42}
'''
        
        response = requests.post('http://localhost:8080/execute', 
                               json={'script': test_script})
        print(f"Execute status: {response.status_code}")
        print(f"Execute response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Execute test failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing Python Code Execution Service...")
    
    if test_health():
        print("✓ Health check passed")
        if test_execute():
            print("✓ Execute test passed")
            print("\n🎉 All tests passed! The service is working correctly.")
        else:
            print("✗ Execute test failed")
    else:
        print("✗ Health check failed - server may not be running")