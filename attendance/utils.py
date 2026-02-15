import face_recognition

def get_face_encoding(image):
    rgb_image = image[:, :, ::-1]
    encodings = face_recognition.face_encodings(rgb_image)
    if encodings:
        return encodings[0]
    return None
