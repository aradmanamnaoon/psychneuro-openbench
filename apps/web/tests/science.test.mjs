import test from 'node:test';
import assert from 'node:assert/strict';
import {compareAggregates, graphText, validateAggregate} from '../dist/science.js';
const hex = letter => letter.repeat(64);
const r = {run_id:hex('a'), split_sha256:hex('b'), provenance_root:hex('c'),
  outer_balanced_accuracy:0.5, dummy_outer_balanced_accuracy:0.5,
  test_balanced_accuracy:0.5, n_train_groups:21, n_test_groups:8};
test('realistic synthetic summary discloses uncertainty',()=>{
  const summary=compareAggregates(r,{...r,run_id:hex('d'),outer_balanced_accuracy:0.6});
  assert.equal(summary.rows.length,5);
  assert.match(summary.caveat,/fictional-participant/);
  assert.ok(Math.abs(summary.difference+0.1)<1e-12);
  assert.equal(summary.rows.at(-1).value,'-0.100');
});
test('self-comparison is clearly distinguished',()=>{
  assert.match(compareAggregates(r,r).caveat,/self-comparison/);
  assert.throws(()=>compareAggregates(r,{...r,test_balanced_accuracy:0.9}),/Conflicting/);
});
test('corrupt IDs, non-finite metrics and impossible groups rejected',()=>{
  for(const change of [{run_id:'spoof'},{outer_balanced_accuracy:NaN},
    {test_balanced_accuracy:1.2},{n_train_groups:-1}]){
    assert.throws(()=>validateAggregate({...r,...change}));
  }
});
test('ordered DAG has accessible text alternative',()=>{
  const nodes=['source','split','model','benchmark'].map((kind,i)=>({
    kind,sha256:hex('abcd'[i]),parents:i?[hex('abcd'[i-1])]:[]
  }));
  assert.equal(graphText(nodes).length,4);
  assert.throws(()=>graphText([...nodes].reverse()));
  assert.throws(()=>graphText(nodes.map((n,i)=>i===2?{...n,parents:[hex('f')]}:n)));
  assert.throws(()=>graphText(nodes.map((n,i)=>i===1?{...n,parents:[]}:n)),/chain edge/);
  assert.throws(()=>graphText(nodes.map((n,i)=>i===1?{...n,parents:[hex('a'),hex('a')]}:n)),/chain edge/);
  assert.throws(()=>graphText(nodes.map((n,i)=>i===2?{...n,sha256:hex('b')}:n)),/duplicate/);
  assert.throws(()=>graphText(nodes.map((n,i)=>i===0?{...n,parents:[hex('d')]}:n)),/chain edge/);
});
