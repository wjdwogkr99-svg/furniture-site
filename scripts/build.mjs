import {cp,rm,mkdir} from 'node:fs/promises';
const dist=new URL('../dist/',import.meta.url);
await rm(dist,{recursive:true,force:true});await mkdir(dist,{recursive:true});await cp(new URL('../public/',import.meta.url),dist,{recursive:true});console.log('Build ready: dist/ (static files, no automatic deployment)');
