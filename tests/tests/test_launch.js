const puppeteer = require('puppeteer')

const url_base = 'http://127.0.0.1:8000/'
const delay_step = 500
const headless = false

const x2 = 200
const y2 = 200

const x3 = 500
const y3 = 100


if (headless) {
	const delay_step = 10
}

describe('Basic puppeteer tests', () => {
	it('should launch the cam admin site', async function(){
		const browser = await puppeteer.launch({headless: headless, defaultViewport: null})//, args: ['--windows-size=1920,1080'], defaultViewport: {width:1920, height:1080}},)
		const page = await browser.newPage()
		await page.goto(url_base)
		await page.waitForTimeout(delay_step)
		await page.click('#noregister',{clickCount: 1})
		await page.waitForTimeout(delay_step)

		// get Canvas
		// const frame = await page.waitForSelector("#Cam_items")
		// find its coordinates
		// const rect = await page.evaluate(el => {
		// 	const {x,y} = el.getBoundingClientRect();
		// 	return {x,y};
		// }, frame);

		// const offset = {x: 220, y: 50}

		// in CAM Canvas

		// Make first Cam
		await page.waitForTimeout(delay_step)
		await page.click('#CAM_items',{clickCount: 1})
		await page.waitForTimeout(delay_step)
		await page.type('#title_1',"test text 1")
		await page.waitForTimeout(delay_step)
		await page.keyboard.press('Enter',{delay:10})
		await page.waitForTimeout(delay_step)

		// Make Second Cam
		await page.mouse.click(x2,y2)
		await page.waitForTimeout(delay_step)
		await page.type('#title_1',"test text 2")
		await page.waitForTimeout(delay_step)
		await page.keyboard.press('Enter',{delay:10})
		await page.waitForTimeout(delay_step)

		// Make Third Cam
		await page.mouse.click(x3,y3)
		await page.waitForTimeout(delay_step)
		await page.type('#title_3',"test text 3")
		await page.waitForTimeout(delay_step)
		await page.keyboard.press('Enter',{delay:10})
		await page.waitForTimeout(delay_step)
		//
		// // Link 1rst and 2nd CAM
		// await page.click('#link_add',{clickCount: 1})
		// await page.waitForTimeout(delay_step)
		// await page.mouse.click(x2+1,y2+1)
		// await page.waitForTimeout(delay_step)
		// await page.mouse.click(x3+1,y3+1)
		// await page.waitForTimeout(delay_step)



		await browser.close()


	})
})