#!/usr/bin/env python3
"""Normalise raw mess-API menus and inject them into index.html.

The IIIT mess API (`mess_get_menus`, one call per Sunday-anchored week) returns
one blob per mess with messy, time-varying category labels: emoji-prefixed on
some messes ("\U0001f963 Cereals"), misspelt on others ("Accompainment"), and
reworded week to week ("Veg Wet Curry" vs "Veg Wet"). The site stores a compact,
normalised form instead:

    WEEKS[effective_from][mess][day][meal] = [{"c": category, "n": name}, ...]

This script maps every known API category onto the site's fixed vocabulary,
drops empty-named rows, trims dish names (keeping internal spacing, which the
site preserves), and writes the result into the <script id="menuData"> block.

Usage:
    python tools/build_menu.py index.html week1.json week2.json ...

Each weekN.json is the raw API response saved verbatim, i.e. {"result": [ ... ]}
(a bare [ ... ] list is also accepted). Each week it contains replaces that same
effective_from in index.html; other weeks are left untouched. Re-running with the
same input is a no-op.
"""
import json
import re
import sys
import unicodedata

# Base category label (leading emoji/symbols stripped, lower-cased, whitespace
# collapsed) -> the site's canonical category. Derived empirically by aligning
# raw API items against the already-normalised site data, dish name by dish name.
CATMAP = {
    'accompaniment': 'Accompaniment', 'accompainment': 'Accompaniment',
    'accoumpaniants': 'Accompaniment', 'additional accompaniment': 'Accompaniment',
    'chutney 2 / accompaniement': 'Accompaniment',
    'cereals': 'Breakfast Sides', 'dry fuits': 'Breakfast Sides',
    'dry fruits': 'Breakfast Sides', 'mandatory': 'Breakfast Sides',
    'bread butter & jam': 'Breakfast Sides', 'bread, butter & jam': 'Breakfast Sides',
    'bread butter jam': 'Breakfast Sides', 'bread, butter, jam': 'Breakfast Sides',
    'chutney 1': 'Pickle/Fresh Chutney', 'chutney 2': 'Pickle/Fresh Chutney',
    'pickle/fresh chutney': 'Pickle/Fresh Chutney',
    'curd/raitha': 'Curd/Raitha', 'curd/raitha/milk': 'Curd/Raitha',
    'dairy 1': 'Dairy 1', 'dairy 2': 'Dairy 2',
    'dal': 'Dal',
    'dessert': 'Dessert', 'dessert/spl': 'Dessert', 'sweet': 'Dessert',
    'sweets': 'Dessert',
    'dish 1': 'Dish 1', 'dish 2': 'Dish 2',
    'flavoured rice': 'Flavoured Rice', 'steamed rice': 'Steamed Rice',
    'plain rice': 'Plain Rice',
    'fruit': 'Fruit', 'fruit/ juice': 'Fruit', 'fruit/juice': 'Fruit',
    'fryums/papad': 'Fryums/Papad', 'papad/fryums': 'Fryums/Papad',
    'papad / fryums': 'Fryums/Papad', 'papad': 'Fryums/Papad',
    'khichdi': 'Khichdi',
    'lentil': 'Rasam/Sambar', 'lentil soup': 'Rasam/Sambar',
    'rasam/sambar': 'Rasam/Sambar', 'rasam/sambar/khichdi': 'Rasam/Sambar',
    'soups': 'Rasam/Sambar',

    'non veg dish': 'Non-Veg', 'non veg': 'Non-Veg', 'non-veg': 'Non-Veg',
    'non veg curry': 'Non-Veg',
    'phulka/chapathi': 'Phulka/Chapathi', 'phulka/chapati': 'Phulka/Chapathi',
    'protein': 'Protein', 'sprouts': 'Protein',
    'salad': 'Salad', 'snack item': 'Snack Item',
    'veg dry': 'Veg Dry', 'veg dry curry': 'Veg Dry',
    'veg wet': 'Veg Wet', 'veg wet curry': 'Veg Wet',
}


def strip_lead(s):
    """Drop leading emoji/symbol/space characters, up to the first letter/digit."""
    for i, ch in enumerate(s):
        if unicodedata.category(ch)[0] in ('L', 'N'):
            return s[i:]
    return ''


def norm_cat(raw):
    if not raw:
        return 'Other'
    key = re.sub(r'\s+', ' ', strip_lead(raw)).strip().lower()
    if not key:
        return 'Other'
    mapped = CATMAP.get(key)
    if mapped is None:
        raise KeyError('Unmapped category %r (base %r) -- add it to CATMAP' % (raw, key))
    return mapped


def transform_week(api_result):
    """[{mess, days:{day:{meal:[{item,category}]}}}] -> {mess:{day:{meal:[{c,n}]}}}"""
    out = {}
    for m in api_result:
        days = {}
        for day, meals in m['days'].items():
            md = {}
            for meal, items in meals.items():
                arr = []
                for it in items:
                    # Names: drop the same leading emoji/symbol prefix the newer
                    # menus carry ("\U0001f957 Chapati"), then trim ends while
                    # keeping internal spacing (the site preserves e.g.
                    # 'Mealmaker  Masala'). This also drops placeholder rows
                    # like '-' that reduce to nothing.
                    n = strip_lead(it.get('item') or '').strip()
                    if not n:
                        continue
                    arr.append({'c': norm_cat(it.get('category')), 'n': n})
                if arr:
                    md[meal] = arr
            if md:
                days[day] = md
        out[m['mess']] = days
    return out


def load_api(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    return data['result'] if isinstance(data, dict) else data


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    index_path, week_paths = argv[1], argv[2:]

    with open(index_path, encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'(<script id="menuData"[^>]*>)(.*?)(</script>)', html, re.S)
    if not m:
        sys.exit('menuData script block not found in %s' % index_path)
    weeks = json.loads(m.group(2))

    changed = []
    for p in week_paths:
        api = load_api(p)
        if not api:
            print('skip %s: empty result' % p)
            continue
        eff = api[0]['effective_from']
        weeks[eff] = transform_week(api)
        changed.append(eff)

    payload = json.dumps(weeks, ensure_ascii=False, separators=(',', ':'))
    html = html[:m.start(2)] + payload + html[m.end(2):]
    with open(index_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)

    print('updated weeks: %s' % ', '.join(sorted(changed)))
    print('menuData now covers: %s' % ', '.join(sorted(weeks)))


if __name__ == '__main__':
    main(sys.argv)
