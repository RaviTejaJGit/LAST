import os
import re
from PIL import Image

def sanitize_url(url):
    # Replace non-alphanumeric characters with underscores
    return re.sub(r'[^a-zA-Z0-9]', '_', url)

def grey(image_path, url):
    image = Image.open(image_path)
    grey_image = image.convert('L')
    grey_image.save('grey.png')

    sanitized_url = sanitize_url(url)  # Sanitize the URL to create a valid filename
    image_save_path = os.path.join('screenshots', sanitized_url + '.png')
    image.save(image_save_path)
    