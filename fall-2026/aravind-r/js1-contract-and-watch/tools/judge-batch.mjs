#!/usr/bin/env node
// Runs the Claude judge on hand-labeling postings for the sampling report and the
// prompt experiment. Every call is a fresh `claude -p` session (no tools, empty
// directory). Replies are validated and saved as JSONL; nothing is repaired or retried.
// It prints only counts, never verdicts, so hand labels can be made blind.
// The held-out set is refused unless --allow-heldout is passed.
//
// node tools/judge-batch.mjs --set dev --n 1-10 --repeats 1 --prompt prompts/judge.v1.md
//   --out experiment/v1-dev.jsonl [--schema v1|v2] [--model claude-sonnet-5-5] [--concurrency 4]
import { readFileSync, appendFileSync, mkdirSync, mkdtempSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { parseArgs } from 'node:util';
import { buildPrompt, ruleSection, personaView, postingView, validateClaudeOutput, quoteFidelity } from '../src/claude-judge.mjs';

const { values: a } = parseArgs({ options: {
  set: { type: 'string' }, n: { type: 'string', default: '1-10' }, repeats: { type: 'string', default: '1' },
  prompt: { type: 'string' }, out: { type: 'string' }, model: { type: 'string', default: 'claude-sonnet-5-5' },
  concurrency: { type: 'string', default: '4' }, 'allow-heldout': { type: 'boolean', default: false },
  schema: { type: 'string', default: 'v1' },
  raw: { type: 'string', default: 'runs/20261101T015849Z-live-baseline/raw-response.json' },
} });
if (!['dev', 'heldout'].includes(a.set) || !a.prompt || !a.out) { console.error('--set dev|heldout, --prompt and --out are required'); process.exit(2); }
if (a.set === 'heldout' && !a['allow-heldout']) { console.error('REFUSED: held-out set is locked until the final run (--allow-heldout)'); process.exit(2); }

const [lo, hi] = a.n.split('-').map(Number);
const draw = JSON.parse(readFileSync('labels/draw.json', 'utf8'));
const rows = draw.rows.filter(r => r.set === a.set && r.n >= lo && r.n <= (hi ?? lo));
const jobs = new Map(JSON.parse(readFileSync(a.raw, 'utf8')).jobs.map(j => [j.id, j]));
const resume = JSON.parse(readFileSync('persona/maya-sehgal.resume.json', 'utf8'));
const prefs = JSON.parse(readFileSync('persona/persona-prefs.json', 'utf8'));
const template = readFileSync(a.prompt, 'utf8');
const rule = ruleSection('CONTRACT.md');
const persona = personaView(resume, prefs);

const tasks = [];
for (const r of rows) for (let k = 1; k <= Number(a.repeats); k++) tasks.push({ ...r, repeat: k });

function call(prompt) {
  return new Promise(resolve => {
    const cwd = mkdtempSync(join(tmpdir(), 'js1-batch-'));
    const p = spawn('claude', ['-p', prompt, '--tools', '', '--no-session-persistence', '--output-format', 'json', '--model', a.model], { cwd });
    let out = '', err = '';
    p.stdout.on('data', d => out += d); p.stderr.on('data', d => err += d);
    p.on('close', code => resolve({ code, out, err }));
  });
}

mkdirSync(dirname(a.out), { recursive: true });
let done = 0, invalid = 0;
async function worker() {
  while (tasks.length) {
    const t = tasks.shift();
    const prompt = buildPrompt(template, { rule, persona, posting: postingView(jobs.get(t.id)) });
    const at = new Date().toISOString();
    const r = await call(prompt);
    let env = null; try { env = JSON.parse(r.out); } catch { /* recorded */ }
    const text = env && !env.is_error ? env.result : null;
    const v = text === null ? { ok: false, errors: [env ? String(env.result) : `unparseable claude output: ${(r.err || r.out).slice(0, 200)}`], value: null } : validateClaudeOutput(text, { schema: a.schema });
    if (!v.ok) invalid++;
    appendFileSync(a.out, JSON.stringify({
      label: 'JUDGMENT', set: t.set, n: t.n, id: t.id, repeat: t.repeat, prompt: a.prompt, at,
      model_requested: a.model, models: env?.modelUsage ? Object.keys(env.modelUsage) : [], session_id: env?.session_id ?? null, exit_code: r.code,
      verdict: v.ok ? v.value.verdict : 'invalid', parsed: v.value,
      ...(a.schema === 'v2' && v.ok ? { quote_fidelity: quoteFidelity(v.value.evidence, jobs.get(t.id)) } : {}), validation_errors: v.errors, raw: text,
    }) + '\n');
    done++;
  }
}
await Promise.all(Array.from({ length: Number(a.concurrency) }, worker));
console.log(`${done} calls written to ${a.out} (${invalid} invalid). Verdicts not printed.`);
