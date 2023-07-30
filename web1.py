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
                file_name = f"images2/img{index}.png"
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
    await page.waitForSelector('div.preview', timeout=5000)

    # Autoscroll to load all images
    await auto_scroll(page)

    images = await page.querySelectorAll('div.preview ')
    print(len(images))
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.'
    }
    browser = await launch(headless=True)
    page = await browser.newPage()
    await stealth(page)

    for i in range(1, 2):  # Scrape 5 pages (20 products per page)
        await page.goto(f"https://www.ajio.com/c/830316017?p={i}")

        # Extract data from page
        urls = await extract_data_from_page(page)
        all_urls.extend(urls)

        if len(all_urls) >= 100:
            break

    await browser.close()

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for index, url in enumerate(all_urls[:100]):
            tasks.append(asyncio.create_task(download_image(session, url, index)))

        await asyncio.gather(*tasks)

asyncio.run(main())
