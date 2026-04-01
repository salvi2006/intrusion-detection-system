import cv2
import sys
from logger import log
from camera_stream import CameraStream
from face_recognizer import FaceRecognizer
from alert_sender import AlertSender

def main():
    log.info("Starting Edge-Based Intrusion Detection System...")
    
    stream = CameraStream()
    recognizer = FaceRecognizer()
    alert_sender = AlertSender()
    
    log.info("System ready. Press 'q' in the video window to quit.")
    
    try:
        while True:
            ret, frame = stream.read_frame()
            if not ret or frame is None:
                continue
                
            # Process frame for faces
            locations, names, confidences = recognizer.detect_and_recognize(frame)
            
            if len(locations) > 0:
                log.info(f"Successfully detected {len(locations)} face(s): {names}")
            
            # Draw results and handle alerts
            for (top, right, bottom, left), name, confidence in zip(locations, names, confidences):
                
                # Default to green for known
                color = (0, 255, 0)
                label = f"KNOWN: {name}"
                
                if name == "UNKNOWN":
                    # Red for unknown
                    color = (0, 0, 255)
                    label = "UNKNOWN"
                    # Trigger alert via the AlertSender module
                    alert_sender.trigger_alert(label, confidence, frame)
                    
                # Draw bounding box
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                # Draw text
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, f"{label} ({confidence:.2f})", (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
                
            # Display the video frame if a monitor is attached (skip in SSH)
            import os
            if os.environ.get('DISPLAY'):
                cv2.imshow('Edge Device - Simulation Mode', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
    except KeyboardInterrupt:
        log.info("Interrupted by user.")
    except Exception as e:
        log.error(f"Unexpected error in main loop: {e}")
    finally:
        stream.release()
        cv2.destroyAllWindows()
        log.info("System shutdown complete.")

if __name__ == "__main__":
    main()
