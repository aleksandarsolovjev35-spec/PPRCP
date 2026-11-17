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
    h = HDR + (14 if spec.get('stereo') else 0) + PAD
    h += len(spec['attrs']) * LH + 5
    h += len(spec['ops']) * LH + 14
    return h


def draw_class(c, x, y, w, spec):
    stereo = spec.get('stereo')
    h = _measure_class(spec, w)
    hdr_h = HDR + (14 if stereo else 0)
    c.rect(x, y, w, h, fill='#ffffff', outline=LINE, width=1.4)
    c.rect(x + 1, y + 1, w - 2.2, hdr_h - 1.6, fill=HEAD_FILL, outline=None)
    c.line([(x, y + hdr_h), (x + w, y + hdr_h)], fill=LINE, width=1.2)
    cy = y + 15
    if stereo:
        c.text(x + w / 2, cy + 1, '«%s»' % stereo, F_STEREO, 'normal', '#374151', anchor='ms')
        cy += 14
    weight = 'bolditalic' if spec.get('abstract') else 'bold'
    c.text(x + w / 2, cy + 12, spec['name'], F_NAME, weight, INK, anchor='ms')
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


def _auto_labels(c, pts, m0=None, m1=None, r0=None, r1=None,
                 m0_at=None, m1_at=None, r0_at=None, r1_at=None):
    """Кратность — над линией у конца связи, имя роли — под линией."""
    def place(pt, other, mult, role, mult_at, role_at):
        dx, dy = other[0] - pt[0], other[1] - pt[1]
        if abs(dx) >= abs(dy):        # горизонтальная связь
            sgn = 1 if dx > 0 else -1
            manch = 'ls' if sgn > 0 else 'rs'
            if mult:
                if mult_at:
                    a = mult_at[2] if len(mult_at) > 2 else 'ls'
                    _lab(c, mult_at[0], mult_at[1], mult, a)
                else:
                    _lab(c, pt[0] + sgn * 8, pt[1] - 7, mult, manch)
            if role:
                if role_at:
                    a = role_at[2] if len(role_at) > 2 else 'ls'
                    _lab(c, role_at[0], role_at[1], role, a, size=9.8, fill='#374151')
                else:
                    _lab(c, pt[0] + sgn * 8, pt[1] + 15, role, manch,
                         size=9.8, fill='#374151')
        else:                          # вертикальная связь
            sgn = 1 if dy > 0 else -1
            if mult:
                if mult_at:
                    a = mult_at[2] if len(mult_at) > 2 else 'ls'
                    _lab(c, mult_at[0], mult_at[1], mult, a)
                else:
                    _lab(c, pt[0] - 9, pt[1] + (10 if sgn > 0 else -4), mult, 'rs')
            if role:
                if role_at:
                    a = role_at[2] if len(role_at) > 2 else 'ls'
                    _lab(c, role_at[0], role_at[1], role, a, size=9.8, fill='#374151')
                else:
                    _lab(c, pt[0] + 9, pt[1] + (10 if sgn > 0 else -4), role, 'ls',
                         size=9.8, fill='#374151')
    place(pts[0], pts[1], m0, r0, m0_at, r0_at)
    place(pts[-1], pts[-2], m1, r1, m1_at, r1_at)


def class_diagram():
    W = 2600
    COLS = [50, 580, 1110, 1640, 2170]
    BW = 400
    specs = {
        'StandardFGOS': dict(name='StandardFGOS', attrs=[
            '- id: Integer {id}', '- code: String', '- title: String',
            '- degreeLevel: String', '- totalCredits: Integer = 240',
            '- maxExamsPerSession: Integer = 5', '- minPracticeCredits: Integer = 12',
            '- minGiaCredits: Integer = 6', '- approvalDate: Date'], ops=[
            '+ check(c: Curriculum): ViolationList',
            '+ thresholds(): Thresholds']),
        'EducationalProgram': dict(name='EducationalProgram', attrs=[
            '- id: Integer {id}', '- code: String «09.03.04»', '- title: String',
            '- level: EducationLevel', '- studyForm: StudyForm'], ops=[
            '+ curriculums(year: String): List',
            '+ addCompetency(k: Competency): void']),
        'Curriculum': dict(name='Curriculum', attrs=[
            '- id: Integer {id}', '- academicYear: String', '- version: String = "1.0"',
            '- status: CurriculumStatus', '- totalCredits: Integer = 240',
            '- protocolNum: String', '- protocolDate: Date',
            '- createdAt: DateTime'], ops=[
            '+ semesterBalance(sem: Integer): Balance',
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
            '+ releasingCurriculums(): List']),
        'AuditLog': dict(name='AuditLog', attrs=[
            '- id: Integer {id}', '- eventTime: DateTime', '- userName: String',
            '- userRole: String', '- action: String', '- entityName: String',
            '- status: String', '- ipAddress: String'], ops=[
            '+ log(e: AuditEvent): void', '+ export(fmt: String): String']),
        'Competency': dict(name='Competency', attrs=[
            '- id: Integer {id}', '- code: String «УК-1 … ПК-4»', '- category: String',
            '- title: String', '- description: String'], ops=[
            '+ matches(pattern: String): Boolean']),
        'Document': dict(name='Document', stereo='abstract', abstract=True, attrs=[
            '- id: Integer {id}', '- docType: DocType', '- status: DocumentStatus',
            '- createdAt: DateTime', '- author: String'], ops=[
            '+ sign(role: Role, hash: String): Signature',
            '+ verify(hash: String): Boolean', '+ nextStep(): Integer']),
        'DocumentSignature': dict(name='DocumentSignature', attrs=[
            '- id: Integer {id}', '- stepOrder: Integer {1..4}', '- roleTitle: String',
            '- signerName: String', '- status: SignatureStatus', '- comment: String',
            '- signedAt: DateTime', '- signHash: String «SHA-256»'], ops=[
            '+ verify(hash: String): Boolean', '+ format(): String']),
        'User': dict(name='User', attrs=[
            '- id: Integer {id}', '- username: String', '- fullName: String',
            '- email: String', '- positionTitle: String'], ops=[
            '+ hasPermission(a: Action): Boolean',
            '+ canSign(step: Integer): Boolean']),
        'Announcement': dict(name='Announcement', attrs=[
            '- id: Integer {id}', '- title: String', '- category: String',
            '- publishDate: Date', '- authorName: String', '- content: Text',
            '- isPinned: Boolean = false'], ops=[
            '+ isVisibleOn(d: Date): Boolean']),
        'ServiceNote': dict(name='ServiceNote', attrs=[
            '- id: Integer {id}', '- noteNum: String', '- noteDate: Date',
            '- reason: String', '- status: NoteStatus', '- createdAt: DateTime',
            '- author: String'], ops=[
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
    H = bottom + 340
    c = Canvas(W, H, scale=2)
    title(c, 'Диаграмма классов — объектная модель портала Центра АНОК (UML 2.5)',
          'Видимость членов: + public, − private. Кратности указаны на концах связей; '
          'ромб у класса-«целого» — композиция; треугольник — генерализация.')

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

    def assoc(pts, start=None, end=None, dash=None, **lab):
        c.line(pts, fill=LINE, width=1.3, dash=dash)
        if start:
            c.arrowhead(pts[0], pts[1], start, LINE, 10)
        if end:
            c.arrowhead(pts[-1], pts[-2], end, LINE, 10)
        _auto_labels(c, pts, **lab)

    # 1. StandardFGOS 1 —— 1..* EducationalProgram
    assoc([R('StandardFGOS', 0.42), L('EducationalProgram', 0.42)],
          m0='1', r0='standard', m1='0..*', r1='programs')
    # 2. EducationalProgram 1 —— 1..* Curriculum
    assoc([R('EducationalProgram', 0.62), L('Curriculum', 0.62)],
          m0='1', r0='program', m1='0..*', r1='curriculums')
    # 3. EducationalProgram ◆—— 0..* Competency
    assoc([B('EducationalProgram', 0.5), T('Competency', 0.5)],
          start='diamond_filled', m0='1', m1='0..*', r1='competencies',
          m1_at=(geo['Competency'][0] + BW + 8, geo['Competency'][1] - 8),
          r1_at=(geo['Competency'][0] + BW + 8 + 46, geo['Competency'][1] - 8))
    # 4. EducationalProgram 0..* —— 1 Department  (верхний канал)
    ch = row_y[0] - 56
    pa, pb = T('EducationalProgram', 0.22), T('Department', 0.24)
    assoc([pa, (pa[0], ch), (pb[0], ch), pb],
          m0='0..*', r0='ownerDept', m1='1',
          m0_at=(pa[0] + 8, ch - 10), r0_at=(pa[0] + 52, ch - 10),
          m1_at=(pb[0] + 8, ch - 10))
    # 5. Curriculum ◁—— Document
    assoc([B('Curriculum', 0.5), T('Document', 0.5)], start='hollow')
    # 6. Document ◆—— 1..* DocumentSignature
    assoc([R('Document', 0.55), L('DocumentSignature', 0.55)],
          start='diamond_filled', m0='1', m1='1..*', r1='signatures')
    # 7. Document ◁—— ServiceNote
    assoc([B('Document', 0.5), T('ServiceNote', 0.5)], start='hollow')
    # 8. Curriculum ◆—— 1..* CurriculumDiscipline
    assoc([R('Curriculum', 0.8), L('CurriculumDiscipline', 0.8)],
          start='diamond_filled', m0='1', m1='1..*', r1='disciplines')
    # 9. CurriculumDiscipline 0..* —— 1 Department
    _d9 = R('CurriculumDiscipline', 0.34)
    _l9 = L('Department', 0.34)
    assoc([_d9, _l9], m0='0..*', r0='implementing',
          m0_at=(_d9[0] + 8, _d9[1] - 8),
          r0_at=(_l9[0] - 8, _l9[1] - 8, 'rs'))
    # 10. Department 1 —— 0..* ServiceNote (выпускающая кафедра)
    gx1 = COLS[3] + BW + 24
    y_ch = bottom + 44
    d1 = L('Department', 0.72)
    s1 = B('ServiceNote', 0.2)
    assoc([d1, (gx1, d1[1]), (gx1, y_ch), (s1[0], y_ch), s1],
          m0='1', m1='0..*', r1='releasingNotes',
          m0_at=(d1[0] - 8, d1[1] - 8, 'rs'),
          m1_at=(s1[0] + 10, y_ch - 9), r1_at=(s1[0] + 10, y_ch + 16))
    # 11. Department 1 —— 0..* ServiceNote (обеспечивающая кафедра)
    gx2 = COLS[3] + BW + 62
    y_ch2 = y_ch + 34
    d2 = L('Department', 0.92)
    s2 = B('ServiceNote', 0.58)
    assoc([d2, (gx2, d2[1]), (gx2, y_ch2), (s2[0], y_ch2), s2],
          m0='1', m1='0..*', r1='implementingNotes',
          m0_at=(d2[0] - 8, d2[1] - 8, 'rs'),
          m1_at=(s2[0] + 10, y_ch2 - 9), r1_at=(s2[0] + 10, y_ch2 + 16))
    # 12. ServiceNote ◆—— 1..* ServiceNoteItem
    assoc([R('ServiceNote', 0.5), L('ServiceNoteItem', 0.5)],
          start='diamond_filled', m0='1', m1='1..*', r1='items')
    # 13. ServiceNoteItem 0..* —— 1 CurriculumDiscipline (канал между колонками 2/3)
    chx = COLS[2] + BW + 38
    sni = L('ServiceNoteItem', 0.78)
    chy = geo['CurriculumDiscipline'][1] + geo['CurriculumDiscipline'][3] + 44
    cdb = B('CurriculumDiscipline', 0.78)
    assoc([sni, (chx, sni[1]), (chx, chy), (cdb[0], chy), cdb],
          m0='0..*', r0='discipline', m1='1',
          m0_at=(chx + 8, sni[1] - 10), r0_at=(chx + 8, sni[1] + 20),
          m1_at=(cdb[0] + 8, chy + 16))
    # 14. User 0..* —— 1 Role
    assoc([B('User', 0.42), T('Role', 0.42)], m0='0..*', r0='role', m1='1')
    # 15. User 0..* —— 0..1 Department
    assoc([T('User', 0.66), B('Department', 0.66)], m0='0..*', r0='department', m1='0..1')

    # ------------------------------------------------------------ примечания
    ax, ay, aw, ah = geo['AuditLog']
    ny = bottom + 30
    note(c, ax + 10, ny, 400, [
        'Журнал append-only. ФИО и роль фиксируются',
        'снимком (user_name, user_role), внешний ключ',
        'на users не объявляется — см. audit_logs',
        'в portal/database/schema.sql.'], fill='#fffdf0')
    c.line([(ax + 200, ay + ah), (ax + 200, ny)], fill='#8a6d00', width=1.0, dash=(6, 4))

    an, ay2, aw2, ah2 = geo['Announcement']
    note(c, an + 10, ay2 + ah2 + 30, 390, [
        'authorName — денормализованный снимок',
        'автора публикации; связь с users',
        'не объявляется (в DDL внешнего ключа нет).'], fill='#fffdf0')
    c.line([(an + 180, ay2 + ah2), (an + 180, ay2 + ah2 + 30)], fill='#8a6d00',
           width=1.0, dash=(6, 4))

    # ------------------------------------------------------------- легенда
    lx, ly, lw, lh = COLS[3] + 30, bottom + 118, 500, 200
    legend_box(c, lx, ly, lw, lh, 'Notation')
    yy = ly + 36
    rows = [('assoc', 'ассоциация (направление навигации не задано)'),
            ('comp', 'композиция: часть существует только в целом'),
            ('gen', 'генерализация: Curriculum и ServiceNote — виды Document'),
            ('note', 'примечание UML')]
    for kind, text in rows:
        if kind == 'assoc':
            c.line([(lx + 18, yy), (lx + 80, yy)], fill=LINE, width=1.3)
        elif kind == 'comp':
            c.line([(lx + 18, yy), (lx + 80, yy)], fill=LINE, width=1.3)
            c.arrowhead((lx + 18, yy), (lx + 80, yy), 'diamond_filled', LINE, 8)
        elif kind == 'gen':
            c.line([(lx + 18, yy), (lx + 80, yy)], fill=LINE, width=1.3)
            c.arrowhead((lx + 18, yy), (lx + 80, yy), 'hollow', LINE, 8)
        else:
            c.poly([(lx + 18, yy - 8), (lx + 62, yy - 8), (lx + 80, yy + 8),
                    (lx + 18, yy + 8)], fill='#fffdf0', outline='#8a6d00', width=1.0)
        c.text(lx + 94, yy + 4, text, 10.6, 'normal', '#374151')
        yy += 31
    c.text(lx + 18, yy + 8, 'Кратности: «1» — ровно один; «0..1» — ноль или один;', 10.2, 'normal', MUTED)
    c.text(lx + 18, yy + 24, '«1..*», «0..*» — множество экземпляров;', 10.2, 'normal', MUTED)
    c.text(lx + 18, yy + 40, '{id} — первичный ключ; {1..8} — ограничение значения.', 10.2, 'normal', MUTED)

    c.save(os.path.join(OUT, 'class_diagram.png'))



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
    r_ball, r_sock = 6.5, 10.0
    ym = (y_top + y_bot) / 2
    if provider == 'top':          # поставщик сверху: гнездо потребителя снизу
        c.line([(x, y_top), (x, ym - r_ball)], fill=LINE, width=1.4)
        c.arc(x, ym, r_sock, 0, 180, fill=LINE, width=1.5)
        c.circle(x, ym, r_ball, fill='#ffffff', outline=LINE, width=1.3)
        c.line([(x, ym + r_sock), (x, y_bot)], fill=LINE, width=1.4)
        if name:
            c.text(x + r_sock + 10, ym + 4, name, size, 'bold', '#1f2937')
    else:                          # поставщик снизу: гнездо потребителя сверху
        c.line([(x, y_bot), (x, ym + r_ball)], fill=LINE, width=1.4)
        c.arc(x, ym, r_sock, 180, 360, fill=LINE, width=1.5)
        c.circle(x, ym, r_ball, fill='#ffffff', outline=LINE, width=1.3)
        c.line([(x, ym - r_sock), (x, y_top)], fill=LINE, width=1.4)
        if name:
            c.text(x + r_sock + 10, ym + 4, name, size, 'bold', '#1f2937')
    return ym


def subsystem_frame(c, x, y, w, h, name, stereo='subsystem', fill='#fcfdff'):
    c.rect(x, y, w, h, fill=fill, outline='#94a3b8', width=1.4)
    st = '«%s»' % stereo
    tab = c.tw(st, 9.6) + c.tw(name, 12.2, 'bold') + 34
    c.rect(x, y, tab, 26, fill='#eef2f7', outline='#94a3b8', width=1.2)
    c.text(x + 10, y + 17, st, 9.6, 'normal', '#475569')
    c.text(x + 18 + c.tw(st, 9.6), y + 18, name, 12.2, 'bold', '#1f2937')


def component_slim(c, x, y, w, h, name, stereo='component', fill='#eef2fb', name_size=12.6):
    """Каноническое изображение компонента UML 2.5: ключевое слово, имя, пиктограмма.

    Внутренние секции не используются — обязанности компонента выносятся
    в примечания, как того требует классическая нотация."""
    c.rect(x, y, w, h, fill=fill, outline=LINE, width=1.4)
    c.text(x + w / 2 - 10, y + 20, '«%s»' % stereo, 9.8, 'normal', '#374151', anchor='ms')
    c.text(x + w / 2 - 10, y + 42, name, name_size, 'bold', INK, anchor='ms')
    _comp_icon(c, x + w - 34, y + 12)


def component_diagram():
    W, H = 1880, 1180
    CX = 940                                  # ось симметрии компоновки
    c = Canvas(W, H, scale=2)
    title(c, 'Component Diagram — ANOK Center Portal',
          'UML 2.5: «component»; assembly connector — provided interface «ball» fitted into '
          'required interface «socket»; «use» — dependency without a formal interface.')

    # ---------------- граница подсистемы --------------------------------
    subsystem_frame(c, 60, 130, 1640, 660, 'ANOK Center Portal')

    # ---------------- компоненты ----------------------------------------
    ui_w, ui_h, ui_y = 400, 78, 168
    component_slim(c, CX - ui_w / 2, ui_y, ui_w, ui_h, 'PortalUI', fill='#e8f1fe')

    k_w, k_h, k_y = 1480, 78, 330
    component_slim(c, CX - k_w / 2, k_y, k_w, k_h, 'HttpKernel', fill='#eef2fb')

    sv_w, sv_h, sv_y, sv_step = 264, 78, 492, 290
    sv_x = [CX - 2 * sv_step - sv_w / 2 + i * sv_step for i in range(5)]
    services = ['CurriculumService', 'FgosValidationEngine', 'WorkflowManager',
                'MemoManager', 'AuditLogger']
    ifaces = ['ICurriculumService', 'IFgosValidation', 'IWorkflow',
              'IMemoProcessing', 'IAuditSink']
    for x, nm in zip(sv_x, services):
        component_slim(c, x, sv_y, sv_w, sv_h, nm, fill='#f3f0fd')

    d_y = 654
    component_slim(c, CX - k_w / 2, d_y, k_w, k_h, 'DataAccessLayer', fill='#eaf5ec')

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
                fill='#fdf4e3', outline=LINE, width=3)
    c.rect(dbx, dby + 12, dbw, dbh - 24, fill='#fdf4e3', outline=None)
    c.line([(dbx, dby + 12), (dbx, dby + dbh - 12)], fill=LINE, width=1.4)
    c.line([(dbx + dbw, dby + 12), (dbx + dbw, dby + dbh - 12)], fill=LINE, width=1.4)
    c.d.arc([dbx * c.s, (dby + dbh - 24) * c.s, (dbx + dbw) * c.s, (dby + dbh) * c.s],
            0, 180, fill=LINE, width=4)
    c.text(CX, dby + 50, '«database» anok_portal', 12.4, 'bold', INK, anchor='ms')
    c.text(CX, dby + 72, '13 tables · 3NF · utf8mb4', 10.0, 'normal', '#374151', anchor='ms')
    c.line([(CX, d_y + 78), (CX, dby)], fill=LINE, width=1.3, dash=(7, 5))
    c.arrowhead((CX, dby), (CX, d_y + 78), 'open', LINE, 10)
    c.text(CX + 14, (d_y + 78 + dby) / 2 + 4, '«use»', 10.4, 'italic', '#374151')

    # ---------------- примечания ----------------------------------------
    note(c, 60, 830, 600, [
        'PortalUI: HTML/CSS/JS are generated by the server (portal/server.py,',
        'portal/index.php); Chart.js, jQuery, DataTables, FullCalendar,',
        'SheetJS and jsPDF are loaded from the jsDelivr CDN.'], fill='#fffdf0')
    note(c, 1210, 830, 610, [
        'HttpKernel: 15 pages (?page=…) and 3 REST endpoints',
        '(/api/stats, /api/plans, /api/announcements), authentication,',
        'RoleCode-based authorization, CSRF token validation.'], fill='#fffdf0')

    # ---------------- легенда -------------------------------------------
    lx, ly, lw, lh = 60, 1000, 1120, 150
    legend_box(c, lx, ly, lw, lh, 'Notation')
    r1, r2 = ly + 46, ly + 100
    c.line([(lx + 26, r1), (lx + 46, r1)], fill=LINE, width=1.3)
    c.arc(lx + 52, r1, 10, 270, 90, fill=LINE, width=1.4)
    c.circle(lx + 52, r1, 6, fill='#ffffff', outline=LINE, width=1.2)
    c.line([(lx + 62, r1), (lx + 84, r1)], fill=LINE, width=1.3)
    c.text(lx + 96, r1 + 5, 'assembly connector: «ball» in «socket»', 10.6, 'normal', '#374151')
    c.line([(lx + 450, r1), (lx + 516, r1)], fill=LINE, width=1.2, dash=(7, 5))
    c.arrowhead((lx + 516, r1), (lx + 450, r1), 'open', LINE, 9)
    c.text(lx + 528, r1 + 5, '«use» dependency (no formal interface)', 10.6,
           'normal', '#374151')
    _comp_icon(c, lx + 26, r2 - 14)
    c.text(lx + 96, r2 + 5, 'component: «component» keyword + icon', 10.6,
           'normal', '#374151')
    c.rect(lx + 450, r2 - 16, 46, 30, fill='#fcfdff', outline='#94a3b8', width=1.3)
    c.text(lx + 528, r2 + 5, '«subsystem» boundary', 10.6, 'normal', '#374151')

    c.save(os.path.join(OUT, 'component_diagram.png'))


# ======================================================================
#  Диаграмма развёртывания
# ======================================================================
def node3d(c, x, y, w, h, stereo, name, depth=16, fill='#eef2fb', sk=11):
    """Узел UML в виде трёхмерного параллелепипеда."""
    c.rect(x, y, w, h, fill=fill, outline=LINE, width=1.4)
    c.poly([(x, y), (x + sk, y - depth), (x + w + sk, y - depth), (x + w, y)],
           fill='#dbe3f4', outline=LINE, width=1.3)
    c.poly([(x + w, y), (x + w + sk, y - depth), (x + w + sk, y + h - depth), (x + w, y + h)],
           fill='#ccd7ee', outline=LINE, width=1.3)
    c.line([(x, y), (x + w, y)], fill=LINE, width=1.4)
    if stereo:
        c.text(x + 14, y + 20, '«%s»' % stereo, 9.8, 'normal', '#374151')
    if name:
        c.text(x + 14, y + 41, name, 13.2, 'bold', INK)


def artifact(c, x, y, w, h, name, lines=(), fill='#ffffff'):
    fold = 12
    c.poly([(x, y), (x + w - fold, y), (x + w, y + fold), (x + w, y + h), (x, y + h)],
           fill=fill, outline=LINE, width=1.2)
    c.poly([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)],
           fill='#eef1f6', outline=LINE, width=1.0)
    c.text(x + 10, y + 15, '«artifact»', 8.8, 'normal', '#4b5563')
    c.text(x + 10, y + 30, name, 11.2, 'bold', INK)
    yy = y + 46
    for ln in lines:
        c.text_clip(x + 10, yy, ln, w - 20, 9.8, 'normal', '#374151')
        yy += 13.5


def env(c, x, y, w, h, stereo, name, note_text=None, fill='#f7f9fe'):
    c.rect(x, y, w, h, fill=fill, outline='#4b5563', width=1.2)
    c.text(x + 10, y + 16, '«%s»' % stereo, 8.8, 'normal', '#4b5563')
    c.text(x + 10, y + 32, name, 11.4, 'bold', '#111827')
    if note_text:
        c.text(x + 10, y + 47, note_text, 9.6, 'normal', '#4b5563')
        return y + 58
    return y + 42


def deployment_diagram():
    W, H = 2480, 1420
    c = Canvas(W, H, scale=2)
    title(c, 'Диаграмма развёртывания — физическая топология портала Центра АНОК',
          'UML 2.5: узел «device» — трёхмерный блок; «execution environment» — среда исполнения внутри узла; '
          '«artifact» — развёртываемый файл; линия связи подписана «protocol» и номером TCP-порта.')

    # ---------------- клиентская станция --------------------------------
    node3d(c, 80, 260, 540, 390, 'device', 'Рабочая станция пользователя')
    y0 = env(c, 106, 316, 488, 300, 'execution environment',
             'Веб-браузер (HTML5, CSS3, ES2020)', 'Chrome 120+ · Firefox 121+ · Edge 120+')
    artifact(c, 124, y0 + 4, 452, 104, 'Страницы портала',
             ['index.php (шаблон) → HTML', 'assets/app.css · assets/app.js',
              'вкладки семестров 1–8'], fill='#ffffff')
    artifact(c, 124, y0 + 120, 452, 78, 'Клиентские модули (CDN)',
             ['Chart.js · FullCalendar · DataTables · SheetJS'], fill='#ffffff')

    # ---------------- сервер приложений ---------------------------------
    node3d(c, 860, 210, 640, 500, 'device', 'Сервер приложений (portal host)')
    y1 = env(c, 886, 266, 588, 420, 'execution environment',
             'Python 3.11 (http.server) / PHP 8.1-FPM', 'порт TCP 8000, многопоточная обработка')
    c.rect(904, y1 + 6, 552, 116, fill='#eef2fb', outline=LINE, width=1.3)
    _comp_icon(c, 1422, y1 + 14)
    c.text(916, y1 + 22, '«component» Portal Application', 10.6, 'bold', INK)
    for i, ln in enumerate(['server.py — роутер, контроллеры, слой сервисов',
                            'index.php — альтернативная реализация (PHP + PDO)',
                            'доступ к БД: PDO / sqlite3, prepared statements']):
        c.text_clip(916, y1 + 42 + i * 16, ln, 520, 9.8, 'normal', '#374151')
    artifact(c, 904, y1 + 136, 552, 108, 'Развёртываемые артефакты',
             ['portal/server.py · portal/index.php',
              'portal/config.php (DB_HOST, DB_NAME, DB_USER)',
              'portal/database/schema.sql · seed.sql'], fill='#ffffff')

    # ---------------- сервер БД -----------------------------------------
    node3d(c, 1740, 250, 580, 430, 'device', 'Сервер баз данных (варианты СУБД)')
    # вариант 1 — MySQL/MariaDB
    c.rect(1766, 300, 528, 168, fill='#f7f9fe', outline='#4b5563', width=1.2)
    c.text(1776, 316, '«execution environment» MySQL 8.0 / MariaDB 10.6', 9.2, 'normal', '#4b5563')
    c.text(1776, 331, 'InnoDB · utf8mb4 · порт TCP 3306', 9.6, 'normal', '#374151')
    artifact(c, 1784, 342, 492, 108, 'anok_portal',
             ['13 таблиц · 3NF · FOREIGN KEY',
              'schema.sql + seed.sql (демо-данные)'], fill='#ffffff')
    # вариант 2 — SQLite
    c.rect(1766, 484, 528, 168, fill='#fdf8ef', outline='#4b5563', width=1.2)
    c.text(1776, 500, '«execution environment» SQLite 3', 9.2, 'normal', '#4b5563')
    c.text(1776, 515, 'автономный режим · файл portal.db (WAL)', 9.6, 'normal', '#374151')
    artifact(c, 1784, 526, 492, 108, 'portal.db',
             ['создаётся автоматически при первом',
              'запуске server.py из schema.sql + seed.sql'], fill='#ffffff')

    # ---------------- линии связи ----------------------------------------
    c.line([(620, 420), (860, 420)], fill=LINE, width=1.6)
    c.text(640, 390, '«protocol» HTTP/1.1 · HTTPS', 10.4, 'bold', '#111827')
    c.text(640, 404, 'TCP 8000', 10.0, 'normal', '#374151')
    c.text(632, 442, 'GET/POST, REST/JSON', 9.6, 'italic', '#4b5563')

    c.line([(1500, 420), (1740, 420)], fill=LINE, width=1.6)
    c.text(1514, 390, '«protocol» SQL (PDO)', 10.4, 'bold', '#111827')
    c.text(1514, 404, 'TCP 3306', 10.0, 'normal', '#374151')
    c.text(1508, 442, 'или файл portal.db', 9.6, 'italic', '#4b5563')

    # ---------------- CDN (необязательный узел) ---------------------------
    node3d(c, 80, 790, 540, 230, 'device', 'CDN библиотек (опционально)', fill='#f4f4f5')
    c.text(94, 856, '«execution environment» jsDelivr / cdnjs', 9.4, 'normal', '#4b5563')
    artifact(c, 104, 872, 492, 90, 'Chart.js · FullCalendar · DataTables',
             ['HTTPS, порт TCP 443', 'без сети — локальные копии в assets/vendor/'],
             fill='#ffffff')
    c.line([(350, 790), (350, 650)], fill='#6b7280', width=1.3, dash=(6, 4))
    c.text(362, 702, '«protocol» HTTPS', 9.8, 'normal', '#374151')
    c.text(362, 716, 'TCP 443', 9.8, 'normal', '#374151')

    # ---------------- резервное копирование -------------------------------
    node3d(c, 1560, 800, 760, 210, 'device', 'Сервер резервного копирования', fill='#f4f4f5')
    artifact(c, 1584, 866, 712, 106, 'Ежедневный дамп anok_portal.sql',
             ['mysqldump / sqlite3 .backup → архив, ротация 30 дней',
              '«protocol» SFTP · TCP 22 (задание cron)'], fill='#ffffff')
    c.line([(2030, 650), (1980, 800)], fill='#6b7280', width=1.3, dash=(6, 4))
    c.text(1890, 726, '«protocol» SFTP · TCP 22', 9.8, 'normal', '#374151')

    # ---------------- легенда ---------------------------------------------
    lx, ly, lw, lh = 80, 1080, 900, 230
    legend_box(c, lx, ly, lw, lh, 'Notation')
    node3d(c, lx + 26, ly + 60, 90, 34, '', '', depth=10, fill='#eef2fb', sk=8)
    c.text(lx + 150, ly + 48, '«device» — физический узел (компьютер, сервер)', 10.6, 'normal', '#374151')
    c.rect(lx + 26, ly + 104, 90, 34, fill='#f7f9fe', outline='#4b5563', width=1.1)
    c.text(lx + 150, ly + 92, '«execution environment» — среда исполнения в узле', 10.6, 'normal', '#374151')
    c.poly([(lx + 26, ly + 146), (lx + 92, ly + 146), (lx + 102, ly + 156),
            (lx + 102, ly + 180), (lx + 26, ly + 180)],
           fill='#ffffff', outline=LINE, width=1.1)
    c.text(lx + 150, ly + 138, '«artifact» — развёртываемый файл', 10.6, 'normal', '#374151')
    c.line([(lx + 26, ly + 200), (lx + 108, ly + 200)], fill=LINE, width=1.5)
    c.text(lx + 150, ly + 190, 'линия связи: «protocol» + TCP-порт', 10.6, 'normal', '#374151')

    note(c, 1020, 1080, 1300, [
        'Вариант 1 (автономный): python3 server.py — SQLite portal.db создаётся из schema.sql и seed.sql',
        'при первом запуске. Вариант 2 (PHP + MySQL/MariaDB): импорт schema.sql и seed.sql,',
        'запуск php -S 0.0.0.0:8000 -t portal. Узлы CDN и резервного копирования — необязательные.'],
        fill='#fffdf0')

    c.save(os.path.join(OUT, 'deployment_diagram.png'))



# ======================================================================
#  Диаграмма последовательности
# ======================================================================
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
                c.rect(x - w / 2, self.top - 6, w, h, fill='#eef2fb', outline=LINE, width=1.4)
                c.text(x, self.top + 8, '«%s»' % stereo, 9.2, 'normal', '#4b5563', anchor='ms')
                c.text(x, self.top + 26, name, 11.0, 'bold', INK, anchor='ms')
                head_bottom.append(self.top + 38)
        # 2. рамки фрагментов (под всеми сообщениями)
        for (x0, x1, op, guards, in_tab, y0, y1) in self.frags:
            c.rect(x0, y0, x1 - x0, y1 - y0, fill=None, outline='#374151', width=1.3,
                   dash=(7, 5))
            tab_w = 58
            if in_tab and guards:
                tab_w = max(58, 66 + c.tw(guards[0][1], 10.0) + 10)
            c.poly([(x0, y0), (x0 + tab_w, y0), (x0 + tab_w, y0 + 21),
                    (x0 + tab_w - 12, y0 + 31), (x0, y0 + 31)],
                   fill='#ffffff', outline='#374151', width=1.3)
            c.text(x0 + 9, y0 + 20, op, 10.4, 'bold', '#111827')
            for k, (gy, guard) in enumerate(guards):
                if k == 0:
                    gx, gy_text = x0 + (66 if in_tab else 70), y0 + 20
                else:
                    c.line([(x0 + 1, gy), (x1 - 1, gy)], fill='#374151', width=1.1, dash=(7, 5))
                    gx, gy_text = x0 + 10, gy - 7
                self.guards_draw.append((gx, gy_text, guard))
        # 3. линии жизни (пунктир) — после рамок, до сообщений
        for x, hb in zip(self.xs, head_bottom):
            c.line([(x, hb), (x, self.bottom)], fill='#6b7280', width=1.1, dash=(6, 5))
        # 4. полосы активности — до сообщений
        for (i, y0, y1, level) in self.acts:
            x = self.xs[i] + level * 7
            c.rect(x - 7, y0, 14, max(20, y1 - y0), fill='#f4f6fb', outline='#374151', width=1.2)
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
                x1, x2 = self.xs[a], self.xs[b]
                if kind == 'sync':
                    c.line([(x1, y), (x2, y)], fill=LINE, width=1.4)
                    c.arrowhead((x2, y), (x1, y), 'filled', LINE, 10)
                else:
                    c.line([(x1, y), (x2, y)], fill=LINE, width=1.2, dash=(6, 4))
                    c.arrowhead((x2, y), (x1, y), 'open', LINE, 10)
                self._label(x1, x2, y, text)
            else:
                _, a, y, text = it
                x = self.xs[a]
                c.line([(x, y), (x + 54, y), (x + 54, y + 26), (x + 8, y + 26)],
                       fill=LINE, width=1.4)
                c.arrowhead((x + 6, y + 26), (x + 44, y + 26), 'filled', LINE, 9)
                self._label(x + 60, x + 60, y + 16, text, align='left')

    def _label(self, x1, x2, y, text, size=10.2, align='center'):
        c = self.c
        w = c.tw(text, size)
        if align == 'left':
            lx = x1
        else:
            lx = (x1 + x2) / 2 - w / 2
            lx = max(min(lx, max(x1, x2) - w - 6), min(x1, x2) + 6)
        c.d.rectangle([lx * c.s - 2, (y - size - 4) * c.s, (lx + w) * c.s + 2, (y - 2) * c.s],
                      fill='#ffffff')
        c.text(lx, y - 6, text, size, 'normal', '#111827')


def _build_sequence(c, top, bottom):
    xs = [180 + i * 300 for i in range(9)]
    heads = [
        ('actor', 'Заведующий\nкафедрой'),
        ('obj', 'boundary', ':PlanPage'),
        ('obj', 'control', ':PlanController'),
        ('obj', 'control', ':WorkflowManager'),
        ('obj', 'control', ':FgosValidationEngine'),
        ('obj', 'entity', ':CurriculumRepository'),
        ('actor', 'Эксперт\nАНОК'),
        ('actor', 'Проректор\nпо УР'),
        ('actor', 'Ректор'),
    ]
    sq = Seq(c, xs, heads, top, bottom)

    # --- 1. инициация проекта плана ---------------------------------------
    m1 = sq.msg(0, 1, '1. Открыть форму плана: GET ?page=plan&id=1')
    m2 = sq.msg(1, 2, '2. Запрос данных плана: planId = 1')
    m3 = sq.msg(2, 5, '3. save(curriculum) — INSERT / UPDATE')
    m4 = sq.msg(5, 2, '4. curriculumId = 1', kind='return')
    act_ctl = m2 - 24
    # --- 2. первичная ЭЦП --------------------------------------------------
    m5 = sq.msg(2, 3, '5. sign(CURRICULUM, step = 1, signer : User)')
    m6 = sq.msg(3, 5, '6. saveSignature(step = 1, sha256)')
    m7 = sq.msg(5, 3, '7. signatureId = 1', kind='return', dy=48)
    m8 = sq.msg(3, 2, '8. signHash = 3f9c… (ЭЦП зафиксирована)', kind='return')
    sq.act(3, m5 - 24, m8 - 8)
    sq.act(5, m3 - 24, m4 - 6)
    sq.act(5, m6 - 24, m7 - 6)
    # --- 3. автоматическая валидация ФГОС ----------------------------------
    m9 = sq.msg(2, 4, '9. validate(curriculumId = 1)')
    m10 = sq.msg(4, 5, '10. findDisciplines(curriculumId = 1)')
    m11 = sq.msg(5, 4, '11. disciplines[51]', kind='return', dy=48)
    sq.act(5, m10 - 24, m11 - 6)
    m12 = sq.self_msg(4, '12. checkTotals() · checkSessionExams() · checkPractice()')
    y_alt = m12 + 16
    # оператор alt — результат экспертизы
    m13 = sq.msg(4, 2, '13. ValidationReport(passed = true)', kind='return', dy=104)
    m14 = sq.msg(2, 1, '14. renderReport(report) — протокол проверки', kind='return', dy=76)
    y_op2 = m14 + 32
    m15 = sq.msg(4, 2, '15. ValidationReport(passed = false, violations[])', kind='return', dy=50)
    m16 = sq.msg(2, 1, '16. Список замечаний ФГОС; возврат на доработку', kind='return', dy=96)
    y_alt_end = m16 + 14
    sq.act(4, m9 - 24, y_alt_end - 8)
    sq.frags.append((*sq.frag(1, 4, 'alt', [(y_alt, '[нарушений нет]'),
                                            (y_op2, '[выявлены нарушения]')]), y_alt, y_alt_end))
    # --- 4. маршрут визирования (шаги 2…4) --------------------------------
    y_loop = m16 + 36
    m17 = sq.msg(6, 1, '17. Визуальный контроль протокола проверки ФГОС (шаг k)')
    m18 = sq.msg(1, 2, '18. signStep(step = k, comment)')
    m19 = sq.msg(2, 3, '19. sign(CURRICULUM, step = k, роль по маршруту)')
    m20 = sq.msg(3, 5, '20. saveSignature(step = k, sha256)')
    m21 = sq.msg(5, 3, '21. ok', kind='return', dy=46)
    m22 = sq.msg(3, 2, '22. signature(step = k)', kind='return', dy=46)
    sq.act(3, m19 - 24, m22 - 8)
    sq.act(5, m20 - 24, m21 - 6)
    m23 = sq.msg(2, 1, '23. k = k + 1 → следующий шаг маршрута', kind='return', dy=60)
    y_loop_end = m23 + 14
    sq.frags.append((*sq.frag(1, 8, 'loop', [(y_loop, 'для каждого шага k = 2…4: Эксперт АНОК → Проректор по УР → Ректор')],
                              guard_in_tab=True), y_loop, y_loop_end))
    # --- 5. утверждение ----------------------------------------------------
    m24 = sq.msg(7, 1, '24. Согласование проекта для Учёного совета')
    m25 = sq.msg(8, 1, '25. Утвердить: протокол УС № 8/26 от 25.06.2026')
    m26 = sq.msg(1, 2, '26. approve(protocolNum = "8/26", protocolDate = "25.06.2026")')
    m27 = sq.msg(2, 3, '27. finalize(protocol) → итоговый хэш')
    m28 = sq.msg(3, 2, '28. finalHash = 8b41… (SHA-256)', kind='return', dy=48)
    sq.act(3, m27 - 24, m28 - 8)
    m29 = sq.msg(2, 1, '29. status = APPROVED, реквизиты протокола сохранены', kind='return')
    m30 = sq.msg(1, 0, '30. Уведомление: учебный план утверждён', kind='return')
    sq.act(1, m1 - 24, m29 - 6)
    sq.act(2, act_ctl, m29 - 6)
    return sq


def sequence_diagram():
    W = 2760
    top = 120
    tmp = Canvas(200, 200)
    sq = _build_sequence(tmp, top, 4000)
    H = int(sq.y + 130)
    c = Canvas(W, H, scale=2)
    title(c, 'Диаграмма последовательности — экспертиза, валидация ФГОС и утверждение учебного плана',
          'UML 2.5: сплошная стрелка — синхронное сообщение, пунктирная с открытой стрелкой — возврат, '
          'вертикальные прямоугольники — периоды активности; alt / loop — комбинированные фрагменты.')
    sq = _build_sequence(c, top, H - 40)
    sq.render()

    lx, ly = 60, H - 108
    legend_box(c, lx, ly, 1280, 92, 'Условные обозначения')
    c.line([(lx + 24, ly + 50), (lx + 118, ly + 50)], fill=LINE, width=1.4)
    c.arrowhead((lx + 118, ly + 50), (lx + 24, ly + 50), 'filled', LINE, 10)
    c.text(lx + 130, ly + 54, 'синхронное сообщение (вызов операции)', 10.6, 'normal', '#374151')
    c.line([(lx + 470, ly + 50), (lx + 564, ly + 50)], fill=LINE, width=1.2, dash=(6, 4))
    c.arrowhead((lx + 564, ly + 50), (lx + 470, ly + 50), 'open', LINE, 10)
    c.text(lx + 576, ly + 54, 'возврат управления (return)', 10.6, 'normal', '#374151')
    c.rect(lx + 836, ly + 40, 14, 24, fill='#f4f6fb', outline='#374151', width=1.2)
    c.text(lx + 860, ly + 54, 'период активности (activation)', 10.6, 'normal', '#374151')
    c.text(lx + 24, ly + 78, '«boundary» — граничный объект (страница портала), «control» — управляющий объект, '
                            '«entity» — сущность предметной области.', 10.2, 'normal', MUTED)

    c.save(os.path.join(OUT, 'sequence_diagram.png'))


# ======================================================================
#  Реляционная схема (ER, нотация «воронья лапка»)
# ======================================================================
def er_table(c, x, y, w, name, cols, comment=None):
    """Таблица ER: шапка + строки (badge, имя, тип). Возвращает геометрию."""
    hh = 30
    rh = 15.2
    h = hh + rh * len(cols) + 8
    c.rect(x, y, w, h, fill='#ffffff', outline='#334155', width=1.3)
    c.rect(x + 1, y + 1, w - 2, hh - 2, fill='#1e2a44', outline=None)
    c.text(x + 10, y + 20, name, 11.8, 'bold', '#ffffff')
    if comment:
        c.text(x + w - 10, y + 20, comment, 9.2, 'normal', '#cbd5e1', anchor='rs')
    c.line([(x, y + hh), (x + w, y + hh)], fill='#334155', width=1.1)
    rows = {}
    yy = y + hh + 4.5
    for (key, cname, ctype) in cols:
        yy += rh
        rows[cname] = yy - 5
        if key:
            col = {'PK': '#b91c1c', 'FK': '#1d4ed8', 'UQ': '#7c3aed'}[key]
            c.text(x + 8, yy, key, 8.6, 'bold', col)
        notnull = '*' in ctype
        ctext = ctype.replace('*', '')
        c.text(x + 40, yy, cname, 10.0, 'bold' if notnull else 'normal', '#111827')
        c.text(x + w - 8, yy, ctext, 9.4, 'bold' if notnull else 'normal',
               '#334155' if notnull else '#6b7280', anchor='rs')
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
            ('', 'publish_date', 'TEXT*'), ('', 'author_name', 'TEXT*'),
            ('', 'content', 'TEXT*'), ('', 'is_pinned', 'INT')]),
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
    H = row_y[2] + row_h[2] + 260
    c = Canvas(W, H, scale=2)
    title(c, 'Реляционная схема базы данных anok_portal — 13 таблиц, 3NF (нотация «воронья лапка»)',
          'PK — первичный ключ, FK — внешний ключ; полужирный тип — обязательное поле (NOT NULL), '
          'обычный — допускает NULL; «воронья лапка» — сторона «многие», кружок — необязательность связи.')

    geo = {}
    for name, (col, r, cols) in tables.items():
        geo[name] = er_table(c, COLS[col], row_y[r], BW, name, cols)

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
        c.line(pts, fill='#334155', width=1.3)
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
       'zero-many', 'zero-one', c_labs=('0..*', (8, -8)), p_labs=('0..1', (8, -8)))
    # 3. educational_programs.department_id → departments.id (верхний канал, y = 142)
    er([(Ledge('educational_programs') + 240, Top('educational_programs')),
        (Ledge('educational_programs') + 240, 142),
        (COLS[3] + 180, 142), (COLS[3] + 180, Top('departments'))],
       'zero-many', 'zero-one', c_labs=('0..*', (-42, -10)), p_labs=('0..1', (10, -10)))
    # 4. curriculum_disciplines.curriculum_id → curriculums.id (верхний канал, y = 96)
    er([(COLS[2] + 150, Top('curriculums')), (COLS[2] + 150, 96),
        (COLS[4] + 160, 96), (COLS[4] + 160, Top('curriculum_disciplines'))],
       'zero-one', 'zero-many', p_labs=('0..1', (-42, -10)), c_labs=('0..*', (10, -10)))
    # 5. curriculum_disciplines.implementing_department_id → departments.id
    y = rowy('curriculum_disciplines', 'implementing_department_id')
    er([(Ledge('curriculum_disciplines'), y), (Redge('departments'), y)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (7, -8)))
    # 6. competencies.program_id → educational_programs.id (канал между столбцами 0 и 1)
    yco = rowy('competencies', 'program_id')
    yp = rowy('educational_programs', 'id')
    gx6 = COLS[0] + BW + 46
    er([(Redge('competencies'), yco), (gx6, yco), (gx6, yp),
        (Ledge('educational_programs'), yp)],
       'zero-many', 'zero-one', c_labs=('0..*', (7, -8)), p_labs=('0..1', (-38, -8)))
    # 7. users.role_id → roles.id
    y = rowy('users', 'role_id')
    er([(Ledge('users'), y), (Redge('roles'), y)],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -8)), p_labs=('0..1', (7, -8)))
    # 8. users.department_id → departments.id (через межстрочный канал)
    gy8 = row_y[0] + row_h[0] + 40
    er([(COLS[2] + 120, Top('users')), (COLS[2] + 120, gy8),
        (COLS[3] + 90, gy8), (COLS[3] + 90, Bot('departments'))],
       'zero-many', 'zero-one', c_labs=('0..*', (-38, -10)), p_labs=('0..1', (8, 15)))
    # 9. service_notes.curriculum_id → curriculums.id (через канал под строкой 1)
    gy9 = row_y[0] + row_h[0] + 76
    er([(Ledge('service_notes'), rowy('service_notes', 'curriculum_id')),
        (COLS[3] - 30, rowy('service_notes', 'curriculum_id')), (COLS[3] - 30, gy9),
        (COLS[2] + 250, gy9), (COLS[2] + 250, Bot('curriculums'))],
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

    # ---------------------------------------------------------- примечания
    ny = row_y[2] + row_h[2] + 44
    note(c, COLS[0] + 20, ny, 470, [
        'document_signatures — полиморфная связь',
        '(doc_type, doc_id) на curriculums / service_notes:',
        'внешний ключ в DDL не объявляется, целостность',
        'обеспечивается на уровне WorkflowManager.'],
        fill='#fffdf0')
    c.line([(COLS[0] + 240, Bot('document_signatures')), (COLS[0] + 240, ny)],
           fill='#8a6d00', width=1.0, dash=(6, 4))

    # ---------------------------------------------------------- легенда
    lx, ly, lw = COLS[4] + 10, row_y[2] + 10, 390
    legend_box(c, lx, ly, lw, 176, 'Нотация связей')
    c.line([(lx + 20, ly + 46), (lx + 128, ly + 46)], fill='#334155', width=1.3)
    er_end(c, (lx + 20, ly + 46), (lx + 128, ly + 46), 'zero-one')
    er_end(c, (lx + 128, ly + 46), (lx + 20, ly + 46), 'zero-many')
    c.text(lx + 18, ly + 82, '"воронья лапка" — сторона «многие» (0..*)', 10.0, 'normal', '#374151')
    c.text(lx + 18, ly + 102, 'черта — сторона «один» (0..1)', 10.0, 'normal', '#374151')
    c.text(lx + 18, ly + 122, 'кружок — необязательность связи (nullable FK)', 10.0, 'normal', '#374151')
    c.text(lx + 18, ly + 148, 'стрелка не рисуется: направление задаёт FK', 10.0, 'normal', MUTED)

    c.save(os.path.join(OUT, 'db_schema_diagram.png'))


if __name__ == '__main__':
    class_diagram()
    component_diagram()
    deployment_diagram()
    sequence_diagram()
    db_schema_diagram()
    print('ok')
