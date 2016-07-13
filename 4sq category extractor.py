import re
import urllib.request
from datetime import date

url = 'https://developer.foursquare.com/categorytree'

print(date.today())
out_file = 'categories-{}.csv'.format(date.today())

_parent = {}
for i in range(0,5):
    _parent[i] = ''
_prev_level = -1
_level = -1
_id = ''
_name = ''

catch_level = False
catch_id = False
catch_name = False

arr = []

with urllib.request.urlopen(url) as f:
    for line in f:
        line = line.decode('UTF-8')
        if '<ul' in str(line):
            _prev_level = _level
            _level = _level + 1
        elif '</ul>' in str(line):
            _prev_level = _level
            _level = _level - 1
        if catch_name == True:
            clean = str(line).strip()
            clean = clean.replace('&amp;', 'and')
            _name = clean
            catch_name = False
            continue
        if '<div class="name">' in str(line):
            catch_name = True
        if '<tt>' in str(line):
            if _level > _prev_level:
                _parent[_level] = _id
            clean = str(line).strip()
            clean = re.sub('( |\t|\n|\r|<tt>|</tt>)+', '', clean)
            _id = clean
            output = '{0},{1},{2},{3}\n'.format(_id, _name, _parent[_level], _level)
            # print(output)
            arr.append(output)

with open(out_file, 'w') as fw:
    for s in arr:
        fw.write(s)