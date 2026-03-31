import requests
import json
import time

BACKEND_URL = "http://localhost:5000/api/alerts"

def simulate_intrusion():
    print(f"Simulating an unknown face detection...")
    
    payload = {
        "event": "intrusion_detected",
        "device_id": "sim_pi_01",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "confidence": 0.85,
        "image": None # Normally a base64 string
    }
    
    print(f"Payload prepared: {json.dumps(payload, indent=2)}")
    print(f"Sending to {BACKEND_URL}...")
    
    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            print("✅ Success! Alert sent successfully.")
            print(f"Server responded: {response.json()}")
        else:
            print(f"❌ Failed! Server returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Is the Node.js backend running?")

if __name__ == "__main__":
    simulate_intrusion()
