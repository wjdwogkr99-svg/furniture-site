import http from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../public/',import.meta.url));
const port=Number(process.env.PORT||5173);
const mime={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'};
http.createServer(async(req,res)=>{try{const requested=decodeURIComponent(new URL(req.url,'http://localhost').pathname);const target=path.resolve(root,'.'+requested);if(target!==root&&!target.startsWith(root+path.sep)){res.writeHead(403).end();return}const meta=await stat(target);const file=meta.isDirectory()?path.join(target,'index.html'):target;const data=await readFile(file);res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-store'}).end(data)}catch{res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'}).end('파일을 찾을 수 없습니다.')}}).listen(port,'127.0.0.1',()=>console.log(`FITFORM: http://localhost:${port}`));
