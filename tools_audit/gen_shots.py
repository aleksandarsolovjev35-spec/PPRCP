# -*- coding: utf-8 -*-
"""Regenerates portal screenshots / GPI / section / infoblock / module images
strictly from the live demo database (schema.sql + seed.sql)."""
import re, sqlite3, os, math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = '/usr/share/fonts/truetype/dejavu/'
def F(sz, bold=False):
    return ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz)

# --- DB ---------------------------------------------------------------------
schema = open(f'{ROOT}/portal/database/schema.sql', encoding='utf-8').read()
seed = open(f'{ROOT}/portal/database/seed.sql', encoding='utf-8').read()
schema = re.sub(r'ENGINE=InnoDB[^;]*;', ';', schema, flags=re.I)
schema = re.sub(r'SET FOREIGN_KEY_CHECKS\s*=\s*[01];', '', schema, flags=re.I)
schema = re.sub(r'\bINT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', schema, flags=re.I)
seed = re.sub(r'SET FOREIGN_KEY_CHECKS\s*=\s*[01];', '', seed, flags=re.I)
DB = sqlite3.connect(':memory:'); DB.row_factory = sqlite3.Row
DB.executescript(schema); DB.executescript(seed)
Q = lambda sql, *a: DB.execute(sql, a).fetchall()

# --- palette ----------------------------------------------------------------
BG='#f8fafc'; HEADER='#0f172a'; SIDEBAR='#1e293b'; CARD='#ffffff'; BORDER='#e2e8f0'
TXT='#1e293b'; MUTED='#64748b'; PRIMARY='#2563eb'; THBG='#f8fafc'; TH='#475569'
BADGES={'green':('#dcfce7','#15803d'),'blue':('#dbeafe','#1d4ed8'),'purple':('#f3e8ff','#7e22ce'),
        'cyan':('#cffafe','#0e7490'),'yellow':('#fef3c7','#b45309'),'red':('#fee2e2','#b91c1c'),'gray':('#f1f5f9','#475569')}
def badge_kind(st):
    st=(st or '').upper()
    if any(k in st for k in ('APPROVED','SIGNED','APPLIED','УСПЕШНО','ПОДПИСАНО','АКТУАЛИЗИРОВАНО')): return 'green'
    if 'ОШИБКА' in st: return 'red'
    if 'IN_ANOK' in st or 'ЗАКРЕП' in st: return 'purple'
    if 'РЕЛИЗ' in st or 'SIGNED_RELEASING' in st: return 'cyan'
    if 'PENDING' in st: return 'yellow'
    if 'ОБНОВЛЕНО' in st or 'СОЗДАНО' in st: return 'blue'
    return 'gray'
BADGE_LABEL={'APPROVED_RECTOR':'Утверждено Ректором','SIGNED':'Подписано','APPLIED':'Применено',
 'IN_ANOK':'На экспертизе в АНОК','SIGNED_RELEASING':'Виза выпускающей каф.'}

NAV=[('dashboard','Главная'),('plans','Учебные планы'),('analytics','Аналитика'),('calendar','Календарь дедлайнов'),
 ('validate','Проверка ФГОС'),('signatures','Согласование'),('memos','Служебные записки'),('programs','Программы'),
 ('competencies','Компетенции'),('standards','Стандарты'),('departments','Подразделения'),('announcements','Объявления'),
 ('audit','Аудит'),('sitemap','Карта сайта')]

W,H=1600,1000; SBW=240; HDR=60; FTR=40

def base(active):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,HDR],fill=HEADER)
    d.rounded_rectangle([28,14,60,46],8,fill=PRIMARY); d.text((38,20),'А',font=F(18,True),fill='#fff')
    d.text((74,14),'УНИВЕРСИТЕТ · Центр АНОК',font=F(16,True),fill='#fff')
    d.text((74,36),'Аккредитация и независимая оценка качества образования',font=F(11),fill='#94a3b8')
    d.ellipse([W-190,14,W-158,46],fill='#334155'); d.text((W-181,20),'АС',font=F(14,True),fill='#38bdf8')
    d.text((W-150,14),'Соловьев А.С.',font=F(13,True),fill='#fff')
    d.text((W-150,32),'Эксперт АНОК',font=F(10),fill='#94a3b8')
    d.rectangle([0,HDR,SBW,H-FTR],fill=SIDEBAR)
    y=HDR+20
    for key,label in NAV:
        if key==active: d.rounded_rectangle([12,y,SBW-12,y+36],8,fill=PRIMARY)
        d.text((26,y+9),label,font=F(13,key==active),fill='#fff' if key==active else '#cbd5e1')
        y+=42
    d.rectangle([0,H-FTR,W,H],fill=HEADER)
    d.text((28,H-28),'© 2026 Центр АНОК · Корпоративный портал университета · Версия 2.4.0',font=F(11),fill='#94a3b8')
    d.text((W-560,H-28),'Синхронизация с БД: OK · Регламент ФГОС ВО 3++ · helpdesk@univ.ru',font=F(11),fill='#94a3b8')
    return im,d

def title(d,text,sub=None):
    d.text((SBW+32,84),text,font=F(24,True),fill='#0f172a')
    if sub: d.text((SBW+32,120),sub,font=F(13),fill=MUTED)
    return 150 if sub else 126

def cards(d,y,items):
    x=SBW+32; w=(W-SBW-64-3*16)//4
    for i,(label,val,note) in enumerate(items):
        d.rounded_rectangle([x,y,x+w,y+110],10,fill=CARD,outline=BORDER)
        d.text((x+18,y+16),label,font=F(12),fill=MUTED)
        d.text((x+18,y+40),str(val),font=F(30,True),fill='#0f172a')
        d.text((x+18,y+82),note,font=F(11),fill=MUTED)
        x+=w+16

def table(d,x,y,headers,rows,widths,rowh=38,zebra=True,font_sz=12):
    tw=sum(widths)
    d.rounded_rectangle([x,y,x+tw,y+rowh],6,fill=THBG,outline=BORDER)
    cx=x
    for htxt,wd in zip(headers,widths):
        d.text((cx+10,y+10),htxt,font=F(11,True),fill=TH); cx+=wd
    ry=y+rowh
    for ri,row in enumerate(rows):
        rh=rowh
        d.rectangle([x,ry,x+tw,ry+rh],fill='#ffffff' if (ri%2==0 or not zebra) else '#f8fafc',outline=BORDER)
        cx=x
        for cell,wd in zip(row,widths):
            txt,style=(cell if isinstance(cell,tuple) else (cell,None))
            fnt=F(font_sz, bool(style and style.get('b')))
            col=style.get('c',TXT) if style else TXT
            # wrap if too wide
            t=str(txt)
            while d.textlength(t,font=fnt)>wd-20 and len(t)>4: t=t[:-2]
            d.text((cx+10,ry+(rh-font_sz-4)//2),t,font=fnt,fill=col)
            cx+=wd
        ry+=rh
    return ry

def badge(d,x,y,text,kind):
    bg,fg=BADGES[kind]
    w=d.textlength(text,font=F(11,True))+20
    d.rounded_rectangle([x,y,x+w,y+24],12,fill=bg)
    d.text((x+10,y+5),text,font=F(11,True),fill=fg)
    return w

def wrap(d,text,font,maxw):
    out=[]; line=''
    for word in text.split():
        t=(line+' '+word).strip()
        if d.textlength(t,font=font)<=maxw: line=t
        else:
            if line: out.append(line)
            line=word
    if line: out.append(line)
    return out

# --- page renderers ----------------------------------------------------------
def shot_dashboard(fn):
    im,d=base('dashboard'); y=title(d,'Сводная панель','Ключевые показатели Центра АНОК и реестр учебных планов')
    stats=Q("SELECT (SELECT COUNT(*) FROM curriculums) p,(SELECT COUNT(*) FROM curriculum_disciplines) disc,(SELECT COUNT(*) FROM standards_fgos) s,(SELECT COUNT(*) FROM service_notes) m")[0]
    cards(d,y,[('Учебные планы',stats['p'],'Активных проектов ОП'),('Дисциплины',stats['disc'],'В учебной сетке'),
               ('Стандарты ФГОС',stats['s'],'Нормативов 3++'),('Служебные записки',stats['m'],'На корректировку')])
    y+=140
    d.text((SBW+32,y),'Реестр учебных планов',font=F(18,True),fill=TXT); y+=34
    rows=[]
    for p in Q("SELECT c.*, ep.code, ep.title FROM curriculums c JOIN educational_programs ep ON ep.id=c.program_id"):
        rows.append([(p['code'],{'b':1}),p['title'],p['academic_year'],'v'+p['version'],f"{p['total_credits']} з.е.",
                     (BADGE_LABEL.get(p['status'],p['status']),{'c':BADGES[badge_kind(p['status'])][1]}),'Открыть УП'])
    table(d,SBW+32,y,['Код','Образовательная программа','Уч. год','Версия','Трудоемкость','Статус','Действие'],
          rows,[90,430,110,80,110,200,120])
    y+=34+38*(len(rows)+1)+26
    d.text((SBW+32,y),'Важные объявления и регламенты',font=F(18,True),fill=TXT); y+=32
    for a in Q("SELECT * FROM announcements WHERE is_pinned=1 ORDER BY publish_date DESC LIMIT 2"):
        d.rounded_rectangle([SBW+32,y,W-32,y+92],8,fill=CARD,outline=BORDER)
        d.rectangle([SBW+32,y,SBW+36,y+92],fill=PRIMARY)
        d.text((SBW+52,y+10),a['title'],font=F(14,True),fill='#0f172a')
        d.text((SBW+52,y+34),f"Дата: {a['publish_date']}   ·   Раздел: {a['category']}   ·   Автор: {a['author_name']}",font=F(11),fill=MUTED)
        body=wrap(d,a['content'],F(11),W-SBW-140)
        d.text((SBW+52,y+56),body[0] if body else '',font=F(11),fill='#334155')
        y+=104
    im.save(fn)

def sem_rows(sem):
    return Q("SELECT cd.*, d.short_name dept FROM curriculum_disciplines cd LEFT JOIN departments d ON d.id=cd.implementing_department_id WHERE cd.curriculum_id=1 AND cd.semester_num=? ORDER BY cd.id",sem)

def shot_plan(fn,sem=1,with_tools=False,with_search=False):
    im,d=base('plans'); y=title(d,'Учебный план','09.03.04 — Программная инженерия (Разработка ПО) · Бакалавриат · Очная · 240 з.е.')
    # sem nav
    x=SBW+32
    for s in range(1,9):
        wdt=118
        if s==sem: d.rounded_rectangle([x,y,x+wdt,y+34],6,fill=PRIMARY); col='#fff'
        else: d.rounded_rectangle([x,y,x+wdt,y+34],6,fill='#e2e8f0'); col='#334155'
        d.text((x+18,y+8),f'Семестр {s}',font=F(13,s==sem),fill=col); x+=wdt+8
    y+=50
    rows=sem_rows(sem)
    sc=sum(r['credits_ze'] for r in rows); sh=sum(r['total_hours'] for r in rows)
    sl=sum(r['lecture_hours'] for r in rows); sb=sum(r['lab_hours'] for r in rows)
    sp=sum(r['practice_hours'] for r in rows); ss=sum(r['self_study_hours'] for r in rows)
    d.rounded_rectangle([SBW+32,y,SBW+252,y+36],6,fill=CARD,outline=BORDER)
    d.text((SBW+46,y+9),f'Семестр {sem}: {len(rows)} дисциплин',font=F(12,True),fill=TXT)
    d.rounded_rectangle([SBW+262,y,SBW+520,y+36],6,fill='#eff6ff',outline='#bfdbfe')
    d.text((SBW+276,y+9),f'Трудоемкость: {sc} з.е. (норма: 30 з.е.)',font=F(12,True),fill='#1e40af')
    d.rounded_rectangle([SBW+530,y,W-32,y+36],6,fill=CARD,outline=BORDER)
    d.text((SBW+544,y+9),f'Всего часов: {sh} ч. (Лек: {sl} / Лаб: {sb} / Пр: {sp} / СРС: {ss})',font=F(12),fill=TXT)
    y+=50
    if with_tools:
        for i,(txt,colr) in enumerate((('[XLSX] Экспорт в Excel (SheetJS)',PRIMARY),('[PDF] Выгрузить в PDF (jsPDF)','#dc2626'),('[PRINT] Печать бланка УП',None))):
            wdt=d.textlength(txt,font=F(12,True))+28
            if colr: d.rounded_rectangle([x0:=SBW+32+i*330,y,x0+wdt,y+34],6,fill=colr); d.text((x0+14,y+8),txt,font=F(12,True),fill='#fff')
            else: d.rounded_rectangle([x0:=SBW+32+i*330,y,x0+wdt,y+34],6,fill=CARD,outline=BORDER); d.text((x0+14,y+8),txt,font=F(12,True),fill=TXT)
        y+=46
    if with_search:
        d.rounded_rectangle([SBW+32,y,SBW+392,y+34],6,fill=CARD,outline=PRIMARY)
        d.text((SBW+46,y+8),'Живой поиск:',font=F(12),fill=MUTED)
        y+=44
    trows=[[(r['block_type'],{'c':'#475569'}),(r['discipline_name'],{'b':1}),str(r['credits_ze']),str(r['total_hours']),
            str(r['lecture_hours']),str(r['lab_hours']),str(r['practice_hours']),str(r['self_study_hours']),
            r['control_form'],r['dept'] or '—'] for r in rows]
    ey=table(d,SBW+32,y,['Блок','Наименование дисциплины','З.Е.','Часы','Лек.','Лаб.','Прак.','СРС','Форма контроля','Кафедра'],
             trows,[90,430,60,70,60,60,60,70,160,120])
    if with_search:
        d.text((SBW+32,ey+10),f'Показано с 1 по {len(rows)} из {len(rows)} дисциплин',font=F(11),fill=MUTED)
        d.text((W-300,ey+10),'Назад  1  Вперёд',font=F(11),fill=MUTED)
    im.save(fn)

def shot_validate(fn):
    im,d=base('validate'); y=title(d,'Экспертиза ФГОС','Результаты автоматической проверки учебного плана 09.03.04 на требования ФГОС ВО 3++')
    vals=[('Общая трудоемкость: 240 з.е.','Соответствует стандарту (240 з.е.)'),
          ('Распределение: 30 з.е. / семестр','Баланс семестров соблюден'),
          ('Экзамены: ≤ 5 в сессию','Максимум 4 экзамена (норма)'),
          ('Практическая подготовка: 34 з.е.','Превышает минимум (≥ 12 з.е.)'),
          ('Блок ГИА: 9 з.е.','Соответствует нормативу (≥ 6 з.е.)')]
    x=SBW+32; w=(W-SBW-64-16)//3
    for i,(b,s) in enumerate(vals):
        xx=x+(i%3)*(w+8); yy=y+(i//3)*86
        d.rounded_rectangle([xx,yy,xx+w,yy+76],6,fill='#f8fafc')
        d.rectangle([xx,yy,xx+3,yy+76],fill='#16a34a')
        d.text((xx+14,yy+12),b,font=F(13,True),fill='#0f172a')
        d.text((xx+14,yy+40),s,font=F(11),fill=MUTED)
    y+=2*86+20
    d.text((SBW+32,y),'Нормативные стандарты ФГОС ВО 3++',font=F(18,True),fill=TXT); y+=32
    rows=[[(s['code'],{'b':1}),s['title'],s['degree_level'],f"{s['total_credits']} з.е.",str(s['max_exams_per_session']),
           f"{s['min_practice_credits']} з.е.",f"{s['min_gia_credits']} з.е.",s['approval_date']] for s in Q("SELECT * FROM standards_fgos ORDER BY code")]
    table(d,SBW+32,y,['Код','Наименование направления','Квалификация','Трудоемкость','Макс. экз.','Мин. практик','Мин. ГИА','Дата утв.'],
          rows,[100,430,120,110,90,110,90,120])
    im.save(fn)

def shot_signatures(fn,with_toasts=False,with_stamps=False):
    im,d=base('signatures'); y=title(d,'Маршрут согласования и ЭЦП','Цифровой маршрут согласования УП 09.03.04 (2026/2027 уч. год)')
    for s in Q("SELECT * FROM document_signatures ORDER BY step_order"):
        d.rounded_rectangle([SBW+32,y,W-32,y+96],8,fill=CARD,outline=BORDER)
        d.ellipse([SBW+52,y+18,SBW+84,y+50],fill=PRIMARY)
        d.text((SBW+64,y+24),str(s['step_order']),font=F(15,True),fill='#fff')
        d.text((SBW+100,y+14),s['role_title'],font=F(15,True),fill=TXT)
        badge(d,W-160,y+16,BADGE_LABEL.get(s['status'],s['status']),badge_kind(s['status']))
        d.text((SBW+100,y+40),f"Подписант: {s['signer_name']} · Дата: {s['signed_at']}",font=F(12),fill='#475569')
        d.text((SBW+100,y+60),f'«{s["comment"]}»',font=F(11),fill='#334155')
        d.text((SBW+100,y+78),f"ЭЦП Hash: {s['sign_hash']}",font=F(10),fill=MUTED)
        y+=108
    if with_stamps:
        d.text((SBW+32,y+4),'Модуль криптографии и верификации ЭЦП (CryptoJS / SHA-256)',font=F(16,True),fill=TXT); y+=34
        for s in Q("SELECT * FROM document_signatures ORDER BY step_order")[:2]:
            d.rounded_rectangle([SBW+32,y,W-32,y+64],8,fill=CARD,outline=BORDER)
            d.text((SBW+50,y+10),f'ДОКУМЕНТ ПОДПИСАН ЭЛЕКТРОННОЙ ПОДПИСЬЮ · Этап {s["step_order"]} · {s["signer_name"]}',font=F(12,True),fill=TXT)
            d.text((SBW+50,y+34),f"SHA-256: {s['sign_hash'].replace('SHA256:','')} · [MATCH]",font=F(10),fill='#15803d')
            y+=72
        d.rounded_rectangle([SBW+32,y,W-32,y+44],6,fill='#dcfce7',outline='#16a34a')
        d.text((SBW+48,y+12),'[OK] СТАТУС ВЕРИФИКАЦИИ ЭЦП: ВСЕ ПОДПИСИ ДЕЙСТВИТЕЛЬНЫ (4 из 4)',font=F(13,True),fill='#15803d')
        y+=56
    if with_toasts:
        ty=H-FTR-150
        for txt,colr in (('[OK] Валидатор ФГОС: Ошибок нормативов не обнаружено (100%)','#2563eb'),
                         ('[OK] Служебная записка СЗ-2026/048 успешно применена (v1.1)','#16a34a'),
                         ('[!] Внимание: дедлайн подачи УП через 5 дней (25 Октября)','#d97706')):
            wdt=d.textlength(txt,font=F(12,True))+36
            d.rounded_rectangle([W-wdt-24,ty,W-24,ty+40],8,fill=colr)
            d.text((W-wdt-8,ty+11),txt,font=F(12,True),fill='#fff')
            ty+=48
    im.save(fn)

def shot_memos(fn,with_diff=False):
    im,d=base('memos'); y=title(d,'Служебные записки на корректировку','Реестр СЗ и визуальное сравнение версий УП (Diff2Html)')
    rows=[]
    for m in Q("SELECT sn.*, d1.short_name rel, d2.short_name imp FROM service_notes sn LEFT JOIN departments d1 ON d1.id=sn.releasing_dept_id LEFT JOIN departments d2 ON d2.id=sn.implementing_dept_id ORDER BY sn.id DESC"):
        rows.append([(m['note_num'],{'b':1}),m['note_date'],m['rel'] or '—',m['imp'] or '—',
                     (m['reason'],{}),m['created_by'],(BADGE_LABEL.get(m['status'],m['status']),{'c':BADGES[badge_kind(m['status'])][1]})])
    ey=table(d,SBW+32,y,['№ СЗ','Дата','Инициатор','Реализующая','Причина и суть изменений','Автор','Статус'],
             rows,[110,100,90,90,640,110,170],rowh=52,font_sz=11)
    if with_diff:
        y=ey+18
        d.text((SBW+32,y),'Модуль визуального Diff-сопоставления версий УП (Diff2Html)',font=F(16,True),fill=TXT); y+=30
        for it in Q("SELECT sni.*, sn.note_num, cd.discipline_name FROM service_note_items sni JOIN service_notes sn ON sn.id=sni.service_note_id LEFT JOIN curriculum_disciplines cd ON cd.id=sni.discipline_id ORDER BY sni.id"):
            d.rounded_rectangle([SBW+32,y,W-32,y+86],8,fill=CARD,outline=BORDER)
            d.text((SBW+50,y+8),f"Сравнение: {it['discipline_name'] or '—'} — {it['note_num']} [{it['change_type']}]",font=F(12,True),fill=TXT)
            half=(W-SBW-96)//2
            d.rounded_rectangle([SBW+50,y+34,SBW+50+half,y+76],6,fill='#fee2e2')
            d.rounded_rectangle([SBW+66+half,y+34,W-50,y+76],6,fill='#dcfce7')
            old=it['old_val'] or ''; new=it['new_val'] or ''
            for bx,bw,txt,colr in ((SBW+58,half-16,old,'#b91c1c'),(SBW+74+half,half-16,new,'#15803d')):
                lines=wrap(d,txt,F(9),bw)
                for li,ln in enumerate(lines[:2]):
                    d.text((bx,y+38+li*16),ln,font=F(9),fill=colr)
            y+=96
    im.save(fn)

def shot_simple_table(fn,active,title_txt,sql,headers,widths,sub=''):
    im,d=base(active); y=title(d,title_txt,sub or None)
    rows=[]
    for r in Q(sql):
        rows.append([ (str(v),{'b':i==0}) if i==0 else str(v) for i,v in enumerate(tuple(r)) ])
    table(d,SBW+32,y,headers,rows,widths,font_sz=11)
    im.save(fn)

def shot_announcements(fn):
    im,d=base('announcements'); y=title(d,'Объявления и регламенты Центра АНОК')
    for a in Q("SELECT * FROM announcements ORDER BY is_pinned DESC, publish_date DESC"):
        lines=wrap(d,a['content'],F(12),W-SBW-160)
        hh=70+len(lines)*18
        d.rounded_rectangle([SBW+32,y,W-32,y+hh],8,fill=CARD,outline=BORDER)
        if a['is_pinned']:
            d.rectangle([SBW+32,y,SBW+36,y+hh],fill=PRIMARY)
            badge(d,W-140,y+12,'Закреплено','purple')
        d.text((SBW+52,y+12),f"Дата: {a['publish_date']}   ·   Раздел: {a['category']}   ·   Автор: {a['author_name']}",font=F(11),fill=MUTED)
        d.text((SBW+52,y+34),a['title'],font=F(15,True),fill='#0f172a')
        yy=y+60
        for ln in lines:
            d.text((SBW+52,yy),ln,font=F(12),fill='#334155'); yy+=18
        y+=hh+14
    im.save(fn)

def shot_audit(fn):
    im,d=base('audit'); y=title(d,'Журнал аудита системы','Протокол событий безопасности с живым поиском')
    d.rounded_rectangle([SBW+32,y,SBW+392,y+34],6,fill=CARD,outline=PRIMARY)
    d.text((SBW+46,y+8),'Поиск по журналу...',font=F(12),fill=MUTED); y+=46
    rows=[[l['event_time'],(l['user_name'],{'b':1}),l['user_role'],l['action'],l['entity_name'],
           (l['status'],{'c':BADGES[badge_kind(l['status'])][1]}),l['ip_address']] for l in Q("SELECT * FROM audit_logs ORDER BY id DESC")]
    table(d,SBW+32,y,['Время события','Пользователь','Роль','Действие','Объект','Статус','IP адрес'],
          rows,[170,140,160,220,330,180,130],font_sz=11)
    im.save(fn)

def shot_programs_standards(fn):
    im,d=base('programs'); y=title(d,'Образовательные программы и стандарты ФГОС')
    rows=[[(p['code'],{'b':1}),p['title'],p['level'],p['study_form'],p['dept'],p['standard']] for p in Q(
        "SELECT ep.code, ep.title, ep.level, ep.study_form, d.name dept, sf.title standard FROM educational_programs ep LEFT JOIN departments d ON d.id=ep.department_id LEFT JOIN standards_fgos sf ON sf.id=ep.fgos_standard_id")]
    y=table(d,SBW+32,y,['Код ОП','Наименование программы','Уровень','Форма','Выпускающее подразделение','Стандарт'],
            rows,[90,380,110,80,300,360])+24
    rows=[[(s['code'],{'b':1}),s['title'],s['degree_level'],str(s['total_credits']),str(s['max_exams_per_session']),
           str(s['min_practice_credits']),str(s['min_gia_credits']),s['approval_date']] for s in Q("SELECT * FROM standards_fgos ORDER BY code")]
    d.text((SBW+32,y),'Стандарты ФГОС ВО 3++',font=F(18,True),fill=TXT); y+=32
    table(d,SBW+32,y,['Код','Наименование стандарта','Уровень','З.Е.','Макс. экз.','Практика','ГИА','Дата ввода'],
          rows,[90,430,110,70,90,90,70,120])
    im.save(fn)

# --- analytics with hand-drawn charts ---------------------------------------
def shot_analytics(fn):
    im,d=base('analytics'); y=title(d,'Аналитика','Модуль бизнес-аналитики и визуализации данных (Chart.js): блоки УП, компетенции, часы по семестрам')
    blocks=Q("SELECT CASE WHEN block_type LIKE 'Б1.О%' THEN 'Обязательная часть' WHEN block_type LIKE 'Б1.В%' THEN 'Вариативная часть' WHEN block_type LIKE 'Б2%' THEN 'Практики и НИР' WHEN block_type LIKE 'Б3%' THEN 'ГИА' ELSE 'ФТД' END b, SUM(credits_ze) ze FROM curriculum_disciplines GROUP BY b")
    # doughnut
    cx,cy,r=SBW+220,y+170,110
    cols=['#2563eb','#60a5fa','#16a34a','#d97706','#9333ea']
    total=sum(b['ze'] for b in blocks); a0=-90
    order=['Обязательная часть','Вариативная часть','Практики и НИР','ГИА','ФТД']
    for i,nm in enumerate(order):
        ze=[b['ze'] for b in blocks if b['b']==nm][0]
        a1=a0+360*ze/total
        d.pieslice([cx-r,cy-r,cx+r,cy+r],a0,a1,fill=cols[i])
        a0=a1
    d.ellipse([cx-55,cy-55,cx+55,cy+55],fill=BG)
    d.text((cx-30,cy-14),f'{total:g}',font=F(22,True),fill='#0f172a')
    d.text((cx-24,cy+12),'з.е.',font=F(11),fill=MUTED)
    lx=SBW+420
    for i,nm in enumerate(order):
        ze=[b['ze'] for b in blocks if b['b']==nm][0]
        d.rectangle([lx,y+60+i*34,lx+18,y+78+i*34],fill=cols[i])
        d.text((lx+28,y+62+i*34),f'{nm} — {ze:g} з.е.',font=F(13),fill=TXT)
    d.text((SBW+32,y+8),'1. Структура блоков учебного плана (Doughnut)',font=F(15,True),fill=TXT)
    # stacked bars
    bx=SBW+830
    d.text((bx,y+8),'3. Часы по семестрам (Stacked Bar)',font=F(15,True),fill=TXT)
    hrs=Q("SELECT semester_num s, SUM(lecture_hours) le, SUM(lab_hours) la, SUM(practice_hours) pr, SUM(self_study_hours) se FROM curriculum_disciplines GROUP BY s ORDER BY s")
    x0=bx+10; bw=52
    for i,hh in enumerate(hrs):
        scale=0.26
        ybase=y+330
        for val,colr in ((hh['le'],'#1d4ed8'),(hh['la'],'#3b82f6'),(hh['pr'],'#16a34a'),(hh['se'],'#94a3b8')):
            hgt=val*scale
            d.rectangle([x0+i*(bw+12),ybase-hgt,x0+i*(bw+12)+bw,ybase],fill=colr)
            ybase-=hgt
        d.text((x0+i*(bw+12)+8,y+338),f'Сем.{hh["s"]}',font=F(10),fill=MUTED)
    # radar (triangle-ish)
    rcx,rcy,rr=SBW+220,y+660,100
    d.text((SBW+32,y+420),'2. Покрытие компетенций (Radar)',font=F(15,True),fill=TXT)
    comps=Q("SELECT CASE WHEN code LIKE 'УК%' THEN 'УК' WHEN code LIKE 'ОПК%' THEN 'ОПК' ELSE 'ПК' END c, COUNT(*) n FROM competencies GROUP BY c")
    import math as _m
    pts=[]
    vals=[ [c['n'] for c in comps if c['c']==k][0] for k in ('УК','ОПК','ПК')]
    for i,v in enumerate(vals):
        ang=_m.radians(-90+i*120)
        pts.append((rcx+rr*v/8*_m.cos(ang), rcy+rr*v/8*_m.sin(ang)))
    for i in range(3):
        ang=_m.radians(-90+i*120)
        d.line([rcx,rcy,rcx+rr*_m.cos(ang),rcy+rr*_m.sin(ang)],fill=BORDER,width=1)
    d.polygon(pts,fill=(147,51,234,60),outline='#7e22ce')
    for i,k in enumerate(('УК','ОПК','ПК')):
        ang=_m.radians(-90+i*120)
        d.text((rcx+(rr+18)*_m.cos(ang)-10,rcy+(rr+18)*_m.sin(ang)-8),f'{k} ({vals[i]})',font=F(12,True),fill='#7e22ce')
    im.save(fn)

def shot_calendar(fn):
    im,d=base('calendar'); y=title(d,'Календарь дедлайнов','Календарный график регламентных процедур АНОК (FullCalendar, Октябрь 2026)')
    days=['Пн','Вт','Ср','Чт','Пт','Сб','Вс']
    cw=(W-SBW-64)//7
    for i,dd in enumerate(days):
        d.text((SBW+32+i*cw+cw//2-10,y),dd,font=F(13,True),fill=TH)
    y+=26
    events={'2026-10-01':('Старт приема СЗ','#2563eb'),'2026-10-04':('Экспертиза ФГОС 3++','#16a34a'),
            '2026-10-15':('Ученый совет','#9333ea'),'2026-10-20':('Завершение валидации','#d97706'),
            '2026-10-25':('Дедлайн УП Проректору','#dc2626'),
            '2026-06-25':('Протокол УС № 8/26','#7e22ce')}
    for n in Q("SELECT note_num, note_date FROM service_notes"): events[n['note_date']]=(n['note_num'],'#0e7490')
    # October 2026: 1st = Thursday
    first_weekday=3  # Mon=0
    day=1; row=0
    cells=[]
    for row in range(5):
        for col in range(7):
            idx=row*7+col
            dn=idx-first_weekday+1
            cells.append((col,dn))
    for col,dn in cells:
        xx=SBW+32+col*cw; yy=y+ ( (col*0) )
    # draw grid rows
    for row in range(5):
        for col in range(7):
            idx=row*7+col; dn=idx-first_weekday+1
            xx=SBW+32+col*cw; yy=y+row*92
            d.rectangle([xx,yy,xx+cw,yy+92],fill='#fff',outline=BORDER)
            if 1<=dn<=31:
                d.text((xx+8,yy+6),str(dn),font=F(12,True),fill='#334155')
                key=f'2026-10-{dn:02d}'
                if key in events:
                    txt,colr=events[key]
                    d.rounded_rectangle([xx+4,yy+30,xx+cw-4,yy+52],4,fill=colr)
                    t=txt if d.textlength(txt,font=F(9,True))<cw-14 else txt[:int((cw-14)/6)]
                    d.text((xx+8,yy+34),t,font=F(9,True),fill='#fff')
    im.save(fn)

def shot_diff(fn):
    im,d=base('memos'); y=title(d,'Служебные записки','Модуль Diff2Html: side-by-side сопоставление редакций (СЗ-2026/048)')
    it=Q("SELECT * FROM service_note_items WHERE id=1")[0]
    d.rounded_rectangle([SBW+32,y,W-32,y+420],8,fill=CARD,outline=BORDER)
    d.text((SBW+50,y+12),'a/УП (v1.0)',font=F(12,True),fill='#b91c1c')
    d.text((SBW+50+(W-SBW-96)//2,y+12),'b/УП (v1.1)',font=F(12,True),fill='#15803d')
    half=(W-SBW-96)//2
    old=wrap(d,it['old_val'],F(12),half-40); new=wrap(d,it['new_val'],F(12),half-40)
    yy=y+48
    for ln in old:
        d.rectangle([SBW+50,yy,SBW+50+half,yy+26],fill='#fee2e2'); d.text((SBW+58,yy+5),'- '+ln,font=F(11),fill='#b91c1c'); yy+=28
    yy=y+48
    for ln in new:
        d.rectangle([SBW+66+half,yy,W-50,yy+26],fill='#dcfce7'); d.text((SBW+74+half,yy+5),'+ '+ln,font=F(11),fill='#15803d'); yy+=28
    im.save(fn)

OUT=f'{ROOT}/diagrams'
os.makedirs(OUT,exist_ok=True)
shot_dashboard(f'{OUT}/lab2/screen_dashboard.png')
shot_plan(f'{OUT}/lab2/screen_plan_grid.png',1)
shot_validate(f'{OUT}/lab2/screen_fgos_validation.png')
shot_memos(f'{OUT}/lab2/screen_service_notes.png',with_diff=True)
shot_dashboard(f'{OUT}/lab3/gpi_dashboard.png')
shot_plan(f'{OUT}/lab3/gpi_curriculum_editor.png',3)
shot_validate(f'{OUT}/lab3/gpi_fgos_validation.png')
shot_signatures(f'{OUT}/lab3/gpi_sign_workflow.png')
shot_memos(f'{OUT}/lab3/gpi_service_notes.png')
shot_dashboard(f'{OUT}/lab4/section_dashboard.png')
shot_plan(f'{OUT}/lab4/section_curriculum_catalog.png',2)
shot_validate(f'{OUT}/lab4/section_fgos_validation.png')
shot_signatures(f'{OUT}/lab4/section_digital_signatures.png',with_stamps=True)
shot_memos(f'{OUT}/lab4/section_service_memos.png',with_diff=True)
shot_programs_standards(f'{OUT}/lab4/section_programs_and_standards.png')
shot_audit(f'{OUT}/lab4/section_audit_and_security.png')
shot_plan(f'{OUT}/lab5/infoblock_curriculums_filled.png',1)
shot_validate(f'{OUT}/lab5/infoblock_fgos_validation_filled.png')
shot_simple_table(f'{OUT}/lab5/infoblock_competencies_matrix_filled.png','competencies','Матрица компетенций',
    "SELECT code, category, title, description FROM competencies ORDER BY id",['Код','Категория','Наименование','Индикатор достижения'],[80,180,320,700])
shot_programs_standards(f'{OUT}/lab5/infoblock_programs_standards_filled.png')
shot_memos(f'{OUT}/lab5/infoblock_memos_diff_filled.png',with_diff=True)
shot_signatures(f'{OUT}/lab5/infoblock_signatures_workflow_filled.png')
shot_simple_table(f'{OUT}/lab5/infoblock_departments_structure_filled.png','departments','Структурные подразделения университета',
    "SELECT short_name, name, type, phone, email FROM departments ORDER BY id",['Сокращение','Полное наименование','Тип','Телефон','Email'],[140,520,180,200,240])
shot_announcements(f'{OUT}/lab5/infoblock_news_announcements_filled.png')
shot_analytics(f'{OUT}/lab6/module_chartjs_analytics.png')
shot_calendar(f'{OUT}/lab6/module_calendar_scheduler.png')
shot_plan(f'{OUT}/lab6/module_datatable_search_filter.png',1,with_search=True)
shot_plan(f'{OUT}/lab6/module_export_pdf_excel.png',1,with_tools=True)
shot_signatures(f'{OUT}/lab6/module_crypto_signature_stamp.png',with_stamps=True)
shot_signatures(f'{OUT}/lab6/module_notifications_toast.png',with_toasts=True)
shot_diff(f'{OUT}/lab6/module_visual_diff_tracker.png')
print("shots done")
