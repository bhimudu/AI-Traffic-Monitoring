# utils/anpr.py
import easyocr
import re

reader = easyocr.Reader(['en'], gpu=False)

def clean_plate(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def read_plate(plate_img):
    result = reader.readtext(plate_img)
    if len(result) == 0:
        return None

    # pick highest confidence
    result = sorted(result, key=lambda x: x[2], reverse=True)
    plate_text = clean_plate(result[0][1])

    if len(plate_text) < 6:
        return None
    return plate_text
