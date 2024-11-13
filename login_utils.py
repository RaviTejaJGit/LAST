import asyncio

async def login(page, url, user, password):
    await page.goto(url)

    # Wait for the username field using XPath
    await page.waitForXPath('//*[@id="username"]', timeout=10000)  # Wait up to 10 seconds
    username_element = await page.xpath('//*[@id="username"]')
    await username_element[0].type(user)

    # Wait for the password field
    await page.waitForXPath('//*[@id="password"]', timeout=10000)
    password_element = await page.xpath('//*[@id="password"]')
    await password_element[0].type(password)