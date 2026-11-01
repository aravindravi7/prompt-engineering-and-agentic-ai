#!/usr/bin/env node
// Asserts that a run reported exactly the expected new ids (seeded runs).
// node tools/check-new-set.mjs --seeded runs/<ts>-seeded-earlier --run runs/<ts>-seeded-second
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parseArgs } from 'node:util';
const { values: a } = parseArgs({ options: { seeded: { type: 'string' }, run: { type: 'string' } } });
const expected = JSON.parse(readFileSync(join(a.seeded, 'seeded-meta.json'), 'utf8')).expected_new_ids;
const got = JSON.parse(readFileSync(join(a.run, 'report.json'), 'utf8')).map(r => r.id).sort((x, y) => x - y);
const ok = JSON.stringify(got) === JSON.stringify(expected);
console.log(`${ok ? 'PASS' : 'FAIL'}: expected new ids ${JSON.stringify(expected)}; reported ${JSON.stringify(got)}`);
process.exit(ok ? 0 : 1);
