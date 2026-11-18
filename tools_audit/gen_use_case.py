"""Варианты использования портала (ЛР1, модель требований, а не матрица прав).

python3 tools_audit/gen_use_case.py — пересобрать только этот рисунок.
Модель и геометрия, переданная на отрисовку, доступны проверке check_use_case.py.
"""
from dataclasses import dataclass
from math import hypot
from pathlib import Path

from uml_kit import Canvas, INK, LINE, MUTED

OUT = Path(__file__).resolve().parents[1] / 'diagrams' / 'use_case_diagram.png'
W, H = 1250, 938
SYSTEM = (165, 126, 1085, 878)  # x0, y0, x1, y1
RX, RY = 121, 40


@dataclass(frozen=True)
class Actor:
    name: str
    x: int
    y: int  # уровень рук
    side: str
    goals: tuple[int, ...]

    def port(self, toward):
        return self.x + (16 if toward[0] >= self.x else -16), self.y


@dataclass(frozen=True)
class UseCase:
    name: str
    x: int
    y: int

    def port(self, toward):
        """Пересечение луча из центра с контуром эллипса, а не его габаритной рамкой."""
        dx, dy = toward[0] - self.x, toward[1] - self.y
        k = hypot(dx / RX, dy / RY)
        return self.x + dx / k, self.y + dy / k


ACTORS = {
    'HEAD_RELEASING': Actor('Заведующий\nвыпускающей\nкафедрой', 118, 293, 'left', (1, 7, 8, 10, 11)),
    'HEAD_IMPLEMENTING': Actor('Заведующий\nреализующей кафедрой', 550, 73, 'top', (11, 12)),
    'VICE_RECTOR': Actor('Проректор\nпо учебной работе', 773, 73, 'top', (7,)),
    'RECTOR': Actor('Ректор\nуниверситета', 986, 73, 'top', (7,)),
    'HEAD_ANOK': Actor('Начальник\nЦентра АНОК', 1140, 272, 'right', (4, 7, 16)),
    'EXPERT_ANOK': Actor('Эксперт\nЦентра АНОК', 1140, 565, 'right', (3, 4, 6, 13)),
    'COUNCIL_SEC': Actor('Секретарь\nУчёного совета', 1140, 815, 'right', (9,)),
    'VIEWER': Actor('Преподаватель\nили студент', 118, 555, 'left', (1, 2, 3, 8, 14, 15, 16)),
    'ADMIN': Actor('Администратор\nпортала', 118, 854, 'left', (15, 17)),
}

CASES = {
    1: UseCase('Найти учебный план\nв реестре', 314, 403),
    2: UseCase('Посмотреть план\nпо семестрам', 398, 569),
    3: UseCase('Сравнить аудиторную\nнагрузку и СРС', 666, 732),
    4: UseCase('Проверить план\nпо ФГОС ВО 3++', 935, 444),
    5: UseCase('Проверить лимит\nэкзаменов', 659, 586),
    6: UseCase('Оформить протокол\nзамечаний', 935, 566),
    7: UseCase('Подписать учебный\nплан ЭЦП', 904, 211),
    8: UseCase('Просмотреть маршрут\nи хэши подписей', 599, 395),
    9: UseCase('Внести реквизиты\nпротокола УС', 935, 815),
    10: UseCase('Создать записку\nна изменение УП', 554, 303),
    11: UseCase('Сравнить версии\nдисциплины', 333, 208),
    12: UseCase('Согласовать записку\nоб изменениях', 598, 190),
    13: UseCase('Внести одобренные\nправки по СЗ', 935, 715),
    14: UseCase('Изучить матрицу\nкомпетенций', 383, 707),
    15: UseCase('Найти контакты\nкафедры', 308, 793),
    16: UseCase('Прочесть регламенты\nи объявления', 599, 486),
    17: UseCase('Просмотреть\nжурнал аудита', 609, 828),
}


@dataclass(frozen=True)
class Link:
    source: str | int
    target: int
    kind: str = 'association'
    label_at: tuple[float, float] | None = None

    def points(self):
        a = ACTORS[self.source] if self.kind == 'association' else CASES[self.source]
        b = CASES[self.target]
        start = a.port((b.x, b.y))
        return start, b.port(start)


LINKS = [Link(role, goal) for role, actor in ACTORS.items() for goal in actor.goals] + [
    Link(4, 5, 'include', (790, 492)),  # обязательная проверка норматива
    Link(6, 4, 'extend', (980, 511)),   # при выявлении нарушений
]


def render():
    # Холст ×4 → PNG ×2: при ширине 165 мм в PDF остаётся 385 dpi.
    c = Canvas(W, H, scale=4)
    labels = []
    routes = []

    def text(owner, x, y, value, size, weight='normal', color=INK, anchor='mm'):
        # Аудит получает реальные границы глифов с тем же шрифтом и привязкой.
        box = c.d.textbbox((x * c.s, y * c.s), value, font=c._font(size, weight), anchor=anchor)
        labels.append((owner, value, tuple(v / c.s for v in box)))
        c.text(x, y, value, size, weight, color, anchor)

    x0, y0, x1, y1 = SYSTEM
    c.rect(x0, y0, x1 - x0, y1 - y0, outline=MUTED, width=1.4)
    text('subject', x0 + 14, y0 + 17, 'Портал Центра АНОК', 18, 'bold', anchor='lm')
    text('title', 24, 38, 'Варианты использования', 21, 'bold', anchor='ls')
    text('title', 24, 64, 'UML 2.5.1', 15, color=MUTED, anchor='ls')

    for link in LINKS:
        pts = link.points()
        routes.append((link, pts))
        if link.kind == 'association':
            c.line(pts, fill='#374151', width=1.6)
        else:
            c.connector(pts, head='open', width=1.6, dash=(7, 5), head_size=10)
            text(link, *link.label_at, f'«{link.kind}»', 16)

    for n, uc in CASES.items():
        x, y = uc.x, uc.y
        box = (x - RX, y - RY, x + RX, y + RY)
        c.d.ellipse(tuple(v * c.s for v in box), fill='white', outline=LINE, width=round(1.5 * c.s))
        text(n, x, y - 23, f'UC-{n}', 12.5, 'bold', MUTED)
        for i, line in enumerate(uc.name.split('\n')):
            text(n, x, y - 5 + i * 20, line, 18)

    for role, a in ACTORS.items():
        x, y = a.x, a.y
        c.circle(x, y - 16, 7, fill='white', width=1.9)
        c.line([(x, y - 9), (x, y + 10)], width=1.9)
        c.line([(x - 16, y), (x + 16, y)], width=1.9)
        c.line([(x - 12, y + 27), (x, y + 10), (x + 12, y + 27)], width=1.9)
        lines = a.name.split('\n')
        ly = y - 36 - 19 * (len(lines) - 1) if a.side == 'top' else y + 42
        # Боковые подписи центрированы в полях, а не в пучках ассоциаций.
        lx = {'left': 85, 'right': W - 85, 'top': x}[a.side]
        for i, line in enumerate(lines):
            text(role, lx, ly + i * 19, line, 16, 'bold')

    # Легенда за пределами предмета: образцы не являются связями модели.
    ly = 909
    c.line([(165, ly), (211, ly)], fill='#374151', width=1.6)
    text('legend', 222, ly, 'участие актора', 16, anchor='lm')
    c.connector([(416, ly), (462, ly)], head='open', dash=(7, 5), width=1.6)
    text('legend', 473, ly, '«include» — обязательная часть', 16, anchor='lm')
    c.connector([(771, ly), (817, ly)], head='open', dash=(7, 5), width=1.6)
    text('legend', 828, ly, '«extend» — при выявлении нарушений', 16, anchor='lm')
    return c, labels, routes


def use_case():
    c, _, _ = render()
    return c.save(str(OUT), output_scale=2)


if __name__ == '__main__':
    print(use_case())
