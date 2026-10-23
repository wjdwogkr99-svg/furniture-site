import test from 'node:test';
import assert from 'node:assert/strict';
import {calculate,products,fit,filterProducts,overlaps} from '../public/model.mjs';
const base={height:175,age:28,popliteal:null,buttock:null,elbow:null};
test('실측값이 각 추정 항목을 우선한다',()=>{assert.deepEqual(calculate({...base,popliteal:440,buttock:500,elbow:700}),{seat:[420,440],depth:[440,460],desk:[680,700],measured:3});const partial=calculate({...base,popliteal:440});assert.deepEqual(partial.depth,calculate(base).depth)});
test('부적절한 입력을 거절한다',()=>{for(const p of [{height:NaN},{age:17},{height:211},{age:101},{popliteal:240},{popliteal:500,elbow:450}])assert.throws(()=>calculate({...base,...p}))});
test('맞닿는 범위만 교집합으로 취급한다',()=>{assert(overlaps([420,450],[450,580]));assert(!overlaps([420,449],[450,580]))});
test('가격·카테고리·저장 필터가 함께 동작한다',()=>{const list=filterProducts(products,{category:'chair',budget:100000});assert(list.length>=3);assert(list.every(p=>p.type==='chair'&&p.price<=100000));assert(list.some(p=>p.id==='loberget'));assert.equal(filterProducts(products,{savedOnly:true,saved:['micke']})[0].id,'micke')});
test('낮은 가격순과 높은 가격순을 구분한다',()=>{const asc=filterProducts(products),desc=filterProducts(products,{sort:'price-desc'});assert.deepEqual(asc.map(p=>p.price),desc.map(p=>p.price).reverse())});
test('사양 상충 제품과 라운지를 자동 적합도로 추천하지 않는다',()=>{const r=calculate(base);assert(!fit(products.find(p=>p.id==='trotten-electric'),r).pass);assert(!fit(products.find(p=>p.id==='poang'),r).pass);const matched=filterProducts(products,{fitOnly:true,result:r});assert(!matched.some(p=>p.type==='lounge'||p.id==='trotten-electric'));assert(matched.some(p=>p.id==='lagkapten-olov'))});
test('MARKUS 한국 중 규격과 제품번호를 보존한다',()=>{const p=products.find(p=>p.id==='markus');assert.deepEqual(p.height,[460,570]);assert(p.price>0);assert.equal(p.article,'50261151')});
test('수집 제품 모두 출처·확인일·가격·치수 상태를 갖는다',()=>{assert(products.length>20);assert.equal(new Set(products.map(p=>p.id)).size,products.length);for(const p of products){assert.match(p.source,/^https:\/\/www\.ikea\.com\/kr\/ko\/p\//);assert(p.price>0);assert.match(p.verifiedAt,/^\d{4}-\d{2}-\d{2}$/);assert(p.height||['missing','conflicting'].includes(p.heightStatus))}});

test('신체 계산 결과를 전달하면 기본으로 치수를 자동 필터한다',()=>{
 const result=calculate(base);
 const list=filterProducts(products,{result});
 for(const id of ['lagkapten-olov','flintan','millberget','mittzon','jaervfjaellet'])assert(list.some(p=>p.id===id));assert(list.every(p=>fit(p,result).pass));
 assert.equal(filterProducts(products,{result,fitOnly:false}).length,products.length);
 const measured=calculate({...base,popliteal:480,buttock:490,elbow:750});
 const ids=filterProducts(products,{result:measured}).map(p=>p.id);
 assert(ids.includes('loberget'));assert(ids.includes('orfjall'));assert(!ids.includes('millberget'));
 assert(ids.includes('trotten-fixed'));assert(!ids.includes('trotten-electric'));
 const short=calculate({...base,height:140});assert(filterProducts(products,{result:short}).every(p=>fit(p,short).pass));
});
test('높이만 맞고 깊이가 불명확한 의자는 자동 필터에서 제외한다',()=>{
 const chair={...products.find(p=>p.id==='millberget'),depth:null};
 assert.equal(fit(chair,calculate(base)).pass,false);
});
test('실측이 같으면 국적·성별·키가 달라도 같은 제품을 제시한다',()=>{
 const measured={...base,popliteal:480,buttock:490,elbow:750};
 assert.deepEqual(filterProducts(products,{result:calculate(measured)}),filterProducts(products,{result:calculate({...measured,height:190,nationality:'외국인',gender:'여성'})}));
});

test('소파·식탁은 업무용 높이가 겹쳐도 자동 추천하지 않는다',()=>{
 const result=calculate(base);
 for(const type of ['sofa','dining']){
  const product={...products[0],type,height:[400,1000],depth:[300,600]};
  assert.equal(fit(product,result).pass,false);
  assert.equal(filterProducts([product],{result}).length,0);
  assert.equal(filterProducts([product],{result,fitOnly:false}).length,1);
 }
 const unknown={...products[0],height:null,heightStatus:'missing'};
 assert.equal(fit(unknown,result).label,'사양 확인 필요');
 assert.equal(fit(unknown,result).pass,false);
});
