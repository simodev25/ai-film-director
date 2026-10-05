// Optional real-browser smoke test. Uses an existing Chrome, not a downloaded browser.
// Start the dashboard, then: node tests/dashboard_browser.cjs http://127.0.0.1:8765
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const {spawn} = require('node:child_process');

async function main() {
  const binary = process.env.CHROME_BIN || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if(!fs.existsSync(binary)) throw new Error('Set CHROME_BIN to an existing Chrome executable.');
  const baseURL = process.argv[2] || 'http://127.0.0.1:8765';
  const base = new URL(baseURL);
  assert.ok(['127.0.0.1','localhost','[::1]'].includes(base.hostname),'Only test a local dashboard');
  const output = fs.mkdtempSync(path.join(process.env.TMPDIR || os.tmpdir(), 'atelier-browser-'));
  const chrome = spawn(binary, ['--headless=new','--disable-gpu','--no-first-run',
    '--no-default-browser-check','--disable-background-networking','--disable-extensions',
    '--remote-debugging-port=0',`--user-data-dir=${path.join(output,'profile')}`,'about:blank'], {stdio:['ignore','ignore','pipe']});
  let socket;
  try {
    const debugURL = await new Promise((resolve,reject)=>{
      let log='';const timer=setTimeout(()=>reject(new Error('Chrome startup timed out')),12000);
      chrome.on('error',reject);
      chrome.stderr.on('data',chunk=>{log+=chunk.toString();const m=log.match(/DevTools listening on (ws:\/\/\S+)/);if(m){clearTimeout(timer);resolve(m[1]);}});
    });
    socket = new WebSocket(debugURL);
    await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
    let serial=0;const pending=new Map();const errors=[];
    socket.addEventListener('message',event=>{
      const message=JSON.parse(event.data);
      if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.text+' '+(message.params.exceptionDetails.exception?.description||''));
      if(message.id && pending.has(message.id)){const p=pending.get(message.id);clearTimeout(p.timer);pending.delete(message.id);message.error?p.reject(new Error(message.error.message)):p.resolve(message.result);}
    });
    const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{
      const id=++serial;const timer=setTimeout(()=>{pending.delete(id);reject(new Error(`CDP timeout: ${method}`));},15000);
      pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params,...(sessionId?{sessionId}:{})}));
    });
    const target=await send('Target.createTarget',{url:'about:blank'});
    const {sessionId}=await send('Target.attachToTarget',{targetId:target.targetId,flatten:true});
    const call=(method,params)=>send(method,params,sessionId);
    const evaluate=async expression=>{
      const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
      if(r.exceptionDetails)throw new Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);
      return r.result.value;
    };
    const waitFor=selector=>evaluate(`new Promise((resolve,reject)=>{const end=Date.now()+10000;const tick=()=>{if(document.querySelector(${JSON.stringify(selector)}))resolve(true);else if(Date.now()>end)reject(Error('Missing selector'));else setTimeout(tick,50)};tick()})`);
    await call('Runtime.enable');await call('Page.enable');
    await call('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
    await call('Page.navigate',{url:base.href});await waitFor('.hero');
    assert.equal(await evaluate(`document.querySelectorAll('#project-select option').length>0`),true);
    const capture=async name=>{const r=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});const p=path.join(output,name);fs.writeFileSync(p,Buffer.from(r.data,'base64'));return p;};
    await evaluate(`Promise.all([...document.querySelectorAll('.hero img')].map(i=>i.complete?Promise.resolve():new Promise(r=>{i.addEventListener('load',r,{once:true});i.addEventListener('error',r,{once:true})})))`);
    console.log('Desktop screenshot:',await capture('atelier-desktop.png'));
    for(const view of ['scenes','media','relations','sources']){
      await evaluate(`document.querySelector('#navigation [data-view="${view}"]').click()`);
      assert.ok(await evaluate(`document.querySelector('#content').textContent.length>80`));
      console.log('View rendered:',view);
    }
    await evaluate(`document.querySelector('#navigation [data-view="relations"]').click()`);
    if(await evaluate(`!!document.querySelector('.connection-board')`)){
      assert.ok(await evaluate(`document.querySelectorAll('.connection-node').length>=1`));
      console.log('Relations screenshot:',await capture('atelier-relations.png'));
    }
    await evaluate(`document.querySelector('#navigation [data-view="media"]').click()`);
    const hasMedia=await evaluate(`!!document.querySelector('.media-card')`);
    if(hasMedia){
      await evaluate(`document.querySelector('.media-card').click()`);
      assert.equal(await evaluate(`document.querySelector('#inspector').open`),true);
      await evaluate(`document.querySelector('#inspector [data-action="close"]').click()`);
      assert.equal(await evaluate(`document.querySelector('#inspector').open`),false);
    }
    await evaluate(`document.querySelector('#navigation [data-view="scenes"]').click()`);
    if(await evaluate(`!!document.querySelector('.shot-card')`)){
      await evaluate(`document.querySelector('.shot-card').click()`);
      assert.equal(await evaluate(`document.querySelector('#inspector').open`),true);
      await evaluate(`document.querySelector('#inspector [data-action="relations"]').click()`);
      assert.equal(await evaluate(`document.querySelector('#inspector').open`),false);
      assert.ok(await evaluate(`!!document.querySelector('.connection-board')`));
    }
    await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
    await evaluate(`document.querySelector('#navigation [data-view="overview"]').click()`);
    assert.ok(await evaluate(`document.documentElement.scrollWidth<=window.innerWidth+1`),'Mobile page should not overflow');
    console.log('Mobile screenshot:',await capture('atelier-mobile.png'));
    assert.deepEqual(errors,[],'No browser runtime exceptions');
    console.log('Real browser checks passed. No project files were modified.');
    await send('Browser.close');
  } finally {
    if(socket)socket.close();
    chrome.kill('SIGTERM');
  }
}
main().catch(error=>{console.error(error);process.exitCode=1;});
