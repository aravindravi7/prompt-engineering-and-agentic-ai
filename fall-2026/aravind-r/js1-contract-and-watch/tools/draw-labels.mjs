#!/usr/bin/env node
// Draws the 20 postings for hand labeling from a saved raw response (no network).
// PM-family = title matches /product manag|program manag/i. Dedupe by title + team
// (Stripe repeats one role across locations; the lowest id is kept). Then a seeded
// shuffle picks 20, and the same order splits them 10 development / 10 held-out.
//
// node tools/draw-labels.mjs --raw runs/<baseline>/raw-response.json --seed 20261031 --out labels
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
import { plainText } from '../src/text.mjs';

const { values: a } = parseArgs({ options: { raw: { type: 'string' }, seed: { type: 'string' }, out: { type: 'string', default: 'labels' } } });
const seed = Number(a.seed);
if (!a.raw || !Number.isInteger(seed)) { console.error('--raw and an integer --seed are required'); process.exit(2); }

export function mulberry32(s) {
  return () => { s |= 0; s = s + 0x6D2B79F5 | 0; let t = Math.imul(s ^ s >>> 15, 1 | s); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}

const jobs = JSON.parse(readFileSync(a.raw, 'utf8')).jobs;
const team = j => (j.departments ?? []).map(d => d.name).join(' / ') || '(none)';
const pm = jobs.filter(j => /product manag|program manag/i.test(j.title)).sort((x, y) => x.id - y.id);
const byKey = new Map();
for (const j of pm) { const k = `${j.title}|${team(j)}`; if (!byKey.has(k)) byKey.set(k, j); }
const pool = [...byKey.values()];

const rand = mulberry32(seed);
const order = pool.map(j => j.id);
for (let i = order.length - 1; i > 0; i--) { const k = Math.floor(rand() * (i + 1)); [order[i], order[k]] = [order[k], order[i]]; }
const picked = order.slice(0, 20).map(id => pool.find(j => j.id === id));

mkdirSync(join(a.out, 'postings'), { recursive: true });
const rows = picked.map((j, i) => ({ set: i < 10 ? 'dev' : 'heldout', n: i < 10 ? i + 1 : i - 9, id: j.id, title: j.title, team: team(j), location: j.location?.name ?? '' }));
writeFileSync(join(a.out, 'draw.json'), JSON.stringify({
  drawn_at: new Date().toISOString(), raw: a.raw, seed, pm_family_filter: '/product manag|program manag/i on title',
  pm_family_postings: pm.length, after_dedupe_title_team: pool.length, rows,
}, null, 2) + '\n');
for (const [i, j] of picked.entries()) {
  const r = rows[i];
  writeFileSync(join(a.out, 'postings', `${r.set}-${String(r.n).padStart(2, '0')}-${j.id}.md`),
    `# ${r.set} ${r.n}: ${j.title}\n\n- id: ${j.id}\n- team: ${r.team}\n- location: ${r.location}\n- url: ${j.absolute_url}\n\n## Description (HTML decoded, tags stripped)\n\n${plainText(j.content).replace(/\n/g, '\n\n')}\n`);
}
console.log(`PM-family ${pm.length} → ${pool.length} after title+team dedupe → 20 drawn (seed ${seed}): 10 dev, 10 held-out`);
