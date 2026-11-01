#!/usr/bin/env node
// Scores Claude judge runs against the hand labels (labels/hand-labels.json).
// A pass = Claude's verdict equals my hand label. Invalid replies count as fails.
// Also prints the sampling spread (verdicts per posting across repeats).
//
// node tools/score.mjs experiment/v1-dev.jsonl experiment/v2-dev.jsonl ...
// node tools/score.mjs --sampling sampling/v1-dev1-5-x4.jsonl
import { readFileSync } from 'node:fs';

const labels = JSON.parse(readFileSync('labels/hand-labels.json', 'utf8'));
const hand = new Map(labels.rows.map(r => [r.id, r]));
if (labels.rows.some(r => !r.label)) { console.error('hand labels incomplete: label every row before scoring'); process.exit(2); }
const read = f => readFileSync(f, 'utf8').trim().split('\n').map(l => JSON.parse(l));

const args = process.argv.slice(2);
if (args[0] === '--sampling') {
  const rows = read(args[1]);
  const by = new Map();
  for (const r of rows) { if (!by.has(r.id)) by.set(r.id, []); by.get(r.id).push(r); }
  console.log('| n | id | title | hand label | verdicts (in call order) | agree with each other | agree with hand label |');
  console.log('|---|---|---|---|---|---|---|');
  for (const [id, rs] of by) {
    rs.sort((x, y) => x.repeat - y.repeat);
    const v = rs.map(r => r.verdict), h = hand.get(id);
    console.log(`| dev ${h.n} | ${id} | ${h.title} | ${h.label} | ${v.join(', ')} | ${new Set(v).size === 1 ? 'yes' : 'no'} | ${v.filter(x => x === h.label).length}/${v.length} |`);
  }
} else {
  console.log('| run | set | n | passes (verdict = hand label) | invalid | quote fidelity ok |');
  console.log('|---|---|---|---|---|---|');
  for (const f of args) {
    const rows = read(f);
    const pass = rows.filter(r => r.verdict === hand.get(r.id)?.label).length;
    const qf = rows.filter(r => r.quote_fidelity).length;
    console.log(`| ${f} | ${rows[0].set} | ${rows.length} | ${pass}/${rows.length} | ${rows.filter(r => r.verdict === 'invalid').length} | ${qf ? `${rows.filter(r => r.quote_fidelity?.ok).length}/${qf}` : 'n/a'} |`);
  }
  console.log('\nPer posting:');
  for (const f of args) for (const r of read(f)) {
    const h = hand.get(r.id);
    if (r.verdict !== h.label) console.log(`- ${f}: ${r.set} ${r.n} (${r.id}) Claude ${r.verdict}, hand ${h.label}`);
  }
}
