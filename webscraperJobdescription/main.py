import asyncio
from pyppeteer import launch

async def scrape_indeed(url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url)

        # Extract job description
        job_description = await page.evaluate('''() => {
            let jobDescription = "";
            let jobDescriptionEls = document.querySelectorAll('.jobsearch-jobDescriptionText div');
            for (let el of jobDescriptionEls) {
                jobDescription += el.innerText + "\\n\\n";
            }
            return jobDescription;
        }''')

        return job_description
    finally:
        if 'browser' in locals():
            await browser.close()

async def main():
    url = 'https://au.indeed.com/viewjob?jk=1234567890abcdef'
    job_description = await scrape_indeed(url)
    print(job_description)

asyncio.run(main())