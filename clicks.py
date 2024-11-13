import csv
import time
import asyncio
from gettext import find
from login_utils import login
from image_filter import grey
from imagetext import text_in_image
from textprocess import process_text
from pyppeteer.errors import ElementHandleError
from csvsearch import find

async def click(page,url,depth):
    if depth == 0:
        return 
    
    slashes = url.count('/')
    if slashes > depth+3:
        return

    if(url!=''):
        await page.goto(url)
        time.sleep(4)
    await page.setViewport({'width':1920,'height':1080})
    await page.screenshot({'path':'main.png','fullpage':True})
    grey('main.png',url)
    
    text=text_in_image('grey.png')
    words = process_text(text)

    for word in words:
        try:
            elements_match = await page.xpath(f'//*[contains(text(), "{word}")]')
        except ElementHandleError as e:
             continue
             
        if len(elements_match)==0:
            continue

        for elem in elements_match:
            bounding_box = await elem.boundingBox()
        
        if bounding_box is None:
                continue
        
        coordinates = {
            'x': bounding_box['x'] + bounding_box['width'] / 2,
            'y': bounding_box['y'] + bounding_box['height'] / 2
        }

        await page.mouse.click(coordinates['x'], coordinates['y'])
        await asyncio.sleep(1)
        if(url!=page.url):
                if (await find(page.url) == False):
                    #print("clicks.py #39 clicked on:",word,"leading to",page.url)
                    with open('urls.csv', 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([page.url])
    return 