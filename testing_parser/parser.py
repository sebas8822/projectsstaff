


import asyncio
from pyppeteer import launch


async def main():
   browserObj =await launch({"headless": False})
   url = await browserObj.newPage()
   await url.goto('https://au.indeed.com/?vjk=d8df76a6607313db&advn=6508411680652221')


   ## Get HTML
   htmlContent = await url.content()
   await browserObj.close()
   return htmlContent


response = asyncio.get_event_loop().run_until_complete(main())
print(response)