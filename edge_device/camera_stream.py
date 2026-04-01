import cv2
import time
import threading
from logger import log
from config import CAMERA_URL

class CameraStream:
    def __init__(self, url=CAMERA_URL):
        self.url = url
        self.cap = None
        self.latest_frame = None
        self.running = False
        self.connect()

    def connect(self):
        log.info(f"Connecting to camera stream at {self.url}...")
        self.cap = cv2.VideoCapture(self.url)
        if self.cap.isOpened():
            self.running = True
            self.thread = threading.Thread(target=self._update, args=())
            self.thread.daemon = True
            self.thread.start()
        else:
            log.warning("Failed to connect to camera. Will retry.")

    def _update(self):
        # Background thread continuously drains the buffer to keep the frame real-time!
        while self.running:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.latest_frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)
                
    def read_frame(self):
        if not self.running or self.cap is None or not self.cap.isOpened():
            log.warning("Camera disconnected. Attempting to reconnect in 5 seconds...")
            time.sleep(5)
            self.connect()
            return False, None
            
        if self.latest_frame is None:
            return False, None
            
        return True, self.latest_frame.copy()
        
    def release(self):
        self.running = False
        if self.cap is not None:
            self.cap.release()
            log.info("Camera stream released.")
