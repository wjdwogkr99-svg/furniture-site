"""Optional browser QA: start npm run dev, then run with Python Playwright and system Chromium."""
import json
import tempfile
from pathlib import Path
artifacts=Path(tempfile.mkdtemp(prefix="fitform-browser-qa-"))
print(f"Screenshots: {artifacts}")
catalog=json.loads((Path(__file__).resolve().parents[1]/'docs/products.json').read_text())
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in [1440,768,390]:
        page=browser.new_page(viewport={'width':width,'height':1000})
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        response=page.goto('http://127.0.0.1:5173/',wait_until='networkidle')
        assert response.status==200
        assert page.locator('#fitOnly').is_checked()
        assert page.locator('#productGrid .product').count()>0
        default_ids=page.locator('[data-save]').evaluate_all('(buttons)=>buttons.map(b=>b.dataset.save)')
        page.locator('#height').fill('190')
        assert '190 cm' in page.locator('#profileSummary').inner_text()
        assert page.locator('[data-save]').evaluate_all('(buttons)=>buttons.map(b=>b.dataset.save)')!=default_ids
        page.locator('#height').fill('139')
        assert page.locator('.product').count()==0
        assert '입력 범위' in page.locator('.empty').inner_text()
        page.locator('#reset').click()
        assert page.locator('[data-save]').evaluate_all('(buttons)=>buttons.map(b=>b.dataset.save)')==default_ids
        page.locator('details.measure summary').click()
        page.locator('#popliteal').fill('480')
        page.locator('#buttock').fill('490')
        page.locator('#elbow').fill('750')
        assert page.locator('#modeBadge').inner_text()=='실측 기반 검토'
        assert page.locator('[data-save="loberget"]').count()==1
        assert page.locator('[data-save="millberget"]').count()==0
        page.locator('#reset').click()
        page.locator('#fitOnly').uncheck()
        assert page.locator('#productGrid .product').count()==min(24,len(catalog))
        while page.locator('#loadMore').is_visible():page.locator('#loadMore').click()
        assert page.locator('.product').count()==len(catalog)
        last_id=page.locator('[data-save]').last.get_attribute('data-save')
        page.locator(f'[data-save="{last_id}"]').click()
        assert page.locator('.product').count()==len(catalog)
        page.locator(f'[data-save="{last_id}"]').click()
        assert page.locator('#savedCount').inner_text()=='0'
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal overflow'
        page.locator('#category [data-value="chair"]').click()
        page.locator('#budget').select_option('100000')
        assert page.locator('#productGrid .product').count()>0
        prices=page.locator('.product-price').all_text_contents()
        values=[int(''.join(filter(str.isdigit,v))) for v in prices]
        assert all(v<=100000 for v in values) and values==sorted(values)
        page.locator('[data-save]').first.click()
        page.reload(wait_until='networkidle')
        page.locator('#fitOnly').uncheck()
        assert page.locator('#savedCount').inner_text()=='1'
        page.locator('[data-compare]').nth(0).check()
        page.locator('[data-compare]').nth(1).check()
        page.locator('[data-compare]').nth(2).check()
        page.locator('[data-compare]').nth(3).click()
        assert page.locator('[data-compare]:checked').count()==3
        assert page.locator('#compareCount').inner_text()=='3'
        page.locator('#compareBtn').click()
        assert page.locator('#modal').is_visible()
        page.locator('#closeModal').click()
        page.locator('#height').fill('180')
        page.locator('#profileForm button[type=submit]').click()
        assert '180 cm' in page.locator('#profileSummary').inner_text()
        page.locator('#reset').click()
        page.locator('#budget').select_option('100000')
        page.locator('#category [data-value="chair"]').click()
        page.locator('#fitOnly').uncheck()
        assert page.locator('.product').count()>=3
        page.locator('#sort').select_option('price-desc')
        assert page.locator('.product h3').first.inner_text()=='BLECKBERGET'
        page.locator('#category [data-value="all"]').click()
        page.locator('#budget').select_option('100000000')
        page.locator('#savedBtn').click()
        assert page.locator('.product').count()==1
        page.locator('[data-save]').click()
        assert page.locator('.empty').is_visible()
        page.reload(wait_until='networkidle')
        page.locator('#fitOnly').uncheck()
        assert page.locator('#savedCount').inner_text()=='0'
        page.locator('#usage [data-value="lounge"]').click()
        page.locator('#fitOnly').check()
        assert page.locator('.product').count()==0
        assert page.locator('#loungeNotice').is_visible()
        page.locator('#usage [data-value="work"]').click()
        page.locator('#nationality [data-value="외국인"]').click()
        assert page.locator('#countryField').is_visible()
        page.locator('#profileForm button[type=submit]').click()
        assert '외국인' in page.locator('#profileSummary').inner_text()
        assert '예시' in page.locator('#modeBadge').inner_text()
        page.locator('#bottomGuide').click()
        assert '검증되지 않은' in page.locator('#modalBody').inner_text()
        page.locator('#closeModal').click()
        page.locator('#reset').click()
        page.locator('#fitOnly').uncheck()
        page.locator('#category [data-value="sofa"]').click()
        assert not page.locator('#fitOnly').is_checked()
        assert page.locator('.product').count()>0
        assert all('개별 용도 확인' in text for text in page.locator('.fit-status').all_text_contents())
        page.locator('#category [data-value="dining"]').click()
        assert page.locator('.product').count()>0
        assert all('개별 용도 확인' in text for text in page.locator('.fit-status').all_text_contents())
        page.locator('#category [data-value="all"]').click()
        while page.locator('#loadMore').is_visible():page.locator('#loadMore').click()
        assert page.locator('.product').count()==len(catalog)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'catalog horizontal overflow'
        assert page.locator('.product-schematic svg').count()==0
        for product_image in page.locator('#productGrid img').all():
            product_image.scroll_into_view_if_needed()
            page.wait_for_function('(img)=>img.complete && img.naturalWidth>0',arg=product_image.element_handle())
        assert not errors, errors
        page.screenshot(path=str(artifacts / f'{width}.png'),full_page=True)
        print(json.dumps({'width':width,'products':len(catalog),'filter_sort_save_compare_profile':'passed','overflow':False,'js_errors':errors}))
        page.close()
    browser.close()
