import json
import os
import time
from logger import log
from config import OFFLINE_QUEUE_FILE

class OfflineQueue:
    def __init__(self):
        self.file_path = OFFLINE_QUEUE_FILE
        if not os.path.exists(self.file_path):
            self.save_queue([])
            
    def load_queue(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
            
    def save_queue(self, events):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(events, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save offline queue: {e}")

    def add_event(self, event):
        events = self.load_queue()
        events.append(event)
        self.save_queue(events)
        log.info(f"Event added to offline queue. Total offline events: {len(events)}")

    def get_events(self):
        return self.load_queue()
        
    def clear_events(self):
        self.save_queue([])
        log.info("Offline queue cleared.")
