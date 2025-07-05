import requests
import json

# Test the Flask API
url = "http://localhost:8080/execute"

# Test script with a main function
test_script = '''
def main():
    print("Hello from the executed script!")
    result = {"message": "Script executed successfully", "value": 42}
    return result
'''

# Prepare the request
data = {"script": test_script}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test health endpoint
try:
    health_response = requests.get("http://localhost:8080/health")
    print(f"\nHealth Check Status: {health_response.status_code}")
    print(f"Health Response: {json.dumps(health_response.json(), indent=2)}")
except Exception as e:
    print(f"Health check error: {e}")