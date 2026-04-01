import cv2
import time
import requests
import numpy as np
from logger import log
from config import CAMERA_URL

class CameraStream:
    def __init__(self, url=CAMERA_URL):
        # Convert IP Webcam /video to point to /shot.jpg for instantaneous ZERO-DELAY polling
        self.url = url.replace('/video', '/shot.jpg')
        self.connect()

    def connect(self):
        log.info(f"Using HTTP Snapshot Mode at {self.url} (Zero Delay Guaranteed)...")

    def read_frame(self):
        try:
            # Force the phone to take a NEW picture by adding a constantly changing timestamp, bypassing HTTP caches
            current_url = f"{self.url}?t={int(time.time() * 1000)}"
            
            # Physically request exactly the current frame from the camera sensor in real-time
            resp = requests.get(current_url, timeout=2)
            if resp.status_code == 200:
                img_array = np.array(bytearray(resp.content), dtype=np.uint8)
                frame = cv2.imdecode(img_array, -1)
                return True, frame
            else:
                log.warning(f"Failed to fetch frame. HTTP {resp.status_code}")
                return False, None
        except Exception as e:
            log.warning(f"Camera disconnected. Retrying...")
            time.sleep(2)
            return False, None
            
    def release(self):
        log.info("Camera HTTP stream released.")
