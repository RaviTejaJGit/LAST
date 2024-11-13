import os
import time
import mss
import numpy as np
from PIL import Image, ImageChops, ImageFile
from fpdf import FPDF
from llm import process_image  # Assuming this function processes the image and returns the processed text or data
from multiprocessing import Value

def detect_change(img1, img2, threshold=5):
    diff = ImageChops.difference(img1, img2)
    np_diff = np.array(diff)
    percent_change = (np.count_nonzero(np_diff) * 100) / np_diff.size
    return percent_change > threshold

def get_screenshot(sct):
    sct_img = sct.grab(sct.monitors[1])
    img = Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb)
    return img

def screenshots(flag):
    folder = 'screenshots'
    os.makedirs(folder, exist_ok=True)
    prev_img = None

    while True:
        #print("Line 27",flag.value)
        if flag.value == 1:
            with mss.mss() as sct:
                img = get_screenshot(sct)
                if prev_img is not None:
                    if detect_change(prev_img, img):
                        timestamp = time.strftime('%Y%m%d_%H%M%S')
                        filename = os.path.join(folder, f'screenshot_{timestamp}.png')
                        img.save(filename)
                        #print(f'Change detected. Screenshot saved: {filename}')
                else:
                    timestamp = time.strftime('%Y%m%d_%H%M%S')
                    filename = os.path.join(folder, f'screenshot_{timestamp}.png')
                    img.save(filename)
                    #print(f'Initial screenshot saved: {filename}')
                
                prev_img = img
                time.sleep(3)
        else:
            time.sleep(3)

def listfiles(directory, table, flag):
    seen_files = set(os.listdir(directory))
    #print("Files in directory:")
    for filename in seen_files:
        table[filename] = None
        #print(filename)
    
    while 1:
        current_files = set(os.listdir(directory))
        new_files = current_files - seen_files
        for filename in new_files:
            table[filename] = None
            #print(filename)
        seen_files = current_files
        time.sleep(1)

def save_to_pdf(text, pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Replace characters that can't be encoded with a placeholder
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')

    pdf.multi_cell(0, 10, safe_text)
    pdf.output(pdf_path)



def readfiles(directory, shared_dict, flag):
    readkey = True
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    assigned_keys = set()
    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')

    while readkey:
        for key in shared_dict.keys():
            if key is None or not(key.lower().endswith(valid_extensions)):
                continue
            
            if key not in assigned_keys and shared_dict[key] is None:
                if key.lower().endswith(valid_extensions):
                    processed_data = None
                    for attempt in range(3):  # Retry mechanism
                        try:
                            if key.lower().endswith(valid_extensions):
                                img_path = os.path.join(directory, key)
                                processed_data = process_image(img_path)
                                break
                        except IOError as e:
                            print(f"Error loading image {img_path}: {e}. Retrying... ({attempt+1}/3)")
                            time.sleep(1)
                    
                    if processed_data is not None:
                        # Convert processed_data to string if it's a list
                        if isinstance(processed_data, list):
                            processed_data = '\n'.join(map(str, processed_data))
                        
                        pdf_filename = os.path.splitext(key)[0] + '.pdf'
                        pdf_path = os.path.join(directory, pdf_filename)
                        save_to_pdf(processed_data, pdf_path)
                        shared_dict[key] = pdf_path
                        assigned_keys.add(key)
                        #print(f"{key} : {shared_dict[key]}")
            else:
                pass
                #print(f"{key} is not an image file and has been skipped.")