const puppeteer = require('puppeteer')

const url_base = 'http://127.0.0.1:8000/'
const delay_step = 500
const headless = false

const x2 = 200
const y2 = 200

const x3 = 500
const y3 = 100

screenshotPath="./screenshots/testThreeConnectedConcepts.png"

if (headless) {
    const delay_step = 10
}

describe('Second puppeteer test', () => {
    it('should launch the cam admin site + Make 3 connected concepts', async function () {
        const browser = await puppeteer.launch({headless: headless, defaultViewport: null})//, args: ['--windows-size=1920,1080'], defaultViewport: {width:1920, height:1080}},)
        const page = await browser.newPage()
        await page.goto(url_base)
        await page.waitForTimeout(delay_step)
        await page.click('#noregister', {clickCount: 1})
        await page.waitForTimeout(delay_step)

        // in CAM Canvas

        // Make first Cam
        await page.waitForTimeout(delay_step)
        await page.click('#CAM_items', {clickCount: 1})
        await page.waitForTimeout(delay_step)
        await page.type('#title_1', "test text 1")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        // Make Second Cam
        await page.mouse.click(x2, y2)
        await page.waitForTimeout(delay_step)
        await page.type('#title_1', "test text 2")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        // Make Third Cam
        await page.mouse.click(x3, y3)
        await page.waitForTimeout(delay_step)
        await page.type('#title_3', "test text 3")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        const button_link = await page.$('#link_add');
        const button_blk_2 = await page.$('#block_form_2');
        const button_blk_3 = await page.$('#block_form_3');
        const button_blk_1 = await page.$('#block_form_1');

        // Link 1rst and 2nd CAM
        await button_link.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_1.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_2.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)

        // Link 2nd and 3rd CAM
        await button_link.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_2.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_3.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)

        // Link 3rd and 1rst CAM with arrow
        await button_link.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_1.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_3.evaluate(b => b.click());
        // Change to arrow
        const button_arrow2 = await page.$('#arrow_option2');
        await button_arrow2.evaluate(b => b.click())
        await page.waitForTimeout(delay_step)

        await page.screenshot({                      // Screenshot the website using defined options
            path: screenshotPath,      // Save the screenshot
            fullPage: true                              // take a fullpage screenshot
        });

        await browser.close()

    })
})