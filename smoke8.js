// 验证：新配色方案（去过浅绿/悬停深绿；没去过灰/悬停金）+ 图例同步
const fs = require('fs');
const { JSDOM } = require('jsdom');
const html = fs.readFileSync('江山万里行-通关文牍.html', 'utf-8');

let pass = 0, fail = 0;
const ok = (n, c, extra) => { (c ? pass++ : fail++); console.log((c ? 'PASS ' : 'FAIL ') + n + (extra ? '  ' + extra : '')); };

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  beforeParse(w) {
    w.requestAnimationFrame = cb => setTimeout(() => cb(Date.now()), 0);
    w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
    w.performance = w.performance || { now: () => Date.now() };
  }
});
const w = dom.window, d = w.document;
function settle() { return new Promise(r => setTimeout(r, 60)); }

(async () => {
  await settle();
  const css = d.querySelector('style').textContent;

  // 1) 颜色变量定义
  const hasVar = (name, val) => css.includes(name + ':' + val) || new RegExp('--' + name.replace('--', '') + '\\s*:').test(css);
  ok('CSS 定义 --v-light 浅绿变量', /--v-light\s*:\s*#c8e6c9/.test(css));
  ok('CSS 定义 --v-dark 深绿变量', /--v-dark\s*:\s*#2e8b57/.test(css));
  ok('CSS 定义 --u-gold 金变量', /--u-gold\s*:\s*#e3b23c/.test(css));

  // 2) 去过=浅绿，没去过=灰 的规则
  ok('去过 .pref.v 填充浅绿', css.includes('.pref.v{fill:var(--v-light);}'));
  ok('没去过 .pref.u 填充灰', css.includes('.pref.u{fill:var(--gray);}'));

  // 3) hover 变色规则
  ok('去过悬停→深绿', css.includes('.pref.v:hover{fill:var(--v-dark)'));
  ok('没去过悬停→金', css.includes('.pref.u:hover{fill:var(--u-gold)'));

  // 4) DOM：去过单元挂 v 类，没去过挂 u 类
  const vPath = d.querySelector('[data-pref="杭州市"]');
  const uPath = d.querySelector('[data-pref="徐州市"]');
  ok('杭州市 路径含 v 类（浅绿/悬停深绿）', !!vPath && vPath.getAttribute('class').split(/\s+/).includes('v'));
  ok('徐州市 路径含 u 类（灰/悬停金）', !!uPath && uPath.getAttribute('class').split(/\s+/).includes('u'));

  // 5) 图例文案同步
  const legend = d.querySelector('.legend').textContent;
  ok('图例含“去过（浅绿）”', legend.includes('去过（浅绿）'));
  ok('图例含“没去过（灰）”', legend.includes('没去过（灰）'));
  ok('图例含悬停说明', legend.includes('悬停：去过→深绿，没去过→金'));

  // 6) 统计计数仍正确（去过 217 / 没去过 208 反映到图例数字）
  const nd = d.getElementById('numProvDone'), nt = d.getElementById('numProvTodo');
  ok('图例数字已渲染（去过数>0）', nd && parseInt(nd.textContent, 10) > 0);
  ok('图例数字已渲染（没去过数>0）', nt && parseInt(nt.textContent, 10) > 0);

  console.log(`\n==== ${pass} PASS / ${fail} FAIL ====`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e); process.exit(2); });
