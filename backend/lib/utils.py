
import base64
from io import BytesIO
from PIL import Image

URL_CANVAS_START = "data:image/png;base64,"
URL_CANVAS_START_AT = len(URL_CANVAS_START)

def fromBase64URL(data):
    return Image.open(BytesIO(base64.b64decode(data[URL_CANVAS_START_AT:])))

def toBase64URL(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return URL_CANVAS_START + base64.b64encode(buffered.getvalue()).decode("utf-8")