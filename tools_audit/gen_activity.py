# -*- coding: utf-8 -*-
"""Диаграмма деятельности UML 2.5 «Экспертиза и утверждение учебного плана».

Нужна для презентации по шаблону (слайд 8): в комплекте ЛР2 её не было.
Обозначения UML 2.5: начальный узел — залитый кружок, действие — прямоугольник
со скруглёнными углами, решение — ромб с охраняющими условиями на выходах,
слияние — ромб без условий, конечный узел — кружок в кольце.
Стиль тот же, что у остальных диаграмм комплекта: монохром, DejaVu, тонкие линии.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'diagrams', 'lab7')
FD = '/usr/share/fonts/truetype/dejavu/'
INK = '#111827'
EDGE = '#374151'
FILL = '#f4f6fb'
S = 2                                   # суперсэмплинг для гладких линий

W, H = 1500, 2000          # высота подрезается по содержимому при сохранении
CX = 700                                # ось основного потока

_f = {}


def F(sz, bold=False):
    k = (sz, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz * S)
    return _f[k]


im = Image.new('RGB', (W * S, H * S), 'white')
d = ImageDraw.Draw(im)


def tw(text, sz, bold=False):
    return d.textlength(text, font=F(sz, bold)) / S


def wrap(text, sz, maxw, bold=False):
    out, cur = [], ''
    for w in text.split():
        probe = (cur + ' ' + w).strip()
        if cur and tw(probe, sz, bold) > maxw:
            out.append(cur)
            cur = w
        else:
            cur = probe
    out.append(cur)
    return out


def text(x, y, s, sz, bold=False, anchor='la', fill=INK):
    d.text((x * S, y * S), s, font=F(sz, bold), fill=fill, anchor=anchor)


def arrow(pts, head=True, color=EDGE):
    pts = [(x * S, y * S) for x, y in pts]
    d.line(pts, fill=color, width=int(1.9 * S), joint='curve')
    if head:
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        import math
        ang = math.atan2(y1 - y0, x1 - x0)
        ln, wd = 13 * S, 6 * S
        bx, by = x1 - ln * math.cos(ang), y1 - ln * math.sin(ang)
        d.polygon([(x1, y1),
                   (bx - wd * math.sin(ang), by + wd * math.cos(ang)),
                   (bx + wd * math.sin(ang), by - wd * math.cos(ang))], fill=color)


def rrect(x, y, w, h, label, sz=25, fill=FILL):
    d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=14 * S,
                        fill=fill, outline=EDGE, width=int(1.9 * S))
    lines = wrap(label, sz, w - 44)
    lh = sz * 1.28
    ty = y + h / 2 - (len(lines) - 1) * lh / 2
    for i, ln in enumerate(lines):
        text(x + w / 2, ty + i * lh, ln, sz, anchor='mm')
    return y + h


def diamond(cx, y, w, h, label, sz=21):
    pts = [(cx, y), (cx + w / 2, y + h / 2), (cx, y + h), (cx - w / 2, y + h / 2)]
    d.polygon([(x * S, y * S) for x, y in pts], fill='#ffffff', outline=EDGE, width=int(1.9 * S))
    lines = wrap(label, sz, w - 90)
    lh = sz * 1.25
    ty = y + h / 2 - (len(lines) - 1) * lh / 2
    for i, ln in enumerate(lines):
        text(cx, ty + i * lh, ln, sz, anchor='mm')
    return y + h


def guard(x, y, s, anchor='la', sz=20):
    """Охраняющее условие — рядом со стрелкой, на белой подложке."""
    w = tw(s, sz) + 12
    if anchor == 'la':
        d.rectangle([(x - 4) * S, (y - 4) * S, (x - 4 + w) * S, (y + sz + 6) * S], fill='white')
        text(x, y, s, sz, fill='#4b5563')
    else:
        d.rectangle([(x - w + 4) * S, (y - 4) * S, (x + 4) * S, (y + sz + 6) * S], fill='white')
        text(x, y, s, sz, anchor='ra', fill='#4b5563')


# ------------------------------------------------------------------ сценарий
BW = 470                        # ширина блока действия
x0 = CX - BW / 2

# начальный узел
d.ellipse([(CX - 13) * S, 70 * S, (CX + 13) * S, 96 * S], fill=INK)
y = 96
arrow([(CX, y), (CX, y + 44)])
y += 44

y = rrect(x0, y, BW, 78, 'Открыть форму учебного плана в портале')
arrow([(CX, y), (CX, y + 40)])
y += 40

y = rrect(x0, y, BW, 104, 'Запросить план и дисциплины из базы данных (planId = 1)')
arrow([(CX, y), (CX, y + 40)])
y += 40

y_d1 = y
y = diamond(CX, y, 360, 132, 'План загружен?')
arrow([(CX, y), (CX, y + 40)])
guard(CX + 18, y + 10, '[да]')
y += 40

y = rrect(x0, y, BW, 104, 'Сохранить проект плана и наложить ЭЦП этапа 1')
arrow([(CX, y), (CX, y + 40)])
y += 40

y = rrect(x0, y, BW, 104, 'Автоматическая проверка ФГОС ВО 3++: 240 з.е., 30 з.е. в семестре, ≤ 5 экзаменов, ≥ 12 з.е. практик, ≥ 6 з.е. ГИА', sz=22)
arrow([(CX, y), (CX, y + 40)])
y += 40

y_d2 = y
y = diamond(CX, y, 380, 138, 'Выявлены нарушения ФГОС?')
arrow([(CX, y), (CX, y + 44)])
guard(CX + 18, y + 10, '[нет]')
y += 44

y_loop_top = y
y = rrect(x0, y, BW, 104, 'Визирование шага k = 2…4: эксперт АНОК → проректор по УР → ректор')
arrow([(CX, y), (CX, y + 40)])
y += 40

y_d3 = y
y = diamond(CX, y, 400, 132, 'Все шаги маршрута подписаны?')
arrow([(CX, y), (CX, y + 40)])
guard(CX + 18, y + 10, '[да]')
y += 40

y = rrect(x0, y, BW, 104, 'Утвердить протоколом Учёного совета № 8/26 и зафиксировать статус APPROVED')
arrow([(CX, y), (CX, y + 40)])
y += 40

y = rrect(x0, y, BW, 78, 'Уведомить инициатора об утверждении')
arrow([(CX, y), (CX, y + 46)])
y += 46

# конечный узел
d.ellipse([(CX - 17) * S, y * S, (CX + 17) * S, (y + 34) * S], outline=INK, width=int(2 * S))
d.ellipse([(CX - 9) * S, (y + 8) * S, (CX + 9) * S, (y + 26) * S], fill=INK)
end_y = y + 17

# --- ветвь «план не загружен»: ошибка и повторный ввод -------------------
ex = 1235
arrow([(CX + 180, y_d1 + 66), (ex, y_d1 + 66)])
guard(CX + 196, y_d1 + 34, '[нет]')
rrect(ex - 130, y_d1 + 30, 260, 72, 'Сообщение об ошибке', sz=21)
arrow([(ex, y_d1 + 30), (ex, y_d1 - 30), (x0 + BW + 4, y_d1 - 30)])

# --- ветвь «нарушения выявлены»: возврат на доработку --------------------
arrow([(CX + 190, y_d2 + 69), (ex, y_d2 + 69)])
guard(CX + 206, y_d2 + 37, '[да]')
rrect(ex - 140, y_d2 + 26, 280, 86, 'Вернуть план на доработку с перечнем замечаний', sz=20)
arrow([(ex, y_d2 + 112), (ex, end_y), (CX + 17, end_y)])

# --- цикл по шагам маршрута ---------------------------------------------
lx = 210
arrow([(CX - 200, y_d3 + 66), (lx, y_d3 + 66), (lx, y_loop_top + 52), (x0 - 2, y_loop_top + 52)])
guard(lx + 14, y_d3 + 36, '[нет] — следующий шаг k')

text(CX, 40, 'Диаграмма деятельности — экспертиза и утверждение учебного плана',
     sz=27, bold=True, anchor='mm')

im = im.resize((W, H), Image.LANCZOS)

# подрезаем белые поля: canvas был взят с запасом
from PIL import ImageOps
box = ImageOps.invert(im.convert('L')).getbbox()
m = 36
im = im.crop((max(0, box[0] - m), max(0, box[1] - m),
              min(im.width, box[2] + m), min(im.height, box[3] + m)))
im.save(os.path.join(OUT, 'activity_diagram.png'))
print('activity diagram:', im.size)
