#!/usr/bin/env node
// Scores Claude judge runs against the hand labels (labels/hand-labels.json).
// A pass = Claude's verdict equals my hand label. Invalid replies count as fails.
// Also prints the sampling spread (verdicts per posting across repeats).
//
// node tools/score.mjs experiment/v1-dev.jsonl experiment/v2-dev.jsonl ...
// node tools/score.mjs --sampling sampling/v1-dev1-5-x4.jsonl
// node tools/score.mjs --rule   (rule verdict, recomputed now, vs hand labels on all 20)
import { readFileSync } from 'node:fs';
import { judgePosting } from '../src/rule.mjs';

const labels = JSON.parse(readFileSync('labels/hand-labels.json', 'utf8'));
const hand = new Map(labels.rows.map(r => [r.id, r]));
if (labels.rows.some(r => !r.label)) { console.error('hand labels incomplete: label every row before scoring'); process.exit(2); }
const read = f => readFileSync(f, 'utf8').trim().split('\n').map(l => JSON.parse(l));

const args = process.argv.slice(2);
if (args[0] === '--rule') {
  const jobs = new Map(JSON.parse(readFileSync('runs/20261101T015849Z-live-baseline/raw-response.json', 'utf8')).jobs.map(j => [j.id, j]));
  const prefs = JSON.parse(readFileSync('persona/persona-prefs.json', 'utf8'));
  let agree = 0; const diff = [];
  for (const h of labels.rows) {
    const r = judgePosting(jobs.get(h.id), prefs);
    const ff = r.rule_justification.first_failed;
    if (r.rule_verdict === h.label) agree++;
    else diff.push(`- ${h.set} ${h.n} (${h.id}) ${h.title}: rule ${r.rule_verdict}${ff ? ` (first failed gate ${ff})` : ''}, hand ${h.label}${h.first_failed_gate ? ` (gate ${h.first_failed_gate})` : ''}`);
    if (r.rule_verdict === h.label && (ff ?? null) !== (h.first_failed_gate ?? null)) diff.push(`- ${h.set} ${h.n} (${h.id}): verdicts agree, first failed gate differs (rule ${ff}, hand ${h.first_failed_gate})`);
  }
  console.log(`Rule (RECORD) vs hand labels: ${agree}/${labels.rows.length} verdicts agree.`);
  console.log(diff.length ? diff.join('\n') : 'No disagreements.');
} else if (args[0] === '--sampling') {
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
