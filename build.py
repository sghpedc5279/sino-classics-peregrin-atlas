# -*- coding: utf-8 -*-
"""Inject mapdata2.json into template.html's /*__MAPDATA__*/null placeholder."""
import json, os

TPL = 'template.html'
DATA = 'mapdata4.json'
OUT = '江山万里行-通关文牍.html'

tpl = open(TPL, encoding='utf-8').read()
raw = open(DATA, encoding='utf-8').read().strip()
assert '/*__MAPDATA__*/null' in tpl, '占位符缺失'
# 基本安全：避免 JSON 中意外出现 </script>
assert '</script' not in raw, 'JSON 含 </script，需转义'
out = tpl.replace('/*__MAPDATA__*/null', '/*__MAPDATA__*/' + raw)
open(OUT, 'w', encoding='utf-8').write(out)
print('written', os.path.getsize(OUT)//1024, 'KB ->', OUT)
