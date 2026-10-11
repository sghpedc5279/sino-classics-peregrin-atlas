// 验证：弹窗全文渲染 + 上一篇/下一篇 + 文征明小楷样式 + 未通关灰色保持
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

  // 1) CSS：文征明小楷 + .pf 类
  const css = d.querySelector('style').textContent;
  ok('CSS 含“文征明小楷”字体声明', css.includes('文征明小楷'));
  ok('CSS 含 .poem .pf 全文样式', css.includes('.poem .pf'));

  // 2) 数据：杭州市含《湖心亭看雪》全文（CSV 重匹配后归杭州）
  const PREF = w.__PREF;
  ok('PREF[杭州市] 存在', !!(PREF && PREF['杭州市']));
  const hz = PREF && PREF['杭州市'] && PREF['杭州市'].texts.find(t => t.t === '湖心亭看雪');
  ok('杭州市《湖心亭看雪》有全文', !!(hz && hz.full && hz.full.includes('天与云与山与水')));
  ok('杭州市 状态 v=1（已通关绿色）', PREF['杭州市'].v === 1);

  // 3) 未通关城市仍灰色（徐州：江苏例外）
  ok('徐州市 v=0（未通关灰色）', PREF && PREF['徐州市'] && PREF['徐州市'].v === 0);

  // 4) 模拟点击 杭州市 路径 -> 弹窗渲染全文
  const path = d.querySelector('[data-pref="杭州市"]');
  ok('地图含 杭州市 data-pref 路径', !!path);
  if (path) {
    const ev = new w.MouseEvent('click', { bubbles: true, cancelable: true });
    path.dispatchEvent(ev);
    await settle();
    const passEl = d.getElementById('pass');
    const inner = passEl ? passEl.innerHTML : '';
    ok('弹窗打开并渲染全文（非空）', inner.includes('class="pf"') && !inner.includes('（暂无全文）'));
    ok('弹窗含 .pf 全文容器', inner.includes('class="pf"'));
    ok('弹窗含“— 全文 —”标签', inner.includes('全文'));
  }

  // 5) 多篇城市（北京市合并后为一个单元，含多篇）翻页可用
  const bj = PREF && PREF['北京市'];
  ok('北京市（合并单元）含多篇古文', !!(bj && bj.texts.length > 10), bj && bj.texts.length);
  const bjPath = d.querySelector('[data-pref="北京市"]');
  if (bjPath) {
    bjPath.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
    await settle();
    let inner = d.getElementById('pass').innerHTML;
    const before = inner;
    const nextBtn = d.getElementById('nextTxt');
    ok('北京市 下一篇按钮可用', !!(nextBtn && !nextBtn.disabled));
    if (nextBtn && !nextBtn.disabled) {
      nextBtn.click();
      await settle();
      const after = d.getElementById('pass').innerHTML;
      ok('点击下一篇后内容更新（翻页生效）', after !== before && after.includes('class="pf"'));
      // 循环翻页
      for (let i = 0; i < bj.texts.length + 2; i++) { const nb = d.getElementById('nextTxt'); if (nb) nb.click(); }
      await settle();
      const wrap = d.getElementById('pass').innerHTML;
      ok('循环翻页后仍含全文', wrap.includes('class="pf"'));
    }
  }

  // 6) 未通关 hover 提示
  const tg = w.hideTip; // 函数存在即可（逻辑在事件里，jsdom 难模拟真实 hover，跳过实际坐标）
  ok('hideTip/showTip 函数存在', typeof w.showTip === 'function' && typeof w.hideTip === 'function');

  console.log(`\n==== ${pass} PASS / ${fail} FAIL ====`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e); process.exit(2); });
