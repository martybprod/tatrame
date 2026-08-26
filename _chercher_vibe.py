import re
txt = open('/Users/martinboucher/Documents/PROJETS_IA/PROJECTS_INDEX.md', encoding='utf-8').read()
for m in re.finditer(r'.{0,100}[Vv]ibe.{0,140}', txt):
    s = m.group(0).replace('\n', ' ')
    print('...', s[:240])
    print('---')
