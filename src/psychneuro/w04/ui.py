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
#alert{white-space:pre-wrap;font-weight:600;color:#8a1b05}li{margin:.5rem 0}
</style></head><body><main><h1>PsychNeuro W04 — private explorer</h1>
<p>Original synthetic aggregates only. Hashes detect changes; they do not establish who created an artifact. No clinical inference.</p>
<section><h2>Internal access</h2><label for="token">Internal access token (not saved)</label>
<input id="token" type="password" autocomplete="off" size="48">
<label for="run1">First run ID</label><input id="run1" pattern="[a-f0-9]{64}" size="64">
<label for="run2">Comparison run ID (optional)</label><input id="run2" pattern="[a-f0-9]{64}" size="64">
<button id="load">Load run(s) and provenance</button><button id="clear">Clear screen</button>
<p id="alert" role="status" aria-live="polite"></p></section>
<section aria-labelledby="scores-title"><h2 id="scores-title">Aggregate comparison</h2><div id="scores"><p>No reports loaded.</p></div></section>
<section aria-labelledby="graph-title"><h2 id="graph-title">Source → split → model → benchmark</h2><ol id="graph"><li>No graph loaded.</li></ol>
<p>For details and split counts, review each exported node. No participant-level rows are exposed.</p></section>
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
    const records=await Promise.all(ids.map(id=>readJson('/w04/v1/benchmarks/'+id,token)));
    const table=document.createElement('table');const caption=add(table,'caption','Prespecified balanced accuracy; not human-data evidence');const head=add(table,'thead','');const hr=add(head,'tr','');
    ['Run','Outer BA','Dummy outer BA','Sealed test BA','Train groups','Test groups'].forEach(x=>add(hr,'th',x));
    const body=add(table,'tbody','');records.forEach(r=>{const tr=add(body,'tr','');[r.run_id.slice(0,12),r.outer_balanced_accuracy,r.dummy_outer_balanced_accuracy,r.test_balanced_accuracy,r.n_train_groups,r.n_test_groups].forEach(x=>add(tr,'td',x));});
    $('scores').appendChild(table);
    const graph=await readJson('/w04/v1/provenance/'+ids[0],token);
    if(!Array.isArray(graph.nodes)||graph.nodes.length!==4)throw new Error('Unexpected provenance graph shape');
    graph.nodes.forEach(n=>{const li=add($('graph'),'li',n.kind+' — '+n.sha256);add(li,'p','Parents: '+(n.parents.join(', ')||'none'));if(n.kind==='split')add(li,'p','Train groups: '+n.metadata.train_groups+'; test groups: '+n.metadata.test_groups);});
    $('alert').textContent='Loaded '+records.length+' aggregate run(s); provenance root '+graph.root;
  }catch(e){$('scores').replaceChildren();$('graph').replaceChildren();$('alert').textContent=e.message||'Request failed';}
});
</script></body></html>'''
