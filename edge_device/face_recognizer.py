import face_recognition
import cv2
import os
import numpy as np
from logger import log
from config import KNOWN_FACES_DIR, FACE_MATCH_THRESHOLD

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()

    def load_known_faces(self):
        if not os.path.exists(KNOWN_FACES_DIR):
            os.makedirs(KNOWN_FACES_DIR)
            log.info(f"Created directory for known faces at: {KNOWN_FACES_DIR}")
            log.info("Please add images of known people to this directory to avoid false alarms.")
            return

        for filename in os.listdir(KNOWN_FACES_DIR):
            filepath = os.path.join(KNOWN_FACES_DIR, filename)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                try:
                    name = os.path.splitext(filename)[0]
                    # Load image and compute encoding
                    image = face_recognition.load_image_file(filepath)
                    encodings = face_recognition.face_encodings(image)
                    if len(encodings) > 0:
                        self.known_face_encodings.append(encodings[0])
                        self.known_face_names.append(name)
                        log.info(f"Loaded known face: {name}")
                    else:
                        log.warning(f"No face found in {filename}")
                except Exception as e:
                    log.error(f"Error loading {filename}: {e}")
                    
        log.info(f"Loaded {len(self.known_face_names)} known faces total.")

    def detect_and_recognize(self, frame):
        # Process at the native frame resolution (1.0x) because the user manually shrunk it in their phone app!
        small_frame = cv2.resize(frame, (0, 0), fx=1.0, fy=1.0)
        
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # Mathematical multiplier to accurately scale the drawing coordinates back up (1 / 1.0 = 1)
        scale = 1
        face_names = []
        confidences = []

        for face_encoding in face_encodings:
            if not self.known_face_encodings:
                # No known faces -> everything is unknown
                face_names.append("UNKNOWN")
                confidences.append(1.0)
                continue

            # Compare current face with known faces
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            # Distance is lower when match is better
            min_distance = face_distances[best_match_index]
            
            if min_distance <= FACE_MATCH_THRESHOLD:
                name = self.known_face_names[best_match_index]
                # convert distance to a mock confidence score (~1 for perfect match)
                confidence = 1.0 - min_distance
            else:
                name = "UNKNOWN"
                confidence = 1.0 - min_distance # lower confidence

            face_names.append(name)
            confidences.append(confidence)

        # Scale face locations back up since we shrunk the frame to 1/4 size
        scaled_locations = []
        for (top, right, bottom, left) in face_locations:
            scaled_locations.append((top * 4, right * 4, bottom * 4, left * 4))

        return scaled_locations, face_names, confidences
