import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image, ImageDraw
from mtcnn import MTCNN
from io import BytesIO
import base64
from .models import AvatarBox
import numpy as np
from django.conf import settings
import os
from lib.utils import fromBase64URL, toBase64URL

detector = MTCNN()
try:
    faceseg_path = tf.keras.utils.get_file('faceseg.zip', settings.FACE_HAIR_MODEL_URL,  cache_subdir='faceseg', extract=True)
    faceseg_path = os.path.dirname(faceseg_path)
    faceseg = tf.saved_model.load(faceseg_path)
except Exception as e:
    print(e)
    print('Error loading faceseg model')

try:
    style_module = hub.load(settings.STYLE_MODULE_URL)
except Exception as e:
    print(e)
    print('Error loading style module')

try:
    style_path = tf.keras.utils.get_file(os.path.basename(settings.SAMPLE_STYLE_IMAGE_URL),settings.SAMPLE_STYLE_IMAGE_URL)
except Exception as e:
    print(e)
    print('Error loading sample styling image')

def crop_face(image, model_height = 218, model_width=178):
  resized_image = tf.image.resize(image, (model_height, model_width))
  mask = faceseg(resized_image[tf.newaxis,...])[0].numpy().argmax(axis=2)[..., tf.newaxis]
  skin_mask = mask == 1
  skin_mask = tf.cast(skin_mask, tf.float32)
  skin_mask = tf.image.resize(skin_mask, image.shape[0:2])
  hair_mask = mask == 2
  hair_mask = tf.cast(hair_mask, tf.float32)
  hair_mask = tf.image.resize(hair_mask, image.shape[0:2])
  return skin_mask, hair_mask

def stylize_image(content_image, style_image, model_height=256, model_width=256):
  resized_content_image = tf.image.resize(content_image, (model_height, model_width))
  style_image = tf.image.resize(style_image, (model_height, model_width))
  stylized_image = style_module(resized_content_image[tf.newaxis, ...], 
                                style_image[tf.newaxis,...])[0][0]
  stylized_image = tf.image.resize(stylized_image, content_image.shape[0:2])
  return stylized_image

def styleAvatar(image, styleFace = True, 
        styleHair = True, styleSide = None, faceHairOnly = False):
    data = fromBase64URL(image)
    data = data.convert('RGB')
    content_image = tf.constant(np.asarray(data)/255.0, dtype = tf.float32)   # detect faces in the image
    style_image = tf.io.decode_image(tf.io.read_file(style_path), dtype=tf.float32, channels=3)
    skin_mask, hair_mask = crop_face(content_image)
    stylized_image = stylize_image(content_image, style_image)

    face = stylized_image*skin_mask if styleFace or not styleHair else content_image*skin_mask
    hair = stylized_image*hair_mask if styleHair or not styleFace else content_image*hair_mask
    background =( (1.0-skin_mask-hair_mask)*tf.ones(shape=content_image.shape) if faceHairOnly
            else (1.0 - skin_mask-hair_mask)*content_image if styleFace or styleHair
            else (1.0 - skin_mask-hair_mask)*stylized_image)
    stylized_image = face + hair + background
    halfMask = np.zeros(shape=content_image.shape)

    _,width,_  = content_image.shape
    if styleSide == 'left':
        halfMask[:,0:width//2,:] = 1.0
    elif styleSide == 'right':
        halfMask[:,width//2:,:] = 1.0
    else:
        halfMask[:,:,:] = 1.0
    
    halfMask = tf.constant(halfMask, dtype=tf.float32)
    if faceHairOnly:
        stylized_image = ( stylized_image*halfMask +
                (1.0-halfMask)*(skin_mask+hair_mask)*content_image
                +(1.0 - halfMask)*background
                )
    else:
        stylized_image = ( stylized_image*halfMask +
                (1.0-halfMask)*content_image)
    to_return = tf.keras.preprocessing.image.array_to_img(stylized_image)
    return toBase64URL(to_return)

def cropAvatar(data, ratio = (2,2)):
    # convert to array
    image = fromBase64URL(data)
    image = image.convert('RGB')
    orgW, orgH = image.size
    pixels = np.asarray(image)    # detect faces in the image
    results = detector.detect_faces(pixels)
    # extract the bounding box from the first face
    toReturn = []
    ratio_w, ratio_h = ratio
    # draw the bounding boxes on the faces
    for result in results:
        if result['confidence'] < 0.99:
            continue
        x, y, width, height = result['box']
        xc, yc  = x+width//2, y+height//2 #center of the box
        width, height = np.ceil(ratio_w*width), np.ceil(ratio_h*height)  
        x, y = max(0, xc-width//2),max(0, yc-height//2)
        width, height = min(orgW, xc+width//2)-x, min(orgH, yc+height//2)-y
        toReturn.append(AvatarBox(x,y,width,height))
    return toReturn