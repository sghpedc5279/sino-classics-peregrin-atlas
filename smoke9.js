// 综合冒烟测试：标题/副标题、持牒人输入、弹窗编辑面板（时间/备注/增删/恢复）、CSV 全覆盖、配色回归
const fs = require('fs');
const { JSDOM } = require('jsdom');

const BUILD = '江山万里行-通关文牍.html';
const html = fs.readFileSync(BUILD, 'utf-8');

let pass = 0, fail = 0;
const ok = (n, c, extra) => { (c ? pass++ : fail++); console.log((c ? 'PASS ' : 'FAIL ') + n + (extra ? '  ' + extra : '')); };

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'http://localhost/',
  beforeParse(w) {
    w.requestAnimationFrame = cb => setTimeout(() => cb(Date.now()), 0);
    w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
    w.performance = w.performance || { now: () => Date.now() };
  }
});
const w = dom.window, d = w.document;
const click = el => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
const input = el => el.dispatchEvent(new w.Event('input', { bubbles: true }));
const settle = () => new Promise(r => setTimeout(r, 80));

(async () => {
  await settle();
  const css = d.querySelector('style').textContent;

  // ---- A. 标题 / 副标题 / 落款 ----
  ok('页面 title 改为「江山万里行 · 通关文牍」', d.querySelector('title').textContent.trim() === '江山万里行 · 通关文牍', d.querySelector('title').textContent);
  ok('主标题 h1 含「江山万里行 · 通关文牍」', /江山万里行\s*·\s*通关文牍/.test(d.querySelector('h1').textContent));
  ok('副标题改为「行万里路，品万卷书」', d.querySelector('.sub').textContent.includes('行万里路，品万卷书'), d.querySelector('.sub').textContent.trim());
  ok('落款 footer 同步更新', d.querySelector('footer').textContent.includes('江山万里行'));

  // ---- B. 持牒人 / 签发 / 文牒编号 改为输入 ----
  const mh = d.getElementById('metaHolder'), mi = d.getElementById('metaIssuer'), mn = d.getElementById('metaNo');
  ok('持牒人字段为可输入', !!mh && mh.tagName === 'INPUT');
  ok('签发字段为可输入', !!mi && mi.tagName === 'INPUT');
  ok('文牒编号字段为可输入', !!mn && mn.tagName === 'INPUT');

  // 输入并验证 localStorage 持久化
  mh.value = '小萌'; mi.value = '家父 · 家母'; mn.value = 'JW-2026-0001';
  input(mh); input(mi); input(mn);
  const holder = JSON.parse(w.localStorage.getItem('jw_passport_holder_v1') || '{}');
  ok('持牒人输入写入 localStorage', holder.name === '小萌' && holder.issuer === '家父 · 家母' && holder.no === 'JW-2026-0001', JSON.stringify(holder));

  // ---- C. 配色回归（去过浅绿/没去过灰/悬停深绿金） ----
  ok('CSS 变量 --v-light 浅绿', /--v-light\s*:\s*#c8e6c9/.test(css));
  ok('CSS 变量 --v-dark 深绿', /--v-dark\s*:\s*#2e8b57/.test(css));
  ok('CSS 变量 --u-gold 金', /--u-gold\s*:\s*#e3b23c/.test(css));
  ok('去过 .pref.v 浅绿', css.includes('.pref.v{fill:var(--v-light);}'));
  ok('没去过 .pref.u 灰', css.includes('.pref.u{fill:var(--gray);}'));
  ok('去过悬停→深绿', css.includes('.pref.v:hover{fill:var(--v-dark)'));
  ok('没去过悬停→金', css.includes('.pref.u:hover{fill:var(--u-gold)'));

  // ---- D. 弹窗编辑面板 ----
  const vPath = d.querySelector('[data-pref="杭州市"]');
  ok('杭州市路径存在且为 v（已通关）', !!vPath && vPath.getAttribute('class').split(/\s+/).includes('v'));
  click(vPath);
  await settle();
  ok('点击地区弹出卡片（mask 显示）', d.getElementById('mask').classList.contains('show'));
  ok('弹窗含“编辑”按钮', !!d.getElementById('ezOpen'));

  // 打开编辑区
  click(d.getElementById('ezOpen'));
  await settle();
  ok('编辑区展开（#editZone.show）', d.getElementById('editZone') && d.getElementById('editZone').classList.contains('show'));

  // 增诗词
  d.getElementById('ezAt').value = '饮湖上初晴后雨';
  d.getElementById('ezAa').value = '苏轼';
  d.getElementById('ezAf').value = '水光潋滟晴方好，山色空蒙雨亦奇。';
  click(d.getElementById('ezAdd'));
  await settle();
  const ov1 = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('新增诗词写入 localStorage.add', ov1['杭州市'] && ov1['杭州市'].add && ov1['杭州市'].add.some(a => a.t === '饮湖上初晴后雨' && a.a === '苏轼'), JSON.stringify(ov1['杭州市'] && ov1['杭州市'].add));
  ok('新增后卡片出现该篇', d.getElementById('pass').textContent.includes('饮湖上初晴后雨'));

  // 编辑到访时间
  const fdEl = d.getElementById('ezFd');
  fdEl.value = '2026.10'; input(fdEl);
  const ov2 = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('到访时间写入 localStorage.fd', ov2['杭州市'].fd === '2026.10', ov2['杭州市'].fd);

  // 编辑旅行备注
  const ntEl = d.getElementById('ezNotes');
  ntEl.value = '旅伴：爸爸；事由：研学年会'; input(ntEl);
  const ov3 = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('旅行备注写入 localStorage.notes', ov3['杭州市'].notes === '旅伴：爸爸；事由：研学年会', ov3['杭州市'].notes);

  // 标记未至（切换 v）
  click(d.getElementById('ezToggle'));
  await settle();
  const ov4 = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('切换“已通关/未至”写入 localStorage.v=false', ov4['杭州市'].v === false);
  ok('杭州市路径 class 变为 u（灰）', vPath.getAttribute('class').split(/\s+/).includes('u'));
  // 再次切换恢复
  click(d.getElementById('ezToggle'));
  await settle();
  const ov4b = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('再次切换恢复为已通关', ov4b['杭州市'].v === true);
  ok('恢复后杭州市路径回到 v（浅绿）', vPath.getAttribute('class').split(/\s+/).includes('v'));

  // 删除一篇（删除刚才自添的，位于列表末尾）
  const delBtns = [...d.querySelectorAll('.ez-del')];
  const delBtn = delBtns[delBtns.length - 1];
  click(delBtn);
  await settle();
  const ov5 = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('删除自添篇目从 add 中移除', ov5['杭州市'].add.length === 0, JSON.stringify(ov5['杭州市'].add));

  // 恢复默认
  click(d.getElementById('ezRestore'));
  await settle();
  const ov6 = JSON.parse(w.localStorage.getItem('jw_passport_overrides_v1') || '{}');
  ok('恢复默认清除该单元覆盖', !ov6['杭州市']);
  ok('恢复后杭州市路径回到 v（浅绿）', vPath.getAttribute('class').split(/\s+/).includes('v'));

  // ---- E. CSV 重匹配全覆盖（所有古文实例均有全文） ----
  const md = JSON.parse(fs.readFileSync('mapdata4.json', 'utf-8'));
  let miss = 0, inst = 0;
  md.prefs.forEach(p => (p.texts || []).forEach(t => { inst++; if (!t.full || !t.full.trim()) miss++; }));
  ok('mapdata4 全部古文实例均含全文', miss === 0, `${inst} 实例，缺失 ${miss}`);

  console.log(`\n==== ${pass} PASS / ${fail} FAIL ====`);
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('ERR', e); process.exit(2); });
