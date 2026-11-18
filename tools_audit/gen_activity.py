"""UML 2.5.1: экспертиза и утверждение учебного плана (ЛР7, слайд 8).

python3 tools_audit/gen_activity.py — пересобрать PNG; check_activity.py — проверить
тот же граф и геометрию, не записывая файлы. Все координаты — в единицах Canvas.
"""
from dataclasses import dataclass
from pathlib import Path

from uml_kit import Canvas, INK, LINE, MUTED

OUT = Path(__file__).resolve().parents[1] / 'diagrams/lab7/activity_diagram.png'
W, H = 1240, 832
LEFT, DIVIDER, RIGHT = 16, 183, W - 16
# Этап 1 предшествует экспертизе; после неё выбирается первый неподписанный этап.
SIGNERS = ('Заведующий выпускающей кафедрой', 'Начальник Центра АНОК',
           'Проректор по учебной работе', 'Ректор')
# Секции (ActivityPartition) группируют узлы по фазе; под названием — участники.
PHASES = {
    'prepare': (64, 250, 'Подготовка', SIGNERS[0].replace(' ', '\n') + ', портал'),
    'review': (250, 436, 'Экспертиза', 'Эксперт АНОК\nи портал'),
    'approve': (436, 772, 'Утверждение', 'Подписанты,\nсекретарь совета\nи портал'),
}
Point = tuple[float, float]


@dataclass(frozen=True)
class Node:
    phase: str
    kind: str
    x: int
    y: int
    w: int
    h: int
    label: str = ''

    @property
    def box(self):
        return self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2

    def port(self, side):
        x0, y0, x1, y1 = self.box
        return {'N': (self.x, y0), 'E': (x1, self.y),
                'S': (self.x, y1), 'W': (x0, self.y)}[side]


def action(phase, x, y, w, label):
    return Node(phase, 'action', x, y, w, 20 + 22 * len(label.splitlines()), label)


def control(phase, kind, x, y):
    d = {'initial': 19, 'final': 26, 'decision': 34, 'merge': 30}[kind]
    return Node(phase, kind, x, y, d, d)


NODES = {
    'start': control('prepare', 'initial', 211, 200),
    'retry': control('prepare', 'merge', 268, 200),
    'open': action('prepare', 403, 200, 180, 'Выбрать проект\nучебного плана'),
    'load': action('prepare', 626, 200, 194, 'Загрузить план\nи дисциплины'),
    'loaded': control('prepare', 'decision', 785, 200),
    'error': action('prepare', 523, 113, 238, 'Сообщить об ошибке'),
    'first': action('prepare', 1083, 200, 235, 'Сохранить проект\nи наложить ЭЦП № 1'),
    'validate': action('review', 1083, 360, 235, 'Проверить план\nпо ФГОС ВО 3++'),
    'valid': control('review', 'decision', 895, 360),
    'remarks': action('review', 595, 360, 213, 'Оформить протокол\nзамечаний'),
    'return': action('review', 346, 360, 193, 'Вернуть проект\nна доработку'),
    'rework_end': control('review', 'final', 210, 360),
    'next': control('approve', 'merge', 895, 491),
    'select': action('approve', 1083, 491, 235, 'Открыть следующий\nнеподписанный этап'),
    'sign': action('approve', 1083, 628, 235, 'Подписать план\nна текущем этапе'),
    'record': action('approve', 681, 628, 242, 'Сохранить ЭЦП этапа\nи хэш SHA-256'),
    'more': control('approve', 'decision', 345, 628),
    'protocol': action('approve', 345, 718, 286, 'Внести номер и дату\nпротокола Учёного совета'),
    'status': action('approve', 681, 718, 264, 'Присвоить статус\n«Утверждён ректором»'),
    'notify': action('approve', 985, 718, 259, 'Уведомить инициатора\nоб утверждении'),
    'approved_end': control('approve', 'final', 1170, 718),
}


@dataclass(frozen=True)
class Flow:
    source: str
    target: str
    ports: str  # стороны выхода и входа, например EW — вправо, в левый край
    bends: tuple[Point, ...] = ()
    guard: str = ''
    label_at: Point | None = None

    def points(self):
        return (NODES[self.source].port(self.ports[0]), *self.bends,
                NODES[self.target].port(self.ports[1]))


FLOWS = (
    Flow('start', 'retry', 'EW'), Flow('retry', 'open', 'EW'),
    Flow('open', 'load', 'EW'), Flow('load', 'loaded', 'EW'),
    Flow('loaded', 'error', 'NE', ((785, 113),), '[ошибка загрузки]', (880, 142)),
    Flow('error', 'retry', 'WN', ((268, 113),)),
    Flow('loaded', 'first', 'EW', guard='[план загружен]', label_at=(884, 180)),
    Flow('first', 'validate', 'SN'), Flow('validate', 'valid', 'WE'),
    Flow('valid', 'remarks', 'WE', guard='[есть нарушения]', label_at=(790, 339)),
    Flow('remarks', 'return', 'WE'), Flow('return', 'rework_end', 'WE'),
    Flow('valid', 'next', 'SN', guard='[нарушений нет]', label_at=(978, 412)),
    Flow('next', 'select', 'EW'), Flow('select', 'sign', 'SN'),
    Flow('sign', 'record', 'WE'), Flow('record', 'more', 'WE'),
    Flow('more', 'next', 'NW', ((345, 491),), '[остались этапы]', (430, 595)),
    Flow('more', 'protocol', 'SN', guard='[все этапы подписаны]', label_at=(456, 665)),
    Flow('protocol', 'status', 'EW'), Flow('status', 'notify', 'EW'),
    Flow('notify', 'approved_end', 'EW'),
)


@dataclass(frozen=True)
class Note:
    target: str
    box: tuple[int, int, int, int]
    anchor_x: int  # пунктир между горизонтальными гранями примечания и действия
    title: str
    text: str

    def link(self):
        _, top, _, bottom = self.box
        node = NODES[self.target]
        above = bottom < node.y
        return ((self.anchor_x, bottom if above else top),
                (self.anchor_x, node.box[1 if above else 3]))


NOTES = {
    'limits': Note('validate', (209, 264, 1034, 310), 1008, 'Автоматическая проверка · бакалавриат',
                   '240 з.е. всего · 30 з.е. в семестре · ≤ 5 экзаменов в сессию · практики ≥ 12 з.е. · ГИА ≥ 6 з.е.'),
    'order': Note('select', (371, 536, 1034, 582), 1008, 'Порядок визирования после экспертизы',
                  '    '.join(f'{i}. {role}' for i, role in enumerate(SIGNERS[1:], 2))),
}


def render():
    c = Canvas(W, H, scale=4)
    labels, routes = [], []

    def text(owner, x, y, value, size, weight='normal', color=INK, anchor='mm'):
        box = c.d.textbbox((x * c.s, y * c.s), value, font=c._font(size, weight), anchor=anchor)
        labels.append((owner, value, tuple(v / c.s for v in box)))
        c.text(x, y, value, size, weight, color, anchor)

    # Рамка деятельности с пятиугольной вкладкой и заголовками секций.
    bottom = PHASES['approve'][1]
    c.rect(LEFT, 12, RIGHT - LEFT, bottom - 12, outline=MUTED)
    c.poly([(LEFT, 12), (690, 12), (690, 42), (676, 56), (LEFT, 56)],
           fill='#f5f6f8', outline=MUTED)
    text('frame', 32, 34, 'act', 18, 'bold', anchor='lm')
    text('frame', 79, 34, 'Экспертиза и утверждение учебного плана', 23, 'bold', anchor='lm')
    text('frame', RIGHT - 15, 34, 'Портал Центра АНОК  ·  UML 2.5.1', 16, color=MUTED, anchor='rm')
    for phase, (top, bot, title, roles) in PHASES.items():
        c.rect(LEFT, top, DIVIDER - LEFT, bot - top, fill='#f5f6f8', outline=MUTED)
        c.line([(DIVIDER, top), (RIGHT, top)], fill='#9ca3af', width=1)
        lines = roles.splitlines()
        ty = (top + bot) / 2 - len(lines) * 9
        text(phase, LEFT + 13, ty, title, 18, 'bold', anchor='lm')
        for i, ln in enumerate(lines):
            text(phase, LEFT + 13, ty + 28 + i * 19, ln, 15, color=MUTED, anchor='lm')

    for edge in FLOWS:
        points = edge.points()
        routes.append((edge, points))
        c.connector(points, head='open', head_size=10, width=1.7)
        if edge.guard:
            text(edge, *edge.label_at, edge.guard, 16, color=MUTED)

    for key, n in NODES.items():
        if n.kind == 'action':
            c.rect(*n.box[:2], n.w, n.h, fill='white', outline=LINE, width=1.6, r=12)
            lines = n.label.splitlines()
            for i, line in enumerate(lines):
                text(key, n.x, n.y + (i - (len(lines) - 1) / 2) * 22, line, 18.5)
        elif n.kind in ('decision', 'merge'):
            c.poly([n.port(side) for side in 'NESW'], fill='white', outline=LINE, width=1.6)
        elif n.kind == 'initial':
            c.circle(n.x, n.y, n.w / 2, fill=INK, outline=INK)
        elif n.kind == 'final':
            c.circle(n.x, n.y, n.w / 2, fill='white', width=1.8)
            c.circle(n.x, n.y, n.w / 2 - 5, fill=INK, outline=INK)

    for key, note in NOTES.items():
        x, y, r, b = note.box
        points = note.link()
        routes.append((key, points))
        c.line(points, fill=MUTED, dash=(5, 4))  # привязка, а не поток управления
        c.poly([(x, y), (r - 11, y), (r, y + 11), (r, b), (x, b)], fill='white', outline=MUTED)
        c.line([(r - 11, y), (r - 11, y + 11), (r, y + 11)], fill=MUTED)
        text(key, x + 12, y + 12, note.title, 14, 'bold', MUTED, 'lm')
        text(key, x + 12, y + 31, note.text, 16, anchor='lm')

    ly = 802
    c.circle(32, ly, 7, fill=INK)
    text('key', 49, ly, 'начало', 16, anchor='lm')
    c.rect(148, ly - 9, 34, 18, r=5)
    text('key', 193, ly, 'действие', 16, anchor='lm')
    c.poly([(320, ly - 10), (331, ly), (320, ly + 10), (309, ly)])
    text('key', 342, ly, 'решение / слияние', 16, anchor='lm')
    c.connector([(548, ly), (586, ly)], head='open', head_size=8)
    text('key', 598, ly, 'поток управления', 16, anchor='lm')
    text('key', 783, ly, '[условие] — выбор ветви', 16, anchor='lm')
    c.circle(1033, ly, 9, fill='white', width=1.4)
    c.circle(1033, ly, 5, fill=INK)
    text('key', 1050, ly, 'конец деятельности', 16, anchor='lm')
    return c, labels, routes


def activity_diagram():
    c, _, _ = render()
    return c.save(str(OUT), output_scale=2)


if __name__ == '__main__':
    print(activity_diagram())
