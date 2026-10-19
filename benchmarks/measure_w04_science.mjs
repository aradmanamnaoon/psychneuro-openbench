/** Reproducible low-level presentation helper microbenchmark. Never an API E2E or clinical metric. */
import {performance} from 'node:perf_hooks';
import os from 'node:os';
import {compareAggregates} from '../apps/web/dist/science.js';
const data={run_id:'a'.repeat(64),split_sha256:'b'.repeat(64),provenance_root:'c'.repeat(64),
  outer_balanced_accuracy:0.5,dummy_outer_balanced_accuracy:0.5,test_balanced_accuracy:0.5,
  n_train_groups:21,n_test_groups:8};
const other={...data,run_id:'d'.repeat(64),outer_balanced_accuracy:0.55};
for(let i=0;i<1000;i++)compareAggregates(data,other);
const samples=[];
for(let i=0;i<10000;i++){
  const before=performance.now();
  compareAggregates(data,other);
  samples.push((performance.now()-before)*1000);
}
samples.sort((a,b)=>a-b);
const pick=q=>samples[Math.floor((samples.length-1)*q)].toFixed(3);
console.log('scope,cpu,node,n,warmup,concurrency,median_us,p95_us,rss_bytes');
console.log(`ts_presentation_only,"${os.cpus()[0]?.model||'unknown'}",${process.version},${samples.length},1000,1,${pick(.5)},${pick(.95)},${process.memoryUsage().rss}`);
