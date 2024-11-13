import asyncio
import os
import shutil
from asyncio.windows_events import NULL
from pyppeteer import launch
from login_utils import login
from csvops import append_csv,trav_csv

def screenshots(url,depth):
    print(type(depth))
    async def start(url,user,password):
        #print(url,depth,"at line11 of lastmain.py")
        browser =  await launch(headless = True,executablePath=r'c:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',ignoreHTTPSErrors=True)
        page = await browser.newPage()

        if(url==''):
            await login(page,url,user,password)
        if os.path.exists('urls.csv'):
            os.remove('urls.csv')
        await append_csv(url)
        await trav_csv(page, depth)
        await browser.close()



    if os.path.exists('screenshots'):
        shutil.rmtree('screenshots')
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    asyncio.get_event_loop().run_until_complete(start(url,user,password))