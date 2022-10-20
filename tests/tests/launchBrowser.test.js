const puppeteer = require('puppeteer')

describe('First Puppeteer Test', () => {
	it('should launch the browser', async function(){
		const browser = await puppeteer.launch({headless: true})
		const page = await browser.newPage()
		await page.goto('http://www.google.com')
		await browser.close() 
	})
})