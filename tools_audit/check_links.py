# -*- coding: utf-8 -*-
"""Ведомость связей диаграмм ЛР2: что с чем соединяет каждая линия.

Для каждой диаграммы печатается таблица «блок A — блок B» по фактическим
координатам концов связей; связь, конец которой не лежит на рамке блока,
помечается как ВИСЯЧАЯ. Запуск:

    python3 tools_audit/check_links.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_lab2_uml as g  # noqa: E402

TOL = 1.2


def boxes_at(pt):
    """Имена блоков, на рамке которых лежит точка."""
    out = []
    for name, x0, y0, x1, y1 in g.GEOM['boxes']:
        x, y = pt
        if x0 - TOL <= x <= x1 + TOL and y0 - TOL <= y <= y1 + TOL:
            on_v = min(abs(x - x0), abs(x - x1)) <= TOL
            on_h = min(abs(y - y0), abs(y - y1)) <= TOL
            if on_v or on_h:
                out.append(name)
    return out


def labels_near(pt, radius=45):
    out = []
    for lb in g.GEOM['labels']:
        cx, cy = (lb[1] + lb[3]) / 2, (lb[2] + lb[4]) / 2
        if math.hypot(cx - pt[0], cy - pt[1]) <= radius:
            out.append(lb[0])
    return out


def dump(title, fn):
    fn()
    print('=== %s: %d связей, %d блоков' % (title, len(g.GEOM['polys']), len(g.GEOM['boxes'])))
    bad = 0
    for i, poly in enumerate(g.GEOM['polys'], 1):
        a, b = boxes_at(poly[0]), boxes_at(poly[-1])
        ends = g.GEOM['ends'][i - 1] if i <= len(g.GEOM['ends']) else (None, None)
        a_s = '/'.join(a) or '— ВИСЯЧИЙ КОНЕЦ —'
        b_s = '/'.join(b) or '— ВИСЯЧИЙ КОНЕЦ —'
        if not a or not b:
            bad += 1
        print('%2d. %-32s %-8s <-> %-32s %-8s' %
              (i, a_s, ends[0] or '', b_s, ends[1] or ''))
        print('     у начала: %s' % (', '.join(labels_near(poly[0])) or '—'))
        print('     у конца : %s' % (', '.join(labels_near(poly[-1])) or '—'))
    print('связей с висячим концом: %d\n' % bad)


if __name__ == '__main__':
    dump('компоненты', lambda: g.component_diagram('ru'))
    dump('развёртывание', lambda: g.deployment_diagram('ru'))
    dump('классы', lambda: g.class_diagram('ru'))
    dump('схема БД', g.db_schema_diagram)
