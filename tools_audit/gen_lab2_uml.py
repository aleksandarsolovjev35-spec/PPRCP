# -*- coding: utf-8 -*-
"""Генератор UML-диаграмм для ЛР № 2 (полная нотация UML 2.5).

Диаграммы:
  * class_diagram.png        — диаграмма классов (атрибуты, операции, кратности,
                               композиция, генерализация, примечания);
  * component_diagram.png    — диаграмма компонентов («component», порты,
                               предоставляемые/требуемые интерфейсы «шарик-гнездо»);
  * deployment_diagram.png   — диаграмма развёртывания («device», среда исполнения,
                               артефакты, линии связи с протоколами);
  * sequence_diagram.png     — диаграмма последовательности (акторы, линии жизни,
                               активации, синхронные/возвратные сообщения, alt/loop);
  * db_schema_diagram.png    — реляционная схема (нотация «воронья лапка», PK/FK,
                               типы, обязательность, кратности 1:N).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from uml_kit import (Canvas, INK, MUTED, LINE, BLUE, HEAD_FILL, ACCENT,  # noqa: E402
                     title, note, legend_box)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'diagrams', 'lab2')

# Рамка фрагмента — аннотация, а не связь: серый длинный пунктир.
# Возвраты сообщений — чёрный короткий пунктир. Так их не спутать.
FRAME_LINE = '#9aa3b2'
F_NAME, F_STEREO, F_MEMBER, F_MULT = 13, 9.5, 10.2, 10.0
LH = 15.4          # межстрочный интервал в секциях атрибутов/операций
HDR = 30.0         # высота секции имени
PAD = 7.0


# ======================================================================
#  Диаграмма классов
# ======================================================================
F_NAME, F_STEREO, F_MEMBER, F_MULT = 14.0, 9.8, 11.6, 10.4
LH = 17.4          # межстрочный интервал в секциях атрибутов/операций
HDR = 33.0         # высота секции имени
PAD = 7.0


def _measure_class(spec, w):
    h = HDR + (14 if (spec.get('stereo') or spec.get('abstract')) else 0) + (15 if spec.get('ru') else 0) + PAD
    h += len(spec['attrs']) * LH + 5
    h += len(spec['ops']) * LH + 14
    return h


def draw_class(c, x, y, w, spec):
    stereo = spec.get('stereo')
    h = _measure_class(spec, w)
    hdr_h = HDR + (14 if (stereo or spec.get('abstract')) else 0) + (15 if spec.get('ru') else 0)
    GEOM['boxes'].append((spec['name'], x, y, x + w, y + h))
    c.rect(x, y, w, h, fill='#ffffff', outline=LINE, width=1.4)
    c.rect(x + 1, y + 1, w - 2.2, hdr_h - 1.6, fill='#f2f2f2', outline=None)
    c.line([(x, y + hdr_h), (x + w, y + hdr_h)], fill=LINE, width=1.2)
    cy = y + 15
    if stereo:
        c.text(x + w / 2, cy + 1, '«%s»' % stereo, F_STEREO, 'normal', '#374151', anchor='ms')
        cy += 14
    elif spec.get('abstract'):
        c.text(x + w / 2, cy + 1, '{abstract}', F_STEREO, 'normal', '#374151', anchor='ms')
        cy += 14
    weight = 'bolditalic' if spec.get('abstract') else 'bold'
    c.text(x + w / 2, cy + 12, spec['name'], F_NAME, weight, INK, anchor='ms')
    if spec.get('ru'):
        c.text(x + w / 2, cy + 27, spec['ru'], 9.6, 'italic', '#374151', anchor='ms')
    ay = y + hdr_h + PAD + LH * 0.70
    for a in spec['attrs']:
        c.text_clip(x + 11, ay, a, w - 22, F_MEMBER, 'normal', '#1f2937')
        ay += LH
    sep = y + hdr_h + PAD + len(spec['attrs']) * LH + 5
    c.line([(x, sep), (x + w, sep)], fill=LINE, width=1.2)
    oy = sep + PAD + LH * 0.70
    for o in spec['ops']:
        c.text_clip(x + 11, oy, o, w - 22, F_MEMBER, 'normal', '#1f2937')
        oy += LH
    return h


GEOM = {'boxes': [], 'polys': [], 'labels': [], 'colors': [], 'ends': [],
        'mults': [], 'roles': [], 'containers': [], 'bars': [], 'lifelines': []}


def _poly(pts, color=LINE, width=1.3):
    """Регистрирует ломаную связи вместе с её цветом (для разрывов на пересечениях)."""
    GEOM['polys'].append(list(pts))
    GEOM['colors'].append((color, width))


def _geom_reset():
    GEOM['boxes'], GEOM['polys'], GEOM['labels'], GEOM['colors'], GEOM['ends'] = [], [], [], [], []
    GEOM['mults'], GEOM['roles'], GEOM['containers'] = [], [], []
    GEOM['bars'], GEOM['lifelines'] = [], []


def _lab(c, x, y, text, anchor='ls', size=F_MULT, fill='#111827', weight='normal'):
    """Подпись с белой подложкой (чтобы линия не пересекала текст)."""
    w = c.tw(text, size, weight)
    if anchor[0] == 'l':
        x0 = x
    elif anchor[0] == 'r':
        x0 = x - w
    else:
        x0 = x - w / 2
    c.d.rectangle([x0 * c.s - 2.5 * c.s, (y - size * 0.95) * c.s - 1,
                   (x0 + w) * c.s + 2.5 * c.s, (y + size * 0.32) * c.s + 1], fill='#ffffff')
    c.text(x, y, text, size, weight, fill, anchor=anchor)
    GEOM['labels'].append((text, x0 - 2.5, y - size * 0.95, x0 + w + 2.5, y + size * 0.32))


def _auto_labels(c, pts, m0=None, m1=None, r0=None, r1=None,
                 m0_at=None, m1_at=None, r0_at=None, r1_at=None,
                 d0=None, d1=None):
    """Кратность — у своего конца связи, имя роли — рядом с ней.

    По UML 2.5 кратность стоит рядом с тем концом, который она описывает,
    поэтому координаты по умолчанию отсчитываются от самого конца полилинии,
    а не от начала обхода: иначе цифра уезжает к дальнему углу и читается как
    относящаяся к чужому классу.
    """
    def place(pt, other, mult, role, mult_at, role_at, deco=None):
        dx, dy = other[0] - pt[0], other[1] - pt[1]
        if abs(dx) >= abs(dy):              # конец на вертикальной грани класса
            sgn = 1 if dx > 0 else -1
            manch = ranch = 'ls' if sgn > 0 else 'rs'
            mx, my = pt[0] + sgn * 8, pt[1] - 7
            rx, ry = pt[0] + sgn * 8, pt[1] + 15
        else:                               # конец на горизонтальной грани класса
            sgn = 1 if dy > 0 else -1
            manch, ranch = 'rs', 'ls'
            mx, my = pt[0] - 13, pt[1] + (14 if sgn > 0 else -8)
            rx, ry = pt[0] + 13, pt[1] + (14 if sgn > 0 else -8)
        if mult:
            a = manch
            if mult_at:
                mx, my = mult_at[0], mult_at[1]
                a = mult_at[2] if len(mult_at) > 2 else 'ls'
            _lab(c, mx, my, mult, a)
            GEOM['mults'].append((mult,) + tuple(GEOM['labels'][-1][1:])
                                 + (pt[0], pt[1], bool(deco)))
        if role:
            a = ranch
            if role_at:
                rx, ry = role_at[0], role_at[1]
                a = role_at[2] if len(role_at) > 2 else 'ls'
            _lab(c, rx, ry, role, a, size=9.8, fill='#374151')
            GEOM['roles'].append((role,) + tuple(GEOM['labels'][-1][1:])
                                 + (pt[0], pt[1], bool(deco)))
    place(pts[0], pts[1], m0, r0, m0_at, r0_at, d0)
    place(pts[-1], pts[-2], m1, r1, m1_at, r1_at, d1)


CLASS_RU = {
    'StandardFGOS': 'стандарт ФГОС ВО',
    'EducationalProgram': 'образовательная программа',
    'Curriculum': 'учебный план',
    'CurriculumDiscipline': 'дисциплина плана',
    'Department': 'кафедра',
    'Competency': 'компетенция',
    'Document': 'документ (абстрактный)',
    'DocumentSignature': 'виза / подпись',
    'User': 'пользователь',
    'Role': 'роль доступа',
    'AuditLog': 'запись журнала аудита',
    'Announcement': 'объявление',
    'ServiceNote': 'служебная записка',
    'ServiceNoteItem': 'позиция записки',
}


def class_diagram(lang=None):
    _geom_reset()
    lang = lang or COMP_LANG
    W = 2700
    COLS = [50, 580, 1110, 1640, 2170]
    BW = 400
    specs = {
        'StandardFGOS': dict(name='StandardFGOS', attrs=[
            '- id: Integer {id}', '- code: String', '- title: String',
            '- degreeLevel: String', '- totalCredits: Integer = 240',
            '- maxExamsPerSession: Integer = 5', '- minPracticeCredits: Integer = 12',
            '- minGiaCredits: Integer = 6', '- approvalDate: Date'], ops=[
            '+ check(curriculum: Curriculum): ViolationList',
            '+ thresholds(): Thresholds']),
        'EducationalProgram': dict(name='EducationalProgram', attrs=[
            '- id: Integer {id}', '- code: String = "09.03.04"', '- title: String',
            '- level: EducationLevel', '- studyForm: StudyForm'], ops=[
            '+ curriculums(year: String): List<Curriculum>',
            '+ addCompetency(competency: Competency): void']),
        'Curriculum': dict(name='Curriculum', attrs=[
            '- academicYear: String', '- version: String = "1.0"',
            '- totalCredits: Integer = 240', '- protocolNum: String',
            '- protocolDate: Date'], ops=[
            '+ semesterBalance(semester: Integer): Balance',
            '+ totalHours(): Integer']),
        'CurriculumDiscipline': dict(name='CurriculumDiscipline', attrs=[
            '- id: Integer {id}', '- blockType: BlockType', '- name: String',
            '- semesterNum: Integer {1..8}', '- creditsZe: Integer',
            '- totalHours: Integer', '- lectureHours: Integer', '- labHours: Integer',
            '- practiceHours: Integer', '- selfStudyHours: Integer',
            '- controlForm: ControlForm'], ops=[
            '+ hoursBalance(): Boolean', '+ hoursPerCredit(): Integer']),
        'Department': dict(name='Department', attrs=[
            '- id: Integer {id}', '- name: String', '- shortName: String',
            '- type: DepartmentType', '- phone: String', '- email: String'], ops=[
            '+ releasingCurriculums(): List<Curriculum>']),
        'AuditLog': dict(name='AuditLog', attrs=[
            '- id: Integer {id}', '- eventTime: DateTime', '- userName: String',
            '- userRole: String', '- action: String', '- entityName: String',
            '- status: String', '- ipAddress: String'], ops=[
            '+ log(event: AuditEvent): void', '+ export(format: String): String']),
        'Competency': dict(name='Competency', attrs=[
            '- id: Integer {id}', '- code: String = "УК-1 … ПК-4"', '- category: String',
            '- title: String', '- description: String'], ops=[
            '+ matches(pattern: String): Boolean']),
        'Document': dict(name='Document', abstract=True, attrs=[
            '- id: Integer {id}', '- docType: DocType', '- status: DocumentStatus',
            '- createdAt: DateTime', '- author: String'], ops=[
            '+ sign(role: Role, hash: String): DocumentSignature',
            '+ verify(hash: String): Boolean', '+ nextStep(): Integer']),
        'DocumentSignature': dict(name='DocumentSignature', attrs=[
            '- id: Integer {id}', '- stepOrder: Integer {1..4}', '- roleTitle: String',
            '- signerName: String', '- status: SignatureStatus', '- comment: String',
            '- signedAt: DateTime', '- signHash: String {SHA-256}'], ops=[
            '+ verify(hash: String): Boolean', '+ format(): String']),
        'User': dict(name='User', attrs=[
            '- id: Integer {id}', '- username: String', '- fullName: String',
            '- email: String', '- positionTitle: String'], ops=[
            '+ hasPermission(action: Action): Boolean',
            '+ canSign(step: Integer): Boolean']),
        'Announcement': dict(name='Announcement', attrs=[
            '- id: Integer {id}', '- title: String', '- category: String',
            '- publishDate: Date', '- authorName: String', '- content: String',
            '- isPinned: Boolean = false'], ops=[
            '+ isVisibleOn(date: Date): Boolean']),
        'ServiceNote': dict(name='ServiceNote', attrs=[
            '- noteNum: String', '- noteDate: Date', '- reason: String'], ops=[
            '+ applyChanges(): void', '+ diff(): ChangeSet']),
        'ServiceNoteItem': dict(name='ServiceNoteItem', attrs=[
            '- id: Integer {id}', '- changeType: ChangeType', '- oldValue: String',
            '- newValue: String'], ops=['+ render(): String']),
        'Role': dict(name='Role', attrs=[
            '- id: Integer {id}', '- roleName: String', '- code: RoleCode',
            '- description: String'], ops=['+ permissions(): Set<Permission>']),
    }
    place = {
        'StandardFGOS': (0, 0), 'EducationalProgram': (1, 0), 'Curriculum': (2, 0),
        'CurriculumDiscipline': (3, 0), 'Department': (4, 0),
        'AuditLog': (0, 1), 'Competency': (1, 1), 'Document': (2, 1),
        'DocumentSignature': (3, 1), 'User': (4, 1),
        'Announcement': (1, 2), 'ServiceNote': (2, 2), 'ServiceNoteItem': (3, 2),
        'Role': (4, 2),
    }
    if lang == 'ru':
        for _n, _sp in specs.items():
            _sp['ru'] = CLASS_RU.get(_n)
    row_y = [150]
    geo, row_h = {}, {}
    for row in range(3):
        for name, (col, r) in place.items():
            if r == row:
                h = _measure_class(specs[name], BW)
                geo[name] = (COLS[col], row_y[row], BW, h)
                row_h[row] = max(row_h.get(row, 0), h)
        if row < 2:
            row_y.append(row_y[row] + row_h[row] + 132)
    bottom = row_y[2] + row_h[2]
    H = bottom + 118
    c = Canvas(W, H, scale=2)
    title(c, 'Диаграмма классов — объектная модель портала Центра АНОК'
             if lang == 'ru' else 'Class Diagram — ANOK Center Portal domain model')

    for name, (x, y, w, h) in geo.items():
        draw_class(c, x, y, w, specs[name])

    def L(n, t=0.5):
        x, y, w, h = geo[n]; return (x, y + h * t)

    def R(n, t=0.5):
        x, y, w, h = geo[n]; return (x + w, y + h * t)

    def T(n, t=0.5):
        x, y, w, h = geo[n]; return (x + w * t, y)

    def B(n, t=0.5):
        x, y, w, h = geo[n]; return (x + w * t, y + h)

    def RY(n, y):
        x, y0, w, h = geo[n]; return (x + w, y)

    def LY(n, y):
        x, y0, w, h = geo[n]; return (x, y)

    def row_y_for(n1, n2, t=0.42):
        """Общая высота концов связи — без диагоналей между классами разной высоты."""
        x1, y1, w1, h1 = geo[n1]
        x2, y2, w2, h2 = geo[n2]
        return min(y1, y2) + t * min(h1, h2)

    def assoc(pts, start=None, end=None, dash=None, **lab):
        # ромб композиции / треугольник обобщения занимает ~20 px у конца связи:
        # кратность этого конца поднимаем выше декорации, иначе ромб ложится на цифру
        for key, kind, pt, other in (('m0_at', start, pts[0], pts[1]),
                                     ('m1_at', end, pts[-1], pts[-2])):
            if kind in ('diamond_filled', 'hollow') and key not in lab and key[:-3] in lab:
                dx, dy = other[0] - pt[0], other[1] - pt[1]
                if abs(dx) >= abs(dy):          # горизонтальная связь
                    sgn = 1 if dx > 0 else -1
                    lab[key] = (pt[0] + sgn * 26, pt[1] - 7, 'ls' if sgn > 0 else 'rs')
                else:                            # вертикальная связь
                    sgn = 1 if dy > 0 else -1
                    lab[key] = (pt[0] - 13, pt[1] + sgn * 32, 'rs')
        _poly(pts, LINE, 1.3)
        GEOM['ends'].append((start, end))
        c.line(pts, fill=LINE, width=1.3, dash=dash)
        if start:
            c.arrowhead(pts[0], pts[1], start, LINE, 10)
        if end:
            c.arrowhead(pts[-1], pts[-2], end, LINE, 10)
        _auto_labels(c, pts, d0=start, d1=end, **lab)

    # 1. StandardFGOS 1 —— 1..* EducationalProgram
    _y = row_y_for('StandardFGOS', 'EducationalProgram')
    assoc([RY('StandardFGOS', _y), LY('EducationalProgram', _y)],
          m0='1', r0='standard', m1='0..*', r1='programs')
    # 2. EducationalProgram 1 —— 1..* Curriculum
    _y = row_y_for('EducationalProgram', 'Curriculum', 0.55)
    assoc([RY('EducationalProgram', _y), LY('Curriculum', _y)],
          m0='1', r0='program', m1='0..*', r1='curriculums')
    # 3. EducationalProgram ◆—— 0..* Competency
    assoc([B('EducationalProgram', 0.5), T('Competency', 0.5)],
          start='diamond_filled', m0='1', m1='0..*', r1='competencies')
    # 4. EducationalProgram 0..* —— 1 Department  (верхний канал)
    ch = row_y[0] - 56
    pa, pb = T('EducationalProgram', 0.22), T('Department', 0.24)
    assoc([pa, (pa[0], ch), (pb[0], ch), pb],
          m0='0..*', r0='ownerDept', m1='1')
    # 5. Curriculum ◁—— Document
    assoc([B('Curriculum', 0.5), T('Document', 0.5)], end='hollow')
    # 6. Document ◆—— 1..* DocumentSignature
    _y = row_y_for('Document', 'DocumentSignature', 0.45)
    assoc([RY('Document', _y), LY('DocumentSignature', _y)],
          start='diamond_filled', m0='1', m1='1..*', r1='signatures')
    # 7. Document ◁—— ServiceNote
    assoc([B('Document', 0.5), T('ServiceNote', 0.5)], start='hollow')
    # 8. Curriculum ◆—— 1..* CurriculumDiscipline
    _y = row_y_for('Curriculum', 'CurriculumDiscipline', 0.72)
    assoc([RY('Curriculum', _y), LY('CurriculumDiscipline', _y)],
          start='diamond_filled', m0='1', m1='1..*', r1='disciplines')
    # 9. CurriculumDiscipline 0..* —— 1 Department
    _y9 = row_y_for('CurriculumDiscipline', 'Department', 0.3)
    _d9 = RY('CurriculumDiscipline', _y9)
    _l9 = LY('Department', _y9)
    assoc([_d9, _l9], m0='0..*', r0='implementing', m1='1',
          m0_at=(_d9[0] + 8, _d9[1] - 8),
          r0_at=(_l9[0] - 8, _l9[1] + 16, 'rs'),
          m1_at=(_l9[0] - 8, _l9[1] - 8, 'rs'))
    # 10. Department 1 —— 0..* ServiceNote (выпускающая кафедра)
    gx1 = COLS[3] + BW + 56
    y_ch = bottom + 26
    d1 = L('Department', 0.72)
    s1 = B('ServiceNote', 0.58)
    assoc([d1, (gx1, d1[1]), (gx1, y_ch), (s1[0], y_ch), s1],
          m0='1', m1='0..*', r1='releasingNotes',
          m0_at=(d1[0] - 8, d1[1] - 8, 'rs'))
    # 11. Department 1 —— 0..* ServiceNote (обеспечивающая кафедра)
    gx2 = COLS[3] + BW + 88
    y_ch2 = y_ch + 30
    d2 = L('Department', 0.92)
    s2 = B('ServiceNote', 0.2)
    assoc([d2, (gx2, d2[1]), (gx2, y_ch2), (s2[0], y_ch2), s2],
          m0='1', m1='0..*', r1='implementingNotes',
          m0_at=(d2[0] - 8, d2[1] + 16, 'rs'))
    # 12. ServiceNote ◆—— 1..* ServiceNoteItem
    _y = row_y_for('ServiceNote', 'ServiceNoteItem', 0.42)
    assoc([RY('ServiceNote', _y), LY('ServiceNoteItem', _y)],
          start='diamond_filled', m0='1', m1='1..*', r1='items')
    # 13. ServiceNoteItem 0..* —— 1 CurriculumDiscipline (обход между колонками 3/4)
    chx = COLS[3] + BW + 22
    sni = R('ServiceNoteItem', 0.62)
    chy = geo['CurriculumDiscipline'][1] + geo['CurriculumDiscipline'][3] + 20
    cdb = B('CurriculumDiscipline', 0.78)
    assoc([sni, (chx, sni[1]), (chx, chy), (cdb[0], chy), cdb],
          m0='0..*', r0='discipline', m1='1',
          m0_at=(sni[0] + 8, sni[1] - 9), r0_at=(sni[0] + 8, sni[1] + 16),
          m1_at=(cdb[0] + 8, cdb[1] + 16))
    # 14. User 0..* —— 1 Role
    assoc([B('User', 0.42), T('Role', 0.42)], m0='0..*', r0='role', m1='1')
    # 15. User 0..* —— 0..1 Department
    assoc([T('User', 0.66), B('Department', 0.66)], m0='0..*', r0='department', m1='0..1')
    # 16. Announcement 0..* —— 0..1 User (автор объявления).
    # Канал: вправо от Announcement, вверх до межрядного коридора, по нему вправо
    # и вверх по свободной щели между DocumentSignature и User — в левую грань User.
    _ann = B('Announcement', 0.5)
    _yb = bottom + 84                    # свободная полоса под нижним рядом
    _x2 = W - 40                         # правое поле: места хватает и линиям, и подписям
    _usr = R('User', 0.55)
    assoc([_ann, (_ann[0], _yb), (_x2, _yb), (_x2, _usr[1]), _usr],
          m0='0..*', m1='0..1', r1='author',
          m0_at=(_ann[0] - 8, _ann[1] + 16, 'rs'),
          m1_at=(_usr[0] + 10, _usr[1] - 8),
          r1_at=(_usr[0] + 10, _usr[1] + 18))

    fname = 'class_diagram.png' if lang == COMP_LANG else 'class_diagram_%s.png' % lang
    c.save(os.path.join(OUT, fname))



# ======================================================================
#  Диаграмма компонентов
# ======================================================================
def _comp_icon(c, x, y):
    """Пиктограмма компонента UML (два выступающих прямоугольника)."""
    c.rect(x + 4, y, 18, 15, fill='#ffffff', outline=LINE, width=1.1)
    c.rect(x, y + 3, 10, 6, fill='#ffffff', outline=LINE, width=1.1)
    c.rect(x, y + 9, 10, 6, fill='#ffffff', outline=LINE, width=1.1)


def component(c, x, y, w, h, name, stereo='component', lines=(), fill='#eef2fb',
              name_size=13.0):
    c.rect(x, y, w, h, fill=fill, outline=LINE, width=1.4)
    c.text(x + w / 2 - 12, y + 15, '«%s»' % stereo, 9.8, 'normal', '#374151', anchor='ms')
    c.text(x + w / 2 - 12, y + 32, name, name_size, 'bold', INK, anchor='ms')
    _comp_icon(c, x + w - 36, y + 12)
    yy = y + 48
    c.line([(x, yy), (x + w, yy)], fill='#9aa7bd', width=1.0)
    yy += 17
    for ln in lines:
        c.text_clip(x + 12, yy, ln, w - 24, 10.4, 'normal', '#374151')
        yy += 15


def ball(c, x, y, r=6.0):
    c.circle(x, y, r, fill='#ffffff', outline=LINE, width=1.2)


def socket(c, x, y, r=7.0, side='bottom'):
    """«Гнездо» требуемого интерфейса: дуга снаружи грани компонента."""
    if side == 'bottom':
        c.arc(x, y + r, r, 180, 360, fill=LINE, width=1.4)
        return (x, y + 2 * r)
    if side == 'top':
        c.arc(x, y - r, r, 0, 180, fill=LINE, width=1.4)
        return (x, y - 2 * r)
    if side == 'left':
        c.arc(x - r, y, r, 270, 90, fill=LINE, width=1.4)
        return (x - 2 * r, y)
    c.arc(x + r, y, r, 90, 270, fill=LINE, width=1.4)
    return (x + 2 * r, y)


def assembly(c, x, y_top, y_bot, name=None, provider='top', size=11.0):
    """Сборочный разъём UML 2.5: «шарик» поставщика надет в «гнездо» потребителя.

    y_top / y_bot — границы компонентов (верхняя и нижняя); provider — с какой
    стороны расположен компонент-поставщик интерфейса."""
    r_ball, r_sock = 6.0, 12.0
    ym = (y_top + y_bot) / 2
    _poly([(x, y_top), (x, ym), (x, y_bot)], LINE, 1.4)
    if provider == 'top':          # поставщик сверху: гнездо потребителя снизу
        c.line([(x, y_top), (x, ym - r_ball)], fill=LINE, width=1.4)
        c.arc(x, ym, r_sock, 0, 180, fill=LINE, width=1.5)
        c.circle(x, ym, r_ball, fill='#ffffff', outline=LINE, width=1.3)
        c.line([(x, ym + r_sock), (x, y_bot)], fill=LINE, width=1.4)
        if name:
            c.text(x + r_sock + 12, ym + 4, name, size, 'bold', '#1f2937')
    else:                          # поставщик снизу: гнездо потребителя сверху
        c.line([(x, y_bot), (x, ym + r_ball)], fill=LINE, width=1.4)
        c.arc(x, ym, r_sock, 180, 360, fill=LINE, width=1.5)
        c.circle(x, ym, r_ball, fill='#ffffff', outline=LINE, width=1.3)
        c.line([(x, ym - r_sock), (x, y_top)], fill=LINE, width=1.4)
        if name:
            c.text(x + r_sock + 12, ym + 4, name, size, 'bold', '#1f2937')
    return ym


def subsystem_frame(c, x, y, w, h, name, stereo='subsystem', fill='#ffffff'):
    c.rect(x, y, w, h, fill=fill, outline='#374151', width=1.4)
    st = '«%s»' % stereo
    tab = c.tw(st, 9.6) + c.tw(name, 12.2, 'bold') + 34
    c.rect(x, y, tab, 26, fill='#f2f2f2', outline='#374151', width=1.2)
    c.text(x + 10, y + 17, st, 9.6, 'normal', '#374151')
    c.text(x + 18 + c.tw(st, 9.6), y + 18, name, 12.2, 'bold', '#1f2937')


def component_slim(c, x, y, w, h, name, stereo='component', fill='#ffffff', name_size=12.6,
                   sub=None):
    """Компонент UML 2.5: ключевое слово, имя, пиктограмма и строка расшифровки."""
    c.rect(x, y, w, h, fill=fill, outline=LINE, width=1.4)
    GEOM['boxes'].append((name, x, y, x + w, y + h))
    c.text(x + w / 2 - 10, y + 20, '«%s»' % stereo, 9.8, 'normal', '#1f2937', anchor='ms')
    c.text(x + w / 2 - 10, y + 42, name, name_size, 'bold', INK, anchor='ms')
    if sub:
        c.text(x + w / 2 - 10, y + 61, sub, 9.8, 'italic', '#374151', anchor='ms')
    _comp_icon(c, x + w - 34, y + 12)


# Язык подписей диаграммы компонентов: 'ru' — кириллица, 'en' — латиница.
COMP_LANG = 'ru'
# Дополнительные подписи (подзаголовок с правилами нотации, примечания, легенда,
# строка с параметрами БД). False — на диаграмме остаются только элементы модели.
COMP_HELPERS = False

COMP_TEXTS = {
    'ru': dict(
        title='Диаграмма компонентов — портал Центра АНОК',
        sub='UML 2.5: «component»; сборочный разъём — «шарик» предоставляемого интерфейса, '
            'надетый в «гнездо» требуемого; «use» — зависимость без формального интерфейса.',
        subsystem='Портал Центра АНОК',
        tables='13 таблиц · 3NF · utf8mb4',
        note1=['PortalUI: HTML/CSS/JS формируются сервером (portal/server.py,',
               'portal/index.php); библиотеки Chart.js, jQuery, DataTables,',
               'FullCalendar, SheetJS, jsPDF — с CDN jsdelivr.'],
        note2=['HttpKernel: 15 страниц (?page=…) и 3 REST-эндпоинта',
               '(/api/stats, /api/plans, /api/announcements), аутентификация,',
               'ролевая авторизация RoleCode, проверка CSRF-токена.'],
        legend='Условные обозначения',
        l1='сборочный разъём: «шарик» в «гнезде»',
        l2='зависимость «use» (нет формального интерфейса)',
        l3='компонент: ключевое слово «component» + пиктограмма',
        l4='граница подсистемы «subsystem»',
        subs={'PortalUI': 'клиентский уровень · web-интерфейс',
              'HttpKernel': 'маршрутизация запросов и контроллеры',
              'CurriculumService': 'учебные планы',
              'FgosValidationEngine': 'проверка на ФГОС',
              'WorkflowManager': 'визирование и ЭЦП',
              'MemoManager': 'служебные записки',
              'AuditLogger': 'журнал аудита',
              'DataAccessLayer': 'доступ к данным'},
    ),
    'en': dict(
        title='Component Diagram — ANOK Center Portal',
        sub='UML 2.5: «component»; assembly connector — provided interface «ball» fitted into '
            'required interface «socket»; «use» — dependency without a formal interface.',
        subsystem='ANOK Center Portal',
        tables='13 tables · 3NF · utf8mb4',
        note1=['PortalUI: HTML/CSS/JS are generated by the server (portal/server.py,',
               'portal/index.php); Chart.js, jQuery, DataTables, FullCalendar,',
               'SheetJS and jsPDF are loaded from the jsDelivr CDN.'],
        note2=['HttpKernel: 15 pages (?page=…) and 3 REST endpoints',
               '(/api/stats, /api/plans, /api/announcements), authentication,',
               'RoleCode-based authorization, CSRF token validation.'],
        legend='Notation',
        l1='assembly connector: «ball» in «socket»',
        l2='«use» dependency (no formal interface)',
        l3='component: «component» keyword + icon',
        l4='«subsystem» boundary',
        subs={'PortalUI': 'presentation layer · web UI',
              'HttpKernel': 'request routing and controllers',
              'CurriculumService': 'curricula',
              'FgosValidationEngine': 'FGOS validation',
              'WorkflowManager': 'approval route & e-signature',
              'MemoManager': 'service notes',
              'AuditLogger': 'audit trail',
              'DataAccessLayer': 'data access'},
    ),
}


def component_diagram(lang=None):
    _geom_reset()
    lang = lang or COMP_LANG
    T = COMP_TEXTS[lang]
    W, H = 1880, (1180 if COMP_HELPERS else 1010)
    CX = 940                                  # ось симметрии компоновки
    c = Canvas(W, H, scale=2)
    title(c, T['title'], T['sub'] if COMP_HELPERS else None)

    # ---------------- граница подсистемы --------------------------------
    subsystem_frame(c, 60, 126, 1640, 690, T['subsystem'])

    # ---------------- компоненты ----------------------------------------
    subs = T['subs']
    ui_w, ui_h, ui_y = 400, 64, 162
    component_slim(c, CX - ui_w / 2, ui_y, ui_w, ui_h, 'PortalUI', fill='#ffffff')

    k_w, k_h, k_y = 1480, 64, 330
    component_slim(c, CX - k_w / 2, k_y, k_w, k_h, 'HttpKernel', fill='#ffffff')

    sv_w, sv_h, sv_y, sv_step = 264, 64, 498, 290
    sv_x = [CX - 2 * sv_step - sv_w / 2 + i * sv_step for i in range(5)]
    services = ['CurriculumService', 'FgosValidationEngine', 'WorkflowManager',
                'MemoManager', 'AuditLogger']
    ifaces = ['ICurriculumService', 'IFgosValidation', 'IWorkflow',
              'IMemoProcessing', 'IAuditSink']
    for x, nm in zip(sv_x, services):
        component_slim(c, x, sv_y, sv_w, sv_h, nm, fill='#ffffff')

    d_y = 666
    component_slim(c, CX - k_w / 2, d_y, k_w, k_h, 'DataAccessLayer', fill='#ffffff')

    # ---------------- сборочные разъёмы ---------------------------------
    assembly(c, CX - 110, ui_y + ui_h, k_y, 'IPortalPages', provider='bottom', size=10.8)
    assembly(c, CX + 110, ui_y + ui_h, k_y, 'IRestApi', provider='bottom', size=10.8)
    centres = [x + sv_w / 2 for x in sv_x]
    for x, nm in zip(centres, ifaces):
        assembly(c, x, k_y + k_h, sv_y, nm, provider='bottom', size=10.6)
    for x in centres:
        assembly(c, x, sv_y + sv_h, d_y, 'IPersistence', provider='bottom', size=10.6)

    # ---------------- хранилище (вне подсистемы) ------------------------
    dbw, dbh, dby = 480, 112, 860
    dbx = CX - dbw / 2
    c.d.ellipse([dbx * c.s, dby * c.s, (dbx + dbw) * c.s, (dby + 24) * c.s],
                fill='#ffffff', outline=LINE, width=3)
    c.rect(dbx, dby + 12, dbw, dbh - 24, fill='#ffffff', outline=None)
    c.line([(dbx, dby + 12), (dbx, dby + dbh - 12)], fill=LINE, width=1.4)
    c.line([(dbx + dbw, dby + 12), (dbx + dbw, dby + dbh - 12)], fill=LINE, width=1.4)
    c.d.arc([dbx * c.s, (dby + dbh - 24) * c.s, (dbx + dbw) * c.s, (dby + dbh) * c.s],
            0, 180, fill=LINE, width=4)
    c.text(CX, dby + (48 if COMP_HELPERS else 62), '«database» anok_portal', 12.4, 'bold', INK, anchor='ms')
    if COMP_HELPERS:
        c.text(CX, dby + 70, T['tables'], 10.0, 'normal', '#1f2937', anchor='ms')
    c.line([(CX, d_y + k_h), (CX, dby)], fill=LINE, width=1.3, dash=(7, 5))
    c.arrowhead((CX, dby), (CX, d_y + k_h), 'open', LINE, 10)
    c.text(CX + 14, (d_y + k_h + dby) / 2 + 4, '«use»', 10.4, 'italic', '#1f2937')

    # ---------------- примечания ----------------------------------------
    if COMP_HELPERS:
        note(c, 60, 830, 600, T['note1'], fill='#ffffff', outline='#374151')
        note(c, 1210, 830, 610, T['note2'], fill='#ffffff', outline='#374151')

    if COMP_HELPERS:
        # ---------------- легенда -------------------------------------------
        lx, ly, lw, lh = 60, 1000, 1120, 150
        legend_box(c, lx, ly, lw, lh, T['legend'])
        r1, r2 = ly + 46, ly + 100
        c.line([(lx + 26, r1), (lx + 46, r1)], fill=LINE, width=1.3)
        c.arc(lx + 52, r1, 10, 270, 90, fill=LINE, width=1.4)
        c.circle(lx + 52, r1, 6, fill='#ffffff', outline=LINE, width=1.2)
        c.line([(lx + 62, r1), (lx + 84, r1)], fill=LINE, width=1.3)
        c.text(lx + 96, r1 + 5, T['l1'], 10.6, 'normal', '#1f2937')
        c.line([(lx + 450, r1), (lx + 516, r1)], fill=LINE, width=1.2, dash=(7, 5))
        c.arrowhead((lx + 516, r1), (lx + 450, r1), 'open', LINE, 9)
        c.text(lx + 528, r1 + 5, T['l2'], 10.6, 'normal', '#1f2937')
        _comp_icon(c, lx + 26, r2 - 14)
        c.text(lx + 96, r2 + 5, T['l3'], 10.6, 'normal', '#1f2937')
        c.rect(lx + 450, r2 - 16, 46, 30, fill='#ffffff', outline='#94a3b8', width=1.3)
        c.text(lx + 528, r2 + 5, T['l4'], 10.6, 'normal', '#1f2937')

    fname = 'component_diagram.png' if lang == COMP_LANG else 'component_diagram_%s.png' % lang
    c.save(os.path.join(OUT, fname))


# ======================================================================
#  Диаграмма развёртывания
# ======================================================================
def node3d(c, x, y, w, h, stereo, name, depth=16, sk=11, fill='#ffffff',
           top='#f1f1f1', side='#e2e2e2'):
    """Узел UML 2.5 — трёхмерный блок (перспектива куба)."""
    c.rect(x, y, w, h, fill=fill, outline=LINE, width=1.5)
    GEOM['boxes'].append((name or 'node', x, y, x + w, y + h))
    GEOM['containers'].append(name or 'node')      # контейнер: линии внутри законны
    c.poly([(x, y), (x + sk, y - depth), (x + w + sk, y - depth), (x + w, y)],
           fill=top, outline=LINE, width=1.3)
    c.poly([(x + w, y), (x + w + sk, y - depth), (x + w + sk, y + h - depth), (x + w, y + h)],
           fill=side, outline=LINE, width=1.3)
    if stereo:
        c.text(x + 14, y + 20, '«%s»' % stereo, 9.6, 'normal', '#374151')
    if name:
        c.text(x + 14, y + 41, name, 13.0, 'bold', INK)


def env(c, x, y, w, h, stereo, name, sub=None):
    """Среда исполнения: узел «executionEnvironment» (вложенный в устройство)."""
    c.rect(x, y, w, h, fill='#ffffff', outline='#374151', width=1.3)
    GEOM['boxes'].append((name, x, y, x + w, y + h))
    GEOM['containers'].append(name)
    c.text(x + 12, y + 18, '«%s»' % stereo, 9.2, 'normal', '#374151')
    c.text(x + 12, y + 34, name, 11.4, 'bold', '#111827')
    if sub:
        c.text(x + 12, y + 49, sub, 9.4, 'italic', '#374151')


def artifact(c, x, y, w, h, name, lines=()):
    """Артефакт UML: прямоугольник с загнутым углом и ключевым словом «artifact»."""
    fold = 12
    c.poly([(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h)],
           fill='#ffffff', outline=LINE, width=1.2)
    GEOM['boxes'].append((name, x, y, x + w, y + h))
    c.poly([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)],
           fill='#f1f1f1', outline=LINE, width=1.0)
    c.text(x + 10, y + 15, '«artifact»', 8.8, 'normal', '#374151')
    c.text(x + 10, y + 32, name, 11.2, 'bold', INK)
    yy = y + 50
    for ln in lines:
        c.text_clip(x + 10, yy, ln, w - 20, 9.8, 'normal', '#1f2937')
        yy += 14


DEP_TEXTS = {
    'ru': dict(
        title='Диаграмма развёртывания — портал Центра АНОК',
        ws='Рабочая станция пользователя',
        browser='веб-браузер',
        pages='Страницы портала', pages_l=['HTML + CSS + JS', 'Chart.js · DataTables',
                                           'FullCalendar · SheetJS'],
        asrv='Сервер приложений',
        pyenv='Python 3.11 (http.server)', pyart='portal/server.py',
        pyart_l=['portal.db — SQLite 3'],
        phpenv='PHP 8.1-FPM', phpart='portal/index.php',
        phpart_l=['portal/config.php'],
        dbsrv='Сервер баз данных',
        dbenv='MySQL 8.0 / MariaDB 10.6',
        dbart='anok_portal', dbart_l=['schema.sql + seed.sql', '13 таблиц · utf8mb4'],
        p1=['«protocol»', 'HTTP/1.1 · TCP 8000'],
        p2=['«protocol»', 'SQL (PDO) · TCP 3306'],
        manifest='«manifest»',
    ),
    'en': dict(
        title='Deployment Diagram — ANOK Center Portal',
        ws='User workstation',
        browser='web browser',
        pages='Portal pages', pages_l=['HTML + CSS + JS', 'Chart.js · DataTables',
                                       'FullCalendar · SheetJS'],
        asrv='Application server',
        pyenv='Python 3.11 (http.server)', pyart='portal/server.py',
        pyart_l=['portal.db — SQLite 3'],
        phpenv='PHP 8.1-FPM', phpart='portal/index.php',
        phpart_l=['portal/config.php'],
        dbsrv='Database server',
        dbenv='MySQL 8.0 / MariaDB 10.6',
        dbart='anok_portal', dbart_l=['schema.sql + seed.sql', '13 tables · utf8mb4'],
        p1=['«protocol»', 'HTTP/1.1 · TCP 8000'],
        p2=['«protocol»', 'SQL (PDO) · TCP 3306'],
        manifest='«manifest»',
    ),
}


def _manifest(c, x0, y0, x1, y1, label):
    """Манифестация UML 2.5: пунктирная стрелка от артефакта к компоненту."""
    _poly([(x0, y0), (x1, y1)], '#374151', 1.2)
    c.line([(x0, y0), (x1, y1)], fill='#374151', width=1.2, dash=(6, 4))
    c.arrowhead((x1, y1), (x0, y0), 'open', '#374151', 9)
    c.text(x1 + 10, (y0 + y1) / 2 + 4, label, 9.8, 'italic', '#111827')


def deployment_diagram(lang=None):
    _geom_reset()
    lang = lang or COMP_LANG
    T = DEP_TEXTS[lang]
    W, H = 1900, 720
    c = Canvas(W, H, scale=2)
    title(c, T['title'])

    # ---------------- рабочая станция ------------------------------------
    # артефакт страниц манифестирует компонент PortalUI (пунктир «manifest»)
    node3d(c, 60, 150, 420, 400, 'device', T['ws'])
    env(c, 84, 200, 372, 180, 'executionEnvironment', T['browser'])
    artifact(c, 104, 248, 332, 118, T['pages'], T['pages_l'])
    component_slim(c, 104, 430, 332, 62, 'PortalUI', sub=None)
    _manifest(c, 270, 366, 270, 430, T['manifest'])

    # ---------------- сервер приложений ----------------------------------
    # оба артефакта (Python и PHP) реализуют один компонент HttpKernel
    node3d(c, 700, 150, 540, 480, 'device', T['asrv'])
    env(c, 724, 200, 492, 130, 'executionEnvironment', T['pyenv'])
    artifact(c, 744, 240, 452, 76, T['pyart'], T['pyart_l'])
    component_slim(c, 880, 360, 200, 56, 'HttpKernel', sub=None, name_size=11.8)
    env(c, 724, 432, 492, 130, 'executionEnvironment', T['phpenv'])
    artifact(c, 744, 472, 452, 76, T['phpart'], T['phpart_l'])
    _manifest(c, 980, 316, 980, 360, T['manifest'])
    _manifest(c, 980, 472, 980, 416, T['manifest'])

    # ---------------- сервер баз данных ----------------------------------
    # данные развёрнуты артефактом схемы; компонент не манифестируется —
    # база хранит состояние, а не реализует поведение портала
    node3d(c, 1420, 150, 380, 340, 'device', T['dbsrv'])
    env(c, 1444, 200, 332, 220, 'executionEnvironment', T['dbenv'])
    artifact(c, 1464, 250, 292, 130, T['dbart'], T['dbart_l'])

    # ---------------- пути связи -----------------------------------------
    for x0, x1, lab in ((480, 700, T['p1']), (1240, 1420, T['p2'])):
        _poly([(x0, 320), (x1, 320)], LINE, 1.6)
        c.line([(x0, 320), (x1, 320)], fill=LINE, width=1.6)
        xm = (x0 + x1) / 2
        c.text(xm, 306, lab[0], 9.8, 'bold', '#111827', anchor='ms')
        c.text(xm, 344, lab[1], 9.8, 'normal', '#1f2937', anchor='ms')

    fname = 'deployment_diagram.png' if lang == COMP_LANG else 'deployment_diagram_%s.png' % lang
    c.save(os.path.join(OUT, fname))


# ======================================================================
#  Диаграмма последовательности
# ======================================================================
SEQ = None          # последняя построенная диаграмма последовательности (для аудита)


class Seq:
    """Диаграмма последовательности UML 2.5: два прохода (разметка → отрисовка)."""

    def __init__(self, c, xs, heads, top, bottom=0):
        self.c = c
        self.xs = xs
        self.heads = heads
        self.top = top
        self.bottom = bottom
        self.y = top + 168
        self.items = []     # ('msg', a, b, kind, y, text) | ('self', a, y, text)
        self.guards_draw = []   # отложенная отрисовка guard'ов (поверх линий жизни)
        self.acts = []      # (i, y0, y1, level)
        self._bars = []     # прямоугольники полос активности
        self._lab_rects = []
        self.frags = []     # (x0, x1, y0, y1, op, guards, guard_in_tab)

    # ---------------------------------------------------------------- разметка
    def msg(self, a, b, text, kind='sync', dy=54):
        y = self.y
        self.items.append(('msg', a, b, kind, y, text))
        self.y += dy
        return y

    def self_msg(self, a, text, dy=76):
        y = self.y
        self.items.append(('self', a, y, text))
        self.y += dy
        return y

    def act(self, i, y0, y1, level=0):
        self.acts.append((i, y0, y1, level))

    def frag(self, i0, i1, op, guards, guard_in_tab=False, pad=46):
        return (self.xs[i0] - pad, self.xs[i1] + pad, op, guards, guard_in_tab)

    # ---------------------------------------------------------------- отрисовка
    def render(self):
        c = self.c
        # 1. заголовки и линии жизни
        head_bottom = []
        for x, head in zip(self.xs, self.heads):
            kind = head[0]
            if kind == 'actor':
                name = head[1]
                c.circle(x, self.top + 6, 9, fill='#ffffff', outline=LINE, width=1.4)
                c.line([(x, self.top + 15), (x, self.top + 40)], fill=LINE, width=1.4)
                c.line([(x - 15, self.top + 24), (x + 15, self.top + 24)], fill=LINE, width=1.4)
                c.line([(x, self.top + 40), (x - 12, self.top + 56)], fill=LINE, width=1.4)
                c.line([(x, self.top + 40), (x + 12, self.top + 56)], fill=LINE, width=1.4)
                lines = name.split('\n')
                for k, ln in enumerate(lines):
                    c.text(x, self.top + 76 + k * 15, ln, 10.6, 'bold', INK, anchor='ms')
                head_bottom.append(self.top + 76 + (len(lines) - 1) * 15 + 10)
            else:
                stereo, name = head[1], head[2]
                w, h = 190, 44
                GEOM['boxes'].append((name, x - w / 2, self.top - 6, x + w / 2, self.top + h - 6))
                c.rect(x - w / 2, self.top - 6, w, h, fill='#eef2fb', outline=LINE, width=1.4)
                c.text(x, self.top + 8, '«%s»' % stereo, 9.2, 'normal', '#4b5563', anchor='ms')
                c.text(x, self.top + 26, name, 11.0, 'bold', INK, anchor='ms')
                head_bottom.append(self.top + 38)
        # 2. контуры рамок фрагментов — под линиями жизни и полосами активности
        for (x0, x1, op, guards, in_tab, y0, y1) in self.frags:
            c.rect(x0, y0, x1 - x0, y1 - y0, fill=None, outline=FRAME_LINE, width=1.1,
                   dash=(11, 7))
        # 3. линии жизни (пунктир) — после рамок, до сообщений
        for x, hb in zip(self.xs, head_bottom):
            c.line([(x, hb), (x, self.bottom)], fill='#6b7280', width=1.1, dash=(6, 5))
            GEOM['lifelines'].append(x)
        # 4. полосы активности — до сообщений
        for (i, y0, y1, level) in self.acts:
            x = self.xs[i] + level * 7
            c.rect(x - 7, y0, 14, max(20, y1 - y0), fill='#f4f6fb', outline='#374151', width=1.2)
            self._bars.append((x, y0, y0 + max(20, y1 - y0)))
            GEOM['bars'].append((x, y0, y0 + max(20, y1 - y0)))
        # Рамки фрагментов — ПОВЕРХ линий жизни и полос активности:
        # вкладка оператора непрозрачная, иначе полоса активации режет слово «loop»
        for (x0, x1, op, guards, in_tab, y0, y1) in self.frags:
            tab_w = 58
            if in_tab and guards:
                tab_w = max(58, 66 + c.tw(guards[0][1], 10.0) + 10)
            c.poly([(x0, y0), (x0 + tab_w, y0), (x0 + tab_w, y0 + 21),
                    (x0 + tab_w - 12, y0 + 31), (x0, y0 + 31)],
                   fill='#ffffff', outline=FRAME_LINE, width=1.2)
            c.text(x0 + 9, y0 + 20, op, 10.4, 'bold', '#111827')
            for k, (gy, guard) in enumerate(guards):
                if k == 0:
                    gx, gy_text = x0 + (66 if in_tab else 70), y0 + 20
                else:
                    # условие ветви alt ставится ВНУТРИ операнда — под разделителем
                    c.line([(x0 + 1, gy), (x1 - 1, gy)], fill=FRAME_LINE, width=1.1,
                           dash=(11, 7))
                    gx, gy_text = x0 + 12, gy + 19
                self.guards_draw.append((gx, gy_text, guard))

        # 5. guard'ы фрагментов — поверх линий жизни и полос активности
        for gx, gy_text, guard in self.guards_draw:
            w = c.tw(guard, 10.0)
            c.d.rectangle([gx * c.s - 3, (gy_text - 11) * c.s, (gx + w) * c.s + 3,
                           (gy_text + 3) * c.s], fill='#ffffff')
            c.text(gx, gy_text, guard, 10.0, 'normal', '#111827')
        # 6. сообщения
        for it in self.items:
            if it[0] == 'msg':
                _, a, b, kind, y, text = it
                la, ra = self._bar_edge(a, y)      # рёбра полос активности
                lb, rb = self._bar_edge(b, y)
                x1, x2 = (ra, lb) if self.xs[b] > self.xs[a] else (la, rb)
                _poly([(x1, y), (x2, y)], '#334155', 1.3)
                if kind == 'sync':
                    c.line([(x1, y), (x2, y)], fill=LINE, width=1.4)
                    c.arrowhead((x2, y), (x1, y), 'filled', LINE, 10)
                elif kind == 'async':
                    # асинхронное сообщение (сигнал): сплошная линия, открытый наконечник
                    c.line([(x1, y), (x2, y)], fill=LINE, width=1.4)
                    c.arrowhead((x2, y), (x1, y), 'open', LINE, 10)
                else:
                    c.line([(x1, y), (x2, y)], fill=LINE, width=1.5, dash=(5, 4))
                    c.arrowhead((x2, y), (x1, y), 'open', LINE, 10)
                self._label(x1, x2, y, text)
            else:
                _, a, y, text = it
                x = self._bar_edge(a, y)[1]
                c.line([(x, y), (x + 54, y), (x + 54, y + 26), (x + 8, y + 26)],
                       fill=LINE, width=1.4)
                c.arrowhead((x + 6, y + 26), (x + 44, y + 26), 'filled', LINE, 9)
                self._label(x + 60, x + 60, y + 16, text, align='left')

    def _wrap(self, text, size, maxw):
        """Разбивает подпись на строки так, чтобы она влезла в коридор между линиями."""
        words, lines, cur = text.split(' '), [], ''
        for wd in words:
            probe = (cur + ' ' + wd).strip()
            if cur and self.c.tw(probe, size) > maxw:
                lines.append(cur)
                cur = wd
            else:
                cur = probe
        lines.append(cur)
        return lines

    def _label(self, x1, x2, y, text, size=10.2, align='center'):
        """Подпись ставится только в свободный коридор между соседними линиями
        жизни: так она не ложится ни на полосу активности, ни на соседнюю линию."""
        c = self.c
        a, b = self._idx(x1), self._idx(x2)
        gap = (self.xs[1] - self.xs[0]) - 56
        lines = [text] if c.tw(text, size) <= gap else self._wrap(text, size, gap)[:3]
        w = max(c.tw(l, size) for l in lines)
        lh = 13.4
        # Подпись целиком НАД линией: при многострочной подписи вторая строка
        # раньше садилась на саму стрелку (базовая линия = y + 1.2).
        top = y - 8 - len(lines) * lh
        last = len(self.xs) - 2          # индекс последнего коридора
        order = list(range(min(a, b), max(a, b))) or [a]
        order = [min(i, last) for i in order]
        if a > b:
            order.reverse()
        lx = None
        for i in order:
            cand = self.xs[i] + (self.xs[i + 1] - self.xs[i]) / 2 - w / 2
            if self._lab_free(cand, top, cand + w, y - 4):
                lx = cand
                break
        if lx is None:
            lx = (x1 + x2) / 2 - w / 2
        for k, ln in enumerate(lines):
            ly = top + (k + 1) * lh + 2
            c.d.rectangle([(lx - 2) * c.s, (ly - size - 2) * c.s,
                           (lx + c.tw(ln, size) + 2) * c.s, (ly + 2) * c.s], fill='#ffffff')
            c.text(lx, ly, ln, size, 'normal', '#111827')
        self._lab_rects.append((lx - 2, top, lx + w + 2, y - 4))
        GEOM['labels'].append((text, lx - 2, top, lx + w + 2, y - 4))

    def _bar_edge(self, i, y):
        """Границы полосы активности (если она активна в точке y), иначе — линия жизни.
        Сообщение обязано начинаться/заканчиваться на ребре полосы, а не в её середине."""
        for (bi, y0, y1, level) in self.acts:
            if bi == i and y0 <= y <= y0 + max(20, y1 - y0):
                x = self.xs[i] + level * 7
                return (x - 7, x + 7)
        x = self.xs[i]
        return (x, x)

    def _idx(self, x):
        return min(range(len(self.xs)), key=lambda i: abs(self.xs[i] - x))

    def _lab_free(self, x0, y0, x1, y1):
        for (bx, by0, by1) in self._bars:
            if not (x1 < bx - 9 or x0 > bx + 9) and not (y1 < by0 or y0 > by1):
                return False
        for (lx0, ly0, lx1, ly1) in self._lab_rects:
            if not (x1 < lx0 - 4 or x0 > lx1 + 4 or y1 < ly0 - 3 or y0 > ly1 + 3):
                return False
        return True


def _build_sequence(c, top, bottom):
    # Порядок линий жизни выбран так, чтобы сообщение актёра шло к :PlanPage через
    # линии жизни других АКТЁРОВ (у них нет полос активности), а внутренние вызовы
    # шли между соседними объектами либо над уже закрытыми полосами. Поэтому ни одна
    # линия связи не проходит сквозь блок активации.
    xs = [180 + i * 300 for i in range(9)]
    heads = [
        ('actor', 'Заведующий\nкафедрой'),   # 0
        ('actor', 'Эксперт\nАНОК'),           # 1
        ('actor', 'Проректор\nпо УР'),        # 2
        ('actor', 'Ректор'),                  # 3
        ('obj', 'boundary', ':PlanPage'),     # 4
        ('obj', 'control', ':PlanController'),# 5
        ('obj', 'control', ':WorkflowManager'),# 6
        ('obj', 'entity', ':CurriculumRepository'),  # 7
        ('obj', 'control', ':FgosValidationEngine'), # 8
    ]
    sq = Seq(c, xs, heads, top, bottom)

    # --- 1. открытие формы плана: только чтение ----------------------------
    # каждый вызов закрыт своим возвратом: 1 закрыт на 6, 2 — на 5, 3 — на 4
    m1 = sq.msg(0, 4, '1. Открыть форму плана: GET ?page=plan&id=1')
    m2 = sq.msg(4, 5, '2. load(planId = 1) — запрос данных плана')
    m3 = sq.msg(5, 7, '3. findById(planId = 1) — SELECT curriculum')
    m4 = sq.msg(7, 5, '4. curriculum: 51 дисциплина, 240 з.е.', kind='return')
    m5 = sq.msg(5, 4, '5. renderForm(curriculum, sem = 1…8)', kind='return', dy=58)
    m6 = sq.msg(4, 0, '6. Форма плана отрисована', kind='return', dy=66)
    sq.act(7, m3, m4)
    # --- 2. сохранение проекта и первичная ЭЦП -----------------------------
    m7 = sq.msg(0, 4, '7. «Сохранить проект и подписать ЭЦП» (POST)')
    m8 = sq.msg(4, 5, '8. save(curriculum); sign(step = 1)')
    m9 = sq.msg(5, 7, '9. save(curriculum) — INSERT / UPDATE')
    m10 = sq.msg(7, 5, '10. curriculumId = 1', kind='return', dy=48)
    m11 = sq.msg(5, 6, '11. sign(CURRICULUM, step = 1, signer : User)')
    m12 = sq.msg(6, 7, '12. saveSignature(step = 1, sha256)')
    m13 = sq.msg(7, 6, '13. signatureId = 1', kind='return', dy=48)
    m14 = sq.msg(6, 5, '14. signHash = 3f9c… (ЭЦП этапа 1)', kind='return', dy=52)
    sq.act(7, m9, m10)
    sq.act(7, m12, m13)
    # --- 3. автоматическая валидация ФГОС ----------------------------------
    m15 = sq.msg(5, 8, '15. validate(curriculumId = 1)')
    m16 = sq.msg(8, 7, '16. findDisciplines(curriculumId = 1)')
    m17 = sq.msg(7, 8, '17. disciplines[51]', kind='return', dy=48)
    sq.act(7, m16, m17)
    m18 = sq.self_msg(8, '18. checkTotals() · checkSessionExams() · checkPractice()')
    y_alt = m18 + 42          # рамка не должна ложиться на возврат self-сообщения
    # ---- фрагмент alt: оператор 1 [нарушений нет] -------------------------
    m19 = sq.msg(8, 5, '19. ValidationReport(passed = true)', kind='return', dy=60)
    m20 = sq.msg(5, 4, '20. renderReport(report) — протокол проверки', kind='return', dy=62)
    m21 = sq.msg(4, 0, '21. Протокол проверки выдан заведующему', kind='return', dy=66)
    # ---- фрагмент alt: оператор 2 [выявлены нарушения] --------------------
    y_op2 = m21 + 104
    sq.y = y_op2 + 40
    m22 = sq.msg(8, 5, '22. ValidationReport(passed = false, violations[])', kind='return', dy=54)
    m23 = sq.msg(5, 4, '23. Список замечаний ФГОС; возврат на доработку', kind='return', dy=58)
    m24 = sq.msg(4, 0, '24. План возвращён на доработку', kind='return', dy=66)
    y_alt_end = m24 + 26
    sq.act(8, m15, m22)
    sq.frags.insert(0, (*sq.frag(1, 8, 'alt', [(y_alt, '[нарушений нет]'),
                                               (y_op2, '[выявлены нарушения]')]), y_alt, y_alt_end))
    # --- 4. визирование: шаги маршрута 2–4 ---------------------------------
    # цикл стоит ПОСЛЕ alt: обе ветви закрыты возвратом пользователю (21 / 24),
    # поэтому продолжение после фрагмента существует только в успешной ветви.
    y_loop = y_alt_end + 44
    sq.y = y_loop + 32
    m25 = sq.msg(1, 4, '25. Подписант шага k открывает протокол ФГОС')
    m26 = sq.msg(4, 5, '26. signStep(step = k, comment)')
    m27 = sq.msg(5, 6, '27. sign(CURRICULUM, step = k, роль по маршруту)')
    m28 = sq.msg(6, 7, '28. saveSignature(step = k, sha256)')
    m29 = sq.msg(7, 6, '29. ok', kind='return', dy=46)
    m30 = sq.msg(6, 5, '30. signature(step = k)', kind='return', dy=46)
    sq.act(6, m27, m30)
    sq.act(7, m28, m29)
    m31 = sq.msg(5, 4, '31. k = k + 1 → следующий подписант маршрута', kind='return', dy=58)
    m32 = sq.msg(4, 1, '32. Протокол ФГОС предъявлен подписанту шага k', kind='return', dy=66)
    y_loop_end = m32 + 34
    sq.frags.append((*sq.frag(1, 7, 'loop',
                              [(y_loop, 'для каждого шага k = 2…4 (только при [нарушений нет]): '
                                        'Эксперт АНОК → Проректор по УР → Ректор')],
                              guard_in_tab=True, pad=28), y_loop, y_loop_end))
    sq.y = y_loop_end + 30
    # --- 5. передача в Учёный совет и утверждение --------------------------
    m33 = sq.msg(2, 4, '33. Согласование проекта для Учёного совета')
    m34 = sq.msg(4, 2, '34. Проект принят к рассмотрению', kind='return', dy=58)
    m35 = sq.msg(3, 4, '35. Утвердить: протокол УС № 8/26 от 25.06.2026')
    m36 = sq.msg(4, 3, '36. Утверждение зарегистрировано', kind='return', dy=58)
    m37 = sq.msg(4, 5, '37. approve(protocolNum = "8/26", protocolDate = "25.06.2026")')
    m38 = sq.msg(5, 6, '38. finalize(protocol) → итоговый хэш')
    m39 = sq.msg(6, 5, '39. finalHash = 8b41… (SHA-256)', kind='return', dy=48)
    sq.act(6, m38, m39)
    m40 = sq.msg(5, 4, '40. status = APPROVED, реквизиты протокола сохранены', kind='return')
    m41 = sq.msg(4, 0, '41. Уведомление: учебный план утверждён', kind='async')
    # Полоса активации = «объект выполняется». Между запросами объект простаивает,
    # поэтому одна сквозная полоса недопустима: дробим по запросам. Полоса ветви alt
    # охватывает обе ветви — вызов открыт в любой из них.
    sq.act(4, m1, m6)       # 1–6   открытие формы (чтение)
    sq.act(4, m7, m24)      # 7–24  сохранение + ЭЦП этапа 1 + проверка ФГОС
    sq.act(4, m25, m32)     # 25–32 визирование (шаг k)
    sq.act(4, m33, m34)     # 33–34 передача в Учёный совет
    sq.act(4, m35, m41)     # 35–41 утверждение и уведомление
    sq.act(5, m2, m5)
    sq.act(5, m8, m23)
    sq.act(5, m26, m31)
    sq.act(5, m37, m40)
    sq.act(6, m11, m14)
    return sq


def sequence_diagram():
    _geom_reset()
    W = 2760
    top = 120
    tmp = Canvas(200, 200)
    sq = _build_sequence(tmp, top, 4000)
    H = int(sq.y + 70)
    c = Canvas(W, H, scale=2)
    title(c, 'Диаграмма последовательности — экспертиза, валидация ФГОС и утверждение учебного плана')
    sq = _build_sequence(c, top, H - 36)
    global SEQ
    SEQ = sq
    sq.render()

    c.save(os.path.join(OUT, 'sequence_diagram.png'))


# ======================================================================
#  Реляционная схема (ER, нотация «воронья лапка»)
# ======================================================================
def er_table(c, x, y, w, name, cols, comment=None):
    """Таблица ER: шапка + строки (badge, имя, тип). Возвращает геометрию."""
    hh = 30
    rh = 15.2
    h = hh + rh * len(cols) + 8
    c.rect(x, y, w, h, fill='#ffffff', outline=LINE, width=1.3)
    # шапка — та же светлая полоса, что и у классов (общий ч/б стиль набора)
    c.rect(x + 1, y + 1, w - 2, hh - 2, fill='#ececec', outline=None)
    c.text(x + 10, y + 20, name, 11.8, 'bold', INK)
    if comment:
        c.text(x + w - 10, y + 20, comment, 9.2, 'normal', '#374151', anchor='rs')
    c.line([(x, y + hh), (x + w, y + hh)], fill=LINE, width=1.1)
    rows = {}
    yy = y + hh + 4.5
    for i, (key, cname, ctype) in enumerate(cols):
        yy += rh
        rows[cname] = yy - 5
        if i:                       # линия-разделитель, шапка уже отделена
            c.line([(x + 1, yy - 11), (x + w - 1, yy - 11)], fill='#e6e8ec', width=0.8)
        if key:
            c.text(x + 8, yy, key, 8.6, 'bold', INK)
        notnull = '*' in ctype
        ctext = ctype.replace('*', '')
        c.text(x + 40, yy, cname, 10.0, 'bold' if notnull else 'normal', '#111827')
        c.text(x + w - 10, yy, ctext, 9.4, 'bold' if notnull else 'normal',
               '#374151' if notnull else '#4b5563', anchor='rs')
    return dict(x=x, y=y, w=w, h=h, rows=rows)


def er_end(c, pt, toward, kind, label=None, lab_off=(0, 0), lab_anchor='ls'):
    """Окончание связи в нотации «воронья лапка»."""
    if kind == 'one':
        c.arrowhead(pt, toward, 'bar', LINE, 9)
    elif kind == 'zero-one':
        c.arrowhead(pt, toward, 'bar', LINE, 9)
        dx, dy = toward[0] - pt[0], toward[1] - pt[1]
        ln = (dx ** 2 + dy ** 2) ** 0.5 or 1
        c.circle(pt[0] + dx / ln * 12, pt[1] + dy / ln * 12, 3.4, fill='#ffffff',
                 outline=LINE, width=1.2)
    elif kind == 'many':
        c.arrowhead(pt, toward, 'crowfoot', LINE, 9)
    elif kind == 'zero-many':
        c.arrowhead(pt, toward, 'crowfoot', LINE, 9)
        dx, dy = toward[0] - pt[0], toward[1] - pt[1]
        ln = (dx ** 2 + dy ** 2) ** 0.5 or 1
        c.circle(pt[0] + dx / ln * 13, pt[1] + dy / ln * 13, 3.4, fill='#ffffff',
                 outline=LINE, width=1.2)
    if label:
        lx, ly = pt[0] + lab_off[0], pt[1] + lab_off[1]
        w = c.tw(label, 9.6)
        c.d.rectangle([lx * c.s - 2, (ly - 10) * c.s, (lx + w) * c.s + 2, (ly + 2) * c.s],
                      fill='#ffffff')
        c.text(lx, ly, label, 9.6, 'normal', '#111827', anchor=lab_anchor)
        x0 = lx - w - 2 if lab_anchor[0] == 'r' else lx - 2
        GEOM['labels'].append((label, x0, ly - 10, x0 + w + 4, ly + 2))


def db_schema_diagram():
    W = 2520
    COLS = [40, 550, 1060, 1570, 2080]
    BW = 400
    tables = {
        'standards_fgos': (0, 0, [
            ('PK', 'id', 'INT AI'), ('', 'code', 'TEXT*'), ('', 'title', 'TEXT*'),
            ('', 'degree_level', 'TEXT*'), ('', 'total_credits', 'INT* 240'),
            ('', 'max_exams_per_session', 'INT* 5'), ('', 'min_practice_credits', 'INT* 12'),
            ('', 'min_gia_credits', 'INT* 6'), ('', 'approval_date', 'TEXT*')]),
        'educational_programs': (1, 0, [
            ('PK', 'id', 'INT AI'), ('', 'code', 'TEXT*'), ('', 'title', 'TEXT*'),
            ('', 'level', 'TEXT*'), ('', 'study_form', 'TEXT*'),
            ('FK', 'fgos_standard_id', 'INT'), ('FK', 'department_id', 'INT')]),
        'departments': (3, 0, [
            ('PK', 'id', 'INT AI'), ('', 'name', 'TEXT*'), ('', 'short_name', 'TEXT*'),
            ('', 'type', 'TEXT*'), ('', 'phone', 'TEXT'), ('', 'email', 'TEXT')]),
        'curriculums': (2, 0, [
            ('PK', 'id', 'INT AI'), ('FK', 'program_id', 'INT'),
            ('', 'academic_year', 'TEXT*'), ('', 'version', 'TEXT*'),
            ('', 'status', 'TEXT*'), ('', 'total_credits', 'INT*'),
            ('', 'approved_protocol_num', 'TEXT'), ('', 'approved_protocol_date', 'TEXT'),
            ('', 'created_by_user', 'TEXT'), ('', 'created_at', 'DATETIME')]),
        'curriculum_disciplines': (4, 0, [
            ('PK', 'id', 'INT AI'), ('FK', 'curriculum_id', 'INT'),
            ('', 'block_type', 'TEXT*'), ('', 'discipline_name', 'TEXT*'),
            ('', 'semester_num', 'INT*'), ('', 'credits_ze', 'INT*'),
            ('', 'total_hours', 'INT*'), ('', 'lecture_hours', 'INT*'),
            ('', 'lab_hours', 'INT*'), ('', 'practice_hours', 'INT*'),
            ('', 'self_study_hours', 'INT*'), ('', 'control_form', 'TEXT*'),
            ('FK', 'implementing_department_id', 'INT')]),
        'competencies': (0, 1, [
            ('PK', 'id', 'INT AI'), ('FK', 'program_id', 'INT'),
            ('', 'code', 'TEXT*'), ('', 'category', 'TEXT*'), ('', 'title', 'TEXT*'),
            ('', 'description', 'TEXT*')]),
        'roles': (1, 1, [
            ('PK', 'id', 'INT AI'), ('', 'role_name', 'TEXT*'), ('', 'code', 'TEXT*'),
            ('', 'description', 'TEXT')]),
        'users': (2, 1, [
            ('PK', 'id', 'INT AI'), ('', 'username', 'TEXT*'), ('', 'full_name', 'TEXT*'),
            ('', 'email', 'TEXT*'), ('FK', 'role_id', 'INT'), ('FK', 'department_id', 'INT'),
            ('', 'position_title', 'TEXT')]),
        'service_notes': (3, 1, [
            ('PK', 'id', 'INT AI'), ('FK', 'curriculum_id', 'INT'),
            ('', 'note_num', 'TEXT*'), ('', 'note_date', 'TEXT*'), ('', 'reason', 'TEXT*'),
            ('FK', 'releasing_dept_id', 'INT'), ('FK', 'implementing_dept_id', 'INT'),
            ('', 'status', 'TEXT*'), ('', 'created_by', 'TEXT'),
            ('', 'created_at', 'DATETIME')]),
        'service_note_items': (4, 1, [
            ('PK', 'id', 'INT AI'), ('FK', 'service_note_id', 'INT'),
            ('FK', 'discipline_id', 'INT'), ('', 'change_type', 'TEXT*'),
            ('', 'old_val', 'TEXT'), ('', 'new_val', 'TEXT')]),
        'document_signatures': (0, 2, [
            ('PK', 'id', 'INT AI'), ('', 'doc_type', 'TEXT*'), ('', 'doc_id', 'INT*'),
            ('', 'step_order', 'INT*'), ('', 'role_title', 'TEXT*'),
            ('', 'signer_name', 'TEXT'), ('', 'status', 'TEXT*'),
            ('', 'comment', 'TEXT'), ('', 'signed_at', 'TEXT'), ('', 'sign_hash', 'TEXT')]),
        'announcements': (1, 2, [
            ('PK', 'id', 'INT AI'), ('', 'title', 'TEXT*'), ('', 'category', 'TEXT*'),
            ('', 'publish_date', 'TEXT*'), ('FK', 'author_id', 'INT'),
            ('', 'author_name', 'TEXT*'), ('', 'content', 'TEXT*'), ('', 'is_pinned', 'INT')]),
        'audit_logs': (2, 2, [
            ('PK', 'id', 'INT AI'), ('', 'event_time', 'TEXT*'), ('', 'user_name', 'TEXT*'),
            ('', 'user_role', 'TEXT*'), ('', 'action', 'TEXT*'), ('', 'entity_name', 'TEXT*'),
            ('', 'status', 'TEXT*'), ('', 'ip_address', 'TEXT*')]),
    }
    row_y = [170]
    row_h = {}
    for row in range(3):
        row_h[row] = max(30 + 15.2 * len(cols) + 8
                         for (c, r, cols) in tables.values() if r == row)
        if row < 2:
            row_y.append(row_y[row] + row_h[row] + 152)
    H = row_y[2] + row_h[2] + 110
    c = Canvas(W, H, scale=2)
    title(c, 'Схема базы данных anok_portal — 13 таблиц, 3NF')

    geo = {}
    _geom_reset()
    for name, (col, r, cols) in tables.items():
        geo[name] = er_table(c, COLS[col], row_y[r], BW, name, cols)
    GEOM['boxes'] = [(n, g['x'], g['y'], g['x'] + g['w'], g['y'] + g['h'])
                     for n, g in geo.items()]

    def rowy(t, col):
        return geo[t]['rows'][col]

    def Ledge(t):
        return geo[t]['x']

    def Redge(t):
        return geo[t]['x'] + geo[t]['w']

    def Top(t):
        return geo[t]['y']

    def Bot(t):
        return geo[t]['y'] + geo[t]['h']

    def er(pts, child_end=None, parent_end=None, c_labs=(), p_labs=()):
        _poly(pts, LINE, 1.3)
        GEOM['ends'].append((child_end, parent_end))
        c.line(pts, fill=LINE, width=1.3)
        if child_end:
            er_end(c, pts[0], pts[1], child_end, *c_labs)
        if parent_end:
            er_end(c, pts[-1], pts[-2], parent_end, *p_labs)

    # 1. educational_programs.fgos_standard_id → standards_fgos.id
    y = rowy('educational_programs', 'fgos_standard_id')
    er([(Ledge('educational_programs'), y), (Redge('standards_fgos'), y)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (7, -8)))
    # 2. curriculums.program_id → educational_programs.id
    y = rowy('curriculums', 'program_id')
    er([(Ledge('curriculums'), y), (Redge('educational_programs'), y)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (8, -8)))
    # 3. educational_programs.department_id → departments.id
    #    канал под строкой 0 (y = 400) и вход в нижнюю грань departments:
    #    верхний канал занят связью 4, нижняя грань departments свободна левее 1690
    _y30 = 400
    er([(Ledge('educational_programs') + 250, Bot('educational_programs')),
        (Ledge('educational_programs') + 250, _y30),
        (COLS[3] + 30, _y30), (COLS[3] + 30, Bot('departments'))],
       'zero-many', 'zero-one', c_labs=('0..*', (10, 15)), p_labs=('0..1', (-40, 15)))
    # 4. curriculum_disciplines.curriculum_id → curriculums.id
    #    подъём от правой грани curriculums мимо спуска связи 3, канал y = 96
    _x4 = Redge('curriculums') + 10
    er([(Redge('curriculums'), rowy('curriculums', 'academic_year')),
        (_x4, rowy('curriculums', 'academic_year')),
        (_x4, 96), (COLS[4] + 160, 96), (COLS[4] + 160, Top('curriculum_disciplines'))],
       'zero-one', 'zero-many', c_labs=('0..1', (10, -10)), p_labs=('0..*', (-42, -10)))
    # 5. curriculum_disciplines.implementing_department_id → departments.id
    #    вход в departments с правой грани; промежуток между столбцами 3 и 4 оставлен
    #    свободным для связи 8 (users → departments)
    y = rowy('curriculum_disciplines', 'implementing_department_id')
    er([(Ledge('curriculum_disciplines'), y), (COLS[3] + BW + 60, y),
        (COLS[3] + BW + 60, 230), (Redge('departments'), 230)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (8, 15)))
    # 6. competencies.program_id → educational_programs.id
    #    обход снизу: вертикаль столбца 0 поднимается в промежутке между строками
    #    и входит в нижнюю грань educational_programs (левая грань занята связями 1 и 2)
    er([(COLS[0] + 160, Top('competencies')), (COLS[0] + 160, 352),
        (COLS[1] + 150, 352), (COLS[1] + 150, Bot('educational_programs'))],
       'zero-many', 'zero-one', c_labs=('0..*', (10, -10)), p_labs=('0..1', (-38, 15)))
    # 7. users.role_id → roles.id
    y = rowy('users', 'role_id')
    yr = rowy('roles', 'id')
    er([(Ledge('users'), y), (1010, y), (1010, yr), (Redge('roles'), yr)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (7, -8)))
    # 8. users.department_id → departments.id
    #    справа от service_notes поднимается в промежутке между столбцами 3 и 4
    #    и входит в правую грань departments (нижняя занята связями 10 и 11)
    er([(COLS[2] + 30, Top('users')), (COLS[2] + 30, 430),
        (COLS[3] + 70, 430), (COLS[3] + 70, Bot('departments'))],
       'zero-many', 'zero-one', c_labs=('0..*', (10, -10)), p_labs=('0..1', (8, 15)))
    # 9. service_notes.curriculum_id → curriculums.id
    #    обход снизу: под строкой 1 до промежутка между столбцами 1 и 2, затем вверх
    #    под curriculums и вход в его нижнюю грань
    _x9 = COLS[2] + BW + 70
    er([(Ledge('service_notes'), rowy('service_notes', 'curriculum_id')),
        (_x9, rowy('service_notes', 'curriculum_id')), (_x9, 480),
        (COLS[2] + 250, 480), (COLS[2] + 250, Bot('curriculums'))],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (8, 15)))
    # 10. service_notes.releasing_dept_id → departments.id
    er([(COLS[3] + 120, Top('service_notes')), (COLS[3] + 120, Bot('departments'))],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -10)), p_labs=('0..1', (8, 15)))
    # 11. service_notes.implementing_dept_id → departments.id
    er([(COLS[3] + 210, Top('service_notes')), (COLS[3] + 210, Bot('departments'))],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -10)), p_labs=('0..1', (8, 15)))
    # 12. service_note_items.service_note_id → service_notes.id
    y = rowy('service_note_items', 'service_note_id')
    er([(Ledge('service_note_items'), y), (Redge('service_notes'), y)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (7, -8)))
    # 13. service_note_items.discipline_id → curriculum_disciplines.id
    er([(COLS[4] + 210, Top('service_note_items')),
        (COLS[4] + 210, Bot('curriculum_disciplines'))],
       'zero-many', 'zero-one', c_labs=('0..*', (10, -10)), p_labs=('0..1', (8, 15)))
    # 14. announcements.author_id → users.id (канал между строками 1 и 2)
    gy14 = row_y[1] + row_h[1] + 40
    er([(COLS[1] + 300, Top('announcements')), (COLS[1] + 300, gy14),
        (COLS[2] + 150, gy14), (COLS[2] + 150, Bot('users'))],
       'zero-many', 'zero-one', c_labs=('0..*', (8, -10)), p_labs=('0..1', (8, 15)))

    c.save(os.path.join(OUT, 'db_schema_diagram.png'))


if __name__ == '__main__':
    class_diagram('ru')
    class_diagram('en')
    component_diagram('ru')
    component_diagram('en')
    deployment_diagram('ru')
    deployment_diagram('en')
    sequence_diagram()
    db_schema_diagram()
    print('ok')
