"""ЛР7, слайд 8: проверить граф, прохождение сценариев и разметку без записи PNG."""
from collections import Counter, defaultdict
from itertools import combinations, pairwise, product
from math import dist, hypot
from pathlib import Path
import re
import sys

from gen_activity import DIVIDER, FLOWS, H, LEFT, NODES, NOTES, PHASES, RIGHT, SIGNERS, W, Flow, render

# Полные пары взаимоисключающих условий для трёх решений; порядок: истина / ложь.
GUARDS = {
    'loaded': ('[план загружен]', '[ошибка загрузки]'),
    'valid': ('[нарушений нет]', '[есть нарушения]'),
    'more': ('[остались этапы]', '[все этапы подписаны]'),
}
# В этом процессе нет ни параллельных ветвей, ни неявных fork/join в действиях.
DEGREES = {'initial': (0, 1), 'action': (1, 1), 'decision': (1, 2), 'merge': (2, 1), 'final': (1, 0)}
NORMAL = {'N': (0, -1), 'E': (1, 0), 'S': (0, 1), 'W': (-1, 0)}


def model_errors():
    if {k for k, n in NODES.items() if n.kind == 'initial'} != {'start'}:
        yield 'Нужен один начальный узел.'
    if {k for k, n in NODES.items() if n.kind == 'decision'} != GUARDS.keys():
        yield 'Ожидались решения о загрузке, результате экспертизы и продолжении визирования.'
    counts = Counter((e.source, e.target) for e in FLOWS)
    if any(a == b or n > 1 for (a, b), n in counts.items()):
        yield 'Дублированный поток или петля узла на себя.'
    for e in FLOWS:
        if e.source not in NODES or e.target not in NODES:
            yield f'Поток без узла на конце: {e}'
        if len(e.ports) != 2 or any(p not in NORMAL for p in e.ports):
            yield f'Неверные стороны присоединения: {e}'
        if bool(e.guard) != (e.label_at is not None):
            yield f'Условие и его надпись не согласованы: {e}'
    for k, n in NODES.items():
        incoming = sum(e.target == k for e in FLOWS)
        out = [e for e in FLOWS if e.source == k]
        if DEGREES.get(n.kind) != (incoming, len(out)):
            yield f'{k} ({n.kind}): входов {incoming}, выходов {len(out)}.'
        if n.phase not in PHASES or (n.kind == 'action') != bool(n.label.strip()):
            yield f'{k}: неверная секция или надпись узла.'
        if {e.guard for e in out} != set(GUARDS.get(k, ('',) if out else ())):
            yield f'{k}: отсутствующее, повторное или лишнее условие.'

    # Сверяем видимые названия и порядок именно с ЭЦП учебного плана, не служебной записки.
    seed = Path(__file__).resolve().parents[1] / 'portal/database/seed.sql'
    rows = re.findall(r"INSERT INTO `document_signatures` [^\n]*?VALUES\s*\(\d+,\s*'CURRICULUM',\s*1,\s*(\d+),\s*'([^']+)'",
                      seed.read_text(encoding='utf-8'))
    aliases = {'Руководитель выпускающего подразделения': 'Заведующий выпускающей кафедрой',
               'Ректор университета': 'Ректор'}
    if sorted((int(i), aliases.get(role, role)) for i, role in rows) != list(enumerate(SIGNERS, 1)):
        yield 'Подписанты или их порядок расходятся с document_signatures (учебный план № 1).'


def scenario_errors():
    """Проводим один маркер управления по нарисованным рёбрам до activity final."""
    out = defaultdict(dict)
    for e in FLOWS:
        out[e.source][e.guard] = e
    covered = set()
    for retries, passed in product((0, 2), (False, True)):
        k, actions = 'start', []
        for _ in range(len(FLOWS) * (len(SIGNERS) + retries + 1)):  # защита от ошибочного вечного цикла
            if NODES[k].kind == 'final':
                break
            if NODES[k].kind == 'action':
                actions.append(k)
            guard = ''
            if k in GUARDS:
                state = {'loaded': actions.count('load') > retries, 'valid': passed,
                         'more': actions.count('record') < len(SIGNERS) - 1}
                guard = GUARDS[k][0 if state[k] else 1]
            edge = out[k][guard]
            covered.add(edge)
            k = edge.target
        expected = ['open', 'load', 'error'] * retries + ['open', 'load', 'first', 'validate']
        if passed:
            expected += ['select', 'sign', 'record'] * (len(SIGNERS) - 1) + ['protocol', 'status', 'notify']
        else:
            expected += ['remarks', 'return']
        if actions != expected or k != ('approved_end' if passed else 'rework_end'):
            yield f'Неверный маршрут: ошибок загрузки {retries}, проверка пройдена: {passed}, остановка: {k}.'
    if covered != set(FLOWS):
        yield 'Не все потоки достижимы из начала и пройдены в сценариях.'


def bounds(p, q):
    return min(p[0], q[0]), min(p[1], q[1]), max(p[0], q[0]), max(p[1], q[1])


def inside(a, b, pad=0):
    return b[0] + pad <= a[0] <= a[2] <= b[2] - pad and b[1] + pad <= a[1] <= a[3] <= b[3] - pad


def gap(a, b):
    # Для ортогонального отрезка его bounding box — сам отрезок (толщина 0).
    return hypot(max(0, a[0] - b[2], b[0] - a[2]), max(0, a[1] - b[3], b[1] - a[3]))


def attached(node, side, tip, outside):
    dx, dy = NORMAL[side]
    return (tip == (node.x + dx * node.w / 2, node.y + dy * node.h / 2)
            and dx * (outside[0] - tip[0]) + dy * (outside[1] - tip[1]) > 0)


def geometry_errors():
    _, labels, routes = render()  # те же координаты, привязки и реальные габариты глифов, что в PNG
    boxes = {k: n.box for k, n in {**NODES, **NOTES}.items()}
    for k, box in boxes.items():
        phase = NODES[k if k in NODES else NOTES[k].target].phase
        top, bottom, _, _ = PHASES[phase]
        if not inside(box, (DIVIDER, top, RIGHT, bottom), 6):
            yield f'{k}: фигура не помещается в свою секцию.'
    for (k, a), (m, b) in combinations(boxes.items(), 2):
        if gap(a, b) < 8:
            yield f'{k} и {m}: наложение или зазор меньше 8.'

    if Counter((k, t) for k, t, _ in labels if k in NODES) != Counter(
            (k, line) for k, n in NODES.items() for line in n.label.splitlines()):
        yield 'Нарисованы не все названия действий.'
    if Counter(k for k, _ in routes) != Counter([*FLOWS, *NOTES]):
        yield 'Нарисованы не все потоки или привязки примечаний.'
    if Counter(k for k, _, _ in labels if isinstance(k, Flow)) != Counter(e for e in FLOWS if e.guard):
        yield 'Нарисованы не все условия переходов.'
    segments = []
    for route, points in routes:
        if isinstance(route, Flow):
            a, b = route.source, route.target
            if not (attached(NODES[a], route.ports[0], points[0], points[1]) and
                    attached(NODES[b], route.ports[1], points[-1], points[-2]) and dist(*points[-2:]) >= 12):
                yield f'{a} → {b}: конец не на контуре или наконечник направлен не в узел.'
        else:
            a, b = route, NOTES[route].target
            for k, (x, y) in ((a, points[0]), (b, points[-1])):
                l, t, r, bot = boxes[k]
                if not (l + 12 <= x <= r - 12 and y in (t, bot)):
                    yield f'{a}: привязка примечания не на границе {k}.'
        for i, (p, q) in enumerate(pairwise(points)):
            seg = bounds(p, q)
            if p == q or (p[0] != q[0] and p[1] != q[1]):
                yield f'{a} → {b}: нулевой или неортогональный отрезок.'
            if not inside(seg, (DIVIDER, PHASES['prepare'][0], RIGHT, PHASES['approve'][1]), 4):
                yield f'{a} → {b}: выход за поле деятельности.'
            for k, box in boxes.items():
                if (k == a and i == 0) or (k == b and i == len(points) - 2):
                    continue  # допустимое касание своего контура проверено выше
                if gap(seg, box) < 6:
                    yield f'{a} → {b}: линия на фигуре {k} или вплотную к ней.'
            for other, j, prev in segments:
                if other == route and i == j + 1:
                    if seg[0] == seg[2] == prev[0] == prev[2] or seg[1] == seg[3] == prev[1] == prev[3]:
                        yield f'{a} → {b}: наложение отрезков или лишнее колено.'
                elif gap(seg, prev) == 0:
                    yield f'{a} → {b}: пересечение с другой линией.'
            segments.append((route, i, seg))

    for owner, text, box in labels:
        outer, pad = (0, 0, W, H), 4
        if owner in boxes:
            outer, pad = boxes[owner], 7 if owner in NODES else 4
        elif owner in PHASES:
            top, bottom, _, _ = PHASES[owner]
            outer = LEFT, top, DIVIDER, bottom
        elif isinstance(owner, Flow):
            near = [gap(box, s) for e, _, s in segments if e == owner]
            if text != owner.guard or not near or min(near) > 18:
                yield f'«{text}»: условие не у своего потока.'
        if not inside(box, outer, pad):
            yield f'«{text}»: подпись обрезана или не помещается с отступом.'
        if any(other != owner and gap(box, b) < 3 for other, b in boxes.items()):
            yield f'«{text}»: подпись на чужой фигуре.'
        if any(gap(box, s) < 6 for _, _, s in segments):
            yield f'«{text}»: надпись на линии или её наконечнике.'
    for (_, t, a), (_, u, b) in combinations(labels, 2):
        if gap(a, b) < 2:
            yield f'Наложение подписей «{t}» и «{u}».'


def main():
    errors = list(model_errors()) or [*scenario_errors(), *geometry_errors()]
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'ЛР7: узлов — {len(NODES)}, потоков — {len(FLOWS)}. Четыре сценария, порядок ЭЦП и геометрия — без нарушений.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
