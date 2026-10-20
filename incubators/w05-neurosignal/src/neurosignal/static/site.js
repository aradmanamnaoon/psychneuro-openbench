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

let spectralResult=null;
const psdChannel=document.getElementById('psd-channel');
const psdCaption=document.getElementById('psd-caption');
function drawSpectrum(){
  if(!spectralResult)return;
  const idx=Number(psdChannel.value);
  const hz=spectralResult.frequencies_hz;
  const power=spectralResult.power_v2_per_hz[idx];
  if(!power || !power.length)return;
  // Display log power with a positive floor; numerical values remain available via the API.
  const logged=power.map(v=>Math.log10(Math.max(v,1e-30)));
  const min=Math.min(...logged),max=Math.max(...logged);
  const span=Math.max(max-min,1e-9);
  const points=logged.map((v,i)=>{
    const x=20+600*i/Math.max(1,logged.length-1);
    const y=235-210*(v-min)/span;
    return (i===0?'M':'L')+x.toFixed(2)+','+y.toFixed(2);
  }).join(' ');
  document.getElementById('psd-line').setAttribute('d',points);
  const peakIndex=1+power.slice(1).indexOf(Math.max(...power.slice(1)));
  const peak=hz[peakIndex];
  psdCaption.textContent='Synthetic channel '+spectralResult.channels[idx]+
    ', approximate peak '+peak.toFixed(1)+' Hz; '+spectralResult.segments+
    ' overlapping windows. Vertical axis: log10(V²/Hz).';
}
psdChannel.addEventListener('change',drawSpectrum);
document.getElementById('psd-run').addEventListener('click',async()=>{
  psdCaption.textContent='Calculating synthetic spectrum…';
  const token=document.getElementById('token').value;
  const tenant=document.getElementById('tenant').value;
  const seed=Number(document.getElementById('seed').value);
  const samples=Number(document.getElementById('samples').value);
  const chunk_size=Number(document.getElementById('chunk').value);
  try{
    const response=await fetch('/v1/spectral/synthetic',{
      method:'POST',cache:'no-store',headers:{'Content-Type':'application/json',
        'Authorization':`Bearer ${token}`,'X-Tenant':tenant},
      body:JSON.stringify({seed,samples,chunk_size,idempotency_key:'psd-synthetic-0001'})
    });
    const payload=await response.json();
    if(!response.ok)throw new Error('HTTP '+response.status+': '+JSON.stringify(payload));
    if(!payload.synthetic_only)throw new Error('Non-synthetic data rejected');
    spectralResult=payload;
    psdChannel.replaceChildren();
    payload.channels.forEach((channel,i)=>{
      const option=document.createElement('option');
      option.value=String(i);option.textContent=channel;
      psdChannel.appendChild(option);
    });
    drawSpectrum();
  }catch(error){psdCaption.textContent='PSD error: '+String(error);}
});
