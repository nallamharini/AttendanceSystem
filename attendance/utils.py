import face_recognition
import numpy as np
import cv2

def get_face_encoding(image):
    """Extract face encoding from image"""
    try:
        # Ensure image is in RGB format (face_recognition expects RGB)
        if len(image.shape) == 2:  # Grayscale
            rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 3:  # BGR
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image
        
        # Ensure the image is uint8
        if rgb_image.dtype != np.uint8:
            rgb_image = rgb_image.astype(np.uint8)
        
        # Get face encodings
        encodings = face_recognition.face_encodings(rgb_image)
        
        if encodings:
            return encodings[0]
        return None
        
    except Exception as e:
        print(f"Error in get_face_encoding: {str(e)}")
        return None

def compare_faces(encoding1, encoding2, tolerance=0.6):
    """Compare two face encodings"""
    if encoding1 is None or encoding2 is None:
        return False
    
    try:
        # Calculate face distance
        distance = face_recognition.face_distance([encoding1], encoding2)[0]
        return distance < tolerance
    except Exception as e:
        print(f"Error in compare_faces: {str(e)}")
        return False
