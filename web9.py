import os
import aiohttp
import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import time

async def download_image(session, url, index):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                file_name = f"images/img{index}.png"
                os.makedirs(os.path.dirname(file_name), exist_ok=True)
                with open(file_name, 'wb') as f:
                    f.write(await response.content.read())
                    print(f"Downloaded {file_name}")
            else:
                print(f"Failed to download {url}")
    except Exception as e:
        print(f"Failed to download {url}: {e}")

async def auto_scroll(page):
    await page.evaluate("""async () => {
        await new Promise((resolve) => {
            let totalHeight = 0;
            const distance = 100;
            const timer = setInterval(() => {
                const scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight - window.innerHeight){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    }""")

async def extract_data_from_page(page):
    urls=[]
    await page.waitForSelector('li.product-base', timeout=5000)

    # Autoscroll to load all images
    await auto_scroll(page)

    images = await page.querySelectorAll('li.product-base')
    for index, product_item in enumerate(images):
        # Get the image element within the product item
        image = await product_item.querySelector('img')

        if image:
            # Get the image source URL
            img_src = await page.evaluate('(element) => element.getAttribute("src")', image)
            print(img_src)

            time.sleep(2)
            if img_src:
                urls.append(img_src)
    return urls 

async def main():
    all_urls = []
    for i in range(201,221):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
            'Accept-Language': 'en-US,en;q=0.8',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document'
        }
        browser = await launch(headless=True)
        page = await browser.newPage()
        await stealth(page)

        await page.goto("  p={}".format(i))

        # Extract data from page
        urls = await extract_data_from_page(page)
        all_urls.extend(urls) 

        await browser.close()

    async with aiohttp.ClientSession(headers=headers) as session:

        tasks = []
        for index, url in enumerate(all_urls):
               tasks.append(asyncio.create_task(download_image(session, url, index)))

        await asyncio.gather(*tasks)

        await browser.close()

asyncio.run(main())
            
