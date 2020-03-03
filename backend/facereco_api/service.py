import os
import base64
from backend.settings import BASE_DIR
from io import BytesIO
import tensorflow as tf
from tensorflow.python.eager.wrap_function import function_from_graph_def
import numpy as np
from scipy.spatial.distance import cdist
from PIL import Image, ImageDraw
from mtcnn import MTCNN
from .models import FaceBox
import json
from .models import FaceTag

URL_CANVAS_START = "data:image/png;base64,"
URL_CANVAS_START_AT = len(URL_CANVAS_START)
FACENET_PATH = os.path.join(BASE_DIR, 'models/facenet/20180402-114759.pb')

graph_def = tf.compat.v1.GraphDef()
loaded = graph_def.ParseFromString(open(FACENET_PATH,'rb').read())

fnmodel = function_from_graph_def(graph_def, inputs=['input:0', 'phase_train:0'], outputs='embeddings:0')
# create the detector, using default weights
detector = MTCNN()

def __fromBase64URL(data):
    return Image.open(BytesIO(base64.b64decode(data[URL_CANVAS_START_AT:])))
def __toBase64URL(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return URL_CANVAS_START + base64.b64encode(buffered.getvalue()).decode("utf-8")
def __getEmbeddings(faces_pixels):
    embeddings = fnmodel(input = tf.constant((faces_pixels - 127.5)/128.0, dtype=tf.float32), phase_train = tf.constant(False)).numpy()
    return (embeddings - np.mean(embeddings, axis=1, keepdims=True))
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
        y_hat = __getEmbeddings(pixels)
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
    y_hat = __getEmbeddings(faces_pixels)
    known_names = []
    known_embeddings = []
    for facetag in FaceTag.objects.all():
        known_names.append(facetag.name)
        known_embeddings.append(json.loads(facetag.data))
    known_embeddings = np.asarray(known_embeddings)
    m = np.arccos(1-cdist(y_hat, known_embeddings, 'cosine'))/np.pi
    identified_ids = np.argmin(m, axis=1)
    boxes = []
    print(m)
    for i in range(len(faces)):
        name = 'unknown'
        d = m[i, identified_ids[i]] 
        if d < 0.25:
            name = known_names[identified_ids[i]]
            print(f'{name} identified with distance {d}')
        boxes.append( FaceBox(__toBase64URL(faces[i]), name))
    return boxes