
# Description: Scrapes a URL and returns the HTML source from dynamic page using pyppeteer
# Add the following in requirements.txt: pyppeteer==1.0.2

import asyncio
from pyppeteer import launch

async def get_page_dynamic(givenUrl):
   """Scrapes a URL of dynamic page using Pyppeteer.

   Args:
       url (string): Fully qualified URL of a page.

   Returns:
       Title (string) and Description Text (list).
   """
   # Downloads the browser in next line
   browser = await launch(
      headless=True,
      handleSIGINT=False,
      handleSIGTERM=False,
      handleSIGHUP=False,
      args= ['--no-sandbox']
   )
   page = await browser.newPage()
   await page.setUserAgent \
      ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

   # Indeed scraping logic that works with url from search page or specific job page
   if 'indeed' in givenUrl and 'jk' in givenUrl:
      jkValue = givenUrl.split('jk=')[1].split('&')[0]
      baseUrl = 'https://au.indeed.com/viewjob?jk='
      url = baseUrl + jkValue
   else:
      url = givenUrl

   await page.goto(url)
   pageTitle = await page.title()

   async def get_value(tagName):
      """Gets value from matching provided tagName.

      Args:
          tagName (string): tags, class, id etc.

      Returns:
          tagText (string): Field value.
      """
      tag = await page.querySelector(tagName)
      tagText = await page.evaluate('(element) => element.innerText', tag) if tag else ""
      return tagText

   try:
      # For indeed webpage and so forth
      if 'indeed' in givenUrl:
         position = await get_value('h1')
         company = await get_value('[data-company-name = "true"]')
         salary = await get_value('#salaryInfoAndJobType')
         details = await get_value('#jobDescriptionText')

      elif 'careerjet' in givenUrl:
         position = await get_value('h1')
         company = await get_value('.company')
         salary = await get_value('.details')
         details = await get_value('.content')

      elif 'careerone' in givenUrl:
         position = await get_value('h1')
         company = await get_value('.jv-subtitle')
         salary = await get_value('.jv-pay-summary')
         details = await get_value('#jvDescription')

      elif 'jora' in givenUrl:
         position = await get_value('.job-title.heading-xxlarge')
         company = await get_value('.company')
         # location = await get_value('.location')
         salary = await get_value('.badge.-default-badge')
         details = await get_value('#job-description-container')

      elif 'glassdoor' in givenUrl:
         position = await get_value('[data-test="job-title"]')
         # location = await get_value('[data-test="location"]')
         company = await get_value('[data-test="employer-name"]')
         salary = await get_value('.small.css-10zcshf.e1v3ed7e1')
         details = await get_value('#JobDescriptionContainer')

      descriptionText = [position, company, salary, details]

   except:
      pTags = await page.querySelectorAll('p, h1, h2, h3, ul')
      descriptionText = [await page.evaluate('(element) => element.innerText', p) for p in pTags]

   await browser.close()
   print('extracted using pyppeteer')
   return pageTitle, descriptionText


async def main():
   result = await get_page_dynamic('https://www.careerjet.com.au/jobad/aub0020120c3c042d3ef8a0c9e508454ae')
   print(result)


if __name__ == '__main__':
   loop = asyncio.get_event_loop()
   loop.run_until_complete(main())