import { Liquid } from 'liquidjs';
import fs from 'node:fs';
import vm from 'node:vm';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const stateSource = fs.readFileSync(path.join(root, 'assets/theme/snippets/bfcm-state.liquid'), 'utf8').replace(/{% doc %}[\s\S]*?{% enddoc %}/, '');
const settings = {bfcm_enabled: true, bfcm_start_at: '2026-11-16T00:00:00-05:00', bfcm_end_at: '2026-11-30T23:59:59-05:00'};
let count = 0;
const check = (name, condition) => { assert.ok(condition, name); count++; };
async function state(now, extra = {}) {
  const engine = new Liquid();
  engine.registerFilter('date', v => Math.floor(Date.parse(v === 'now' ? now : v) / 1000));
  return (await engine.parseAndRender(stateSource, {settings: {...settings, ...extra}})).trim();
}
for (const [now, expected] of [['2026-11-16T04:59:59Z', 'normal'], ['2026-11-16T05:00:00Z', 'active'], ['2026-12-01T04:59:59Z', 'active'], ['2026-12-01T05:00:00Z', 'normal']]) {
  check(`Boundary ${now}`, await state(now) === expected);
}
check('Disabled restores normal', await state('2026-11-20T00:00:00Z', {bfcm_enabled: false}) === 'normal');
check('Old schedule cannot restart next year', await state('2027-11-20T00:00:00Z') === 'normal');
check('Invalid schedule fails closed', await state('2026-11-20T00:00:00Z', {bfcm_start_at: 'invalid'}) === 'normal');
check('Renewed schedule runs next year', await state('2027-11-20T00:00:00Z', {bfcm_start_at: '2027-11-15T00:00:00-05:00', bfcm_end_at: '2027-11-29T23:59:59-05:00'}) === 'active');

const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'bfcm-test-'));
const theme = path.join(tmp, 'theme');
try {
  execFileSync('python3', ['-c', "import sys,shutil;sys.path.insert(0,'tests');from test_campaign import CampaignTests,prepare;t=CampaignTests();t.setUp();prepare(t.source,t.output,t.config);shutil.copytree(t.output,sys.argv[1]);t.temp.cleanup()", theme], {cwd: root});
  const layout = fs.readFileSync(path.join(theme, 'layout/theme.liquid'), 'utf8').replace("{% render 'bfcm-clock', state: bfcm_state %}", '');
  const engine = new Liquid({root: path.join(theme, 'snippets'), extname: '.liquid'});
  engine.registerTag('doc', {parse(t, tokens) {while (tokens.length) if (tokens.shift().name === 'enddoc') break;}, render() {return '';}});
  for (const type of ['section', 'sections']) engine.registerTag(type, {parse(t) {this.name = t.args.replace(/['"]/g, '');}, render() {return `[${type}:${this.name}]`;}});
  const context = {settings, request: {page_type: 'index'}, content_for_layout: 'BASELINE_CONTENT'};
  engine.options.globals = context;
  for (const [now, active] of [['2026-11-15T00:00:00Z', false], ['2026-11-20T00:00:00Z', true], ['2026-12-01T05:00:00Z', false]]) {
    engine.registerFilter('date', v => Math.floor(Date.parse(v === 'now' ? now : v) / 1000));
    const html = await engine.parseAndRender(layout, context);
    check(`Homepage routing ${now}`, active ? html.includes('[section:bfcm-home]') && !html.includes('BASELINE_CONTENT') : html.includes('BASELINE_CONTENT') && !html.includes('[section:bfcm-home]'));
    check(`Header/footer routing ${now}`, html.includes(`[sections:header-group${active ? '-bfcm' : ''}]`) && html.includes(`[sections:footer-group${active ? '-bfcm' : ''}]`));
  }
  engine.registerFilter('date', v => Math.floor(Date.parse(v === 'now' ? '2026-11-20T00:00:00Z' : v) / 1000));
  context.request.page_type = 'product';
  const product = await engine.parseAndRender(layout, context);
  check('Product page content remains during campaign', product.includes('BASELINE_CONTENT') && !product.includes('[section:bfcm-home]'));
} finally {fs.rmSync(tmp, {recursive: true, force: true});}

const clockSource = fs.readFileSync(path.join(root, 'assets/theme/snippets/bfcm-clock.liquid'), 'utf8').match(/{% javascript %}([\s\S]*?){% endjavascript %}/)[1];
let now = Date.parse('2026-12-01T04:59:59Z'), scheduled, redirect;
const events = {}, stored = new Map();
const context = {
  document: {hidden: false, querySelector: () => ({dataset: {state: 'active', enabled: 'true', start: settings.bfcm_start_at, end: settings.bfcm_end_at}}), addEventListener: (type, fn) => events[type] = fn},
  window: {Shopify: {}, addEventListener: (type, fn) => events[type] = fn},
  Date: {now: () => now, parse: Date.parse}, URL,
  location: {href: 'https://example.com/?utm_source=demo', replace: url => redirect = url},
  sessionStorage: {getItem: key => stored.get(key), setItem: (key, value) => stored.set(key, value)},
  setTimeout: (fn, delay) => {scheduled = {fn, delay}; return 1;}, clearTimeout: () => {}
};
vm.runInNewContext(clockSource, context);
check('Open tab schedules boundary refresh', scheduled.delay === 1100);
now += 1100; scheduled.fn();
check('Refresh preserves tracking params', redirect.includes('bfcm_refresh=') && redirect.includes('utm_source=demo'));
redirect = undefined; events.pageshow();
check('Cached response does not loop immediately', redirect === undefined);
console.log(`${count} lifecycle checks passed. Shopify rendering/network behavior still requires draft preview.`);
