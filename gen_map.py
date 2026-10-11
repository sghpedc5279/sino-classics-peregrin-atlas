# -*- coding: utf-8 -*-
"""从已有足迹图 HTML 中提取中国 GeoJSON，生成简化 SVG 路径数据"""
import json, math

SRC = r'C:/Users/sghpe/Desktop/BaiduSyncdisk/2026培训/社会培训足迹图.html'
OUT = r'C:/Users/sghpe/WorkBuddy/2026-09-29-07-49-59/mapdata.json'

src = open(SRC, encoding='utf-8').read()
i = src.index('const CHINA_GEO =')
j = src.index('{', i)
depth = 0
for k in range(j, len(src)):
    if src[k] == '{':
        depth += 1
    elif src[k] == '}':
        depth -= 1
        if depth == 0:
            end = k + 1
            break
data = json.loads(src[j:end])
features = data['features']

LAT0, LON0 = 35.0, 104.0
KX = math.cos(math.radians(LAT0))


def proj(lon, lat):
    return ((lon - LON0) * KX, -(lat - LAT0))


def area_deg(ring):
    s = 0.0
    for a in range(len(ring) - 1):
        x1, y1 = ring[a]
        x2, y2 = ring[a + 1]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def dp(pts, tol):
    """Douglas-Peucker"""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        s, e = stack.pop()
        if e - s < 2:
            continue
        x1, y1 = pts[s]
        x2, y2 = pts[e]
        dx, dy = x2 - x1, y2 - y1
        d2 = dx * dx + dy * dy
        best, bi = -1.0, -1
        for m in range(s + 1, e):
            px, py = pts[m]
            if d2 == 0:
                dist = math.hypot(px - x1, py - y1)
            else:
                t = ((px - x1) * dx + (py - y1) * dy) / d2
                t = max(0.0, min(1.0, t))
                dist = math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
            if dist > best:
                best, bi = dist, m
        if best > tol:
            keep[bi] = True
            stack.append((s, bi))
            stack.append((bi, e))
    return [p for p, k in zip(pts, keep) if k]


# ---------- 主图：收集各省份多边形（过滤掉离岛） ----------
main_polys = {}      # name -> list of ring(proj coords)
labels = {}          # name -> (lon, lat)
nanhai_islands = []  # 南海小岛
jd_lines = []        # 九段线

for f in features:
    name = f['properties'].get('name', '')
    geom = f['geometry']
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    if not name:  # 九段线
        for poly in polys:
            ring = [tuple(p[:2]) for p in poly[0]]
            jd_lines.append(ring)
        continue
    props = f['properties']
    lab = props.get('centroid') or props.get('center')
    labels[name] = tuple(lab[:2])
    kept = []
    for poly in polys:
        ring = [tuple(p[:2]) for p in poly[0]]
        a = area_deg(ring)
        lons = [p[0] for p in ring]
        lats = [p[1] for p in ring]
        in_nanhai = min(lons) > 104.0 and (min(lats) < 18.0 or
                                           (max(lats) < 21.6 and min(lons) > 113.0))
        if in_nanhai:
            nanhai_islands.append(ring)
            continue
        is_mini = name.startswith(('香港', '澳门'))
        if a < 0.015 and not is_mini:
            continue
        kept.append(ring)
    main_polys[name] = kept

TOL = 0.09

# ---------- 计算主图 bbox ----------
allpts = []
for name, rings in main_polys.items():
    for r in rings:
        allpts.extend(proj(*p) for p in r)
xs = [p[0] for p in allpts]
ys = [p[1] for p in allpts]
XMIN, XMAX = min(xs), max(xs)
YMIN, YMAX = min(ys), max(ys)

W, H, PAD = 1000.0, 760.0, 12.0
S = min((W - 2 * PAD) / (XMAX - XMIN), (H - 2 * PAD) / (YMAX - YMIN))
OX = PAD + ((W - 2 * PAD) - (XMAX - XMIN) * S) / 2.0
OY = PAD + ((H - 2 * PAD) - (YMAX - YMIN) * S) / 2.0


def to_svg(ring):
    a = area_deg(ring)
    tol = TOL if a > 0.8 else (TOL * 0.4 if a > 0.15 else TOL * 0.15)
    pts = [proj(*p) for p in ring]
    pts = dp(pts, tol)
    seg = []
    for idx, (x, y) in enumerate(pts):
        sx = (x - XMIN) * S + OX
        sy = (y - YMIN) * S + OY
        seg.append(('M' if idx == 0 else 'L') + f'{sx:.1f} {sy:.1f}')
    return ' '.join(seg) + ' Z'


provinces = []
for name in main_polys:
    d = ' '.join(to_svg(r) for r in main_polys[name])
    lon, lat = labels[name]
    x, y = proj(lon, lat)
    provinces.append({
        'name': name,
        'd': d,
        'lx': round((x - XMIN) * S + OX, 1),
        'ly': round((y - YMIN) * S + OY, 1),
    })

# ---------- 南海诸岛插图 ----------
NX0, NX1 = 104.5, 124.0
NY0, NY1 = 2.0, 24.5
BW, BH, BP = 108.0, 168.0, 8.0


def nproj(lon, lat):
    return ((lon - NX0) / (NX1 - NX0), (NY1 - lat) / (NY1 - NY0))


def npath(ring):
    pts = [nproj(*p) for p in dp(ring, 0.004)]
    seg = []
    for idx, (fx, fy) in enumerate(pts):
        sx = BP + fx * (BW - 2 * BP)
        sy = BP + fy * (BH - 2 * BP)
        seg.append(('M' if idx == 0 else 'L') + f'{sx:.1f} {sy:.1f}')
    return ' '.join(seg) + (' Z' if len(pts) > 3 else '')


nanhai_islands = [r for r in nanhai_islands if area_deg(r) > 0.0015]
nanhai = {
    'w': BW, 'h': BH,
    'islands': [npath(r) for r in nanhai_islands],
    'lines': [npath(r) for r in jd_lines],
}

out = {'w': W, 'h': H, 'provinces': provinces, 'nanhai': nanhai,
       'proj': {'lat0': LAT0, 'lon0': LON0, 'kx': KX, 'xmin': XMIN, 'ymin': YMIN,
                's': S, 'ox': OX, 'oy': OY}}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

import os
print('provinces', len(provinces))
print('size KB', round(os.path.getsize(OUT) / 1024, 1))
print('viewBox', W, H, 'scale', round(S, 2))
print('nanhai islands', len(nanhai['islands']), 'lines', len(nanhai['lines']))
for p in provinces:
    print(p['name'], len(p['d']), p['lx'], p['ly'])
