import cv2
import time
from logger import log
from config import CAMERA_URL

class CameraStream:
    def __init__(self, url=CAMERA_URL):
        self.url = url
        self.cap = None
        self.connect()

    def connect(self):
        log.info(f"Connecting to camera stream at {self.url}...")
        self.cap = cv2.VideoCapture(self.url)
        if not self.cap.isOpened():
            log.warning("Failed to connect to camera. Will retry.")
            
    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            log.warning("Camera disconnected. Attempting to reconnect in 5 seconds...")
            time.sleep(5)
            self.connect()
            return False, None
            
        ret, frame = self.cap.read()
        if not ret:
            log.warning("Failed to read frame. Stream might have dropped.")
            self.cap.release()
            return False, None
            
        return True, frame
        
    def release(self):
        if self.cap is not None:
            self.cap.release()
            log.info("Camera stream released.")
