import os
import base64
from backend.settings import BASE_DIR
from PIL import Image
from io import BytesIO
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from scipy.spatial.distance import cdist
from PIL import Image, ImageDraw
from mtcnn import MTCNN
from .models import FaceBox
from tensorflow.keras import backend as K
from tensorflow import keras
import json
from .models import FaceTag

URL_CANVAS_START = "data:image/png;base64,"
URL_CANVAS_START_AT = len(URL_CANVAS_START)
KERAS_FACENET_PATH = os.path.join(BASE_DIR, 'models/facenet_keras.h5')

fnmodel = load_model(KERAS_FACENET_PATH, custom_objects={'tf': tf})
# create the detector, using default weights
detector = MTCNN()

def __fromBase64URL(data):
    return Image.open(BytesIO(base64.b64decode(data[URL_CANVAS_START_AT:])))
def __toBase64URL(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return URL_CANVAS_START + base64.b64encode(buffered.getvalue()).decode("utf-8")

def __detect_face(pixels, required_size=(160,160)):
    # convert to array
    # detect faces in the image
    results = detector.detect_faces(pixels)
    # extract the bounding box from the first face
    face_array = []
    # draw the bounding boxes on the faces
    for result in results:
        if result['confidence'] < 0.99:
            continue
        x1, y1, width, height = result['box']
        x2, y2 = x1+width, y1+height
        # extract the face
        face = pixels[y1:y2, x1:x2]
        # resize pixels to the model size
        img = Image.fromarray(face)
        img = img.resize(required_size)
        face_array.append(img)
    return face_array
def detect_face(data):
    # load image from file
    image = __fromBase64URL(data)
    # convert to RGB, if needed
    image = image.convert('RGB')
    pixels = np.asarray(image)
    toReturn = []
    for img in __detect_face(pixels):
        toReturn.append(FaceBox(__toBase64URL(img)))
    return toReturn
def save_face_embedding(data, name):
    try:
        image = __fromBase64URL(data)
        image = image.convert('RGB')
        pixels = np.asarray(image)
        pixels = np.expand_dims(pixels, axis=0)
        mean = pixels.mean(axis=(1,2,3), keepdims=True)
        std =  pixels.std(axis=(1,2,3), keepdims=True)
        y_hat = fnmodel.predict((pixels - mean)/std)
        embedding_str = json.dumps(y_hat[0].tolist())
        FaceTag.objects.update_or_create(
            defaults = {
                'data': embedding_str
            },
            name = name
        )
        return 'OK'
    except Exception as e:
        print(e)
        return 'ERROR'

def identify_face(data, required_size=(160,160)):
    # load image from file
    image = __fromBase64URL(data)
    # convert to RGB, if needed
    image = image.convert('RGB')
    pixels = np.asarray(image)
    faces = __detect_face(pixels)
    pixels_array = []
    for face in faces:
        pixels_array.append(np.asarray(face))
    faces_pixels = np.asarray(pixels_array)
    mean = faces_pixels.mean(axis=(1,2,3), keepdims=True)
    std =  faces_pixels.std(axis=(1,2,3), keepdims=True)
    y_hat = fnmodel.predict((faces_pixels - mean)/std)
    known_names = []
    known_embeddings = []
    for facetag in FaceTag.objects.all():
        known_names.append(facetag.name)
        known_embeddings.append(json.loads(facetag.data))
    known_embeddings = np.asarray(known_embeddings)
    m = cdist(y_hat, known_embeddings)
    identified_ids = np.argmin(m, axis=1)
    boxes = []
    print(m)
    for i in range(len(faces)):
        name = 'unknown'
        d = m[i, identified_ids[i]] 
        if d < 8.5:
            name = known_names[identified_ids[i]]
            print(f'{name} identified with distance {d}')
        boxes.append( FaceBox(__toBase64URL(faces[i]), name))
    return boxes