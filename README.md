# 江山万里行 · 通关文牍 ｜ Sino-Classics Peregrin Atlas

> 以中国古典诗文为注脚的旅行足迹地图：按省市/地级区记录足迹，点击区域可查看对应古文卡片，支持本地编辑与个性化保存。

一个以“中华古典名篇”为注脚的中国旅行地图。它从一个亲子旅行纪念项目成长为一个可复刻、可扩展、可二次创作的数字人文作品：

- 单文件、零依赖、可直接双击打开
- 以 333 个地级行政区为地图单元
- 已去过/未去过地区用颜色区分，悬停及点击可查看详细卡片
- 每个地区展示与当地相关的古诗文、作者、写作地、描写地等信息
- 支持自定义持牒人、证书编号、到访日期、备注与诗文增删
- 通过本地 localStorage 持久保存编辑结果

---

## 中文

### 项目简介

本项目最初是一份为孩子制作的“旅行足迹通关文牍”，灵感来自传统“通关文牒”与古典旅行记忆的叠加：每到一个地方，便在地图上对应一个地区，展开一张“通关文牒”卡片，展示匹配到的古典诗文、作者与地方关联。

在当前版本中，项目已发展为一个“可复刻的数字人文小作品”：

- 数据生成脚本与原始 CSV 均保留在仓库中
- 地图、文本与交互逻辑被拆成可理解的模块
- 可通过脚本重建单文件最终成果
- 适合作为数字人文、图书情报、档案学等课程的真实案例材料

### 主要功能

- 中国地图可视化：基于 SVG 路径渲染，无依赖第三方地图库
- 333 个地级行政区单元：更细粒度地记录足迹
- 通关状态区分：已通关 / 未至，悬停时颜色变化
- 诗文卡片：点击区域后显示对应古典篇目、作者、出处、关联类型、全文
- 可编辑层：修改旅行日期、备注、卡片内容，以及区分已通关与未至
- 统计面板：已通关省份数、比例、进度、诗文篇数等实时更新
- 本地检索：按篇名、作者、地点或全文关键词快速定位

### 仓库结构

```text
sino-classics-peregrin-atlas/
├── 江山万里行-通关文牍.html      # 最终生成的单文件地图应用
├── template.html                # 单文件模板，包含 MAPDATA 占位符
├── build.py                     # 将 mapdata4.json 注入模板并生成 HTML
├── gen_from_csv.py              # 从 CSV 重匹配地理单元与古文素材
├── gen_map.py                   # 地图与地理数据生成脚本
├── gen_pref.py                  # 地级行政区数据生成脚本
├── gen_texts.py                 # 文本数据生成脚本
├── texts_full.py                # 基础全文字典
├── texts_full_extra.py          # 补充全文数据
├── texts_extra_b1.py            # 分批全文补充（b1）
├── texts_extra_b1r.py           # 分批全文补充（b1r）
├── texts_extra_b2.py            # 分批全文补充（b2）
├── texts_extra_b3.py            # 分批全文补充（b3）
├── texts_extra_b4.py            # 分批全文补充（b4）
├── texts_extra_b5.py            # 分批全文补充（b5）
├── mapdata3.json                # 生成前的地理/通关数据
├── mapdata4.json                # 重匹配后的最终数据
├── data/
│   └── 全国333地级行政区-古诗文素材推荐匹配总表.csv
├── smoke7.js                   # 冒烟测试（配色与基础交互）
├── smoke8.js                   # 冒烟测试（全文与编辑面板）
├── smoke9.js                   # 冒烟测试（全覆盖检查）
├── PROMPT.md                   # 精炼版项目提示词/工作流说明
├── README.md                   # 项目说明文档
├── .gitignore
└── LICENSE                     # 若本仓库配置了许可证文件
```

### 快速开始

#### 方式 1：直接打开

双击打开 `江山万里行-通关文牍.html` 即可使用。

无需本地服务器，也不需要网络连接，适合直接分享或本地展示。

#### 方式 2：重建生成文件

```bash
python gen_from_csv.py
python build.py
```

说明：

- `gen_from_csv.py` 会从 CSV 与原始数据生成更新后的 `mapdata4.json`
- `build.py` 会把 `mapdata4.json` 注入 `template.html`，生成最终 HTML

#### 方式 3：运行回归测试

```bash
node smoke9.js
```

需要本机已安装 `jsdom`，或设置 `NODE_PATH` 指向包含该依赖的目录。

### 数据流程

1. 地理数据与状态生成：`gen_map.py` / `gen_pref.py`
2. 古文重匹配与全文补齐：`gen_from_csv.py`
3. 模板注入生成最终页面：`build.py`

最终产物是一个单文件应用，保留了整体数据结构和所有交互逻辑。

### 许可证

- 代码与数据：MIT License
- 古典文本：多为公有领域文本
- CSV 素材表：版权归原整理者/来源方所有，二次引用请注明出处

---

## English

### Overview

This project is a travel atlas grounded in classical Chinese poetry and prose. It records a journey across China by mapping each location to a historical text, author, or cultural association.

The project evolved from a child-focused travel passport into a reusable digital humanities artifact:

- single-file, no dependency, openable by double-click
- structured around 333 prefecture-level administrative units
- colored by visitation status: visited vs. unvisited
- click a region to view matched classical passages and metadata
- editable local state for names, dates, notes, and custom text additions

### Features

- SVG-based China map without external map libraries
- Prefecture-level visualization for detailed footprint tracking
- Hover/click interactions with semantic cards for each region
- Matched literary entries including authors, place associations, text type, and full text
- Personalizable passport metadata saved in browser localStorage
- Real-time statistics for completion rate and total unlocked texts
- Search by title, author, place, or full text content

### Quick Start

Open the generated single-file app:

```bash
# Optional rebuild
python gen_from_csv.py
python build.py
```

Then open:

```text
江山万里行-通关文牍.html
```

Run tests:

```bash
node smoke9.js
```

### Project Structure

See the Chinese section above for file descriptions. The core generated artifact is `江山万里行-通关文牍.html`, while the data pipeline scripts live at the repository root.

### License

- Code and dataset structure: MIT License
- Classical texts: public domain or source-dependent
- CSV master reference table: please respect the original source and attribution requirements

---

## 适合的使用场景

- 个人旅行足迹记录
- 家庭纪念与亲子互动
- 数字人文教学案例
- 文化地图/古典文献关联展示
- 个人数字记忆载体的二次定制

## 目标与愿景

这个项目的核心不是单纯的“地图”，而是把“地理足迹”和“文化记忆”连接起来：

- 你走过哪里
- 你读过哪些文字
- 这些文字如何与地方、时代与人生发生关联

最终，它希望成为一张“行万里路，品万卷书”的中国文化地图。

---

如果你愿意，我还可以继续帮你把 README 再优化成更适合 GitHub 展示的版本，例如：

- 增加项目截图展示区
- 改成更偏“技术文档”风格
- 改成更偏“产品介绍”风格
- 补充中文版/英文版分栏展示的最终版
