import requests
import time
import base64
import cv2
import threading
from logger import log
from offline_queue import OfflineQueue
from config import BACKEND_URL, DEVICE_ID, ALERT_COOLDOWN

class AlertSender:
    def __init__(self):
        self.offline_queue = OfflineQueue()
        self.last_alert_time = 0
        self.cooldown = ALERT_COOLDOWN
        
        # Start a background thread to sync offline events
        self.sync_thread = threading.Thread(target=self._sync_offline_events, daemon=True)
        self.sync_thread.start()

    def _sync_offline_events(self):
        while True:
            events = self.offline_queue.get_events()
            if events:
                log.info(f"Attempting to sync {len(events)} offline events to backend.")
                success_count = 0
                for event in list(events): # copy to iterate safely
                    try:
                        response = requests.post(BACKEND_URL, json=event, timeout=5)
                        if response.status_code in [200, 201]:
                            success_count += 1
                            events.remove(event)
                    except requests.RequestException:
                        break # stop trying if backend is still down
                
                # save remaining events
                if success_count > 0:
                    log.info(f"Successfully synced {success_count} events.")
                self.offline_queue.save_queue(events)
            
            time.sleep(10) # check every 10 seconds

    def _image_to_base64(self, frame):
        if frame is None:
            return None
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')

    def trigger_alert(self, label, confidence, frame=None):
        current_time = time.time()
        
        if label != "UNKNOWN":
            return # Only alert on unknown faces
            
        if current_time - self.last_alert_time < self.cooldown:
            # Too early to send another alert
            return
            
        self.last_alert_time = current_time
        log.warning(f"INTRUSION DETECTED: {label} ({confidence:.2f})")
        
        # Build payload
        payload = {
            "event": "intrusion_detected",
            "device_id": DEVICE_ID,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "confidence": float(confidence),
            "image": self._image_to_base64(frame)
        }
        
        # Try to send to backend, fallback to offline queue
        try:
            response = requests.post(BACKEND_URL, json=payload, timeout=3)
            if response.status_code in [200, 201]:
                log.info("Alert sent to backend successfully.")
            else:
                log.warning(f"Backend responded with {response.status_code}. Queueing offline.")
                self.offline_queue.add_event(payload)
        except requests.RequestException as e:
            log.warning(f"Connection to backend failed ({str(e)}). Queueing offline.")
            self.offline_queue.add_event(payload)
