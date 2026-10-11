# 江山万里行 · 通关文牍 ｜ Sino-Classics Peregrin Atlas

> 一张以“中华古典名篇”为注脚的中国旅行足迹地图 · 单文件 · 零依赖 · 双击即开

---

## 中文

### 一、项目缘起

本项目最初是一份为孩子（昵称“萌宝”）所做的**亲子旅行足迹记录**——“萌宝旅行足迹通关文牒”。
灵感来自传统科举的“通关文牒”意象：把中国的 34 个省级行政区（与脚下的地级市）想象成一座座需要“通关”的城池，每到一个地方，便在该处盖上一枚印章，并配上一首与该地血脉相连的中国古典诗词或古文。
地图之上，去过的省份以浅绿标识（悬停转深绿），未至者以灰标识（悬停转金）；点击任一地区，便弹出一张“通关文牒”卡片，展示匹配而来的名篇全文，配文征明小楷字体的典雅排版。它既是给孩子的人文启蒙，也是一幅可生长的“诗与远方”长卷。

### 二、项目演变

1. **原型阶段**：以一份包含 425 个地理单元的地图为底，手工标注少数去过的地方，卡片里只配零星几首诗，全文依赖少量手工录入。
2. **配色与地图粒度重构**：应需求把全国地图重绘为 **333 个地级行政区** 单元并重新上色（浅绿／灰／悬停深绿／悬停金），同时把北京、上海、天津、重庆四个直辖市合并为单单元，使粒度与中小学地理教材一致。
3. **CSV 驱动的古文重匹配**：引入一份《全国333地级行政区-古诗文素材推荐匹配总表》（695 条素材、按“作者故乡／写作地／描写地／名篇”等依据推荐匹配地点），用脚本把所有古文**按推荐地点自动重匹配**到地图单元，并自动补齐绝大多数篇目的全文。
4. **可编辑化（当前形态）**：标题升级为“江山万里行 · 通关文牍”，副标题改为“行万里路，品万卷书”；新增**用户可编辑能力**——持牒人、签发、文牒编号改为自由输入；在每张卡片内可编辑到访时间、增删旅行备注（旅伴、事由等）、增删古诗词，并可标记“已通关／未至”，全部通过浏览器本地（localStorage）持久化，支持“恢复默认”。
   至此，它从一个“给孩子看的成品”，自然长成了一件**可个性化、可沉淀的个人数字记忆载体**。

### 三、上传为开源仓库的目的

把这份作品开源，怀着两层期待：

- **作为“从 0 开始的数字人文”课程真实素材**：希望高校数字人文、图书情报、档案学相关课程的师生，
  能以它为案例，**一起复刻、并优化整个项目**——从数据整理（CSV↔GeoJSON 匹配）、古典文本结构化，
  到前端可视化与可编辑交互，完整经历一个微型数字人文项目的 lifecycle。仓库里保留了全部脚本、原始数据与冒烟测试，可逐文件拆解学习。
- **作为“个人数字记忆”项目**：中华古典名篇浩如烟海，我们穷尽一生也读不全；但可以先取我们**足迹已达或欲至**的那一部分，
  把它们当作华夏万里江山与我们人生旅程的**亲切注脚**。你完全可以 fork 一份，填入自己的路线、自己的诗、自己的家人名字，
  让它成为独属于你的通关文牍。

### 四、文件结构

```
sino-classics-peregrin-atlas/
├── 江山万里行-通关文牍.html      # 最终成品：单文件、零依赖，双击浏览器即开（已嵌入全部数据）
├── template.html                # 单文件模板，含 /*__MAPDATA__*/null 占位符
├── build.py                     # 把 mapdata4.json 注入模板，生成上面的 HTML
├── gen_from_csv.py              # 按 CSV 推荐地点重匹配古文 + 合并直辖市 + 补齐全文
├── gen_map.py / gen_pref.py / gen_texts.py  # 上游地理/文本数据生成脚本
├── texts_full.py                # 古典名篇全文字典（基础）
├── texts_full_extra.py          # 补全批次（古诗/词/短篇文言文/曲）
├── texts_extra_b1..b5.py, b1r.py# 按作者逐篇录入的全文补全（批次）
├── mapdata3.json                # 重匹配前的地理+通关数据（gen_from_csv 的输入）
├── mapdata4.json                # 重匹配后的数据（build.py 的输入）
├── data/
│   └── 全国333地级行政区-古诗文素材推荐匹配总表.csv  # 古文推荐匹配总表（驱动重匹配）
├── smoke7.js / smoke8.js / smoke9.js  # jsdom 冒烟测试（配色/全文/编辑面板/全覆盖）
└── PROMPT.md                    # 本项目精炼合并后的“提示词与工作流”文档
```

### 五、如何复刻 / 运行

1. （可选）重跑数据管线：
   ```bash
   python gen_from_csv.py     # 读取 CSV + mapdata3.json，生成 mapdata4.json
   python build.py            # 把 mapdata4.json 注入 template.html
   ```
2. 直接打开 `江山万里行-通关文牍.html` 即可使用（无需任何服务器或网络）。
3. 运行测试：`node smoke9.js`（需本机 `npm i jsdom` 或已配置 `NODE_PATH` 指向含 jsdom 的目录）。

### 六、许可证

代码与数据以 MIT 许可证发布；古典名篇文本属公有领域，CSV 素材表版权归原作者/整理者所有，引用请注明出处。

---

## English

### 1. Origin

The project began as a **parent–child travel journal** for a child (nicknamed “Mengbao”): the “Mengbao Travel Footprint Passport.”
It borrows the imagery of the traditional imperial *tonghuan wending* (passport of passage): China’s 34 provincial-level regions (and the prefecture-level cities beneath them) are imagined as cities to be “cleared,” each stamped upon visit and annotated with a Chinese classical poem or essay bound to that place.
On the map, visited regions are tinted light green (deepening to dark green on hover) and unvisited ones are grey (turning gold on hover). Clicking any region opens a “passport card” showing the matched classical text in full, set in an elegant “Wen Zhengming small-script” typeface. It is both a humanities primer for a child and a growing scroll of “poetry and distant lands.”

### 2. Evolution

1. **Prototype** — built on a 425-unit map, with only a handful of visited places and a few manually entered poems.
2. **Recoloring & map granularity** — redrawn to **333 prefecture-level units** with the new palette (light-green / grey / hover-dark-green / hover-gold), and the four municipalities (Beijing, Shanghai, Tianjin, Chongqing) merged into single units to match school geography textbooks.
3. **CSV-driven re-matching** — a master spreadsheet (*古诗文素材推荐匹配总表*, 695 entries) recommends a matching location for each text by criterion (author’s birthplace / writing place / depicted place / famous piece). A script re-matches every text to the map and auto-fills the vast majority of full texts.
4. **Editable (current form)** — retitled “江山万里行 · 通关文牍” with subtitle “行万里路，品万卷书”; added **user-editing**: the passport holder, issuer and serial number become free-text inputs; each card lets you edit the visit date, add/travel notes (companions, purposes), add/remove poems, and toggle “cleared / not-yet,” all persisted in the browser via `localStorage`, with a “restore defaults” option.
   Thus it grew from a finished “gift for a child” into a **personalizable, accretive digital-memory artifact**.

### 3. Why we open-sourced it

Two hopes:

- **As real course material for “Digital Humanities from Zero”** — we invite students and teachers in digital humanities, library & information science, and archival studies to **replicate and improve the whole project together**: from data wrangling (CSV ↔ GeoJSON matching) and structuring classical texts, to front-end visualization and editable interaction — experiencing a complete micro digital-humanities lifecycle. The repo keeps every script, the raw data, and the smoke tests for step-by-step study.
- **As a “personal digital memory” project** — the Chinese canon is boundless and none of us will ever read it all; but we can take the part our **footprints have reached or will reach**, and treat them as **intimate annotations to both the land of China and our own journey**. Fork it, fill in your own routes, your own poems, your own family names, and make it your own passport.

### 4. File structure

*(see the Chinese section above; the built single-file `江山万里行-通关文牍.html` is zero-dependency and opens by double-click.)*

### 5. How to replicate / run

1. (Optional) Regenerate: `python gen_from_csv.py` then `python build.py`.
2. Just open `江山万里行-通关文牍.html` in any browser — no server, no network.
3. Tests: `node smoke9.js` (requires `jsdom` available on `NODE_PATH`).

### 6. License

Code and data are released under the MIT License. Classical texts are in the public domain; the CSV master table’s copyright belongs to its compilers — please cite sources when reusing.
