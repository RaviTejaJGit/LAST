from PIL import Image
import pytesseract

def text_in_image(image):
    im = Image.open(image)
    pytesseract.pytesseract.tesseract_cmd = r"AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
    text = pytesseract.image_to_string(im,lang='eng')
    words = set(text.split('\n'))
    #print("Line9:",words) important to find what all words it read
    return words