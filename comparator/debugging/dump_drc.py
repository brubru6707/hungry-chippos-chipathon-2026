#!/usr/bin/env python3
"""Dump DRC violation markers (rule, coordinates) from KLayout .lyrdb files."""
import sys, glob
import klayout.rdb as rdb

run_dir = sys.argv[1] if len(sys.argv) > 1 else '/foss/designs/comparator/layout/klayout_drc_run'
total = 0
for path in sorted(glob.glob(run_dir + '/*.lyrdb')):
    db = rdb.ReportDatabase('drc')
    db.load(path)
    items = list(db.each_item())
    if not items:
        continue
    print(f"\n=== {path.split('/')[-1]} ({len(items)} items) ===")
    for item in items:
        cat = db.category_by_id(item.category_id())
        for v in item.each_value():
            print(f"  {cat.path()}: {v.to_s()}")
        total += 1
print(f"\nTOTAL: {total}")
