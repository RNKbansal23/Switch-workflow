'use strict';
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const output = path.resolve('.proofdesk/qa');
  fs.mkdirSync(output, {recursive:true});
  const browser = await chromium.launch({headless:true,
    ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE} : {})});
  const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto(process.env.PROOFDESK_QA_URL);
    await page.getByText('Local workspace connected', {exact:true}).waitFor();
    assert.equal(await page.locator('#metric-total').textContent(), '1');
    await page.screenshot({path:path.join(output,'desktop.png'),fullPage:true});
    await page.getByRole('button', {name:'New case'}).click();
    await page.locator('[name="summary"]').fill('Browser QA <script> text is escaped');
    await page.locator('[name="request_key"]').fill('browser-qa-report');
    await page.locator('[name="steps"]').fill("Call order_total('10.05', 1, '10')");
    await page.locator('[name="expected"]').fill('9.05');
    await page.locator('[name="actual"]').fill('10.05');
    await page.getByRole('button', {name:'Create case',exact:false}).click();
    await page.locator('#detail-view h1').filter({hasText:'Browser QA <script> text is escaped'}).waitFor();
    assert.equal(await page.locator('#detail-view script').count(), 0);
    await page.getByRole('button', {name:'Back to case desk'}).click();
    await page.locator('#search').fill('no-such-case-qa');
    await page.getByRole('heading', {name:'No matching cases.'}).waitFor();
    await page.locator('#search').fill('');
    await page.getByRole('button', {name:'Switch setup'}).click();
    await page.getByText('Live Switch connection not yet verified', {exact:true}).waitFor();
    for (const width of [390,768,1440]) {
      await page.setViewportSize({width,height:900});
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Setup overflow at ${width}`);
    }
    await page.getByRole('button', {name:'Case desk'}).click();
    await page.locator(`[data-case="${process.env.PROOFDESK_QA_CASE}"]`).click();
    await page.getByRole('tab', {name:'Patch',exact:true}).click();
    await page.locator('.diff-add').first().waitFor();
    await page.getByRole('tab', {name:'Checks',exact:true}).click();
    assert.equal(await page.locator('.evidence-table').count(), 2);
    assert.equal(await page.locator('.evidence-table').first().locator('.check-pass').count(), 11);
    await page.screenshot({path:path.join(output,'checks-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Checks overflow at 390');
    await page.setViewportSize({width:1440,height:1000});
    await page.getByRole('tab', {name:'Checks',exact:true}).press('ArrowRight');
    assert.equal(await page.getByRole('tab', {name:'Timeline'}).getAttribute('aria-selected'), 'true');
    await page.getByRole('tab', {name:'Overview',exact:true}).click();
    await page.getByText('QA fixture thread', {exact:true}).waitFor();
    await page.setViewportSize({width:390,height:844});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Detail overflow at 390');
    await page.locator('#toast').evaluate(element => { element.hidden = true; });
    await page.screenshot({path:path.join(output,'mobile.png'),fullPage:true});
    await page.setViewportSize({width:1440,height:1000});
    await page.getByRole('button', {name:'Run independent checks'}).click();
    await page.getByRole('button', {name:'Accept patch'}).waitFor({state:'visible'});
    await page.locator('[name="reviewer"]').fill('Browser QA operator');
    await page.locator('[name="reason"]').fill('Automated disposable-fixture test: inspected candidate and eleven checks.');
    await page.getByRole('button', {name:'Accept patch'}).click();
    await page.getByRole('button', {name:'Create reply draft'}).click();
    await page.getByRole('button', {name:'Close local case'}).click();
    await page.getByText('Local patch accepted and case closed.', {exact:false}).waitFor();
    await page.getByRole('tab', {name:'Overview',exact:true}).click();
    await page.getByText('Ready for your words', {exact:true}).waitFor();
    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', {name:'Export report'}).click();
    const download = await downloadPromise;
    await download.saveAs(path.join(output,'fixture-report.html'));
    const report = fs.readFileSync(path.join(output,'fixture-report.html'),'utf8');
    assert.ok(report.includes('Browser QA operator'));
    assert.ok(report.includes('DRAFT ONLY'));
    await page.getByRole('button', {name:'Back to case desk'}).click();
    for (const width of [390,768,1440]) {
      await page.setViewportSize({width,height:900});
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Desk overflow at ${width}`);
    }
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({passed:true,widths:[390,768,1440],screenshots:output,
      checked:['intake','escaped customer text','search','setup','patch','checks','keyboard tabs','verification job','human review','draft','closure','report export'],
      mode:'Disposable prepared fixtures; not a live Switch run'},null,2));
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode=1;});
