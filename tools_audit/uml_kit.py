# -*- coding: utf-8 -*-
"""Небольшой векторный движок поверх Pillow для отрисовки UML-диаграмм.

Все координаты задаются в «проектных» единицах; изображение рисуется с
суперсэмплингом (scale), затем уменьшается методом LANCZOS — это даёт
гладкие линии и чёткий текст без внешних зависимостей (cairo/graphviz).
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

_FONT_DIRS = ['/usr/share/fonts/truetype/dejavu/']
try:  # курсивные начертания DejaVu поставляются вместе с matplotlib
    import matplotlib as _mpl
    _FONT_DIRS.append(os.path.join(os.path.dirname(_mpl.__file__),
                                   'mpl-data', 'fonts', 'ttf') + os.sep)
except Exception:  # pragma: no cover
    pass
_FONT_FILES = {
    'normal': 'DejaVuSans.ttf',
    'bold': 'DejaVuSans-Bold.ttf',
    'italic': 'DejaVuSans-Oblique.ttf',
    'bolditalic': 'DejaVuSans-BoldOblique.ttf',
    'mono': 'DejaVuSansMono.ttf',
}


def _font_path(name):
    for d in _FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return os.path.join(_FONT_DIRS[0], name)


FONT_DIR = _FONT_DIRS[0]

INK = '#111827'
MUTED = '#4b5563'
LINE = '#111827'
BLUE = '#1d4ed8'
HEAD_FILL = '#e8eefc'
ACCENT = '#0f3d8a'


class Canvas:
    def __init__(self, w, h, scale=2, bg='#ffffff'):
        self.w, self.h, self.s = w, h, scale
        self.im = Image.new('RGB', (int(w * scale), int(h * scale)), bg)
        self.d = ImageDraw.Draw(self.im)
        self._fonts = {}

    # ---------------------------------------------------------------- fonts
    def _font(self, size, weight='normal'):
        key = (round(size, 1), weight)
        if key not in self._fonts:
            self._fonts[key] = ImageFont.truetype(
                _font_path(_FONT_FILES[weight]), max(6, int(round(size * self.s))))
        return self._fonts[key]

    def tw(self, text, size=12, weight='normal'):
        """Ширина строки в проектных единицах."""
        f = self._font(size, weight)
        return self.d.textlength(text, font=f) / self.s

    def th(self, size=12, weight='normal'):
        f = self._font(size, weight)
        a, b = f.getmetrics()
        return (a + b) / self.s

    def text(self, x, y, text, size=12, weight='normal', fill=INK, anchor='ls'):
        """anchor: горизонталь l/m/r + вертикаль s (baseline) / m / t."""
        self.d.text((x * self.s, y * self.s), text, font=self._font(size, weight),
                    fill=fill, anchor=anchor)

    def text_clip(self, x, y, text, max_w, size=12, weight='normal', fill=INK, anchor='ls'):
        """Текст с усечением по ширине (…)."""
        if self.tw(text, size, weight) <= max_w:
            self.text(x, y, text, size, weight, fill, anchor)
            return
        ell = '…'
        while text and self.tw(text + ell, size, weight) > max_w:
            text = text[:-1]
        self.text(x, y, text + ell, size, weight, fill, anchor)

    # ---------------------------------------------------------------- shapes
    def line(self, pts, fill=LINE, width=1.2, dash=None, cap=True):
        pts = [(x * self.s, y * self.s) for x, y in pts]
        w = max(1, int(round(width * self.s)))
        if not dash:
            self.d.line(pts, fill=fill, width=w, joint='curve')
            return
        # пунктир: рисуем участками
        on, off = dash
        dist_left = on * self.s
        off_left = off * self.s
        drawing = True
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            seg = math.hypot(x2 - x1, y2 - y1)
            if seg == 0:
                continue
            ux, wy = (x2 - x1) / seg, (y2 - y1) / seg
            pos = 0.0
            while pos < seg:
                step = (dist_left if drawing else off_left)
                step = min(step, seg - pos)
                if drawing:
                    sx, sy = x1 + ux * pos, y1 + wy * pos
                    ex, ey = x1 + ux * (pos + step), y1 + wy * (pos + step)
                    self.d.line([(sx, sy), (ex, ey)], fill=fill, width=w)
                pos += step
                if drawing:
                    dist_left -= step
                    if dist_left <= 1e-6:
                        drawing = False
                        off_left = off * self.s
                else:
                    off_left -= step
                    if off_left <= 1e-6:
                        drawing = True
                        dist_left = on * self.s

    def rect(self, x, y, w, h, fill=None, outline=LINE, width=1.2, r=0, dash=None):
        box = [x * self.s, y * self.s, (x + w) * self.s, (y + h) * self.s]
        wd = max(1, int(round(width * self.s)))
        if r:
            if fill:
                self.d.rounded_rectangle(box, radius=r * self.s, fill=fill)
            if outline:
                if dash:
                    # скруглённый пунктир аппроксимируем: рисуем по контуру
                    self.d.rounded_rectangle(box, radius=r * self.s, outline=outline, width=wd)
                else:
                    self.d.rounded_rectangle(box, radius=r * self.s, outline=outline, width=wd)
            return
        if fill:
            self.d.rectangle(box, fill=fill)
        if outline:
            if dash:
                x0, y0, x1, y1 = box
                self._rect_dashed(x0 / self.s, y0 / self.s, x1 / self.s, y1 / self.s, outline, width, dash)
            else:
                self.d.rectangle(box, outline=outline, width=wd)

    def _rect_dashed(self, x0, y0, x1, y1, fill, width, dash):
        self.line([(x0, y0), (x1, y0)], fill, width, dash)
        self.line([(x1, y0), (x1, y1)], fill, width, dash)
        self.line([(x1, y1), (x0, y1)], fill, width, dash)
        self.line([(x0, y1), (x0, y0)], fill, width, dash)

    def poly(self, pts, fill=None, outline=LINE, width=1.2, dash=None):
        spts = [(x * self.s, y * self.s) for x, y in pts]
        if fill:
            self.d.polygon(spts, fill=fill)
        if outline:
            if dash:
                self.line(list(pts) + [pts[0]], outline, width, dash)
            else:
                self.d.line(spts + [spts[0]], fill=outline,
                            width=max(1, int(round(width * self.s))), joint='curve')

    def circle(self, cx, cy, r, fill=None, outline=LINE, width=1.2):
        box = [(cx - r) * self.s, (cy - r) * self.s, (cx + r) * self.s, (cy + r) * self.s]
        self.d.ellipse(box, fill=fill, outline=outline,
                       width=max(1, int(round(width * self.s))))

    def arc(self, cx, cy, r, start, end, fill=LINE, width=1.2):
        box = [(cx - r) * self.s, (cy - r) * self.s, (cx + r) * self.s, (cy + r) * self.s]
        self.d.arc(box, start, end, fill=fill, width=max(1, int(round(width * self.s))))

    # ---------------------------------------------------------------- arrows
    def arrowhead(self, tip, frm, kind='open', fill=LINE, size=11):
        """kind: open | filled | hollow | crowfoot | bar."""
        tx, ty = tip
        dx, dy = tx - frm[0], ty - frm[1]
        ln = math.hypot(dx, dy) or 1.0
        ux, uy = dx / ln, dy / ln
        px, py = -uy, ux
        if kind == 'open':
            a = size
            p1 = (tx - ux * a + px * a * 0.55, ty - uy * a + py * a * 0.55)
            p2 = (tx - ux * a - px * a * 0.55, ty - uy * a - py * a * 0.55)
            self.line([p1, tip], fill, 1.4)
            self.line([p2, tip], fill, 1.4)
        elif kind == 'filled':
            a = size
            p1 = (tx - ux * a + px * a * 0.5, ty - uy * a + py * a * 0.5)
            p2 = (tx - ux * a - px * a * 0.5, ty - uy * a - py * a * 0.5)
            self.poly([tip, p1, p2], fill=fill, outline=fill, width=1)
        elif kind == 'hollow':
            a = size * 2.0 / 1.7
            p1 = (tx - ux * a + px * a * 0.62, ty - uy * a + py * a * 0.62)
            p2 = (tx - ux * a - px * a * 0.62, ty - uy * a - py * a * 0.62)
            self.poly([tip, p1, p2], fill='#ffffff', outline=fill, width=1.4)
        elif kind == 'crowfoot':
            a = size
            for sgn in (1, -1):
                p = (tx - ux * a + px * a * sgn, ty - uy * a + py * a * sgn)
                self.line([p, tip], fill, 1.3)
            self.line([(tx - ux * a, ty - uy * a)], fill, 1.3) if False else None
        elif kind == 'bar':
            a = size * 0.55
            self.line([(tx - ux * a + px * a * 1.6, ty - uy * a + py * a * 1.6),
                       (tx - ux * a - px * a * 1.6, ty - uy * a - py * a * 1.6)], fill, 1.6)
        elif kind == 'diamond_filled':
            # Ромб композиции рисуется ОТ рамки класса НАРУЖУ, вдоль линии связи:
            # вершина касается рамки, тело ромба лежит вне блока (иначе он ложится
            # поверх текста последней операции).
            a = size
            b = size * 0.45
            base = (tx, ty)
            p1 = (base[0] - ux * a + px * b, base[1] - uy * a + py * b)
            p2 = (base[0] - ux * 2 * a, base[1] - uy * 2 * a)
            p3 = (base[0] - ux * a - px * b, base[1] - uy * a - py * b)
            self.poly([base, p1, p2, p3], fill=fill, outline=fill, width=1)
        elif kind == 'diamond_hollow':
            a = size
            b = size * 0.45
            base = (tx, ty)
            p1 = (base[0] + ux * a + px * b, base[1] + uy * a + py * b)
            p2 = (base[0] + ux * 2 * a, base[1] + uy * 2 * a)
            p3 = (base[0] + ux * a - px * b, base[1] + uy * a - py * b)
            self.poly([base, p1, p2, p3], fill='#ffffff', outline=fill, width=1.3)

    def connector(self, pts, head=None, tail=None, fill=LINE, width=1.2, dash=None,
                  head_size=11, label=None, label_pos=0.5, label_side=1,
                  label_size=10.5, label_fill=MUTED, label_weight='normal',
                  bg='#ffffff'):
        """Полилиния со стрелками на концах. label рисуется у сегмента label_pos."""
        self.line(pts, fill=fill, width=width, dash=dash)
        if tail:
            self.arrowhead(pts[0], pts[1], tail, fill, head_size)
        if head:
            self.arrowhead(pts[-1], pts[-2], head, fill, head_size)
        if label:
            self.polyline_label(pts, label, label_pos, label_side, label_size,
                                label_fill, label_weight, bg)

    def polyline_label(self, pts, label, pos=0.5, side=1, size=10.5,
                       fill=MUTED, weight='normal', bg='#ffffff', pad=3):
        # точка на середине нужного сегмента
        segs = list(zip(pts, pts[1:]))
        lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
        total = sum(lens) or 1.0
        target = total * pos
        acc = 0.0
        for (a, b), ln in zip(segs, lens):
            if acc + ln >= target or ln == lens[-1]:
                t = (target - acc) / (ln or 1)
                x = a[0] + (b[0] - a[0]) * t
                y = a[1] + (b[1] - a[1]) * t
                dx, dy = (b[0] - a[0]) / (ln or 1), (b[1] - a[1]) / (ln or 1)
                break
            acc += ln
        else:
            x, y = pts[-1]
            dx, dy = 1, 0
        nx, ny = -dy, dx
        w = self.tw(label, size, weight)
        # размещаем подпись «над» сегментом (с учётом направления)
        lx = x + nx * side * (size * 0.75 + pad) - w / 2
        ly = y + ny * side * (size * 0.75 + pad)
        if abs(dy) < 0.5:      # горизонтальный сегмент: текст над/под линией
            ly = y + (-8 if side > 0 else 14)
        if abs(dx) < 0.5:      # вертикальный сегмент: текст слева/справа
            lx = x + (6 if side > 0 else -w - 6)
        if bg:
            self.d.rectangle([lx * self.s - 2 * self.s, (ly - size) * self.s,
                              (lx + w) * self.s + 2 * self.s, (ly + 3) * self.s], fill=bg)
        self.text(lx, ly, label, size, weight, fill)

    def save(self, path, *, output_scale=1):
        """Масштаб PNG относительно проектных единиц (независим от суперсэмплинга)."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        im = self.im.resize((int(self.w * output_scale), int(self.h * output_scale)), Image.LANCZOS)
        im.save(path, optimize=True)
        return path


# -------------------------------------------------------------------- helpers
def title(c, text, sub=None, x=44, y=46):
    c.text(x, y, text, 21, 'bold', INK)
    if sub:
        c.text(x, y + 26, sub, 12, 'normal', MUTED)


def note(c, x, y, w, lines, size=10.5, pad=10, fill='#fffbe6', outline='#b58900',
         line_h=None):
    """UML-примечание: прямоугольник с загнутым углом."""
    fold = 14
    fs = size
    line_h = line_h or fs + 4.5
    h = pad * 2 + line_h * len(lines)
    c.poly([(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h)],
           fill=fill, outline=outline, width=1.1)
    c.poly([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)],
           fill=fill, outline=outline, width=1.1)
    for i, ln in enumerate(lines):
        c.text(x + pad, y + pad + line_h * (i + 0.82), ln, fs, 'normal', '#3f3f46')
    return (x, y, w, h)


def legend_box(c, x, y, w, h, title_text='Условные обозначения'):
    c.rect(x, y, w, h, fill='#ffffff', outline='#9ca3af', width=1.0)
    c.text(x + 12, y + 22, title_text, 11.5, 'bold', '#374151')
