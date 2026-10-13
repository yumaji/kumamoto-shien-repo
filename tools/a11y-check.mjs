// アクセシビリティの自動検査（JIS X 8341-3:2016 = WCAG 2.0 のうち、機械で確認できる項目）
//
//   node tools/a11y-check.mjs index.html accessibility.html
//
// 問題が無ければ終了コード 0。問題があれば a11y-report.md に内容を書き、終了コード 1。
// 自動検査で分かるのは一部だけなので、構成を大きく変えたときは accessibility.html の
// チェックリストに沿って手でも確認すること（OPERATIONS.md 9節）。
//
// 必要なもの: npm install --no-save playwright-core axe-core html-validate
// ブラウザは GitHub Actions に入っている Chrome を使う。手元では CHROME_PATH で指定できる。
import { chromium } from 'playwright-core';
import { HtmlValidate } from 'html-validate';
import { createRequire } from 'node:module';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const files = process.argv.slice(2);
if (!files.length) { console.error('検査する HTML ファイルを指定してください'); process.exit(2); }

const require = createRequire(import.meta.url);
const axeSource = readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const problems = [];  // { file, kind, detail }

// 1) HTML の構文（4.1.1 構文解析）
const validator = new HtmlValidate({ extends: ['html-validate:recommended'] });
for (const file of files) {
  const report = await validator.validateFile(file);
  for (const r of report.results) for (const m of r.messages) {
    problems.push({ file, kind: 'HTML の構文', detail: `${m.line}行目: ${m.message}（${m.ruleId}）` });
  }
}

const browser = await chromium.launch(process.env.CHROME_PATH
  ? { executablePath: process.env.CHROME_PATH } : { channel: 'chrome' });

for (const file of files) {
  const url = pathToFileURL(resolve(file)).href;

  // 2) axe-core による WCAG 2.0 レベル A・AA の検査を、パソコンとスマホの幅で
  for (const [label, viewport] of [['パソコン幅', { width: 1280, height: 900 }], ['スマホ幅', { width: 390, height: 844 }]]) {
    const page = await browser.newPage({ viewport });
    await page.goto(url);
    await page.addScriptTag({ content: axeSource });
    const result = await page.evaluate(() => axe.run(document, {
      runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] },
    }));
    for (const v of result.violations) {
      const sc = v.tags.filter(t => /^wcag\d{3,}$/.test(t)).map(t => t.replace(/^wcag(\d)(\d)(\d+)$/, '$1.$2.$3')).join(', ');
      for (const n of v.nodes) {
        const msg = (n.any[0] || n.all[0] || n.none[0] || {}).message || v.help;
        problems.push({ file, kind: `${v.help}（達成基準 ${sc}、${label}）`, detail: `\`${n.target.join(' ')}\` — ${msg}` });
      }
    }
    await page.close();
  }

  // 3) 200% 拡大（1.4.4）：1280px の画面を 200% にした状態で横スクロールが出ないか
  {
    const page = await browser.newPage({ viewport: { width: 640, height: 900 } });
    await page.goto(url);
    const w = await page.evaluate(() => document.documentElement.scrollWidth);
    if (w > 640) problems.push({ file, kind: '200% 拡大（達成基準 1.4.4）', detail: `横幅が ${w}px になり、横スクロールが発生する` });
    await page.close();
  }

  // 4) フォーカスの可視化（2.4.7）：Shift+Tab で戻るとき、画面上部に固定したナビの下に隠れないか
  {
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    await page.goto(url);
    if (await page.locator('.nav-filter').count()) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.locator('footer a').last().focus();
      const hidden = new Set();
      const count = await page.evaluate(() => document.querySelectorAll('a[href],button').length);
      for (let i = 0; i < count; i++) {
        await page.keyboard.press('Shift+Tab');
        const h = await page.evaluate(() => {
          const el = document.activeElement;
          if (!el || el === document.body || el.closest('.nav-filter')) return null;
          const nav = document.querySelector('.nav-filter').getBoundingClientRect();
          const r = el.getBoundingClientRect();
          return (nav.top <= 1 && r.top < nav.bottom && r.bottom <= nav.bottom + 1) ? el.textContent.trim().slice(0, 30) : null;
        });
        if (h) hidden.add(h);
      }
      for (const h of hidden) problems.push({ file, kind: 'フォーカスが固定ナビに隠れる（達成基準 2.4.7）', detail: `「${h}」` });
    }
    await page.close();
  }
}
await browser.close();

if (!problems.length) {
  console.log(`問題は見つかりませんでした（${files.join(', ')}）`);
  process.exit(0);
}

const lines = [
  'サイトの更新後に実行したアクセシビリティの自動検査で、JIS X 8341-3:2016（適合レベル AA）を満たさない箇所が見つかりました。',
  '',
  '**このままだと、アクセシビリティ方針（accessibility.html）で表明している「適合レベル AA に準拠」が事実と食い違います。** 修正してください。',
  '',
];
for (const file of files) {
  const mine = problems.filter(p => p.file === file);
  if (!mine.length) continue;
  lines.push(`## ${file}`, '');
  for (const kind of [...new Set(mine.map(p => p.kind))]) {
    lines.push(`### ${kind}`, '');
    const details = [...new Set(mine.filter(p => p.kind === kind).map(p => p.detail))];
    for (const d of details.slice(0, 15)) lines.push(`- ${d}`);
    if (details.length > 15) lines.push(`- ほか ${details.length - 15} 件`);
    lines.push('');
  }
}
lines.push('よくある原因：文字色に `--amber` を使った（文字には `--amber-ink` を使う）、リンクの文言が「こちら」だけ、など。OPERATIONS.md 9節を参照。');
writeFileSync('a11y-report.md', lines.join('\n') + '\n');
console.log(lines.join('\n'));
process.exit(1);
