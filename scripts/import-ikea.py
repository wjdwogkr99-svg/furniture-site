#!/usr/bin/env python3
"""Refresh a reviewable Korean IKEA snapshot; no deployment or live user requests."""
import argparse
import concurrent.futures
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'chair': 'https://www.ikea.com/kr/ko/cat/desk-chairs-20652/',
    'table': 'https://www.ikea.com/kr/ko/cat/desks-computer-desks-20649/',
    'dining': 'https://www.ikea.com/kr/ko/cat/dining-tables-21825/',
    'sofa': 'https://www.ikea.com/kr/ko/cat/sofas-fu003/',
    'lounge': 'https://www.ikea.com/kr/ko/cat/armchairs-16239/',
}

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.parts=[]; self.skip=0; self.cards=[]
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag in ('script', 'style'): self.skip+=1
        if 'data-product-compact' in attrs:
            self.cards.append((attrs.get('data-product-number'), attrs.get('data-product-name')))
    def handle_endtag(self, tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
    @property
    def text(self): return re.sub(r'\s+', ' ', ' '.join(self.parts))

def download(url, cache, refresh=False):
    if not url.startswith('https://www.ikea.com/kr/ko/'):
        raise ValueError('Only official Korean IKEA URLs are accepted')
    target=cache/hashlib.sha256(url.encode()).hexdigest()
    if refresh or not target.exists():
        time.sleep(.15)
        result=subprocess.run(['curl','--fail','--silent','--show-error','--location',
                               '--max-time','45','--proto','=https',url],capture_output=True,check=True)
        target.write_bytes(result.stdout)
    return target.read_bytes()

def product_schema(source, article):
    for raw in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',source,re.S):
        data=json.loads(raw)
        if data.get('@type')=='Product' and re.sub(r'\D','',data.get('sku',''))==article:
            url=data.get('offers',{}).get('url','')
            if not re.fullmatch(r'https://www\.ikea\.com/kr/ko/p/[a-z0-9-]*'+article+r'/',url):
                raise ValueError('Matching Korean product URL not found')
            return data
    raise ValueError('Matching Korean product SKU not found; redirect or unavailable product')

def measurements(source):
    result={}
    for name,value in re.findall(r'<span[^>]*class="[^"]*measurements-tab__measurement-name[^"]*"[^>]*>(.*?)</span>\s*<span[^>]*class="[^"]*measurements-tab__measurement-value[^"]*"[^>]*>(.*?)</span>',source,re.S):
        label=html.unescape(re.sub('<[^>]+>','',name)).strip()
        text=html.unescape(re.sub('<[^>]+>','',value)).strip()
        match=re.fullmatch(r'(\d+(?:\.\d+)?)\s*cm',text)
        if match: result[label]=round(float(match[1])*10)
    return result

def dimension(values, label):
    return values.get(label)

def parse_product(source, article, group):
    data=product_schema(source,article); text=measurements(source)
    offer=data.get('offers',{})
    if offer.get('priceCurrency')!='KRW': raise ValueError('KRW price missing')
    price=float(offer['price'])
    if price<=0 or not price.is_integer(): raise ValueError('Invalid price')
    url=offer['url']; full=data['name']; name=full.split()[0]
    category=data.get('category','')
    # Category listings can contain floor protectors, chair parts and sofa covers.
    if group=='chair' and ('의자' not in category or any(x in full for x in ['프레임','커버','시트/','하부프레임','발보호','매트'])): raise ValueError('Not a complete chair')
    if group in ('table','dining') and ('책상' not in category and '테이블' not in category or any(x in full for x in ['상판','하부프레임','다리,'])): raise ValueError('Not a complete table')
    if group in ('sofa','lounge') and (any(x in category for x in ['커버','다리','쿠션','액세서리','풋스툴','스툴']) or not any(x in category for x in ['소파','암체어','의자','라운지체어','릴렉스체어'])): raise ValueError('Not complete seating')
    low=dimension(text,'최소 시트 높이') if group=='chair' else dimension(text,'최소 높이')
    high=dimension(text,'최대 시트 높이') if group=='chair' else dimension(text,'최대 높이')
    single=dimension(text,'시트 높이') if group in ('chair','lounge','sofa') else dimension(text,'높이')
    height=[low,high] if low is not None and high is not None else [single,single] if single else None
    depth=dimension(text,'시트 깊이') if group in ('chair','lounge','sofa') else None
    width=dimension(text,'시트 폭') if group in ('chair','lounge','sofa') else None
    topwidth=dimension(text,'길이') or dimension(text,'폭'); topdepth=dimension(text,'깊이')
    size=f'{topwidth} × {topdepth} mm' if topwidth and topdepth else '상판 크기 확인 필요'
    return dict(id='ikea-'+article,article=article,name=name,ko=full.split()[1],brand='IKEA',type=group,
                price=int(price),currency='KRW',height=height,depth=[depth,depth] if depth else None,
                seatWidth=width,spec='상판 높이' if group in ('table','dining') else '좌면 높이',
                other='상판 크기' if group in ('table','dining') else '좌면 깊이',
                otherText=size if group in ('table','dining') else '확인 필요',
                source=url,desc=full.split(' - ',1)[-1],
                note='한국 공식 치수표 기준. 조절 수치 범위가 없으면 단일 표기값만 비교하며, 너비·하부 여유·착석감은 별도 확인하세요.',
                heightStatus='verified' if height else 'missing'), data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--refresh',action='store_true',help='Refetch instead of using the local download cache')
    parser.add_argument('--cache',type=Path,default=Path(tempfile.gettempdir())/'fitform-ikea-cache')
    args=parser.parse_args(); args.cache.mkdir(parents=True,exist_ok=True)
    original=json.loads((ROOT/'docs/products.json').read_text())
    for product in original:
        if 'article' not in product:
            product['article']=re.search(r'(\d{8})/$',product['source'])[1]
    day=datetime.now(ZoneInfo('Asia/Seoul')).date().isoformat()
    report=dict(checkedAt=day,categories=[],failures=[],excluded=[],images=[],coverage='Public category listing snapshots; not a complete IKEA inventory. Color-only variants are not expanded.')
    jobs={p['article']:(p['source'],p['type'],p) for p in original}
    families={p['name'] for p in original}
    for group,url in CATEGORIES.items():
        try:
            source=download(url,args.cache,args.refresh).decode(); page=Page(source)
            count=re.search(r'totalCount&quot;:(\d+)',source)
            report['categories'].append(dict(type=group,url=url,listed=len(page.cards),reportedTotal=int(count[1]) if count else None))
            for article,full in page.cards:
                if not article or not full: continue
                name=full.split()[0]
                if article in jobs or name in families: continue
                match=re.search(r'https://www\.ikea\.com/kr/ko/p/[^"<>\s#]*'+article+r'/',html.unescape(source))
                if match: jobs[article]=(match[0],group,None); families.add(name)
        except Exception as error: report['failures'].append(dict(source=url,error=str(error)))
    image_dir=ROOT/'public/assets/ikea'; image_dir.mkdir(exist_ok=True)
    def fetch(item):
        article,(url,group,existing)=item
        try:
            source=download(url,args.cache,args.refresh).decode()
            if existing and not existing['id'].startswith('ikea-'):
                data=product_schema(source,article); product=dict(existing)
                # Keep reviewed measurements, especially MARKUS Korea and conflicting TROTTEN.
                offer=data['offers']
                if offer.get('priceCurrency')!='KRW' or float(offer['price'])<=0: raise ValueError('Valid KRW price missing')
                product['price']=int(offer['price'])
            else: product,data=parse_product(source,article,group)
            images=data.get('image',[]); first=images[0] if images else None
            image_url=first.get('contentUrl') if isinstance(first,dict) else first
            product.update(verifiedAt=day,dataStatus='verified',image=None,imageSource=None,imageNote='한국 공식 제품 사진 확인 필요. 임의 이미지나 도식을 사용하지 않습니다.')
            if image_url:
                try:
                    image=download(image_url+'?f=m',args.cache,args.refresh)
                    if not image.startswith(b'\xff\xd8'): raise ValueError('Official image is not a JPEG')
                    local=f'assets/ikea/{article}.jpg'; (ROOT/'public'/local).write_bytes(image)
                    product.update(image=local,imageSource=image_url,imageNote='해당 IKEA 한국 판매 페이지의 공식 제품 사진. 색상·구성은 제품 상세를 확인하세요.')
                    proof=dict(article=article,productUrl=url,imageUrl=image_url,downloadUrl=image_url+'?f=m',localPath=local,sha256=hashlib.sha256(image).hexdigest())
                except Exception as error:
                    proof=None; report['failures'].append(dict(source=image_url,error=str(error)))
            else: proof=None
            return product,proof
        except ValueError as error:
            report['excluded' if not existing else 'failures'].append(dict(source=url,error=str(error)))
        except Exception as error: report['failures'].append(dict(source=url,error=str(error)))
        if existing:
            product=dict(existing); product.update(dataStatus='unavailable',image=None,imageSource=None,imageNote='한국 공식 제품 사진 확인 필요. 임의 이미지나 도식을 사용하지 않습니다.')
            return product,None
        return None,None
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for index,(product,proof) in enumerate(pool.map(fetch,jobs.items()),1):
            if product: results.append(product)
            if proof: report['images'].append(proof)
            if index%10==0: print(f'Checked {index}/{len(jobs)} products',flush=True)
    # Preserve the prior successful snapshot if all network reads fail.
    if not report['images']: raise SystemExit('No official product images verified; existing catalog not replaced')
    report.update(productCount=len(results),imageCount=len(report['images']),missingImageCount=sum(not p['image'] for p in results))
    payload=json.dumps(results,ensure_ascii=False,indent=2)+'\n'
    (ROOT/'docs/products.json').write_text(payload)
    (ROOT/'public/products.mjs').write_text('export const products = '+payload.rstrip()+';\n')
    (ROOT/'docs/ikea-import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['productCount','imageCount','missingImageCount','categories']},ensure_ascii=False,indent=2))
    print(f"Failures: {len(report['failures'])}; exclusions: {len(report['excluded'])}")

if __name__=='__main__': main()
