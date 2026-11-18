"""Проверить нотацию и разметку рисунка ЛР1, не перезаписывая PNG."""
from itertools import combinations
from math import dist
from pathlib import Path
import re
import sys

from check_geometry import seg_hits_box
from gen_use_case import ACTORS, CASES, LINKS, SYSTEM, W, H, RX, RY, Link, render


def contains(outer, inner):
    return outer[0] <= inner[0] <= inner[2] <= outer[2] and outer[1] <= inner[1] <= inner[3] <= outer[3]


def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def radius2(case, p, pad=0):
    return ((p[0] - case.x) / (RX + pad)) ** 2 + ((p[1] - case.y) / (RY + pad)) ** 2


def enters(p, q, case, pad):
    # В нормированных координатах эллипс — единичная окружность. Проверяем
    # ближайшую к центру точку всего отрезка (не только его концы).
    x, y = (p[0] - case.x) / (RX + pad), (p[1] - case.y) / (RY + pad)
    dx, dy = (q[0] - p[0]) / (RX + pad), (q[1] - p[1]) / (RY + pad)
    t = max(0, min(1, -(x * dx + y * dy) / (dx * dx + dy * dy)))
    return (x + t * dx) ** 2 + (y + t * dy) ** 2 < 1 - 1e-7


def intersect(p, q, r, s):
    """Пересечение/наложение отрезков, кроме единственного общего конца."""
    def side(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    a, b, c, d = side(p, q, r), side(p, q, s), side(r, s, p), side(r, s, q)
    if max(abs(a), abs(b), abs(c), abs(d)) < 1e-7:
        axis = int(abs(q[1] - p[1]) > abs(q[0] - p[0]))
        a0, a1 = sorted((p[axis], q[axis]))
        b0, b1 = sorted((r[axis], s[axis]))
        return min(a1, b1) - max(a0, b0) > 1e-7
    return not ({p, q} & {r, s}) and a * b <= 0 and c * d <= 0


def model_errors():
    report = Path(__file__).resolve().parents[1] / 'reports/lab1/LR1_Report_Variant15.md'
    roles = set(re.findall(r'^\|[^\n|]+\| `([A-Z_]+)` \|', report.read_text(encoding='utf-8'), re.M))
    if set(ACTORS) != roles:
        yield f'Роли не совпадают с таблицей ЛР1: {set(ACTORS) ^ roles}'
    if set(CASES) != set(range(1, 18)):
        yield 'Ожидались UC-1…UC-17.'
    seen = set()
    for link in LINKS:
        a, b, kind = link.source, link.target, link.kind
        if (a, b) in seen or a == b:
            yield f'Дубликат или петля: {link}'
        seen.add((a, b))
        if kind == 'association':
            valid = a in ACTORS and b in CASES
        else:
            valid = (kind in ('include', 'extend') and a in CASES and b in CASES
                     and link.label_at is not None)
        if not valid:
            yield f'Недопустимый тип, концы или обозначение связи: {link}'
    if (set(ACTORS) | set(CASES)) - {n for pair in seen for n in pair}:
        yield 'Есть изолированный актор или прецедент.'
    if {(e.source, e.target, e.kind) for e in LINKS if e.kind != 'association'} != {
            (4, 5, 'include'), (6, 4, 'extend')}:
        yield 'Экспертиза включает контроль экзаменов; замечания расширяют экспертизу, не наоборот.'
    signers = {e.source for e in LINKS if e.target == 7 and e.kind == 'association'}
    if signers != {'HEAD_RELEASING', 'HEAD_ANOK', 'VICE_RECTOR', 'RECTOR'}:
        yield 'У UC-7 должны быть четыре подписанта маршрута.'


def geometry_errors():
    _, labels, routes = render()
    sheet = (0, 0, W, H)
    for n, uc in CASES.items():
        if not contains(SYSTEM, (uc.x - RX, uc.y - RY, uc.x + RX, uc.y + RY)):
            yield f'UC-{n} не внутри системы.'
    for (n, a), (m, b) in combinations(CASES.items(), 2):
        if radius2(a, (b.x, b.y)) <= 4:
            yield f'Наложение UC-{n} и UC-{m}.'
    actors = {role: (a.x - 16, a.y - 23, a.x + 16, a.y + 27) for role, a in ACTORS.items()}
    for role, box in actors.items():
        if overlap(box, SYSTEM) or not contains(sheet, box):
            yield f'Актор {role} не снаружи рамки или обрезан.'
    for (name, a), (other, b) in combinations(actors.items(), 2):
        if overlap(a, b):
            yield f'Наложение акторов {name} и {other}.'
    for owner, text, box in labels:
        if (owner == 'subject' or isinstance(owner, Link)) and not contains(SYSTEM, box):
            yield f'Подпись «{text}» вне системы.'
        if not contains(sheet, box) or (owner in ACTORS and overlap(SYSTEM, box)):
            yield f'Подпись «{text}» за полем или не с той стороны рамки.'
        if any(overlap(box, actor) for actor in actors.values()):
            yield f'Подпись «{text}» пересекает фигурку актора.'
        for n, uc in CASES.items():
            if n == owner:
                if any(radius2(uc, (x, y), -4) >= 1 for x in box[::2] for y in box[1::2]):
                    yield f'Подпись «{text}» не помещается в UC-{n}.'
            else:
                closest = (max(box[0], min(uc.x, box[2])), max(box[1], min(uc.y, box[3])))
                if radius2(uc, closest, 2) <= 1:
                    yield f'Подпись «{text}» на чужом эллипсе UC-{n}.'
    for (_, text, a), (_, other, b) in combinations(labels, 2):
        if overlap(a, b):
            yield f'Наложение подписей «{text}» и «{other}».'

    obstacles = [(text, *box) for _, text, box in labels]
    obstacles.extend((role, *box) for role, box in actors.items())
    segments = []
    for edge, pts in routes:
        tag = f'{edge.source} — UC-{edge.target}'
        if abs(radius2(CASES[edge.target], pts[-1]) - 1) > 1e-6:
            yield f'{tag}: конец не на эллипсе назначения.'
        if edge.source in ACTORS:
            a = ACTORS[edge.source]
            if pts[0] not in ((a.x - 16, a.y), (a.x + 16, a.y)):
                yield f'{tag}: начало не на фигурке актора.'
        elif abs(radius2(CASES[edge.source], pts[0]) - 1) > 1e-6:
            yield f'{tag}: начало не на исходном эллипсе.'
        for p, q in zip(pts, pts[1:]):
            if dist(p, q) < 1:
                yield f'{tag}: вырожденный отрезок.'
                continue
            for n, uc in CASES.items():
                if enters(p, q, uc, 0 if n in (edge.source, edge.target) else 6):
                    yield f'{tag}: линия заходит в UC-{n}.'
            for obstacle in obstacles:
                if seg_hits_box(p, q, obstacle, inset=0):
                    yield f'{tag}: линия на элементе «{obstacle[0]}».'
            for r, s, other in segments:
                if intersect(p, q, r, s):
                    yield f'Пересечение линий «{tag}» и «{other}».'
            segments.append((p, q, tag))


def main():
    errors = list(model_errors()) or list(geometry_errors())
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'ЛР1: акторов — {len(ACTORS)}, прецедентов — {len(CASES)}, связей — {len(LINKS)}. '
          'Семантика и геометрия: нарушений нет.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
