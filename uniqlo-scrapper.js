const { chromium } = require('playwright');
const fs = require('fs');
const csvWriter = require('csv-write-stream');
const path = require('path');

const queries = ['女裝_外套', '女裝_洋裝', '女裝_裙裝', '女裝_褲裝', '女裝_襯衫', '女裝_T恤', '男裝_外套', '男裝_褲裝', '男裝_襯衫', '男裝_T恤'];

const scrapeQuery = async (query) => {
    const browser = await chromium.launch({
        headless: false, // Set to true for headless mode
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' // Adjust this path to match your Chrome installation
    });

    const context = await browser.newContext();
    const page = await context.newPage();

    console.log('Opening CSV file for writing...');
    const writer = csvWriter({ headers: ["title", "product_link", "product_image_url", "price", "color_codes"] });
    writer.pipe(fs.createWriteStream(path.join(__dirname, `uniqlo_${query}.csv`), { encoding: 'utf-8' }));

    let numProducts = 1;
    for (let pageCnt = 1;; ++pageCnt) {
        await page.goto(`https://www.uniqlo.com/tw/zh_TW/search.html?description=${query}&page=${pageCnt}`, { timeout: 60000 });

        try {
            console.log('Waiting for pagination to load...');
            await page.waitForSelector('.h-pagination', { timeout: 10000 });
        } catch (e) {
            console.log(`No more pages to scrape.`);
            break;
        }
        
        console.log('Scrolling to pagination element...');
        await page.evaluate(() => {
            const paginationElement = document.querySelector('.h-pagination');
            if (paginationElement) {
                paginationElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
        console.log('Sleeping for 2 seconds to allow page to load...');
        await page.waitForTimeout(2000);

        console.log('Finding all product elements on the page...');
        const productElements = await page.$$('.product-li');

        numProducts = productElements.length;
        console.log(`Found ${numProducts} products on this page.`);
        
        for (const product of productElements) {
            try {
                // Get the href attribute
                const linkElement = await product.$('.product-herf');
                const href = await linkElement.getAttribute('href');

                // Get the product title from the alt attribute of the main image
                const titleElement = await product.$('.picture-img');
                const title = await titleElement.getAttribute('alt');

                // Get the main image URL
                const imgUrl = await titleElement.getAttribute('src');

                // Get the price from the element with class 'h-currency bold'
                const priceElement = await product.$('.h-currency.bold');
                const price = await priceElement.textContent();

                const blockElement = await product.$('.block');
                const colorImages = await blockElement.$$('img.picture-img');
                const colorCodes = [];
                for (const colorImage of colorImages) {
                    const colorImageUrl = await colorImage.getAttribute('src');
                    console.log('colorImageUrl:', colorImageUrl);
                    const regex = /COL\d{2}/;
                    const colorCode = colorImageUrl.match(regex)[0];
                    console.log('colorCode', colorCode);
                    colorCodes.push(colorCode);
                }

                // Write the extracted data to the CSV file
                writer.write({ title, product_link: href,  product_image_url: imgUrl, price, color_codes: colorCodes.join(',')});

                console.log(`Processed product: ${title}`);
            } catch (e) {
                console.log(`Error processing product: ${e}`);
                continue;
            }
        }
    }

    console.log('Scraping completed. Closing WebDriver...');
    writer.end();
    await browser.close();
}

(async () => {
    const threads = [];
    for (const query of queries) {
        threads.push(scrapeQuery(query));
    }
    await Promise.all(threads);
})();


