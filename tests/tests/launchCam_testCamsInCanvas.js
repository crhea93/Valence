 const puppeteer = require('puppeteer')

 const url_base = 'http://127.0.0.1:8000/'
 const delay_step = 200
 const headless = false

 const x2_2 = 200
 const y2_2 = 200
 const x2_3 = x2_2*2
 const y2_3 = y2_2

const x3_2 = 200
const y3_2 = 200
const x3_3 = x3_2*2
const y3_3 = y3_2

const x4_2 = 200
const y4_2 = 200
const x4_3 = x4_2*2
const y4_3 = y4_2

screenshotPath2="./screenshots/testThreeConnectedConcepts.png"
screenshotPath3="./screenshots/testDraggingCam.png"
screenshotPath3_2="./screenshots/testDraggingCam_afterdrag1.png"
screenshotPath4="./screenshots/testTextSize.png"

 if (headless) {
     const delay_step = 10
 }

 describe('Testing actions on canvas with puppeteer test', () => {

     it('should launch the cam admin site + Make 3 connected concepts', async function () {
         const browser = await puppeteer.launch({headless: headless, defaultViewport: null})
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
         await page.mouse.click(x2_2, y2_2)
         await page.waitForTimeout(delay_step)
         await page.type('#title_2', "test text 2")
         await page.waitForTimeout(delay_step)
         await page.keyboard.press('Enter', {delay: 10})
         await page.waitForTimeout(delay_step)

         // Make Third Cam
         await page.mouse.click(x2_3, y2_3)
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
             path: screenshotPath2,      // Save the screenshot
             fullPage: true                              // take a fullpage screenshot
         });

         await browser.close()

     })


    it('Make 3 connected concepts + Drag each one', async function () {
        const browser = await puppeteer.launch({headless: headless, defaultViewport: null})
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
        await page.mouse.click(x3_2, y3_2)
        await page.waitForTimeout(delay_step)
        await page.type('#title_2', "test text 2")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        // Make Third Cam
        await page.mouse.click(x3_3, y3_3)
        await page.waitForTimeout(delay_step)
        await page.type('#title_3', "test text 3")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        const button_link = await page.$('#link_add');
        const button_blk_1 = await page.$('#block_form_1');
        const button_blk_2 = await page.$('#block_form_2');
        const button_blk_3 = await page.$('#block_form_3');

        // Link 1rst and 2nd CAM
        await button_link.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_1.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_2.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)

        // Link 2nd and 3rd CAM
        // await button_link.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_2.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_3.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)

        // Link 3rd and 1rst CAM with arrow
        // await button_link.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_1.evaluate(b => b.click());
        await page.waitForTimeout(delay_step)
        await button_blk_3.evaluate(b => b.click());
        // Change to arrow
        const button_arrow2 = await page.$('#arrow_option2');
        await button_arrow2.evaluate(b => b.click())
        await page.waitForTimeout(delay_step)

        delay_step2 = delay_step *2
        
         await page.screenshot({           // Screenshot the website using defined options
             path: screenshotPath3,      // Save the screenshot
             fullPage: true                              // take a fullpage screenshot
         });

        // console.log('hey')
        // const bounding_box = await button_blk_1.boundingBox();
        // console.log(await bounding_box)
        // console.log('hey1.2')
        // console.log(await button_blk_1.asElement().boxModel())
        // console.log('hey3_2')
        // console.log(await button_blk_1.evaluate())
        // console.log('hey3_2')

        // drag node
        // let bounding_box = await button_blk_1.boundingBox();
        // let x = bounding_box.x + bounding_box.width / 2;
        // let y = bounding_box.y + bounding_box.height / 2;

        // const rect = await page.evaluate((button_blk_1) => {
        // const {top, left, bottom, right} = button_blk_1.getBoundingClientRect();
        // return {top, left, bottom, right};
        //     }, button_blk_1);

        // const middlex = (rect[1]-rect[3])/2
        // const middley = (rect[0]-rect[2])/2

        // console.log(button_blk_1)


        // await button_blk_1.evaluate(b => b.click())
        await page.waitForTimeout(500);
        await page.mouse.move(x3_2+3, y3_2+3);
        await page.waitForTimeout(500);
        // await button_blk_1.evaluate(b => b.mouse.up())
       // await page.waitForTimeout(5000);
         await page.mouse.down();
         await page.mouse.move(x3_2*4, y3_2*4, { steps: 10 });
         await page.mouse.up();
         await page.waitForTimeout(1000);

         await page.screenshot({           // Screenshot the website using defined options
             path: screenshotPath3_2,      // Save the screenshot
             fullPage: true                              // take a fullpage screenshot
         });

        await browser.close()

    }  );


it('Create concepts + test different text sizes', async function () {
        const browser = await puppeteer.launch({headless: headless, defaultViewport: null})
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
        await page.mouse.click(x4_2, y4_2)
        await page.waitForTimeout(delay_step)
        await page.type('#title_2', "abcdefghijklmnopqrstuvwxyz")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        // Make Third Cam
        await page.mouse.click(x4_3, y4_3)
        await page.waitForTimeout(delay_step)
            await page.type('#title_3', "abcdefghijklmnopqrstuvwxyz abcdefghijklmnopqrstuvwxyz")
        await page.waitForTimeout(delay_step)
        await page.keyboard.press('Enter', {delay: 10})
        await page.waitForTimeout(delay_step)

        const button_link = await page.$('#link_add');
        const button_blk_1 = await page.$('#block_form_1');
        const button_blk_2 = await page.$('#block_form_2');
        const button_blk_3 = await page.$('#block_form_3');


        await page.screenshot({                      // Screenshot the website using defined options
             path: screenshotPath4,      // Save the screenshot
             fullPage: true                              // take a fullpage screenshot
         });

        await browser.close()

    }  )


 })
