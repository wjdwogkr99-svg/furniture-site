import {createHash} from 'node:crypto';
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {products} from '../public/products.mjs';
const pub=new URL('../public/',import.meta.url);
test('HTML ID·코드 선택자·연결 파일이 일치한다',async()=>{const html=await readFile(new URL('index.html',pub),'utf8');const js=await readFile(new URL('app.js',pub),'utf8');const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);assert.equal(new Set(ids).size,ids.length);for(const m of js.matchAll(/\$\('([^']+)'\)/g))assert(ids.includes(m[1]),m[1]);for(const m of html.matchAll(/(?:src|href)="([^"#]+)"/g)){const u=m[1];if(!u.startsWith('http')&&!u.startsWith('#'))await access(new URL(u,pub))}for(const p of products)if(p.image)await access(new URL(p.image,pub))});

test('모든 제품 사진은 해당 한국 공식 페이지에서 받은 파일과 일치한다',async()=>{
 const report=JSON.parse(await readFile(new URL('../docs/ikea-import-report.json',import.meta.url),'utf8'));
 const snapshot=JSON.parse(await readFile(new URL('../docs/products.json',import.meta.url),'utf8'));
 assert.deepEqual(snapshot,products);
 for(const product of products){
  assert(!product.image||product.image.startsWith('assets/ikea/'));
  if(!product.image)continue;
  const proof=report.images.find(p=>p.article===product.article);
  assert(proof,product.id);assert.equal(proof.imageUrl,product.imageSource);
  assert.equal(proof.productUrl,product.source);
  assert.match(proof.imageUrl,/^https:\/\/www\.ikea\.com\/kr\/ko\/images\/products\//);
  const bytes=await readFile(new URL(product.image,pub));
  assert.equal(createHash('sha256').update(bytes).digest('hex'),proof.sha256);
 }
});
