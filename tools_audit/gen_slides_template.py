# -*- coding: utf-8 -*-
"""Презентация ЛР7 по приложенному шаблону (4:3, 720×540 pt, 14 слайдов).

Шаблон: белый фон, чёрный текст без рамок и колонтитулов, заголовок по центру,
маркированные списки «•», таблица сравнения средств с синей шапкой и светлыми
строками, слайды с диаграммами — только заголовок и рисунок.

Слайды рендерятся в 1600×1200 px и вставляются в PPTX 10×7,5 дюйма без полей,
поэтому pptx, pdf и png совпадают попиксельно.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'diagrams', 'lab7')
REP = os.path.join(ROOT, 'reports', 'lab7')
os.makedirs(OUT, exist_ok=True)

FD = '/usr/share/fonts/truetype/dejavu/'
W, H = 1600, 1200
M = 96                       # поля (≈40 pt)
TITLE_TOP = 62
TITLE_SZ = 62
BLACK = '#000000'
GREY = '#808080'
BLUE = '#4472c4'
ROW_A = '#dce6f2'
ROW_B = '#c9d6ee'

_f = {}


def F(sz, bold=False):
    k = (sz, bold)
    if k not in _f:
        _f[k] = ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz)
    return _f[k]


_meas = ImageDraw.Draw(Image.new('RGB', (1, 1)))


def tw(s, sz, bold=False):
    return _meas.textlength(s, font=F(sz, bold))


def wrap(s, sz, maxw, bold=False):
    out, cur = [], ''
    for w in s.split():
        probe = (cur + ' ' + w).strip()
        if cur and tw(probe, sz, bold) > maxw:
            out.append(cur)
            cur = w
        else:
            cur = probe
    out.append(cur)
    return out


class Slide:
    def __init__(self):
        self.im = Image.new('RGB', (W, H), 'white')
        self.d = ImageDraw.Draw(self.im)
        self.y = 0

    def title(self, text, sz=TITLE_SZ, bold=False, top=TITLE_TOP):
        lines = wrap(text, sz, W - 2 * M, bold)
        lh = int(sz * 1.18)
        y = top
        for ln in lines:
            self.d.text((W / 2, y), ln, font=F(sz, bold), fill=BLACK, anchor='ma')
            y += lh
        self.y = y + 46

    def bullets(self, items, sz=40, lh=30, indent=0, gap=18):
        """items: строки; строка, начинающаяся с ' ' — подпункт без маркера."""
        for it in items:
            if it.startswith('  '):
                lines = wrap(it.strip(), sz, W - 2 * M - 60 - indent)
                x = M + 60 + indent
                for i, ln in enumerate(lines):
                    self.d.text((x, self.y), ln, font=F(sz), fill=BLACK, anchor='la')
                    self.y += int(sz * 1.25)
            else:
                lines = wrap(it, sz, W - 2 * M - 40 - indent)
                for i, ln in enumerate(lines):
                    if i == 0:
                        self.d.text((M + indent, self.y), '•', font=F(sz), fill=BLACK, anchor='la')
                    self.d.text((M + 42 + indent, self.y), ln, font=F(sz), fill=BLACK, anchor='la')
                    self.y += int(sz * 1.25)
            self.y += gap
        self.y += lh

    def table(self, head, rows, col0=420, head_h=112, row_h=92, sz=25):
        """Таблица шаблона: синяя шапка, светлые строки, диагональ в 1-й ячейке."""
        total = W - 2 * M
        ncol = len(head)
        cw = [col0] + [(total - col0) / (ncol - 1)] * (ncol - 1)
        x, y = M, self.y
        self.d.rectangle([x, y, x + total, y + head_h], fill=BLUE)
        cx = x
        for i, h in enumerate(head):
            if i:
                self.d.line([cx, y, cx, y + head_h], fill='white', width=3)
            if h:
                lines = wrap(h, sz, cw[i] - 26, True)[:2]
                lh = int(sz * 1.2)
                ty = y + head_h / 2 - (len(lines) - 1) * lh / 2
                for k, ln in enumerate(lines):
                    self.d.text((cx + cw[i] / 2, ty + k * lh), ln, font=F(sz, True),
                                fill='white', anchor='mm')
            cx += cw[i]
        # диагональ и подписи «критерий / средство» в левой ячейке шапки
        self.d.line([x, y + head_h, x + cw[0], y], fill='white', width=3)
        self.d.text((x + 16, y + 12), 'Критерий', font=F(24), fill='white', anchor='la')
        self.d.text((x + cw[0] - 16, y + head_h - 40), 'Средство', font=F(24),
                    fill='white', anchor='la')
        y += head_h
        for r, row in enumerate(rows):
            self.d.rectangle([x, y, x + total, y + row_h],
                             fill=ROW_A if r % 2 == 0 else ROW_B)
            cx = x
            for i, cell in enumerate(row):
                if i:
                    self.d.line([cx, y, cx, y + row_h], fill='white', width=3)
                lines = wrap(cell, sz, cw[i] - 26)[:2]
                lh = int(sz * 1.2)
                ty = y + row_h / 2 - (len(lines) - 1) * lh / 2
                for k, ln in enumerate(lines):
                    self.d.text((cx + 14, ty + k * lh), ln, font=F(sz), fill=BLACK, anchor='lm')
                cx += cw[i]
            y += row_h
        self.y = y + 34

    def picture(self, path, bottom=H - 46, pad_top=22):
        im = Image.open(path).convert('RGB')
        # обрезаем белые поля картинки: иначе диаграмма занимает пол-слайда
        from PIL import ImageOps
        box = ImageOps.invert(im.convert('L')).getbbox()
        if box:
            m = 10
            im = im.crop((max(0, box[0] - m), max(0, box[1] - m),
                          min(im.width, box[2] + m), min(im.height, box[3] + m)))
        top = self.y + pad_top
        box_w, box_h = W - 2 * M, bottom - top
        sc = min(box_w / im.width, box_h / im.height)
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        self.im.paste(im, (int(W / 2 - im.width / 2), int(top + (box_h - im.height) / 2)))
        self.y = bottom

    def caption(self, text, sz=26):
        self.d.text((W / 2, H - 54), text, font=F(sz), fill=GREY, anchor='ma')

    def save(self, name):
        p = os.path.join(OUT, name)
        self.im.save(p)
        return p


# ------------------------------------------------------------------ 1. титул
s = Slide()
title = 'Разработка корпоративного портала на тему «Университет. Центр аккредитации и независимой оценки качества образования (АНОК)»'
lines = wrap(title, 60, W - 2 * M - 60)
y = 300
for ln in lines:
    s.d.text((W / 2, y), ln, font=F(60), fill=BLACK, anchor='ma')
    y += 74
for ln in ('Выполнил: студент группы П-41 Соловьёв А.С.',
           'Проверил: к.т.н. Шевнина Ю.С.'):
    y += 34
    s.d.text((W / 2, y), ln, font=F(38), fill=GREY, anchor='ma')
    y += 46
s.save('tpl_slide_01_title.png')

# ------------------------------------------------------------------ 2. цель
s = Slide()
s.title('Цель работы')
s.bullets([
    'Цель: разработать корпоративный портал Центра АНОК, автоматизирующий ведение, '
    'экспертизу и утверждение учебных планов вуза по ФГОС ВО 3++.',
    'Задачи:',
    '  проанализировать предметную область и сформулировать требования (ЛР1);',
    '  спроектировать модель данных и построить UML-диаграммы (ЛР2);',
    '  разработать шаблон дизайна и интерфейсы разделов (ЛР3–ЛР5);',
    '  подключить готовые модули: DataTables, Chart.js, FullCalendar, CryptoJS (ЛР6);',
    '  развернуть стенд, наполнить данными, проверить сценарии и оформить отчёт (ЛР7).',
], sz=36)
s.save('tpl_slide_02_goal.png')

# ------------------------------------------------------------------ 3. область
s = Slide()
s.title('Краткое описание предметной области')
s.bullets([
    'Центр АНОК ведёт реестр образовательных программ и учебных планов университета.',
    'План содержит 51 дисциплину по 8 семестрам: 240 з.е., 8640 часов, формы контроля, '
    'обеспечивающие кафедры.',
    'Проверка ФГОС автоматизирована: 240 з.е. всего, 30 з.е. в семестре, не более 5 экзаменов '
    'в сессию, не менее 12 з.е. практик и 6 з.е. ГИА.',
    'Маршрут визирования: заведующий кафедрой → эксперт АНОК → проректор по УР → ректор; '
    'каждый шаг подтверждается ЭЦП с хэшем SHA-256.',
    'Служебные записки фиксируют изменения дисциплин «Было → Стало», все действия попадают '
    'в журнал аудита.',
], sz=33)
s.save('tpl_slide_03_domain.png')

# ------------------------------------------------------------------ 4. use case
s = Slide()
s.title('Диаграмма вариантов использования')
s.picture(os.path.join(ROOT, 'diagrams', 'use_case_diagram.png'))
s.save('tpl_slide_04_usecase.png')

# ------------------------------------------------------------------ 5. требования
s = Slide()
s.title('Требования к порталу')
s.bullets([
    'Функциональные:',
    '  реестр планов и семестровая карточка с поиском, сортировкой и экспортом в Excel и PDF;',
    '  автоматическая экспертиза ФГОС с перечнем замечаний и возвратом на доработку;',
    '  электронное визирование с проверкой хэшей SHA-256 и статусами этапов;',
    '  служебные записки с визуальным сравнением версий;',
    '  журнал аудита, роли и разграничение доступа к документам.',
    'Нефункциональные:',
    '  запуск без внешних сервисов: Python 3.11 и SQLite (или MySQL);',
    '  параметризованные запросы, адаптивная вёрстка, готовые отчёты.',
], sz=33)
s.save('tpl_slide_05_requirements.png')

# ------------------------------------------------------------------ 6. сравнение
s = Slide()
s.title('Результат сравнения инструментальных средств разработки портала', sz=52)
s.table(
    ['', 'Drupal 11 + PHP', 'Собственный модуль (Python)', '1С-Битрикс'],
    [
        ['Готовый предметный модуль', 'нужен свой', 'входит в проект', 'нет'],
        ['Стоимость лицензии', '0 ₽', '0 ₽', 'от 150 000 ₽'],
        ['Требования к хостингу', 'PHP 8.4 + MySQL', 'Python 3.11 + SQLite', 'PHP + MySQL, 512 МБ'],
        ['Скорость развёртывания', 'средняя', 'высокая', 'низкая'],
        ['Гибкость доработки', 'средняя', 'высокая', 'средняя'],
        ['Вывод', 'избыточен для ЛР', 'выбран', 'избыточен по цене'],
    ], col0=420, sz=25)
s.save('tpl_slide_06_comparison.png')

# ------------------------------------------------------------------ 7. классы
s = Slide()
s.title('Диаграмма классов')
s.picture(os.path.join(ROOT, 'diagrams', 'lab2', 'class_diagram.png'))
s.save('tpl_slide_07_class.png')

# ------------------------------------------------------------------ 8. деятельность
s = Slide()
s.title('Диаграмма деятельности')
s.picture(os.path.join(OUT, 'activity_diagram.png'))
s.save('tpl_slide_08_activity.png')

# ------------------------------------------------------------------ 9. развёртывание
s = Slide()
s.title('Диаграмма развертывания')
s.picture(os.path.join(ROOT, 'diagrams', 'lab2', 'deployment_diagram.png'))
s.save('tpl_slide_09_deployment.png')

# ------------------------------------------------------------------ 10. компоненты
s = Slide()
s.title('Диаграмма компонентов')
s.picture(os.path.join(ROOT, 'diagrams', 'lab2', 'component_diagram.png'))
s.save('tpl_slide_10_components.png')

# ------------------------------------------------------------------ 11. схема БД
s = Slide()
s.title('Схема БД')
s.picture(os.path.join(ROOT, 'diagrams', 'lab2', 'db_schema_diagram.png'))
s.save('tpl_slide_11_db.png')

# ------------------------------------------------------------------ 12. установка
s = Slide()
s.title('Пример установленного и настроенного программного обеспечения')
s.y = 250
s.bullets([
    'Стенд развёрнут на Python 3.11 со встроенным HTTP-сервером и СУБД SQLite.',
    'Запуск: python portal/server.py → http://127.0.0.1:8000/',
    'База anok_portal создаётся автоматически и наполняется демонстрационными данными.',
], sz=31, gap=10)
s.picture(os.path.join(ROOT, 'diagrams', 'lab2', 'screen_dashboard.png'), bottom=H - 90)
s.save('tpl_slide_12_installed.png')

# ------------------------------------------------------------------ 13. интерфейсы
s = Slide()
s.title('Примеры пользовательских интерфейсов')
top_min = 230
cap_h = 44
bw = (W - 2 * M - 40) / 2
bh = H - 70 - cap_h - top_min
pics = [os.path.join(ROOT, 'diagrams', 'lab2', 'screen_plan_grid.png'),
        os.path.join(ROOT, 'diagrams', 'lab2', 'screen_fgos_validation.png')]
caps = ['Учебный план по семестрам', 'Экспертиза ФГОС ВО 3++']
sizes = []
for pr in pics:
    im = Image.open(pr).convert('RGB')
    sc = min(bw / im.width, bh / im.height)
    sizes.append((im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)))
imh = max(i.height for i in sizes)
top = top_min + (bh - imh) / 2
for i, im in enumerate(sizes):
    x = M + i * (bw + 40) + (bw - im.width) / 2
    s.im.paste(im, (int(x), int(top)))
    s.d.text((M + i * (bw + 40) + bw / 2, top + imh + 14), caps[i],
             font=F(28), fill=GREY, anchor='ma')
s.save('tpl_slide_13_ui.png')

# ------------------------------------------------------------------ 14. результаты
s = Slide()
s.title('Результаты')
s.bullets([
    '15 разделов портала, 13 таблиц базы данных в 3НФ, 51 дисциплина, 240 з.е.',
    '4 этапа визирования с ЭЦП SHA-256, 7 ролей, неизменяемый журнал аудита.',
    'Экспорт плана в Excel и PDF, аналитика Chart.js, календарь FullCalendar, '
    'сравнение версий Diff2Html.',
    'Портал развёрнут локально и проверен по сценариям ЛР1–ЛР6.',
    'Подготовлены отчёты ЛР1–ЛР7, пояснительная записка и презентация.',
], sz=34)
s.save('tpl_slide_14_results.png')

# ------------------------------------------------------------------ pptx + pdf
slides = sorted(f for f in os.listdir(OUT) if f.startswith('tpl_slide_') and f.endswith('.png'))
assert len(slides) == 14, slides

from pptx import Presentation
from pptx.util import Emu

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(9144000), Emu(6858000)   # 10 × 7,5 дюйма, 4:3
blank = prs.slide_layouts[6]
for f in slides:
    sl = prs.slides.add_slide(blank)
    sl.shapes.add_picture(os.path.join(OUT, f), 0, 0, prs.slide_width, prs.slide_height)
prs.core_properties.title = 'Корпоративный портал университета — Модуль Центра АНОК (Вариант 15)'
prs.core_properties.author = 'Соловьёв А.С., группа П-41'
prs.save(os.path.join(REP, 'LR7_Presentation_Variant15.pptx'))

imgs = [Image.open(os.path.join(OUT, f)).convert('RGB') for f in slides]
imgs[0].save(os.path.join(REP, 'LR7_Presentation_Variant15.pdf'), save_all=True,
             append_images=imgs[1:], resolution=160.0,
             title='Корпоративный портал университета — Модуль Центра АНОК (Вариант 15)',
             author='Соловьёв А.С., группа П-41')
print('slides:', len(slides), '→ pptx + pdf')
