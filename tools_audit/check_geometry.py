# -*- coding: utf-8 -*-
"""Автопроверка геометрии диаграмм ЛР2: линии не должны заходить внутрь блоков,
подписи не должны попадать внутрь блоков."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_lab2_uml as g


def seg_hits_box(p, q, box, inset=3.0):
    name, x0, y0, x1, y1 = box
    x0, y0, x1, y1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    if x0 >= x1 or y0 >= y1:
        return False
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if abs(pk) < 1e-9:
            if qk < 0:
                return False
        else:
            t = qk / pk
            if pk < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return t1 > t0


def rect_in_box(r, box, inset=1.0):
    _, x0, y0, x1, y1 = box
    return (r[3] > x0 + inset and r[1] < x1 - inset and
            r[4] > y0 + inset and r[2] < y1 - inset)


def on_border(pt, box, tol=2.5):
    """Точка лежит на рамке блока (с допуском tol)."""
    _, x0, y0, x1, y1 = box
    x, y = pt
    if not (x0 - tol <= x <= x1 + tol and y0 - tol <= y <= y1 + tol):
        return False
    return (min(abs(x - x0), abs(x - x1)) <= tol) or (min(abs(y - y0), abs(y - y1)) <= tol)


def report(title, fn):
    fn()
    bad_seg, bad_lab, free_end = [], [], []
    for poly in g.GEOM['polys']:
        for p, q in zip(poly, poly[1:]):
            for box in g.GEOM['boxes']:
                if seg_hits_box(p, q, box):
                    bad_seg.append((p, q, box[0]))
    for lb in g.GEOM['labels']:
        for box in g.GEOM['boxes']:
            if rect_in_box(lb, box):
                bad_lab.append((lb[0], box[0]))
    for poly in g.GEOM['polys']:
        for tag, pt in (('начало', poly[0]), ('конец', poly[-1])):
            if not any(on_border(pt, b) for b in g.GEOM['boxes']):
                free_end.append((tag, tuple(round(v, 1) for v in pt)))
    flush = []
    for lb in g.GEOM['labels']:
        for b in g.GEOM['boxes']:
            dx = max(b[1] - lb[3], lb[1] - b[3])
            dy = max(b[2] - lb[4], lb[2] - b[4])
            if -0.5 < dx < 2 and -0.5 < dy < 2:
                flush.append((lb[0], b[0]))
    print('%s: блоков %d, линий внутрь блоков — %d, подписей внутрь блоков — %d, '
          'концов не на рамке блока — %d, подписей вплотную к рамке — %d'
          % (title, len(g.GEOM['boxes']), len(bad_seg), len(bad_lab), len(free_end), len(flush)))
    for p, q, n in bad_seg:
        print('    %s→%s пересекает %s' % (p, q, n))
    for t, n in bad_lab:
        print('    подпись "%s" внутри %s' % (t, n))
    for tag, pt in free_end:
        print('    %s связи %s не лежит на рамке блока' % (tag, pt))


def report_crossings(title, fn):
    """Пересечения связей между собой (в плотной сетке полностью не устранимы)."""
    fn()
    segs = [(p, q) for poly in g.GEOM['polys'] for p, q in zip(poly, poly[1:])]
    n = 0
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            p, q = segs[i]
            r, s = segs[j]
            vert = hor = None
            if abs(p[0] - q[0]) < 1e-6 and abs(r[1] - s[1]) < 1e-6:
                vert, hor = (p, q), (r, s)
            elif abs(r[0] - s[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6:
                vert, hor = (r, s), (p, q)
            if not vert:
                continue
            x, y = vert[0][0], hor[0][1]
            if (min(vert[0][1], vert[1][1]) < y < max(vert[0][1], vert[1][1]) and
                    min(hor[0][0], hor[1][0]) < x < max(hor[0][0], hor[1][0])):
                n += 1
    print('%s: пересечений связей между собой — %d' % (title, n))


if __name__ == '__main__':
    report('компоненты', lambda: g.component_diagram('ru'))
    report('развёртывание', lambda: g.deployment_diagram('ru'))
    report('классы', lambda: g.class_diagram('ru'))
    report('схема БД', g.db_schema_diagram)
    print()
    for title, fn in (('компоненты', lambda: g.component_diagram('ru')),
                      ('развёртывание', lambda: g.deployment_diagram('ru')),
                      ('классы', lambda: g.class_diagram('ru')),
                      ('схема БД', g.db_schema_diagram)):
        report_crossings(title, fn)
