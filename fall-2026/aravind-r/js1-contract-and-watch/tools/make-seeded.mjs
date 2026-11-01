#!/usr/bin/env node
// Builds a SEEDED / CONSTRUCTED "earlier" response from a real saved response by
// removing postings, so a second run against the real response has a known change.
// Removed: the ids given with --fixed, plus --pm PM-family rule-not-relevant ids and
// --nonpm non-PM ids, each drawn with --seed. No network.
//
// --exclude labels/draw.json keeps the 20 hand-labeling postings out of the draws.
// node tools/make-seeded.mjs --raw runs/<live-baseline>/raw-response.json --seed 20261031
//   --fixed 8195440,8165137,8223723 --pm 3 --nonpm 2 --runs runs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
import { judgePosting } from '../src/rule.mjs';
import { mulberry32 } from './rand.mjs';

const { values: a } = parseArgs({ options: {
  raw: { type: 'string' }, seed: { type: 'string' }, fixed: { type: 'string', default: '' },
  pm: { type: 'string', default: '0' }, nonpm: { type: 'string', default: '0' }, runs: { type: 'string', default: 'runs' },
  prefs: { type: 'string', default: 'persona/persona-prefs.json' },
  exclude: { type: 'string' }, // a labels/draw.json: its ids are never drawn
  name: { type: 'string', default: 'seeded-earlier' },
} });
const seed = Number(a.seed);
if (!a.raw || !Number.isInteger(seed)) { console.error('--raw and an integer --seed are required'); process.exit(2); }

const text = readFileSync(a.raw, 'utf8');
const doc = JSON.parse(text);
const prefs = JSON.parse(readFileSync(a.prefs, 'utf8'));
const isPm = j => /product manag|program manag/i.test(j.title);
const excluded = a.exclude ? JSON.parse(readFileSync(a.exclude, 'utf8')).rows.map(r => r.id) : [];
const fixed = a.fixed ? a.fixed.split(',').map(Number) : [];
for (const id of fixed) if (!doc.jobs.some(j => j.id === id)) { console.error(`fixed id ${id} is not in the response`); process.exit(2); }

const rand = mulberry32(seed);
function draw(pool, n) {
  const ids = pool.map(j => j.id).sort((x, y) => x - y);
  for (let i = ids.length - 1; i > 0; i--) { const k = Math.floor(rand() * (i + 1)); [ids[i], ids[k]] = [ids[k], ids[i]]; }
  return ids.slice(0, n);
}
const pmNotRelevant = doc.jobs.filter(j => isPm(j) && !fixed.includes(j.id) && !excluded.includes(j.id) && judgePosting(j, prefs).rule_verdict === 'not_relevant');
const pmIds = draw(pmNotRelevant, Number(a.pm));
const nonPmIds = draw(doc.jobs.filter(j => !isPm(j) && !fixed.includes(j.id) && !excluded.includes(j.id)), Number(a.nonpm));
const removed = [...fixed, ...pmIds, ...nonPmIds];

const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
const dir = join(a.runs, `${stamp}-${a.name}`);
mkdirSync(dir, { recursive: true });
writeFileSync(join(dir, 'raw-response.json'), JSON.stringify({ ...doc, jobs: doc.jobs.filter(j => !removed.includes(j.id)) }));
const meta = {
  label: 'SEEDED / CONSTRUCTED: not a response any server sent. It is the real saved response below with postings removed, so that a second run against the real response has a known change.',
  built_at: new Date().toISOString(), from_raw: a.raw, seed, excluded_from_draws: a.exclude ? `${excluded.length} labeling ids from ${a.exclude}` : 'none',
  removed: { fixed_rule_relevant: fixed, pm_family_rule_not_relevant: pmIds, non_pm: nonPmIds },
  expected_new_ids: [...removed].sort((x, y) => x - y),
  removed_titles: Object.fromEntries(removed.map(id => [id, doc.jobs.find(j => j.id === id).title])),
  jobs_in_real_response: doc.jobs.length, jobs_in_constructed_response: doc.jobs.length - removed.length,
};
writeFileSync(join(dir, 'seeded-meta.json'), JSON.stringify(meta, null, 2) + '\n');
console.log(dir);
