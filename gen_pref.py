# -*- coding: utf-8 -*-
"""抓取地级行政区划 GeoJSON -> 简化投影 -> mapdata2.json (prefecture 级)"""
import json, math, urllib.request
from concurrent.futures import ThreadPoolExecutor

SRC = 'mapdata.json'
OUT = 'mapdata2.json'
TOL = 1.05  # 屏幕空间抽稀容差(px)

# 省/直辖市/特区 adcode -> 简称(与现有 visited/ABBR 一致)
ADCODE = {
 110000:'北京',120000:'天津',130000:'河北',140000:'山西',150000:'内蒙古',
 210000:'辽宁',220000:'吉林',230000:'黑龙江',310000:'上海',320000:'江苏',
 330000:'浙江',340000:'安徽',350000:'福建',360000:'江西',370000:'山东',
 410000:'河南',420000:'湖北',430000:'湖南',440000:'广东',450000:'广西',
 460000:'海南',500000:'重庆',510000:'四川',520000:'贵州',530000:'云南',
 540000:'西藏',610000:'陕西',620000:'甘肃',630000:'青海',640000:'宁夏',
 650000:'新疆',710000:'台湾',810000:'香港',820000:'澳门'
}
FULL2SHORT = {
 '北京市':'北京','天津市':'天津','河北省':'河北','山西省':'山西','内蒙古自治区':'内蒙古',
 '辽宁省':'辽宁','吉林省':'吉林','黑龙江省':'黑龙江','上海市':'上海','江苏省':'江苏',
 '浙江省':'浙江','安徽省':'安徽','福建省':'福建','江西省':'江西','山东省':'山东',
 '河南省':'河南','湖北省':'湖北','湖南省':'湖南','广东省':'广东','广西壮族自治区':'广西',
 '海南省':'海南','重庆市':'重庆','四川省':'四川','贵州省':'贵州','云南省':'云南',
 '西藏自治区':'西藏','陕西省':'陕西','甘肃省':'甘肃','青海省':'青海','宁夏回族自治区':'宁夏',
 '新疆维吾尔自治区':'新疆','台湾省':'台湾','香港特别行政区':'香港','澳门特别行政区':'澳门'
}

md = json.load(open(SRC, encoding='utf-8'))
proj = md['proj']
def pr(lon, lat):
    x = (lon - proj['lon0']) * proj['kx']
    y = -(lat - proj['lat0'])
    return ((x - proj['xmin']) * proj['s'] + proj['ox'],
            (y - proj['ymin']) * proj['s'] + proj['oy'])

def area_deg(ring):
    a = 0.0
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]; x2, y2 = ring[(i+1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2.0

def dp(pts, tol):
    if len(pts) < 3: return pts
    dmax, idx = 0.0, 0
    for i in range(1, len(pts)-1):
        x0, y0 = pts[0]; x1, y1 = pts[i]; x2, y2 = pts[-1]
        dx, dy = x2-x0, y2-y0
        norm = math.hypot(dx, dy)
        if norm == 0:
            d = math.hypot(x1-x0, y1-y0)
        else:
            d = abs(dx*(y0-y1) - (x0-x1)*dy) / norm
        if d > dmax: dmax, idx = d, i
    if dmax > tol:
        l = dp(pts[:idx+1], tol); r = dp(pts[idx:], tol)
        return l[:-1] + r
    return [pts[0], pts[-1]]

def to_path(ring):
    pts = [pr(*p) for p in ring]
    pts = dp(pts, TOL)
    if pts[0] != pts[-1]: pts.append(pts[0])
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'

def fetch(adcode):
    url = f'https://geo.datav.aliyun.com/areas_v3/bound/{adcode}_full.json'
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    try:
        data = urllib.request.urlopen(req, timeout=60).read()
        return adcode, json.loads(data)
    except Exception as e:
        print('  FALLBACK', ADCODE[adcode], repr(e)[:80])
        return adcode, None

print('downloading 34 provinces...')
results = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    futs = {ex.submit(fetch, c): c for c in ADCODE}
    for f in futs:
        c, j = f.result()
        results[c] = j
        if j: print('  got', ADCODE[c], len(j['features']), 'features')

# 省份标签位置(沿用现有，匹配更稳定)
label_lookup = {}
for p in md['provinces']:
    nm = p['name']
    short = FULL2SHORT.get(nm, nm)
    label_lookup[short] = (p['lx'], p['ly'])

# 现有省级多边形(回退用)
prov_fallback = {}
for p in md['provinces']:
    prov_fallback[FULL2SHORT.get(p['name'], p['name'])] = p['d']

NANHAI_KEYS = ('三沙', '南沙', '西沙', '中沙', '东沙', '南海岛')

# 足迹城市坐标：用于判定"到访过的地级市"(精确着色,避免整省泛绿)
FOOT = {
 '北京':(116.41,39.90,'2025.07'),'鞍山':(122.99,41.11,'2025.07'),'沈阳':(123.43,41.80,'2025.07'),'大连':(121.62,38.92,'2024.07'),
 '齐齐哈尔':(123.92,47.35,'2025.07'),'牡丹江':(129.61,44.56,'2025.08'),'绥芬河':(131.15,44.42,'2025.08'),'哈尔滨':(126.53,45.80,'2025.08'),
 '长春':(125.32,43.82,'2024.07'),'吉林市':(126.55,43.84,'2024.07'),'梅河口':(125.32,42.53,'2024.07'),'长白山':(128.05,42.06,'2024.07'),
 '延吉':(129.51,42.91,'2024.07'),'珲春':(130.37,42.87,'2024.07'),'通化':(125.93,41.72,'2024.07'),
 '扬州':(119.41,32.39,'2025.05'),'苏州':(120.58,31.30,'2020.08'),'南京':(118.78,32.04,'2024.06'),'连云港':(119.22,34.60,'2023.05'),
 '深圳':(114.06,22.55,'2025.01'),'广州':(113.26,23.13,'2023.03'),'潮州':(116.63,23.66,'2025.01'),'汕头':(116.68,23.35,'2025.01'),
 '澳门':(113.55,22.20,'2025.01'),'香港':(114.17,22.32,'2025.01'),'烟台':(121.39,37.52,'2024.08'),'上海':(121.47,31.23,'2023.05'),
 '宁波':(121.55,29.87,'2023.07'),'嘉兴':(120.76,30.75,'2023.11'),'湖州':(120.09,30.89,'2022.11'),'武汉':(114.30,30.59,'2021.04'),
 '信阳':(114.09,32.13,'2021.04'),'哈密':(93.51,42.83,'2023.02'),'吐鲁番':(89.18,42.95,'2026.04'),'乌鲁木齐':(87.62,43.82,'2026.04'),
 '邯郸':(114.49,36.61,'2023.03'),'厦门':(118.09,24.48,'2023.03'),'太原':(112.55,37.87,'2026.08'),'五台山':(113.59,38.99,'2026.08'),
 '杭州':(120.15,30.27,'2022.11'),'安吉':(119.68,30.64,'2022.11'),'昌吉':(87.31,44.02,'2026.05'),'青岛':(120.38,36.07,'2026.07'),
 '长沙':(112.94,28.23,'2026.10'),'张家界':(110.48,29.12,'2026.10'),'湘西':(109.73,28.32,'2026.10')
}

prefs = []
for adcode, short in ADCODE.items():
    j = results[adcode]
    if not j:
        # 回退：现有省级多边形作为单个 pref(台湾等地级缺失)
        if short in prov_fallback:
            prefs.append({'prov': short, 'name': short, 'd': prov_fallback[short], 'v': 0})
        continue
    for feat in j['features']:
        props = feat.get('properties', {})
        nm = props.get('name', '')
        g = feat.get('geometry') or {}
        if g.get('type') == 'Polygon':
            polys = [g['coordinates']]
        elif g.get('type') == 'MultiPolygon':
            polys = g['coordinates']
        else:
            continue
        rings = []
        paths = []
        total = 0.0
        skip_feat = False
        for poly in polys:
            ring = [tuple(pt[:2]) for pt in poly[0]]
            a = area_deg(ring)
            total += a
            if any(k in nm for k in NANHAI_KEYS):
                skip_feat = True
                break
            if a < 0.04:
                continue
            rings.append(ring)
            paths.append(to_path(ring))
        if skip_feat or not paths:
            continue
        prefs.append({'prov': short, 'name': nm, 'd': ''.join(paths), 'rings': rings})

# 点-面包含判定：坐标落在哪个地级市轮廓内,则该市标记为到访(v=1)
def _pip(pt, rings):
    x, y = pt
    for ring in rings:
        inside = False
        n = len(ring)
        for i in range(n):
            x1, y1 = ring[i]; x2, y2 = ring[(i+1) % n]
            if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        if inside:
            return True
    return False

for pf in prefs:
    pf['v'] = 0
    for name, (lo, la, dt) in FOOT.items():
        if _pip((lo, la), pf.get('rings', [])):
            pf['v'] = 1
            pf['fc'] = name
            pf['fd'] = dt
            break
    pf.pop('rings', None)

# 兜底：任一省份若完全无地级 polygon（如香港/澳门抓取失败），用省级多边形补一个
present = set(p['prov'] for p in prefs)
for adcode, short in ADCODE.items():
    if short not in present and short in prov_fallback:
        prefs.append({'prov': short, 'name': short, 'd': prov_fallback[short], 'v': 0})

# 省级行政区轮廓(金色描边用)
provinces = []
for p in md['provinces']:
    provinces.append({'name': FULL2SHORT.get(p['name'], p['name']), 'd': p['d']})

# 省标签
plabels = []
for short, (lx, ly) in label_lookup.items():
    plabels.append({'name': short, 'lx': lx, 'ly': ly})

out = {
 'w': md['w'], 'h': md['h'],
 'proj': proj,
 'plabels': plabels,
 'prefs': prefs,
 'provinces': provinces,
 'nanhai': md['nanhai']
}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
import os
n_v = sum(1 for pf in prefs if pf['v'])
print('prefs total', len(prefs), '| visited prefs (green)', n_v)
print('OUT KB', round(os.path.getsize(OUT)/1024, 1))
