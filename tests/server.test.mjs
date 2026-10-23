import test from 'node:test';
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {once} from 'node:events';

test('개발 서버가 HTML·모듈·이미지를 제공하고 외부 경로를 차단한다',async(t)=>{
  const child=spawn(process.execPath,['scripts/serve.mjs'],{
    cwd:new URL('../',import.meta.url),env:{...process.env,PORT:'0'},stdio:['ignore','pipe','pipe']
  });
  t.after(async()=>{const exited=once(child,'exit');child.kill();await exited});
  const base=await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Server startup timed out')),5000);
    let output='';
    child.stdout.on('data',chunk=>{output+=chunk;const match=output.match(/http:\/\/localhost:(\d+)/);if(match){clearTimeout(timer);resolve(`http://127.0.0.1:${match[1]}`)}});
    child.once('error',error=>{clearTimeout(timer);reject(error)});
    child.once('exit',code=>{clearTimeout(timer);reject(new Error(`Server exited: ${code}`))});
  });
  for(const [file,mime] of [['/','text/html'],['/index.html','text/html'],['/model.mjs','text/javascript'],['/style.css','text/css'],['/assets/hero.jpg','image/jpeg']]){
    const response=await fetch(base+file);
    assert.equal(response.status,200,file);
    assert.ok(response.headers.get('content-type').startsWith(mime),file);
    assert.ok((await response.arrayBuffer()).byteLength>0,file);
  }
  assert.equal((await fetch(base+'/missing-file')).status,404);
  assert.equal((await fetch(base+'/%2e%2e%2fpackage.json')).status,403);
});
