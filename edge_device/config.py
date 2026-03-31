import os

# Camera URL (e.g., from IP Webcam app: http://<phone-ip>:8080/video)
CAMERA_URL = os.getenv("CAMERA_URL", "http://192.168.1.100:8080/video")

# Face match tolerance (lower is stricter, default for face_recognition is 0.6)
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.55"))

# Alert cooldown per person in seconds
ALERT_COOLDOWN = int(os.getenv("ALERT_COOLDOWN", "300")) # 5 minutes default

# Backend URL for sending alerts
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000/api/alerts")

# Identify this edge device
DEVICE_ID = os.getenv("DEVICE_ID", "pi_01")

# Paths
KNOWN_FACES_DIR = os.path.join(os.path.dirname(__file__), "known_faces")
OFFLINE_QUEUE_FILE = os.path.join(os.path.dirname(__file__), "offline_events.json")
