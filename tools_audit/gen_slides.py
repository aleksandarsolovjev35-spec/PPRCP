# -*- coding: utf-8 -*-
"""Regenerates the 12 defense slides (dark theme) with data consistent with the portal DB,
then packs them into reports/lab7/LR7_Presentation_Variant15.{pptx,pdf}.

Layout rules (shared by every slide):
  * one grid: left/right margin 60 px, gutter 30 px, columns from cols();
  * every card has the same inner padding (PAD) and title offset; bullet lists align
    their marker with the card title;
  * single-line labels inside rows / badges / chips are vertically centred (anchor "lm");
  * the content block of each slide is vertically centred between the header rule and
    the footer, so no slide is top-heavy;
  * all text is drawn through helpers that word-wrap / shrink-to-fit and assert that nothing
    leaves its container, so overflow regressions fail the build instead of silently
    producing broken slides.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = '/usr/share/fonts/truetype/dejavu/'
_FONTS = {}


def F(sz, bold=False):
    key = (sz, bold)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz)
    return _FONTS[key]


BG = '#111827'; PANEL = '#1f2937'; ACC = '#2563eb'; SKY = '#38bdf8'; TXT = '#f9fafb'; MUT = '#9ca3af'
GREEN = '#34d399'; PURP = '#a78bfa'; AMBER = '#fbbf24'; RED = '#f87171'; CHIP = '#374151'
W, H = 1920, 1080
MARGIN = 60                 # left/right safe margin
GUT = 30                    # gutter between cards
PAD = 30                    # inner padding of a card
TITLE_H = 54                # distance from card title baseline block to body
CONTENT_TOP = 170           # first content line under the header rule
CONTENT_BOTTOM = H - 80     # nothing below this line except the footer
OUT = f'{ROOT}/diagrams/lab7'
os.makedirs(OUT, exist_ok=True)

# ----------------------------------------------------------------------------- helpers

class Overflow(Exception):
    pass


_measure = ImageDraw.Draw(Image.new('RGB', (1, 1)))


def tw(text, font):
    return _measure.textlength(text, font=font)


def cols(n, gap=GUT, x0=MARGIN, width=W - 2 * MARGIN):
    """Column grid: list of (x, w); the last column absorbs rounding so edges stay flush."""
    cw = (width - gap * (n - 1)) // n
    out = [(x0 + i * (cw + gap), cw) for i in range(n)]
    lx, _ = out[-1]
    out[-1] = (lx, x0 + width - lx)
    return out


def wrap(text, font, maxw):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        cand = (cur + ' ' + w).strip()
        if tw(cand, font) <= maxw or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    for ln in lines:
        if tw(ln, font) > maxw:
            raise Overflow(f'word too long for {maxw}px: {ln!r}')
    return lines


def fit_font(text, maxw, size, bold=False, min_size=12):
    while size > min_size and tw(text, F(size, bold)) > maxw:
        size -= 1
    if tw(text, F(size, bold)) > maxw:
        raise Overflow(f'cannot fit {text!r} into {maxw}px')
    return F(size, bold)


def T(d, x, y, text, font, fill, maxw=None, maxy=CONTENT_BOTTOM, anchor='la'):
    """Draw one line; assert it stays inside [x, x+maxw] and above maxy.
    anchor 'la' = top-left (y is top), 'lm' = y is the vertical middle, 'ra' = right-aligned."""
    if maxw is None:
        maxw = W - MARGIN - x
    width = tw(text, font)
    if width > maxw + 0.5:
        raise Overflow(f'text {text!r} ({width:.0f}px) wider than {maxw}px')
    bottom = y + font.size * 0.7 if anchor[1] == 'm' else y + font.size * 1.25
    if bottom > maxy:
        raise Overflow(f'text {text!r} below bottom limit {maxy}')
    d.text((x, y), text, font=font, fill=fill, anchor=anchor)
    return width


def TR(d, right_x, y, text, font, fill, maxw=None, maxy=CONTENT_BOTTOM):
    """Right-aligned single line (right edge at right_x)."""
    width = tw(text, font)
    return T(d, right_x - width, y, text, font, fill, maxw or width + 1, maxy)


def TC(d, cx, y, text, font, fill, maxw):
    """Horizontally centred single line."""
    width = tw(text, font)
    if width > maxw:
        raise Overflow(f'centered text {text!r} wider than {maxw}px')
    d.text((cx - width / 2, y), text, font=font, fill=fill)


def para(d, x, y, text, font, fill, maxw, lh=None, maxy=CONTENT_BOTTOM):
    lh = lh or int(font.size * 1.45)
    for ln in wrap(text, font, maxw):
        T(d, x, y, ln, font, fill, maxw, maxy); y += lh
    return y


def para_height(text, font, maxw, lh=None):
    lh = lh or int(font.size * 1.45)
    return lh * len(wrap(text, font, maxw))


def card(d, x, y, w, h, border=ACC):
    if x < MARGIN - 1 or x + w > W - MARGIN + 1 or y + h > CONTENT_BOTTOM + 1 or y < CONTENT_TOP - 1:
        raise Overflow(f'card {x},{y},{w},{h} leaves the safe area')
    d.rounded_rectangle([x, y, x + w, y + h], 12, fill=PANEL)
    d.rectangle([x, y, x + w, y + 6], fill=border)


def titled_card(d, x, y, w, h, title, color):
    """Card with a uniform title; returns (body_x, body_y, inner_width)."""
    card(d, x, y, w, h, color)
    T(d, x + PAD, y + PAD, title, F(24, True), color, w - 2 * PAD)
    return x + PAD, y + PAD + TITLE_H, w - 2 * PAD


def bullets(d, x, y, items, maxw, sz=20, col=TXT, step=None, maxy=CONTENT_BOTTOM):
    """Bulleted list; marker aligned with the card title, long items wrap. Returns y after the last line."""
    font = F(sz); step = step or int(sz * 2.4); lh = int(sz * 1.4)
    for t in items:
        lines = wrap(t, font, maxw - 26)
        d.ellipse([x, y + lh / 2 - 5, x + 10, y + lh / 2 + 5], fill=SKY)
        yy = y
        for ln in lines:
            T(d, x + 26, yy + lh / 2, ln, font, col, maxw - 26, maxy, anchor='lm')
            yy += lh
        y = yy + (step - lh)
    return y - (step - lh)


def bullets_height(items, maxw, sz=20, step=None):
    font = F(sz); step = step or int(sz * 2.4); lh = int(sz * 1.4); h = 0
    for t in items:
        h += lh * len(wrap(t, font, maxw - 26)) + (step - lh)
    return h - (step - lh)


def bullet_card_h(items, inner, sz=20, step=None):
    return PAD + TITLE_H + bullets_height(items, inner, sz, step) + PAD


def chips(d, x, y, items, maxw, font, pad=18, gap=14, row=54, hgt=40, fill=CHIP, col=TXT, maxy=CONTENT_BOTTOM):
    x0 = x; cx = x
    for a in items:
        w = tw(a, font) + 2 * pad
        if w > maxw:
            raise Overflow(f'chip {a!r} wider than {maxw}px')
        if cx + w > x0 + maxw + 0.5:
            cx = x0; y += row
        if y + hgt > maxy:
            raise Overflow(f'chip {a!r} below bottom limit {maxy}')
        d.rounded_rectangle([cx, y, cx + w, y + hgt], hgt // 2, fill=fill)
        T(d, cx + pad, y + hgt / 2, a, font, col, w - 2 * pad, maxy, anchor='lm')
        cx += w + gap
    return y + hgt


def chips_height(items, maxw, font, pad=18, gap=14, row=54, hgt=40):
    cx = 0; rows = 1
    for a in items:
        w = tw(a, font) + 2 * pad
        if cx + w > maxw + 0.5:
            cx = 0; rows += 1
        cx += w + gap
    return hgt + (rows - 1) * row


def chip_row(d, x, y, items, maxw, font, gap=14, hgt=40, fill=CHIP, col=TXT):
    """One row of equal-width chips with centred labels (edges flush with the container)."""
    for (cx, cw), a in zip(cols(len(items), gap, x, maxw), items):
        if tw(a, font) > cw - 16:
            raise Overflow(f'chip {a!r} wider than {cw - 16}px')
        d.rounded_rectangle([cx, y, cx + cw, y + hgt], hgt // 2, fill=fill)
        TC(d, cx + cw / 2, y + hgt / 2 - font.size * 0.72, a, font, col, cw - 16)
    return y + hgt


def badge(d, right_x, cy, text, font, col, fill=CHIP, pad=20, hgt=44):
    """Right-aligned pill with vertically centred text."""
    w = tw(text, font) + 2 * pad
    d.rounded_rectangle([right_x - w, cy - hgt / 2, right_x, cy + hgt / 2], 10, fill=fill)
    T(d, right_x - w + pad, cy, text, font, col, w - 2 * pad, anchor='lm')
    return w


def stat_tiles(d, y, tiles, h, vsz=40, lsz=17):
    """Row of equal-width metric tiles: big value + caption, same baseline in every tile."""
    for (x, w), (v, lab, c) in zip(cols(len(tiles)), tiles):
        card(d, x, y, w, h, c)
        T(d, x + PAD, y + PAD, v, fit_font(v, w - 2 * PAD, vsz, True), c, w - 2 * PAD)
        T(d, x + PAD, y + h - PAD - lsz, lab, fit_font(lab, w - 2 * PAD, lsz), MUT, w - 2 * PAD)
    return y + h


def new_slide(num):
    im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=ACC); d.rectangle([0, H - 8, W, H], fill=ACC)
    T(d, MARGIN, H - 48, 'Корпоративный портал университета — Модуль Центра АНОК | 2026', F(16), MUT, maxy=H, anchor='lm')
    TR(d, W - MARGIN, H - 48 - 10, f'Слайд {num} из 12', F(16, True), SKY, maxy=H)
    return im, d


HEAD_TOP, HEAD_RULE = 8, 130          # header band: below the top bar, above the blue rule


def head(d, title, sub):
    """Header block (title + subtitle) and the right badge are centred between the two blue lines."""
    mid = (HEAD_TOP + HEAD_RULE) / 2
    bw, bx = 460, W - MARGIN - 460
    maxw = bx - GUT - MARGIN
    tf, sf = fit_font(title, maxw, 34, True), fit_font(sub, maxw, 18)
    gap = 10
    block = tf.size + gap + sf.size
    top = mid - block / 2
    T(d, MARGIN, top + tf.size / 2, title, tf, TXT, maxw, anchor='lm')
    T(d, MARGIN, top + tf.size + gap + sf.size / 2, sub, sf, MUT, maxw, anchor='lm')
    bh = 56
    d.rounded_rectangle([bx, mid - bh / 2, W - MARGIN, mid + bh / 2], 10, fill=PANEL)
    T(d, bx + 20, mid, 'ПРКП · Вариант 15 · Центр АНОК', F(16), MUT, bw - 40, anchor='lm')
    d.rectangle([0, HEAD_RULE, W, HEAD_RULE + 6], fill=ACC)


def render(num, title, sub, body, filename):
    """Draw `body(d, y0)` twice: a dry run to measure its height, then centred vertically."""
    scratch = ImageDraw.Draw(Image.new('RGB', (W, H), BG))
    bottom = body(scratch, CONTENT_TOP)
    free = CONTENT_BOTTOM - bottom
    if free < 0:
        raise Overflow(f'slide {num}: content {bottom - CONTENT_BOTTOM}px too tall')
    y0 = CONTENT_TOP + free // 2
    im, d = new_slide(num); head(d, title, sub)
    body(d, y0)
    im.save(f'{OUT}/{filename}')


# ----------------------------------------------------------------------------- S1 title
def s1():
    im, d = new_slide(1)
    cx = W // 2
    badge_txt = 'ИТОГОВАЯ ЗАЩИТА ПРОЕКТА КОРПОРАТИВНОГО ПОРТАЛА'
    bf = F(17, True); bw = tw(badge_txt, bf) + 80
    d.rounded_rectangle([cx - bw / 2, 140, cx + bw / 2, 196], 28, fill=ACC)
    T(d, cx - bw / 2 + 40, 168, badge_txt, bf, '#fff', bw - 80, anchor='lm')
    TC(d, cx, 250, 'Проектирование и разработка корпоративного веб-портала', F(40, True), TXT, W - 2 * MARGIN)
    TC(d, cx, 322, '«Модуль Центра аккредитации и независимой оценки', F(36, True), SKY, W - 2 * MARGIN)
    TC(d, cx, 382, 'качества образования (АНОК)»', F(36, True), SKY, W - 2 * MARGIN)
    feats = [('Нормативная база', ['ФГОС 3++', 'матрицы ЗЕТ', 'лимиты часов и компетенций'], ACC),
             ('Сквозной воркфлоу', ['Согласование УП', 'служебные записки', 'протоколы УС'], PURP),
             ('Криптография ЭЦП', ['Хеширование SHA-256', 'проверка УЦ', 'штампы'], GREEN),
             ('Интерактивный UX', ['Chart.js', 'FullCalendar', 'Diff-трекер версий', 'SheetJS'], SKY)]
    cy = 500; ch = PAD + TITLE_H + 4 * 30 + PAD - 6
    for (x, w), (t, lines, c) in zip(cols(4), feats):
        card(d, x, cy, w, ch, c)
        T(d, x + PAD, cy + PAD, t, F(22, True), TXT, w - 2 * PAD)
        for i, ln in enumerate(lines):
            T(d, x + PAD, cy + PAD + TITLE_H + i * 30, ln, F(16), MUT, w - 2 * PAD)
    iy = cy + ch + 60
    card(d, MARGIN, iy, W - 2 * MARGIN, 120, CHIP)
    T(d, MARGIN + PAD, iy + 40, 'Дисциплина: Проектирование и разработка корпоративных порталов (ПРКП)', F(18), MUT, 1100, anchor='lm')
    T(d, MARGIN + PAD, iy + 80, 'Специализация: Вариант № 15 (Университет — Центр АНОК)', F(18, True), SKY, 1100, anchor='lm')
    rx = W - MARGIN - PAD
    TR(d, rx, iy + 40 - 11, 'Выполнил: студент группы П-41 Соловьёв А.С.', F(18), TXT)
    TR(d, rx, iy + 80 - 11, 'Год разработки: 2026 · г. Москва', F(18), MUT)
    im.save(f'{OUT}/slide_01_title.png')


# ----------------------------------------------------------------------------- S2 context & goals
def s2(d, y):
    left = ['Центр АНОК: экспертиза и валидация УП по ФГОС ВО 3++', 'Объект автоматизации — учебный план (240 з.е., 8 семестров)',
            'Маршрут утверждения: каф. → АНОК → Проректор → Ректор', 'Служебные записки на корректировку дисциплин («Было → Стало»)']
    right = ['Алгоритмическая валидация нормативов (240 / 30 / ≤5 / ≥12 / ≥6)', 'Исключение ошибок несбалансированности з.е.',
             'Прозрачный жизненный цикл утверждения с ЭЦП (SHA-256)', 'Единое информационное пространство кафедр']
    (x1, cw), (x2, _) = cols(2); inner = cw - 2 * PAD
    ch = max(bullet_card_h(left, inner, 19), bullet_card_h(right, inner, 19))
    bx, by, iw = titled_card(d, x1, y, cw, ch, 'Предметная область', SKY); bullets(d, bx, by, left, iw, 19)
    bx, by, iw = titled_card(d, x2, y, cw, ch, 'Цели разработки', GREEN); bullets(d, bx, by, right, iw, 19)
    y += ch + GUT
    actors = ['Зав. выпускающей каф.', 'Зав. реализующей каф.', 'Эксперт АНОК', 'Начальник АНОК', 'Проректор по УР', 'Ректор',
              'Секретарь УС', 'Преподаватель / студент', 'Администратор']
    af = F(17, True); aw = W - 2 * MARGIN
    ah = PAD + TITLE_H + chips_height(actors, aw - 2 * PAD, af) + PAD
    bx, by, iw = titled_card(d, MARGIN, y, aw, ah, 'Основные акторы (9 ролей)', PURP)
    chips(d, bx, by, actors, iw, af, maxy=y + ah)
    y += ah + GUT
    T(d, MARGIN, y, 'Нормативные требования ФГОС ВО 3++, проверяемые порталом', F(22, True), AMBER)
    y += 44
    norms = [('240 з.е.', 'общая трудоемкость ОП', ACC), ('30 з.е.', 'в каждом из 8 семестров', SKY), ('≤ 5', 'экзаменов в сессию', AMBER),
             ('≥ 12 з.е.', 'практическая подготовка (Б2)', GREEN), ('≥ 6 з.е.', 'блок ГИА (Б3)', PURP)]
    return stat_tiles(d, y, norms, 130, 34, 16)


# ----------------------------------------------------------------------------- S3 architecture
def s3(d, y):
    layers = [('Web UI', 'HTML5/CSS3, адаптив, JS-модули (Chart.js, FullCalendar, DataTables, SheetJS, jsPDF, CryptoJS, SweetAlert2/Toastify, Diff2Html)', ACC),
              ('HTTP Router', '15 разделов + REST API (/api/stats, /api/plans, /api/announcements)', SKY),
              ('Service Layer', 'CurriculumService · ValidationEngine · WorkflowManager · MemoManager · AuditLogger', PURP),
              ('Data Access', 'PDO MySQL / sqlite3, Prepared Statements; СУБД MySQL 8 / MariaDB / SQLite (13 таблиц, FK)', GREEN)]
    lw = W - 2 * MARGIN; inner = lw - 2 * PAD
    for i, (name, desc, c) in enumerate(layers):
        h = PAD + TITLE_H + para_height(desc, F(21), inner, 32) + PAD - 8
        bx, by, iw = titled_card(d, MARGIN, y, lw, h, f'{i + 1}. {name}', c)
        para(d, bx, by, desc, F(21), TXT, iw, 32)
        if i < len(layers) - 1:
            d.polygon([(W // 2 - 14, y + h + 6), (W // 2 + 14, y + h + 6), (W // 2, y + h + 22)], fill=MUT)
        y += h + GUT
    metrics = [('< 50 мс', 'отклик страниц', GREEN), ('< 30 МБ', 'потребление RAM', SKY), ('python3 server.py', 'запуск одной командой', AMBER)]
    return stat_tiles(d, y, metrics, 120, 30, 16)


# ----------------------------------------------------------------------------- S4 data model
def s4(d, y):
    rows = [('curriculums', 'Реестр учебных планов', '1'), ('curriculum_disciplines', 'Семестровая матрица дисциплин', '51'),
            ('standards_fgos', 'Нормативы ФГОС 3++', '3'), ('educational_programs', 'Паспорта ОП', '1'), ('competencies', 'Матрица УК/ОПК/ПК', '13'),
            ('departments', 'Подразделения (выпускающие/обеспечивающие/АНОК)', '9'), ('document_signatures', 'Этапы визирования + SHA-256', '4'),
            ('service_notes', 'Служебные записки', '4'), ('service_note_items', 'Диффы «Было → Стало»', '4'), ('users', 'Учетные записи', '7'),
            ('roles', 'Роли доступа', '7'), ('announcements', 'Регламенты и объявления', '4'), ('audit_logs', 'Журнал аудита с IP', '7')]
    total = sum(int(r[2]) for r in rows)
    rows.append((f'Итого: {len(rows)} таблиц', 'записей в seed.sql', str(total)))
    grid = cols(2); rh, step = 90, 100
    for i, (nm, desc, cnt) in enumerate(rows):
        x, cw = grid[i % 2]; yy = y + (i // 2) * step
        is_total = i == len(rows) - 1
        card(d, x, yy, cw, rh, ACC if is_total else CHIP)
        T(d, x + PAD, yy + 32, nm, F(20, True), TXT if is_total else SKY, cw - 160, anchor='lm')
        T(d, x + PAD, yy + 62, desc, F(16), MUT, cw - 160, anchor='lm')
        bx = x + cw - PAD - 84
        d.rounded_rectangle([bx, yy + 20, bx + 84, yy + 70], 8, fill=ACC if is_total else CHIP, outline=ACC)
        TC(d, bx + 42, yy + 45 - 14, cnt, F(24, True), '#fff' if is_total else TXT, 84)
    y += (len(rows) + 1) // 2 * step - step + rh + GUT
    card(d, MARGIN, y, W - 2 * MARGIN, 64, GREEN)
    T(d, MARGIN + PAD, y + 32, 'Каскадная целостность: FOREIGN KEYS в schema.sql; PRAGMA foreign_key_check = 0 нарушений', F(19, True), GREEN, W - 2 * MARGIN - 2 * PAD, anchor='lm')
    return y + 64


# ----------------------------------------------------------------------------- S5 structure
def s5(d, y):
    groups = [('Учебные планы', ['dashboard', 'plans', 'plan (сем. 1–8)', 'competencies'], ACC),
              ('Качество / ФГОС', ['validate', 'standards', 'analytics (Chart.js)'], GREEN),
              ('Документооборот', ['signatures (ЭЦП)', 'memos (Diff)', 'calendar (FullCalendar)'], PURP),
              ('Справочники', ['programs', 'departments', 'announcements'], SKY),
              ('Служебные', ['audit', 'sitemap', 'REST API ×3'], AMBER)]
    rowh, rowstep = 56, 70
    ch = PAD + TITLE_H + rowstep * max(len(g[1]) for g in groups) - (rowstep - rowh) + PAD
    for (x, cw), (g, items, c) in zip(cols(5), groups):
        card(d, x, y, cw, ch, c)
        T(d, x + PAD - 8, y + PAD, g, fit_font(g, cw - 2 * PAD + 16, 22, True), c, cw - 2 * PAD + 16)
        yy = y + PAD + TITLE_H
        for it in items:
            d.rounded_rectangle([x + PAD - 8, yy, x + cw - PAD + 8, yy + rowh], 8, fill=CHIP)
            label = it if it.startswith('REST') else '?page=' + it
            T(d, x + PAD + 8, yy + rowh / 2, label, fit_font(label, cw - 2 * PAD - 16, 16), TXT, cw - 2 * PAD - 16, anchor='lm')
            yy += rowstep
    y += ch + GUT
    sem_items = [f'Семестр {i} · 30 з.е.' for i in range(1, 9)]
    sem_font = F(16, True); inner = W - 2 * MARGIN - 2 * PAD
    nh = PAD + TITLE_H + 36 + 44 + 40 + PAD
    bx, by, iw = titled_card(d, MARGIN, y, W - 2 * MARGIN, nh, 'Навигация', SKY)
    T(d, bx, by, 'Сайдбар: 14 пунктов меню + страница просмотра плана · адаптив ≤ 768px · футер со статусом синхронизации', F(19), MUT, iw)
    T(d, bx, by + 36, 'Сквозная семестровая навигация на странице плана (?page=plan&id=1&sem=N), баланс 30 з.е. / 1080 ч в каждом семестре:', F(17), TXT, iw)
    chip_row(d, bx, by + 36 + 44, sem_items, iw, sem_font)
    return y + nh


# ----------------------------------------------------------------------------- S6 fgos
def s6(d, y):
    hdr = ['Критерий', 'Норма', 'Факт', 'Статус']
    rows = [('Общая трудоемкость', '240 з.е.', '240 з.е.', 'СООТВЕТСТВУЕТ'), ('Баланс семестров 1–8', '30 з.е. / 1080 ч', '30 / 1080 в каждом', 'СООТВЕТСТВУЕТ'),
            ('Экзаменов в сессию', '≤ 5', '4', 'СООТВЕТСТВУЕТ'), ('Практическая подготовка (Б2)', '≥ 12 з.е.', '34 з.е.', 'СООТВЕТСТВУЕТ'),
            ('Блок ГИА (Б3)', '≥ 6 з.е.', '9 з.е.', 'СООТВЕТСТВУЕТ')]
    tx, tw_ = MARGIN, W - 2 * MARGIN
    offs = [PAD, 620, 1000, 1420]
    widths = [offs[1] - offs[0] - 20, offs[2] - offs[1] - 20, offs[3] - offs[2] - 20, tw_ - offs[3] - PAD]
    for off, htxt, wd in zip(offs, hdr, widths):
        T(d, tx + off, y + 14, htxt, F(20, True), SKY, wd, anchor='lm')
    d.rectangle([tx, y + 40, tx + tw_, y + 42], fill=CHIP)
    y += 56
    rh, step = 86, 100
    for r in rows:
        card(d, tx, y, tw_, rh, CHIP)
        for off, val, wd in zip(offs, r, widths):
            ok = val == 'СООТВЕТСТВУЕТ'
            T(d, tx + off, y + rh / 2 + 3, val, F(19, ok), GREEN if ok else TXT, wd, anchor='lm')
        y += step
    y += GUT - (step - rh)
    card(d, tx, y, tw_, 70, AMBER)
    T(d, tx + PAD, y + 38, 'Блоки УП: Б1.О 117 · Б1.В 71 · Б2 34 · Б3 9 · ФТД 9 з.е. = 240', F(20, True), AMBER, tw_ - 2 * PAD, anchor='lm')
    return y + 70


# ----------------------------------------------------------------------------- S7 memos
def s7(d, y):
    rows = [('СЗ-2026/048', 'Матанализ: 3 → 5 з.е., зачет → экзамен', 'ПРИМЕНЕНА', GREEN),
            ('СЗ-2026/052', 'Алгоритмизация: 36 ч практики → 36 ч лабораторных', 'ПРИМЕНЕНА', GREEN),
            ('СЗ-2026/059', 'Мобильная разработка → Каф. ИСТ', 'НА ЭКСПЕРТИЗЕ', PURP),
            ('СЗ-2026/061', 'График преддипломной практики: сдвиг на 2 недели', 'ВИЗА ВЫПУСКАЮЩЕЙ', SKY)]
    rx, rw = MARGIN, W - 2 * MARGIN; rh, step = 100, 116
    for nm, desc, st, c in rows:
        card(d, rx, y, rw, rh, c)
        cy = y + rh / 2 + 3
        T(d, rx + PAD, cy, nm, F(22, True), SKY, 240, anchor='lm')
        T(d, rx + PAD + 260, cy, desc, F(20), TXT, rw - PAD - 260 - 400, anchor='lm')
        badge(d, rx + rw - PAD, cy, st, F(19, True), c)
        y += step
    y += GUT - (step - rh)
    dh = PAD + TITLE_H + 38 + 12 + 38 + PAD
    bx, by, iw = titled_card(d, rx, y, rw, dh, 'Diff2Html (side-by-side): СЗ-2026/048', RED)
    d.rounded_rectangle([bx, by, bx + iw, by + 38], 6, fill='#3b1f24')
    T(d, bx + 14, by + 19, '- Семестр 1: Матанализ — 3 з.е. (108 ч.) · Зачет · Каф. ВМ', F(18), RED, iw - 28, anchor='lm')
    d.rounded_rectangle([bx, by + 50, bx + iw, by + 88], 6, fill='#1b3a30')
    T(d, bx + 14, by + 69, '+ Семестр 1: Матанализ — 5 з.е. (180 ч.) [+2 з.е.] · Экзамен · Каф. ВМ', F(18), GREEN, iw - 28, anchor='lm')
    return y + dh


# ----------------------------------------------------------------------------- S8 signatures
def s8(d, y):
    steps = [('1', 'Руководитель выпускающего подразделения', 'Иванов И.И. (Зав. каф. ПИ)', '2026-06-15', 'da15dc1a…ede6'),
             ('2', 'Начальник Центра АНОК', 'Кузнецов В.П. (Нач. АНОК)', '2026-06-18', '2e4aab7…6dc9'),
             ('3', 'Проректор по учебной работе', 'Смирнов А.Н. (Проректор по УР)', '2026-06-22', '67c1ef7…1f2d'),
             ('4', 'Ректор университета', 'Михайлов С.В. (Ректор) · протокол УС № 8/26 от 25.06.2026', '2026-06-25', '36f5e44…184')]
    sx, sw_ = MARGIN, W - 2 * MARGIN; rh, step = 136, 152
    for n, role, who, dt, hh in steps:
        card(d, sx, y, sw_, rh, GREEN)
        cx, cy = sx + PAD + 30, y + rh / 2 + 3
        d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=ACC)
        TC(d, cx, cy - 15, n, F(26, True), '#fff', 60)
        tx = sx + PAD + 90; tw_ = sw_ - PAD - 90 - PAD
        T(d, tx, y + 22, role, F(22, True), TXT, tw_)
        T(d, tx, y + 60, f'{who} · {dt}', F(17), MUT, tw_)
        T(d, tx, y + 94, f'SHA-256: {hh} · [MATCH] (пересчет совпадает с хранилищем)', F(15), GREEN, tw_)
        y += step
    y += GUT - (step - rh)
    card(d, sx, y, sw_, 70, SKY)
    T(d, sx + PAD, y + 38, 'Верификация на странице ?page=signatures: CryptoJS пересчитывает payload и сверяет с БД (4 из 4 действительны)', F(19), MUT, sw_ - 2 * PAD, anchor='lm')
    return y + 70


# ----------------------------------------------------------------------------- S9 analytics
def s9(d, y):
    vals = [('117', 'Б1.О обязательная з.е.', ACC), ('71', 'Б1.В вариативная з.е.', SKY), ('34', 'Б2 практики з.е.', GREEN), ('9', 'Б3 ГИА з.е.', AMBER), ('9', 'ФТД з.е.', PURP)]
    y = stat_tiles(d, y, vals, 150, 46, 18) + GUT
    left = ['Учебные планы: 1 · Дисциплины: 51', 'Стандарты ФГОС: 3 · Служебные записки: 4', 'Реестр УП с переходом к семестровой сетке', 'Лента закрепленных регламентов АНОК']
    right = ['Doughnut: структура блоков (117/71/34/9/9)', 'Radar: покрытие компетенций УК 5 · ОПК 4 · ПК 4', 'Stacked Bar: 1080 ч в каждом семестре',
             'Данные диаграмм вычисляются на сервере из БД']
    (x1, cw), (x2, _) = cols(2); inner = cw - 2 * PAD
    ch = max(bullet_card_h(left, inner, 20), bullet_card_h(right, inner, 20))
    bx, by, iw = titled_card(d, x1, y, cw, ch, 'Сводная панель', SKY); bullets(d, bx, by, left, iw, 20)
    bx, by, iw = titled_card(d, x2, y, cw, ch, 'Диаграммы Chart.js', PURP); bullets(d, bx, by, right, iw, 20)
    y += ch + GUT
    eh = PAD + TITLE_H + 26 + PAD - 6
    bx, by, iw = titled_card(d, MARGIN, y, W - 2 * MARGIN, eh, 'Экспорт страницы плана', GREEN)
    T(d, bx, by, 'SheetJS → XLSX семестровой сетки · jsPDF → PDF-выписка из учебного плана · window.print() → печать бланка УП', F(19), MUT, iw)
    return y + eh


# ----------------------------------------------------------------------------- S10 ux
def s10(d, y):
    tok = [('#0f172a', 'header'), ('#1e293b', 'sidebar'), ('#f8fafc', 'page'), ('#2563eb', 'primary'), ('#15803d', 'ok'), ('#b91c1c', 'err'), ('#7e22ce', 'anok'), ('#b45309', 'warn')]
    for (x, w), (c, nm) in zip(cols(8, gap=24), tok):
        d.rounded_rectangle([x, y, x + w, y + 80], 10, fill=c, outline='#475569')
        T(d, x + 12, y + 92, nm, F(15), MUT, w - 12)
        T(d, x + 12, y + 114, c, F(13), '#6b7280', w - 12)
    y += 140 + GUT
    left = ['Header 60px sticky + Sidebar 240px + Main 1200px + Footer', 'Типографика: 24/18/14/12px, системный стек шрифтов',
            'Адаптив ≤ 768px: сайдбар 70px, overflow-x таблиц', '14 пунктов меню, подсветка активного раздела']
    right = ['DataTables: живой поиск и пагинация плана', 'SheetJS / jsPDF: экспорт XLSX и PDF', 'FullCalendar: график процедур АНОК',
             'Diff2Html: сравнение версий УП', 'SweetAlert2 / Toastify: диалоги и уведомления']
    (x1, cw), (x2, _) = cols(2); inner = cw - 2 * PAD
    ch = max(bullet_card_h(left, inner, 19), bullet_card_h(right, inner, 19))
    bx, by, iw = titled_card(d, x1, y, cw, ch, 'Шаблон дизайна', SKY); bullets(d, bx, by, left, iw, 19)
    bx, by, iw = titled_card(d, x2, y, cw, ch, 'Готовые модули (ЛР № 6)', GREEN); bullets(d, bx, by, right, iw, 19)
    y += ch + GUT
    eh = PAD + TITLE_H + 26 + PAD - 6
    bx, by, iw = titled_card(d, MARGIN, y, W - 2 * MARGIN, eh, 'Принципы', PURP)
    T(d, bx, by, 'Единая палитра из ЛР № 3 · статусные бейджи · семестровая навигация 1–8 на каждой странице плана · деградация без CDN', F(19), MUT, iw)
    return y + eh


# ----------------------------------------------------------------------------- S11 security
def s11(d, y):
    left = ['Prepared Statements — исключены SQL-инъекции', 'htmlspecialchars / html.escape — защита от XSS',
            'FOREIGN KEYS — ссылочная целостность (0 нарушений)', 'PRAGMA foreign_key_check — контроль при каждом старте']
    right = ['7 записей: время, пользователь, роль, действие, статус, IP', 'Живой поиск по журналу (client-side)',
             'Фиксация валидаций, виз ЭЦП и служебных записок', 'Статусные бейджи: УСПЕШНО / ОШИБКА / ОБНОВЛЕНО']
    (x1, cw), (x2, _) = cols(2); inner = cw - 2 * PAD
    ch = max(bullet_card_h(left, inner, 20, 54), bullet_card_h(right, inner, 20, 54))
    bx, by, iw = titled_card(d, x1, y, cw, ch, 'Безопасность', GREEN); bullets(d, bx, by, left, iw, 20, step=54)
    bx, by, iw = titled_card(d, x2, y, cw, ch, 'Журнал аудита', SKY); bullets(d, bx, by, right, iw, 20, step=54)
    y += ch + GUT
    tests = [('15 / 15', 'страниц отвечают HTTP 200', GREEN), ('3 / 3', 'REST-эндпоинта возвращают JSON', SKY),
             ('5 / 5', 'критериев ФГОС подтверждены', AMBER), ('4 / 4', 'подписей SHA-256 верифицированы', PURP)]
    y = stat_tiles(d, y, tests, 170, 48, 18) + GUT
    card(d, MARGIN, y, W - 2 * MARGIN, 70, CHIP)
    T(d, MARGIN + PAD, y + 38, 'Все 15 страниц и 3 REST-эндпоинта отвечают HTTP 200 · оффлайн-деградация CDN-модулей без потери данных (проверка typeof перед вызовом библиотек)', F(19), MUT, W - 2 * MARGIN - 2 * PAD, anchor='lm')
    return y + 70


# ----------------------------------------------------------------------------- S12 conclusion
def s12(d, y):
    items = ['Полный цикл ЛР № 1–7: требования → проектирование → дизайн → разделы → инфоблоки → модули → защита',
             'Портал: 15 разделов + REST API, 13 таблиц БД с FOREIGN KEYS, 51 дисциплина (240 з.е., баланс 30/1080)',
             'Экспертиза ФГОС 3++: 5/5 критериев соответствуют; маршрут ЭЦП 4 этапа с верификацией SHA-256',
             '9 готовых модулей: Chart.js, FullCalendar, DataTables, SheetJS, jsPDF, CryptoJS, SweetAlert2, Toastify, Diff2Html',
             'Комплект документов: 7 отчетов (MD/DOCX/PDF), пояснительная записка, презентация 12 слайдов']
    rw = W - 2 * MARGIN; inner = rw - 2 * PAD
    ch = bullet_card_h(items, inner, 24, 72)
    bx, by, iw = titled_card(d, MARGIN, y, rw, ch, 'Результаты проекта', SKY)
    bullets(d, bx, by, items, iw, 24, step=72)
    y += ch + GUT
    fh = PAD + TITLE_H + 30 + PAD
    card(d, MARGIN, y, rw, fh, ACC)
    T(d, MARGIN + PAD, y + PAD, 'Итог: требования варианта № 15 выполнены полностью', F(28, True), SKY, inner)
    T(d, MARGIN + PAD, y + PAD + TITLE_H + 4, 'Москва, 2026 · студент группы П-41 Соловьёв А.С.', F(20), MUT, inner)
    return y + fh


# ----------------------------------------------------------------------------- build
s1()
render(2, 'Контекст и цели проекта', 'Предметная область, акторы и нормативные требования', s2, 'slide_02_context_goals.png')
render(3, 'Архитектура и стек технологий', 'Многоуровневая архитектура без тяжеловесных фреймворков', s3, 'slide_03_architecture_stack.png')
render(4, 'Информационная модель и структура базы данных', '13 нормализованных таблиц (3NF) с FOREIGN KEYS', s4, 'slide_04_data_model.png')
render(5, 'Структура портала и навигация', '15 функциональных страниц + сквозная семестровая навигация', s5, 'slide_05_portal_structure.png')
render(6, 'Автоматизированная экспертиза ФГОС ВО 3++', 'Все показатели вычисляются из БД (функция validate_curriculum)', s6, 'slide_06_fgos_validation.png')
render(7, 'Управление изменениями УП', 'Служебные записки с версионными изменениями «Было → Стало»', s7, 'slide_07_visual_diff.png')
render(8, 'Цифровое визирование и ЭЦП', '4 этапа согласования с криптографическими штампами SHA-256', s8, 'slide_08_crypto_signature.png')
render(9, 'Аналитика и сводная панель', 'Chart.js: структура блоков, компетенции, часы по семестрам', s9, 'slide_09_analytics_export.png')
render(10, 'Пользовательский интерфейс', 'Адаптивный дизайн, единая палитра, готовые модули', s10, 'slide_10_interactive_ux.png')
render(11, 'Тестирование и безопасность', 'Защита данных и протоколирование действий', s11, 'slide_11_testing_security.png')
render(12, 'Заключение и результаты', 'Портал Центра АНОК готов к демонстрации и защите', s12, 'slide_12_conclusion_impact.png')
print('slides done')

# ----------------------------------------------------------------------------- PPTX + PDF
SLIDES = sorted(f for f in os.listdir(OUT) if f.startswith('slide_') and f.endswith('.png'))
assert len(SLIDES) == 12, SLIDES
REP = f'{ROOT}/reports/lab7'

try:
    from pptx import Presentation
    from pptx.util import Emu
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(12192000), Emu(6858000)  # 16:9, matches 1920x1080 images
    blank = prs.slide_layouts[6]
    for f in SLIDES:
        s = prs.slides.add_slide(blank)
        s.shapes.add_picture(f'{OUT}/{f}', 0, 0, prs.slide_width, prs.slide_height)
    prs.core_properties.title = 'Корпоративный портал университета — Модуль Центра АНОК (Вариант 15)'
    prs.core_properties.author = 'Соловьёв А.С., группа П-41'
    prs.save(f'{REP}/LR7_Presentation_Variant15.pptx')
    print('pptx done')
except ImportError:
    print('python-pptx not installed — PPTX not rebuilt')

imgs = [Image.open(f'{OUT}/{f}').convert('RGB') for f in SLIDES]
imgs[0].save(f'{REP}/LR7_Presentation_Variant15.pdf', save_all=True, append_images=imgs[1:], resolution=72.0,
             title='Корпоративный портал университета — Модуль Центра АНОК (Вариант 15)', author='Соловьёв А.С., группа П-41')
print('pdf done')
