"""Accessible private static explorer; no third-party code or stored tokens."""
PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>W04 private scientific explorer</title>
<style>
body{font:1rem/1.5 system-ui,sans-serif;margin:auto;max-width:66rem;padding:1.5rem;background:#fafafa;color:#192334}
input,button{font:inherit;padding:.45rem;margin:.3rem}input{max-width:100%;}button{cursor:pointer}
button:focus-visible,input:focus-visible{outline:3px solid #174ea6;outline-offset:3px}
section{background:white;padding:1rem;margin:1rem 0;border:1px solid #aaa;border-radius:.5rem}
code{word-break:break-all}table{border-collapse:collapse;width:100%}th,td{padding:.5rem;border:1px solid #aaa;text-align:left}
#alert{white-space:pre-wrap;font-weight:600;color:#8a1b05}li{margin:.5rem 0} @media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* Mobile and keyboard-safe layout: long SHA digests must never widen the page. */
#graph pre{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;max-width:100%}
*,*::before,*::after{box-sizing:border-box}
html,body,main,section{max-width:100%;min-width:0}
li,p,td,th,#alert,#graph{overflow-wrap:anywhere}
#scores{overflow-x:auto;max-width:100%}
input{max-width:calc(100% - .6rem)}
@media(max-width:640px){
  body{padding:.65rem}
  section{padding:.75rem}
  input,button{display:block;width:100%;max-width:100%;margin:.35rem 0}
  #scores table{min-width:33rem}
  #scores{overflow-x:auto}
}
</style></head><body><main><h1>PsychNeuro W04 — private explorer</h1>
<p>Original synthetic aggregates only. Hashes detect changes; they do not establish who created an artifact. No clinical inference.</p>
<section><h2>Internal access</h2><label for="token">Internal access token (not saved)</label>
<input id="token" type="password" autocomplete="off" size="48">
<label for="run1">First run ID</label><input id="run1" pattern="[a-f0-9]{64}" size="64">
<label for="run2">Comparison run ID (optional)</label><input id="run2" pattern="[a-f0-9]{64}" size="64">
<button id="load">Load run(s) and provenance</button><button id="clear">Clear screen</button>
<p id="alert" role="status" aria-live="polite"></p></section>
<section aria-labelledby="create-title"><h2 id="create-title">Original synthetic benchmark</h2>
<p>No human or third-party datasets. A run is synchronous; metadata jobs below cannot stop fitting.</p>
<form id="create-form"><label for="dataset">Authorized dataset</label><select id="dataset" required><option value="">Load private catalog first</option></select>
<button id="catalog" type="button">Load authorized dataset catalog</button>
<label for="generator-seed">Generator seed</label><input id="generator-seed" type="number" min="0" max="4294967295" value="73" required>
<label for="split-seed">Participant split seed</label><input id="split-seed" type="number" min="0" max="4294967295" value="42" required>
<label for="participants">Fictional participants (24–80)</label><input id="participants" type="number" min="24" max="80" value="36" required>
<label for="trials">Trials per participant (8–40)</label><input id="trials" type="number" min="8" max="40" value="12" required>
<button type="submit">Execute W03 grouped benchmark</button></form>
<button id="rights">Preview dataset/run rights</button><p id="rights-display" role="status" aria-live="polite"></p></section>
<section aria-labelledby="scores-title"><h2 id="scores-title">Aggregate comparison</h2><div id="scores"><p>No reports loaded.</p></div></section>
<section aria-labelledby="graph-title"><h2 id="graph-title">Source → split → model → benchmark</h2><ol id="graph"><li>No graph loaded.</li></ol>
<p>For details and split counts, review each exported node. No participant-level rows are exposed.</p>
<button id="download">Download A integrity-only JSON artifact</button><label for="receipt">Private JSON receipt to verify</label><input id="receipt" type="file" accept=".json,application/json"><button id="verify">Verify receipt</button>
<p>Hashes detect changes but do not authenticate a signer or source.</p></section>
<section aria-labelledby="jobs-title"><h2 id="jobs-title">Durable synthetic computation queue</h2>
<p>The separate PRIVATE operator worker executes queued jobs. Browser requests cannot start a privileged worker.
Cancelling an active fit invalidates its fenced result publication but cannot interrupt an in-flight scikit-learn CPU call;
resuming a cancelled job requires a fresh P25 grant and restarts fitting from the synthetic source.</p>
<label for="job-key">Idempotency key (reuse for exact retry)</label><input id="job-key" size="48" value="fictional-demo-job-1" maxlength="80">
<label for="job-id">Durable job ID (64-character lowercase hex)</label><input id="job-id" size="64" pattern="[a-f0-9]{64}">
<button id="job-create">Queue synthetic experiment</button><button id="job-status">Get durable status</button>
<button id="job-cancel">Cancel queued/running job</button><button id="job-resume">Resume cancelled job</button>
<p id="job-display" role="status" aria-live="polite"></p></section>
</main><script>
'use strict';
const $=id=>document.getElementById(id);
const valid=id=>/^[a-f0-9]{64}$/.test(id);
const add=(node,tag,value)=>{const child=document.createElement(tag);child.textContent=String(value);node.appendChild(child);return child;};
async function readJson(path,token){const r=await fetch(path,{headers:{'X-Internal-Token':token},cache:'no-store'});if(!r.ok)throw new Error('Request rejected ('+r.status+'). Check rights, token, or run ID.');return r.json();}
$('clear').addEventListener('click',()=>{$('token').value='';$('run1').value='';$('run2').value='';$('scores').replaceChildren();$('graph').replaceChildren();$('alert').textContent='Cleared.';});
$('load').addEventListener('click',async()=>{
  const token=$('token').value;const ids=[$('run1').value.trim(),$('run2').value.trim()].filter(Boolean);
  $('alert').textContent='';$('scores').replaceChildren();$('graph').replaceChildren();
  if(!token||!ids.length||ids.some(id=>!valid(id))){$('alert').textContent='Enter a token and one or two 64-character hexadecimal run IDs.';return;}
  try{
    const records=await Promise.all(ids.map(id=>readJson('/w04/v2/runs/'+id,token)));
    const table=document.createElement('table');const caption=add(table,'caption','Prespecified balanced accuracy; not human-data evidence');const head=add(table,'thead','');const hr=add(head,'tr','');
    ['Run','Outer BA','Dummy outer BA','Sealed test BA','Train groups','Test groups'].forEach(x=>add(hr,'th',x));
    const body=add(table,'tbody','');records.forEach(r=>{const tr=add(body,'tr','');[r.run_id.slice(0,12),r.outer_balanced_accuracy,r.dummy_outer_balanced_accuracy,r.test_balanced_accuracy,r.n_train_groups,r.n_test_groups].forEach(x=>add(tr,'td',x));});
    $('scores').appendChild(table);
    const graph=await readJson('/w04/v2/runs/'+ids[0]+'/graph',token);
    if(!Array.isArray(graph.nodes)||graph.nodes.length!==4)throw new Error('Unexpected provenance graph shape');
    graph.nodes.forEach(n=>{const li=add($('graph'),'li',n.kind+' — '+n.sha256);add(li,'p','Parents: '+(n.parents.join(', ')||'none'));if(n.kind==='split')add(li,'p','Train groups: '+n.metadata.train_groups+'; test groups: '+n.metadata.test_groups);
     add(li,'pre',JSON.stringify(n.metadata,null,2));});
    $('alert').textContent='Loaded '+records.length+' aggregate run(s); provenance root '+graph.root;
  }catch(e){$('scores').replaceChildren();$('graph').replaceChildren();$('alert').textContent=e.message||'Request failed';}
});

async function postJson(path,token,data){const r=await fetch(path,{method:'POST',headers:{'X-Internal-Token':token,'Content-Type':'application/json'},body:JSON.stringify(data),cache:'no-store',credentials:'omit'});if(!r.ok)throw new Error('Request rejected ('+r.status+').');return r.json();}
const notifyError=e=>{$('alert').textContent=e instanceof Error?e.message:'Request failed';};
async function loadCatalog(){const cat=await readJson('/w04/v2/catalog',$('token').value);$('dataset').replaceChildren();for(const item of cat.datasets){const option=document.createElement('option');option.value=String(item.id);option.textContent=String(item.id)+' — '+String(item.scope);$('dataset').appendChild(option);}if(!cat.datasets.length)throw new Error('No authorized datasets');return cat;}
$('catalog').addEventListener('click',async()=>{try{const cat=await loadCatalog();$('rights-display').textContent='Loaded '+cat.datasets.length+' rights-scoped synthetic source(s).';}catch(e){notifyError(e);}});
$('rights').addEventListener('click',async()=>{try{const token=$('token').value;const run=await readJson('/w04/v2/rights/preview',token);const cat=await loadCatalog();$('rights-display').textContent='Dataset '+cat.datasets[0].id+'; run '+(run.allowed?'ALLOWED':'DENIED')+' ('+run.reason+'); original fictional aggregates only.';}catch(e){notifyError(e);}});
$('create-form').addEventListener('submit',async e=>{e.preventDefault();try{const token=$('token').value;const cat=await loadCatalog();if(!cat.datasets.some(x=>x.id===$('dataset').value))throw new Error('Select an authorized dataset');const asInt=(id,min,max)=>{const n=Number($(id).value);if(!Number.isSafeInteger(n)||n<min||n>max)throw new Error('Invalid '+id);return n;};$('alert').textContent='Running CPU benchmark (synchronously)';const run=await postJson('/w04/v2/runs',token,{generator_seed:asInt('generator-seed',0,4294967295),split_seed:asInt('split-seed',0,4294967295),n_participants:asInt('participants',24,80),trials_per_participant:asInt('trials',8,40)});$('run1').value=run.run_id;$('load').click();}catch(e){notifyError(e);}});
$('download').addEventListener('click',async()=>{try{const id=$('run1').value.trim();if(!valid(id))throw new Error('Invalid run A ID');const data=await readJson('/w04/v2/runs/'+id+'/artifact',$('token').value);const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='w04-'+id+'.json';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);$('alert').textContent='Integrity-only artifact exported.';}catch(e){notifyError(e);}});
$('verify').addEventListener('click',async()=>{try{const file=$('receipt').files[0];if(!file||file.size>250000)throw new Error('Choose JSON receipt under 250KB');const data=JSON.parse(await file.text());const verified=await postJson('/w04/v2/artifacts/verify',$('token').value,data);$('alert').textContent='Receipt hash verification OK (not independently signed): '+verified.provenance_root;}catch(e){notifyError(e);}});
function experimentSettings(){
 const asInt=(id,min,max)=>{const n=Number($(id).value);if(!Number.isSafeInteger(n)||n<min||n>max)throw new Error('Invalid '+id);return n;};
 return {generator_seed:asInt('generator-seed',0,4294967295),split_seed:asInt('split-seed',0,4294967295),
 n_participants:asInt('participants',24,80),trials_per_participant:asInt('trials',8,40)};
}
async function jobStatus(){
 const id=$('job-id').value.trim();if(!valid(id))throw new Error('Invalid durable job ID');
 const job=await readJson('/w04/v3/jobs/'+id,$('token').value);
 $('job-display').textContent='State: '+job.state+'; revision: '+job.revision+'; attempts: '+job.attempts+
 '; checkpoint: '+(job.checkpoint_stage||'none')+
 '. Queued jobs require the separately authorized private worker.';
 return job;
}
$('job-create').addEventListener('click',async()=>{
 try{
 const key=$('job-key').value.trim();
 if(!/^[A-Za-z0-9_.-]{1,80}$/.test(key))throw new Error('Invalid idempotency key');
 const result=await postJson('/w04/v3/jobs',$('token').value,
  {schema_version:'w04-job-submit-5',idempotency_key:key,experiment:experimentSettings()});
 $('job-id').value=result.id;await jobStatus();
 }catch(e){notifyError(e);}
});
$('job-status').addEventListener('click',async()=>{try{await jobStatus();}catch(e){notifyError(e);}});
$('job-cancel').addEventListener('click',async()=>{
 try{const job=await jobStatus();await postJson('/w04/v3/jobs/'+job.id+'/cancel',$('token').value,{});await jobStatus();}
 catch(e){notifyError(e);}
});
$('job-resume').addEventListener('click',async()=>{
 try{const job=await jobStatus();await postJson('/w04/v3/jobs/'+job.id+'/resume',$('token').value,{});await jobStatus();}
 catch(e){notifyError(e);}
});
</script></body></html>'''
