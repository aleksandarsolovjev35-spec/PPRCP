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
    # контейнеры (узлы развёртывания, среды исполнения) могут содержать линии
    containers = set(g.GEOM.get('containers', ()))
    leaves = [b for b in g.GEOM['boxes'] if b[0] not in containers]
    for poly in g.GEOM['polys']:
        for p, q in zip(poly, poly[1:]):
            for box in leaves:
                if seg_hits_box(p, q, box):
                    bad_seg.append((p, q, box[0]))
    for lb in g.GEOM['labels']:
        for box in leaves:
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
    def _d(lb):
        t, x0, y0, x1, y1, ex, ey = lb[:7]
        dx = max(x0 - ex, 0, ex - x1)
        dy = max(y0 - ey, 0, ey - y1)
        return (dx * dx + dy * dy) ** 0.5
    far = [(lb[0], round(_d(lb))) for lb in g.GEOM.get('mults', [])
           if _d(lb) > (30 if lb[7] else 14)]
    print('%s: блоков %d, линий внутрь блоков — %d, подписей внутрь блоков — %d, '
          'концов не на рамке блока — %d, подписей вплотную к рамке — %d, '
          'кратностей далеко от своего конца — %d'
          % (title, len(g.GEOM['boxes']), len(bad_seg), len(bad_lab), len(free_end), len(flush),
             len(far)))
    for t, d in far:
        print('    кратность "%s" в %d px от конца связи' % (t, d))
    for p, q, n in bad_seg:
        print('    %s→%s пересекает %s' % (p, q, n))
    for t, n in bad_lab:
        print('    подпись "%s" внутри %s' % (t, n))
    for tag, pt in free_end:
        print('    %s связи %s не лежит на рамке блока' % (tag, pt))


EXPECT = {'zero-one': '0..1', 'zero-many': '0..*'}


def report_ends(title, fn):
    """Соответствие символа на конце связи (ER) подписи кратности у этого конца."""
    import math
    fn()
    bad = []
    for i, poly in enumerate(g.GEOM['polys']):
        kinds = g.GEOM['ends'][i] if i < len(g.GEOM['ends']) else (None, None)
        for k, (kind, pt) in enumerate(zip(kinds, (poly[0], poly[-1]))):
            if kind not in EXPECT:
                continue
            want = EXPECT[kind]
            labels = [lb[0] for lb in g.GEOM['labels']
                      if math.hypot((lb[1] + lb[3]) / 2 - pt[0], (lb[2] + lb[4]) / 2 - pt[1]) <= 40]
            if want not in labels:
                bad.append((i + 1, 'начало' if k == 0 else 'конец', kind, want, labels))
    print('%s: символов конца без своей кратности — %d' % (title, len(bad)))
    for b in bad:
        print('    связь %d, %s: символ %s ждёт «%s», рядом %s' % b)


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


def report_sequence():
    """Последовательность: подписи не должны ложиться на полосы активности
    и на чужие линии жизни (это и есть «наезды» на блоки)."""
    g.sequence_diagram()
    labs, bars, xs = g.GEOM['labels'], g.GEOM['bars'], g.GEOM['lifelines']
    on_bar = [t for (t, x0, y0, x1, y1) in labs for (bx, by0, by1) in bars
              if x1 > bx - 7 and x0 < bx + 7 and y1 > by0 and y0 < by1]
    on_life = [t for (t, x0, y0, x1, y1) in labs for x in xs if x0 < x < x1]
    in_head = [t for (t, x0, y0, x1, y1) in labs for b in g.GEOM['boxes']
               if x1 > b[1] and x0 < b[3] and y1 > b[2] and y0 < b[4]]
    sq = g.SEQ
    thru = []
    for it in sq.items:
        if it[0] != 'msg':
            continue
        _, a, b, _k, y, text = it
        la, ra = sq._bar_edge(a, y)
        lb, rb = sq._bar_edge(b, y)
        x1, x2 = (ra, lb) if sq.xs[b] > sq.xs[a] else (la, rb)
        lo, hi = min(x1, x2), max(x1, x2)
        for (bi, by0, by1, level) in sq.acts:
            bx = sq.xs[bi] + level * 7
            if by0 <= y <= by0 + max(20, by1 - by0) and lo < bx - 7 and hi > bx + 7:
                thru.append(text[:40])
    print('последовательность: подписей %d, на полосах активности — %d, '
          'поверх линий жизни — %d, в заголовках — %d, сквозь полосы активности — %d'
          % (len(labs), len(on_bar), len(on_life), len(in_head), len(thru)))
    for t in (on_bar + on_life + in_head)[:6]:
        print('   !', t[:70])


if __name__ == '__main__':
    report('компоненты', lambda: g.component_diagram('ru'))
    report('развёртывание', lambda: g.deployment_diagram('ru'))
    report('классы', lambda: g.class_diagram('ru'))
    report('схема БД', g.db_schema_diagram)
    report_ends('схема БД', g.db_schema_diagram)
    print()
    for title, fn in (('компоненты', lambda: g.component_diagram('ru')),
                      ('развёртывание', lambda: g.deployment_diagram('ru')),
                      ('классы', lambda: g.class_diagram('ru')),
                      ('схема БД', g.db_schema_diagram)):
        report_crossings(title, fn)
    print()
    report_sequence()
