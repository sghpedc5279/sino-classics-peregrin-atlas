# -*- coding: utf-8 -*-
"""按 CSV 推荐匹配地点重匹配古文，并合并直辖市为单单元，生成 mapdata4.json。
保留原 mapdata3.json 的通关状态 v、访问时间 fd、地理结构(w/h/proj/plabels/provinces/nanhai)。
全文优先取自 texts_full.FULL；缺失的留空，后续补全。"""
import csv, json, re, sys, os
sys.path.insert(0, '.')
from texts_full import FULL as FULL_BASE

# 依次合并所有补全批次；非空值优先，避免被空占位覆盖
EXTRA_FILES = [
    'texts_full_extra',   # 第一批（古诗/词/短篇文言文/曲）
    'texts_extra_b1', 'texts_extra_b2', 'texts_extra_b3',
    'texts_extra_b4', 'texts_extra_b5', 'texts_extra_b1r',
]
FULL = dict(FULL_BASE)
for _mod in EXTRA_FILES:
    try:
        m = __import__(_mod)
        for _k, _v in m.FULL_EXTRA.items():
            if _v and _v.strip():
                FULL[_k] = _v
            elif _k not in FULL:
                FULL[_k] = _v
    except Exception as _e:
        print('skip', _mod, _e)

MAP3 = 'mapdata3.json'
CSV  = 'C:/Users/sghpe/Downloads/全国333地级行政区-古诗文素材推荐匹配总表.csv'
OUT  = 'mapdata4.json'

MUNI = {'北京','上海','天津','重庆'}
PROV = MUNI | {'河北','山西','内蒙古','辽宁','吉林','黑龙江','江苏','浙江','安徽','福建',
              '江西','山东','河南','湖北','湖南','广东','广西','海南','四川','贵州','云南',
              '西藏','陕西','甘肃','青海','宁夏','新疆','香港','澳门','台湾'}

def split_loc(l):
    for p in PROV:
        if l.startswith(p):
            return p, l[len(p):]
    return None, l

def norm_title(t):  return t.strip().strip('《》').strip()
def norm_author(a): return re.sub(r'[（(][^）)]*[）)]', '', a.strip()).strip()
def dynasty(a):
    m = re.search(r'[（(]([^）)]*)[）)]', a)
    return m.group(1) if m else '—'

# ---- 解析 CSV ----
rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig')))
loc_texts = {}
for r in rows:
    prov, city = split_loc(r['推荐匹配地点'].strip())
    if not prov:
        continue
    city = city or prov            # 香港/澳门/台湾 等无后缀
    t = norm_title(r['篇目']); a = norm_author(r['作者'])
    basis = r['匹配依据']
    if '故乡' in basis:       lt = 'birth'
    elif '写作地' in basis:   lt = 'write'
    elif '描写' in basis or '产' in basis: lt = 'desc'
    else:                     lt = 'famous'
    key = (prov, city)
    loc_texts.setdefault(key, []).append({
        't': t, 'a': a, 'd': dynasty(r['作者']), 'g': r['学段/素材来源'],
        'place': r['描写地点'], 'lt': lt, 'basis': basis, 'type': r['类型']
    })

QUOTE_TYPES = {'蒙学格言','楹联','清言格言','蒙学经典','金文'}

def build_text(x):
    t = x['t']; a = x['a']
    full = FULL.get((t, a), '')
    if not full and x['type'] in QUOTE_TYPES:
        full = t.strip('"').strip()
    return {
        't': t, 'a': a, 'd': x['d'], 'g': x['g'], 'place': x['place'],
        'lt': x['lt'], 'basis': x['basis'], 'type': x['type'],
        'full': full
    }

# ---- 载入旧数据 ----
d3 = json.load(open(MAP3, encoding='utf-8'))
old_prefs = d3['prefs']

# 按省归集直辖市 districts
muni_groups = {}
other_prefs = []
for pf in old_prefs:
    if pf.get('prov') in MUNI and not pf['name'].endswith('市'):
        muni_groups.setdefault(pf['prov'], []).append(pf)
    else:
        other_prefs.append(pf)

new_prefs = []
used_csv = set()
missing_full = set()

# 直辖市合并
for prov, dists in muni_groups.items():
    d = ' '.join(p['d'] for p in dists if p.get('d'))
    v = max((p.get('v', 0) for p in dists), default=0)
    fd = next((p['fd'] for p in dists if p.get('fd')), '')
    key = (prov, '市')
    raw = loc_texts.get(key, [])
    used_csv.add(key)
    texts = []
    for x in raw:
        bt = build_text(x); texts.append(bt)
        if not bt['full']: missing_full.add((bt['t'], bt['a']))
    new_prefs.append({'prov': prov, 'name': prov + '市', 'd': d, 'v': v, 'fd': fd, 'texts': texts})

# 其余 pref：按 (prov, name) 匹配
for pf in other_prefs:
    name = pf['name']
    key = (pf['prov'], name)
    raw = loc_texts.get(key, [])
    used_csv.add(key)
    texts = []
    for x in raw:
        bt = build_text(x); texts.append(bt)
        if not bt['full']: missing_full.add((bt['t'], bt['a']))
    new_prefs.append({'prov': pf['prov'], 'name': name, 'd': pf.get('d', ''),
                      'v': pf.get('v', 0), 'fd': pf.get('fd', ''), 'texts': texts})

# ---- 统计 ----
n_texts = sum(len(p['texts']) for p in new_prefs)
empty_prefs = [p['name'] for p in new_prefs if not p['texts']]
unused_csv = [k for k in loc_texts if k not in used_csv]

out = dict(d3)
out['prefs'] = new_prefs
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

print('新 pref 数:', len(new_prefs), '(原', len(old_prefs), ')')
print('匹配到的古文实例数:', n_texts)
print('有匹配文本的 pref 数:', sum(1 for p in new_prefs if p['texts']))
print('空匹配(无 CSV 文本) pref 数:', len(empty_prefs), '->', empty_prefs[:30])
print('CSV 单元未被地图使用(地图缺该单元):', len(unused_csv), '->', unused_csv[:30])
print('缺失全文的(篇目,作者)数:', len(missing_full))
print('written', os.path.getsize(OUT)//1024, 'KB ->', OUT)
