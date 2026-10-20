'use strict';
const form=document.getElementById('experiment');
const status=document.getElementById('status');
const output=document.getElementById('result');
form.addEventListener('submit',async(event)=>{
  event.preventDefault();
  status.textContent='Running local synthetic computation…'; output.textContent='';
  const token=document.getElementById('token').value;
  const tenant=document.getElementById('tenant').value;
  const seed=Number(document.getElementById('seed').value);
  const samples=Number(document.getElementById('samples').value);
  const chunk_size=Number(document.getElementById('chunk').value);
  try{
    const response=await fetch('/v1/demo',{
      method:'POST',cache:'no-store',headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`,'X-Tenant':tenant},
      body:JSON.stringify({seed,samples,chunk_size,idempotency_key:'demo-only-0001'})
    });
    const data=await response.json();
    if(!response.ok)throw new Error(`HTTP ${response.status}: ${JSON.stringify(data)}`);
    status.textContent='Synthetic demonstration finished. No human signal processed.';
    output.textContent=JSON.stringify(data,null,2);
  }catch(err){status.textContent='Run failed: '+String(err);}
});
