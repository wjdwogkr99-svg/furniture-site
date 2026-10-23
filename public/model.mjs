// FITFORM prototype model: height coefficients are design placeholders, not Humanscale formulas.
export const round5=n=>Math.round(n/5)*5;
export function calculate(p){
 if(!Number.isFinite(p.height)||p.height<140||p.height>210||!Number.isFinite(p.age)||p.age<18||p.age>100)throw Error('성인 18–100세, 키 140–210 cm 범위에서 입력해 주세요.');
 for(const [key,min,max] of [['popliteal',250,650],['buttock',300,750],['elbow',400,1000]])if(p[key]!==null&&(!Number.isFinite(p[key])||p[key]<min||p[key]>max))throw Error('실측값의 입력 범위를 확인해 주세요.');
 if(p.popliteal!==null&&p.elbow!==null&&p.elbow<=p.popliteal)throw Error('바닥에서 팔꿈치까지 높이는 무릎 뒤 높이보다 커야 합니다.');
 const h=p.height*10;
 return {seat:p.popliteal!==null?[p.popliteal-20,p.popliteal]:[round5(h*.24),round5(h*.26)],depth:p.buttock!==null?[round5(p.buttock-60),round5(p.buttock-40)]:[round5(h*.255),round5(h*.28)],desk:p.elbow!==null?[p.elbow-20,p.elbow]:[round5(h*.38),round5(h*.40)],measured:[p.popliteal,p.buttock,p.elbow].filter(v=>v!==null).length};
}
export {products} from './products.mjs';
export const overlaps=(a,b)=>Math.max(a[0],b[0])<=Math.min(a[1],b[1]);
export function fit(p,r,usage='work'){
 if(!p.height)return {pass:false,label:'사양 확인 필요',detail:'공식 높이 정보가 상충하여 자동 비교에서 제외됩니다.'};
 if(usage==='lounge'||p.type==='lounge')return {pass:false,label:'개별 착석 확인',detail:'라운지 자세의 적합도는 별도 확인이 필요합니다.'};
 const height=overlaps(p.height,p.type==='table'?r.desk:r.seat);
 const depth=p.depth?overlaps(p.depth,r.depth):true;
 return {pass:height&&depth,label:height&&depth?'비교 범위 겹침':'범위 재검토',detail:p.type==='table'?(height?'상판 높이 범위가 겹칩니다. 하부 여유도 확인하세요.':'목표 작업면 높이와 겹치지 않습니다.'):`좌면 높이 ${height?'겹침':'불일치'} · 깊이 ${depth?'겹침':'불일치'}`};
}

export function filterProducts(products,options={}){
 const {category='all',budget=Infinity,sort='price-asc',fitOnly=false,result,usage='work',savedOnly=false,saved=[]}=options;
 return products.filter(p=>(category==='all'||p.type===category)&&p.price<=budget&&(!savedOnly||saved.includes(p.id))&&(!fitOnly||(result&&fit(p,result,usage).pass))).sort((a,b)=>sort==='price-desc'?b.price-a.price:sort==='name'?a.name.localeCompare(b.name):a.price-b.price);
}
