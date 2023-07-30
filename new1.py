import asyncio
import csv
from bs4 import BeautifulSoup
from pyppeteer import launch

async def scrape_companies_names(page):
    try:
        # Wait for the page to load
        await page.waitForSelector('.table-rows', timeout=20000)
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    # Scroll to the top of the page
    await page.evaluate("window.scrollTo(0, 0)")

    # Render the page and get the HTML
    html = await page.content()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Get the list of companies names
    companies_names = soup.find_all("div", class_="table-value company-name")

    # Return the list of companies names
    return [company.text.strip() for company in companies_names]

async def main():
    # Launch the headless Chrome browser
    browser = await launch()

    # Create a new page
    page = await browser.newPage()

    all_company_names = []

    try:
        await page.goto("https://500.co/companies")  # Await the page.goto() method

        company_names = await scrape_companies_names(page)
        all_company_names.extend(company_names)

        for i in range(1, 21):
            next_button = await page.querySelector('li.next')
            if not next_button or "disabled" in await page.evaluate('(el) => el.className', next_button):
                break
            else:
                # Click on the "Next" button
                await next_button.click()
                
                # Get the next 15 companies names
                next_companies = await scrape_companies_names(page)

                # Add the next 15 companies names to the list
                all_company_names.extend(next_companies)

    except Exception as e:
        print(f"An error occurred: {e}")

    # Close the browser
    await browser.close()

    # Create a CSV file
    with open("companies.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        # Write the header row
        writer.writerow(["Company Name"])
        # Write the companies names to the CSV file
        for company_name in all_company_names:
            writer.writerow([company_name])

if __name__ == "__main__":
    asyncio.run(main())
