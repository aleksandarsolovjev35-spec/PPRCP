# -*- coding: utf-8 -*-
"""Regenerates UML/architecture diagrams consistent with the actual code & data."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = '/usr/share/fonts/truetype/dejavu/'
def F(sz, bold=False):
    return ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz)
BG='#f8fafc'; INK='#0f172a'; MUT='#64748b'; BLUE='#2563eb'; LB='#dbeafe'; BORDER='#e2e8f0'
OUT=f'{ROOT}/diagrams'

def tx(d,x,y,s,sz=13,b=False,c=INK): d.text((x,y),s,font=F(sz,b),fill=c)

# ---------------------------------------------------------------- use case
def use_case():
    W,Hh=2200,2160; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,30,'Диаграмма вариантов использования — портал Центра АНОК',22,True)
    d.rounded_rectangle([430,90,W-430,Hh-40],16,outline=BLUE,width=2)
    tx(d,760,104,'ГРАНИЦА СИСТЕМЫ: КОРПОРАТИВНЫЙ ПОРТАЛ УНИВЕРСИТЕТА (МОДУЛЬ АНОК)',13,True,BLUE)
    actorsL=[('Руководитель выпускающего\nподразделения (HEAD_RELEASING)',180),('Руководитель реализующего\nподразделения (HEAD_IMPLEMENTING)',480),
             ('Секретарь Ученого совета\n(COUNCIL_SEC)',900),('Преподаватель / Студент\n(VIEWER)',1300)]
    actorsR=[('Эксперт Центра АНОК\n(EXPERT_ANOK)',180),('Начальник Центра АНОК\n(HEAD_ANOK)',480),('Проректор по учебной работе\n(VICE_RECTOR)',780),
             ('Ректор университета\n(RECTOR)',1080),('Администратор портала\n(ADMIN)',1500)]
    apos={}
    for name,y in actorsL:
        d.rounded_rectangle([40,y,W and 380,y+110],10,fill='#eff6ff',outline='#bfdbfe')
        d.ellipse([70,y+30,110,y+70],fill=BLUE)
        for i,ln in enumerate(name.split('\n')): tx(d,125,y+28+i*22,ln,12,i==0)
        apos[name.split('\n')[0]]= (380,y+55,'L')
    for name,y in actorsR:
        d.rounded_rectangle([W-380,y,W-40,y+110],10,fill='#f5f3ff',outline='#ddd6fe')
        d.ellipse([W-110,y+30,W-70,y+70],fill='#7c3aed')
        for i,ln in enumerate(name.split('\n')): tx(d,W-360,y+28+i*22,ln,12,i==0)
        apos[name.split('\n')[0]]=(W-380,y+55,'R')
    groups=[('БЛОК 1: УЧЕБНЫЕ ПЛАНЫ',[('UC-1 Просмотр реестра УП',['VIEWER','HEAD_RELEASING']),
        ('UC-2 Просмотр УП по семестрам (1–8)',['VIEWER']),('UC-3 Анализ нагрузки и СРС',['VIEWER','EXPERT_ANOK'])]),
      ('БЛОК 2: ЭКСПЕРТИЗА ФГОС 3++',[('UC-4 Автоматическая валидация УП',['EXPERT_ANOK','HEAD_ANOK']),
        ('UC-5 Контроль лимита экзаменов (≤ 5)',['EXPERT_ANOK']),('UC-6 Протокол замечаний',['EXPERT_ANOK','HEAD_ANOK'])]),
      ('БЛОК 3: СОГЛАСОВАНИЕ И ЭЦП',[('UC-7 Наложение визы ЭЦП',['HEAD_RELEASING','HEAD_ANOK','VICE_RECTOR','RECTOR']),
        ('UC-8 Просмотр цепочки подписания и SHA-256',['VIEWER','HEAD_RELEASING']),('UC-9 Утверждение протокола УС',['COUNCIL_SEC','RECTOR'])]),
      ('БЛОК 4: СЛУЖЕБНЫЕ ЗАПИСКИ',[('UC-10 Создание СЗ на изменение УП',['HEAD_RELEASING']),
        ('UC-11 Сравнение версий «Было → Стало»',['HEAD_RELEASING','HEAD_IMPLEMENTING']),
        ('UC-12 Согласование обеспечивающей кафедрой',['HEAD_IMPLEMENTING']),('UC-13 Применение правок в УП',['EXPERT_ANOK'])]),
      ('БЛОК 5: СПРАВОЧНИКИ И АДМИНИСТРИРОВАНИЕ',[('UC-14 Матрица компетенций (УК/ОПК/ПК)',['VIEWER']),
        ('UC-15 Справочник подразделений и контактов',['VIEWER','ADMIN']),('UC-16 Лента регламентов и объявлений',['VIEWER','HEAD_ANOK']),
        ('UC-17 Журнал аудита действий',['ADMIN'])])]
    keymap={'VIEWER':'Преподаватель / Студент','HEAD_RELEASING':'Руководитель выпускающего','HEAD_IMPLEMENTING':'Руководитель реализующего',
      'COUNCIL_SEC':'Секретарь Ученого совета','EXPERT_ANOK':'Эксперт Центра АНОК','HEAD_ANOK':'Начальник Центра АНОК','VICE_RECTOR':'Проректор по учебной работе',
      'RECTOR':'Ректор университета','ADMIN':'Администратор портала'}
    y=150
    for gname,ucs in groups:
        d.rounded_rectangle([470,y,W-470,y+34],6,fill='#e2e8f0')
        tx(d,900,y+8,gname,12,True,'#334155'); y+=44
        for uc,acs in ucs:
            ecx=1100; ecy=y+42
            d.ellipse([ecx-230,ecy-36,ecx+230,ecy+36],fill='#ffffff',outline=BLUE,width=2)
            tx(d,ecx-d.textlength(uc,font=F(13,True))/2,ecy-9,uc,13,True)
            for a in acs:
                ax,ay,side=apos[keymap[a]]
                d.line([(ax,ay),(ecx-230 if side=='L' else ecx+230,ecy)],fill='#94a3b8',width=1)
            y+=92
        y+=18
    im.save(f'{OUT}/use_case_diagram.png')

# ---------------------------------------------------------------- db schema
def db_schema():
    W,Hh=2100,1500; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Схема базы данных anok_portal (13 таблиц, 3NF, FOREIGN KEYS)',22,True)
    tables={
     'departments':(60,110,['PK id','name / short_name','type: RELEASING | IMPLEMENTING | EXPERT_ANOK | MANAGEMENT','phone / email']),
     'roles':(60,330,['PK id','role_name / code','description']),
     'standards_fgos':(60,520,['PK id','code (09.03.04…)','total_credits=240 / max_exams=5','min_practice=12 / min_gia=6']),
     'users':(60,740,['PK id','FK role_id → roles','FK department_id → departments','username / full_name / email']),
     'announcements':(60,960,['PK id','title / category','publish_date / is_pinned']),
     'audit_logs':(60,1160,['PK id','event_time / user_name / user_role','action / entity_name / status / ip']),
     'educational_programs':(760,110,['PK id','FK fgos_standard_id → standards_fgos','FK department_id → departments','code / title / level / study_form']),
     'curriculums':(760,340,['PK id','FK program_id → educational_programs','academic_year / version / status','total_credits / protocol № 8/26']),
     'competencies':(760,570,['PK id','FK program_id → educational_programs','code УК/ОПК/ПК / category','title / description']),
     'service_notes':(760,800,['PK id','FK curriculum_id → curriculums','FK releasing/implementing → departments','note_num / reason / status']),
     'service_note_items':(760,1040,['PK id','FK service_note_id → service_notes','FK discipline_id → curriculum_disciplines','change_type / old_val / new_val']),
     'curriculum_disciplines':(1460,110,['PK id','FK curriculum_id → curriculums','FK implementing_department_id → departments','semester 1..8 / credits_ze / часы','control_form']),
     'document_signatures':(1460,420,['PK id','doc_type / doc_id (полиморфная связь)','step_order 1..4 / role_title','signer_name / signed_at / sign_hash SHA-256']),
    }
    pos={}
    for name,(x,y,lines) in tables.items():
        h=46+len(lines)*26
        colors={'departments':'#16a34a','roles':'#1d4ed8','standards_fgos':'#b45309','users':'#1d4ed8','announcements':'#b45309','audit_logs':'#334155',
                'educational_programs':'#16a34a','curriculums':'#7c3aed','competencies':'#b45309','service_notes':'#b91c1c','service_note_items':'#b91c1c',
                'curriculum_disciplines':'#7c3aed','document_signatures':'#334155'}
        d.rectangle([x,y,x+620,y+34],fill=colors[name])
        tx(d,x+12,y+8,f'table: {name}',14,True,'#fff')
        d.rectangle([x,y+34,x+620,y+h],fill='#fff',outline=BORDER)
        for i,ln in enumerate(lines):
            col='#b91c1c' if ln.startswith('PK') else ('#1d4ed8' if ln.startswith('FK') else '#334155')
            tx(d,x+12,y+44+i*26,ln,12,False,col)
        pos[name]=(x,y,h)
    links=[('educational_programs','standards_fgos'),('educational_programs','departments'),('curriculums','educational_programs'),
      ('curriculum_disciplines','curriculums'),('curriculum_disciplines','departments'),('competencies','educational_programs'),
      ('users','roles'),('users','departments'),('service_notes','curriculums'),('service_notes','departments'),
      ('service_note_items','service_notes'),('service_note_items','curriculum_disciplines')]
    for a,b in links:
        x1,y1,h1=pos[a]; x2,y2,h2=pos[b]
        c1=(x1+310,y1+h1); c2=(x2+310,y2)
        if x1==x2:
            d.line([(x1+620,y1+h1//2),(x2+620,y2+h2//2)],fill=BLUE,width=2)
        else:
            sx = x1+620 if x1<x2 else x1
            ex = x2 if x2>x1 else x2+620
            d.line([(sx,y1+h1//2),(ex,y2+h2//2)],fill=BLUE,width=2)
    im.save(f'{OUT}/lab2/db_schema_diagram.png')

# ---------------------------------------------------------------- class
def class_diagram():
    W,Hh=2100,1400; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Диаграмма классов — объектная модель предметной области',22,True)
    cls={
     'Curriculum':(820,90,['academicYear; version; status','totalCredits; protocolNum','protocolDate'],['validate(); approve()']),
     'EducationalProgram':(120,90,['code; title; level','studyForm'],['']),
     'StandardFGOS':(120,330,['totalCredits=240; maxExams=5','minPractice=12; minGia=6'],['check(plan)']),
     'CurriculumDiscipline':(1520,90,['blockType; semesterNum','creditsZe; totalHours','lecture/lab/practice/selfHours','controlForm'],['hoursBalance()']),
     'Department':(1520,420,['name; shortName','type; phone; email'],['']),
     'DocumentSignature':(820,380,['stepOrder; roleTitle','signerName; status','signedAt; signHash SHA-256'],['sign(); verify()']),
     'ServiceNote':(820,660,['noteNum; noteDate; reason','status; createdBy'],['apply()']),
     'ServiceNoteItem':(1520,700,['changeType','oldVal; newVal'],['diff()']),
     'User':(120,620,['username; fullName','email; positionTitle'],['']),
     'Role':(120,880,['roleName; code','description'],['']),
     'AuditLog':(820,940,['eventTime; userName','userRole; action','entityName; status; ip'],['log()']),
    }
    pos={}
    for name,(x,y,attrs,meth) in cls.items():
        h=40+len(attrs)*24+ (24+len(meth)*24 if meth[0] else 10)
        d.rectangle([x,y,x+520,y+36],fill='#1e293b'); tx(d,x+14,y+8,name,15,True,'#fff')
        d.rectangle([x,y+36,x+520,y+36+len(attrs)*24],fill='#fff',outline=BORDER)
        for i,a in enumerate(attrs): tx(d,x+14,y+42+i*24,a,12)
        y2=y+36+len(attrs)*24
        if meth[0]:
            d.rectangle([x,y2,x+520,y2+24+len(meth)*24],fill='#f8fafc',outline=BORDER)
            for i,m in enumerate(meth): tx(d,x+14,y2+6+i*24,m,12,False,'#1d4ed8')
        pos[name]=(x,y,h if h else 100)
    rel=[('Curriculum','EducationalProgram','1 — *'),('Curriculum','CurriculumDiscipline','1 — *'),
         ('EducationalProgram','StandardFGOS','* — 1'),('Curriculum','DocumentSignature','1 — *'),
         ('Curriculum','ServiceNote','1 — *'),('ServiceNote','ServiceNoteItem','1 — *'),
         ('CurriculumDiscipline','Department','* — 1'),('User','Role','* — 1'),('User','Department','* — 1')]
    for a,b,lab in rel:
        x1,y1,h1=pos[a]; x2,y2,h2=pos[b]
        p1=(x1+260,y1+h1); p2=(x2+260,y2)
        if abs(x1-x2)<10: d.line([(x1+520,y1+h1//2),(x2,y2+h2//2)],fill='#475569',width=2)
        else: d.line([(x1+260,y1+h1),(x2+260,y2)],fill='#475569',width=2)
        mx,my=( (p1[0]+p2[0])//2,(p1[1]+p2[1])//2 )
        tx(d,mx+6,my-8,lab,11,True,'#475569')
    im.save(f'{OUT}/lab2/class_diagram.png')

# ---------------------------------------------------------------- component
def component():
    W,Hh=1900,1200; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Диаграмма компонентов — модульная структура портала (15 разделов + REST API)',20,True)
    layers=[('КЛИЕНТСКИЙ УРОВЕНЬ (Web Browser): HTML5/CSS3, JS-модули Chart.js, FullCalendar, DataTables, SheetJS, jsPDF, CryptoJS, SweetAlert2/Toastify, Diff2Html (CDN)',110,'#dbeafe'),
      ('HTTP KERNEL / ROUTER: dashboard · plans · plan · analytics · calendar · validate · signatures · memos · programs · competencies · standards · departments · announcements · audit · sitemap · /api/*',330,'#e0e7ff'),
      ('SERVICE LAYER: CurriculumService · ValidationEngine (ФГОС 3++) · WorkflowManager (ЭЦП) · MemoManager (СЗ) · AuditLogger',560,'#ede9fe'),
      ('DATA ACCESS LAYER: PDO MySQL / sqlite3, Prepared Statements → schema.sql + seed.sql (13 таблиц)',790,'#dcfce7')]
    for txt,y,colr in layers:
        d.rounded_rectangle([120,y,W-120,y+170],12,fill=colr,outline=BORDER)
        lines=txt.split(': ',1)
        tx(d,150,y+18,lines[0],15,True)
        for i in range(0,len(lines[1]),110):
            pass
        body=lines[1]
        import textwrap
        for i,ln in enumerate(textwrap.wrap(body,110)):
            tx(d,150,y+52+i*26,ln,13)
    for y in (280,510,740):
        d.line([(W//2,y),(W//2,y+50)],fill='#475569',width=2)
        d.polygon([(W//2-8,y+42),(W//2+8,y+42),(W//2,y+54)],fill='#475569')
    im.save(f'{OUT}/lab2/component_diagram.png')

# ---------------------------------------------------------------- deployment
def deployment():
    W,Hh=1900,900; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Диаграмма развёртывания — физическая топология',20,True)
    nodes=[('«Client Workstation»\nWeb-браузер (HTML5/CSS3/JS)\nмодули CDN',140,300,'#dbeafe'),
           ('«App Server»\nPython 3 http.server / PHP 8\nportal/server.py · portal/index.php\nпорт TCP 8000',760,260,'#e0e7ff'),
           ('«Database Server»\nMySQL 8 / MariaDB 10.6 (TCP 3306)\nили SQLite (portal.db)\n13 таблиц, FOREIGN KEYS',1380,300,'#dcfce7')]
    for txt,x,y,colr in nodes:
        d.rounded_rectangle([x,y,x+420,y+260],12,fill=colr,outline='#475569',width=2)
        for i,ln in enumerate(txt.split('\n')): tx(d,x+24,y+30+i*44,ln,15,i==0)
    d.line([(560,430),(760,390)],fill='#475569',width=3)
    tx(d,600,360,'HTTP/HTTPS (TCP 8000)',13,True,'#475569')
    d.line([(1180,390),(1380,430)],fill='#475569',width=3)
    tx(d,1200,360,'SQL / PDO (TCP 3306)',13,True,'#475569')
    im.save(f'{OUT}/lab2/deployment_diagram.png')

# ---------------------------------------------------------------- sequence
def sequence():
    W,Hh=2000,1200; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Диаграмма последовательности — экспертиза, валидация и утверждение УП',20,True)
    lanes=['Зав. выпускающей\nкафедрой','Портал\n(HTTP Router)','FGOS Validation\nEngine','Эксперт /\nНачальник АНОК','Проректор\nпо УР','Ректор\nуниверситета']
    xs=[180+i*300 for i in range(6)]
    for x,nm in zip(xs,lanes):
        d.rounded_rectangle([x-110,90,x+110,170],8,fill='#1e293b')
        for i,ln in enumerate(nm.split('\n')): tx(d,x-d.textlength(ln,font=F(13,True))/2,104+i*22,ln,13,True,'#fff')
        d.line([(x,170),(x,Hh-60)],fill='#94a3b8',width=2)
    msgs=[(0,1,'1. Инициирует проект УП, накладывает первичную ЭЦП'),
          (1,2,'2. Запуск валидации: 240 з.е., 30/сем, ≤ 5 экз., ≥ 12 практ., ≥ 6 ГИА'),
          (2,3,'3. Протокол проверки: замечаний нет'),
          (3,1,'4. Положительная виза АНОК (SHA-256)'),
          (1,4,'5. Согласование для Ученого совета'),
          (4,5,'6. Передача на утверждение'),
          (5,1,'7. Утверждение: протокол УС № 8/26 от 25.06.2026, финальный хэш')]
    y=220
    for a,b,txt in msgs:
        d.line([(xs[a],y),(xs[b],y)],fill=BLUE,width=2)
        dirr = 1 if b>a else -1
        d.polygon([(xs[b]-dirr*12,y-6),(xs[b]-dirr*12,y+6),(xs[b],y)],fill=BLUE)
        tx(d,min(xs[a],xs[b])+20,y-26,txt,12,True,'#334155')
        y+=120
    im.save(f'{OUT}/lab2/sequence_diagram.png')

# ---------------------------------------------------------------- sitemap
def sitemap():
    W,Hh=2000,1250; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Карта разделов портала (Sitemap): 15 страниц + REST API',20,True)
    d.rounded_rectangle([760,90,1240,170],10,fill=BLUE)
    tx(d,830,110,'ГЛАВНАЯ (Сводная панель)',15,True,'#fff'); tx(d,880,140,'?page=dashboard',12,False,'#dbeafe')
    groups=[('УЧЕБНЫЕ ПЛАНЫ',['plans — Реестр планов','plan&id&sem — Сетка семестров 1–8','competencies — Матрица УК/ОПК/ПК'],120),
      ('КАЧЕСТВО / ФГОС',['validate — Экспертиза ФГОС 3++','standards — Стандарты 3++','analytics — Аналитика (Chart.js)'],520),
      ('ДОКУМЕНТООБОРОТ',['signatures — Согласование и ЭЦП','memos — Служебные записки + Diff','calendar — Календарь (FullCalendar)'],920),
      ('СПРАВОЧНИКИ',['programs — Программы','departments — Подразделения (9)','announcements — Объявления'],1320),
      ('СЛУЖЕБНЫЕ',['audit — Журнал аудита','sitemap — Карта сайта','/api/stats · /api/plans · /api/announcements'],1700)]
    for g,items,x in groups:
        d.line([(1000,170),(x+140,240)],fill='#94a3b8',width=2)
        d.rounded_rectangle([x,240,x+280,300],8,fill='#1e293b')
        tx(d,x+20,260,g,13,True,'#fff')
        y=320
        for it in items:
            d.rounded_rectangle([x,y,x+280,y+64],8,fill='#fff',outline=BORDER)
            nm,_,url=it.partition(' — ')
            tx(d,x+14,y+8,nm,13,True)
            tx(d,x+14,y+34,(url or nm),10,False,MUT)
            y+=76
    im.save(f'{OUT}/lab4/sitemap_architecture.png')

# ---------------------------------------------------------------- palette
def palette():
    W,Hh=1700,1100; im=Image.new('RGB',(W,Hh),'#fff'); d=ImageDraw.Draw(im)
    tx(d,60,30,'Дизайн-токены: цветовое решение и типографика',22,True)
    tokens=[('--bg-header','#0f172a','Шапка (Slate-900)'),('--bg-sidebar','#1e293b','Навигация (Slate-800)'),
      ('--page-bg','#f8fafc','Фон страниц'),('--card-bg','#ffffff','Карточки и таблицы'),('--primary','#2563eb','Акцент / кнопки'),
      ('--primary-hover','#1d4ed8','Hover'),('--text-main','#1e293b','Основной текст'),('--text-muted','#64748b','Метаданные'),
      ('--border','#e2e8f0','Разделители'),('--badge-green','#15803d','Утверждено / Подписано'),('--badge-purple','#7e22ce','На экспертизе'),
      ('--badge-yellow','#b45309','На согласовании'),('--badge-red','#b91c1c','Ошибка ФГОС')]
    y=100
    for name,hexc,desc in tokens:
        d.rounded_rectangle([80,y,160,y+52],8,fill=hexc,outline=BORDER)
        tx(d,180,y+6,name,14,True); tx(d,180,y+30,hexc,12,False,MUT)
        tx(d,520,y+16,desc,13); y+=64
    tx(d,1000,100,'Типографика',17,True)
    ty=140
    for sample,sz,b,desc in (('Заголовок раздела h1',24,True,'24px / 700'),('Подзаголовок h2',18,True,'18px / 600'),
        ('Метрики карточек',32,True,'32px / 800'),('Основной текст',14,False,'14px / 1.5'),('Заголовки таблиц TH',12,True,'12px / 600 caps'),
        ('Метаданные',12,False,'12–13px'),('Хэши / код (mono)',11,False,'11–12px monospace')):
        tx(d,1000,ty,sample,sz,b); tx(d,1000,ty+sz+8,desc,11,False,MUT); ty+=sz+44
    im.save(f'{OUT}/lab3/ui_palette_typography.png')

# ---------------------------------------------------------------- wireframe
def wireframe():
    W,Hh=1900,1200; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,20,'Шаблон дизайна портала: разметка страницы (header / nav / main / footer)',20,True)
    X,Y=60,80; WW=1300
    d.rectangle([X,Y,X+WW,Y+60],fill='#0f172a')
    d.rounded_rectangle([X+20,Y+14,X+52,Y+46],8,fill=BLUE); tx(d,X+30,Y+20,'А',16,True,'#fff')
    tx(d,X+66,Y+12,'УНИВЕРСИТЕТ · Центр АНОК',14,True,'#fff')
    tx(d,X+66,Y+34,'Аккредитация и независимая оценка качества образования',10,False,'#94a3b8')
    tx(d,X+WW-260,Y+12,'Соловьев А.С.',12,True,'#fff'); tx(d,X+WW-260,Y+32,'Эксперт АНОК',10,False,'#94a3b8')
    d.rectangle([X,Y+60,X+240,Y+1040],fill='#1e293b')
    nav=['Главная','Учебные планы','Аналитика','Календарь дедлайнов','Проверка ФГОС','Согласование','Служебные записки','Программы','Компетенции','Стандарты','Подразделения','Объявления','Аудит','Карта сайта']
    yy=Y+80
    for i,nm in enumerate(nav):
        if i==1: d.rounded_rectangle([X+10,yy-6,X+230,yy+26],6,fill=BLUE)
        tx(d,X+24,yy,nm,12,i==1,'#fff' if i==1 else '#cbd5e1'); yy+=34
    d.rectangle([X+240,Y+60,X+WW,Y+1040],fill='#f8fafc')
    tx(d,X+270,Y+90,'Основная рабочая область (max-width 1200px, padding 32px)',14,True,'#334155')
    for i in range(4):
        d.rounded_rectangle([X+270+i*250,Y+130,X+270+i*250+230,Y+230],8,fill='#fff',outline=BORDER)
    d.rounded_rectangle([X+270,Y+260,X+WW-40,Y+560],8,fill='#fff',outline=BORDER)
    for r in range(6):
        d.line([(X+270,Y+300+r*42),(X+WW-40,Y+300+r*42)],fill=BORDER)
    d.rectangle([X,Y+1040,X+WW,Y+1090],fill='#0f172a')
    tx(d,X+20,Y+1056,'© 2026 Центр АНОК · Версия 2.4.0',11,False,'#94a3b8')
    tx(d,X+WW-520,Y+1056,'Синхронизация с БД: OK · Регламент ФГОС ВО 3++',11,False,'#94a3b8')
    ax=X+WW+40
    notes=[('1. Заголовочная часть (Header, 60px, sticky): логотип «А», наименование, профиль пользователя'),
      ('2. Навигация (Sidebar, 240px): 14 разделов меню, подсветка активного пункта #2563eb'),
      ('3. Основная часть (Main): карточки метрик, табличные контейнеры, border-radius 10px'),
      ('4. Нижняя часть (Footer, 48px): строка статуса синхронизации и версии системы'),
      ('Адаптив ≤ 768px: sidebar 70px с иконками, overflow-x у таблиц, карточки в 1 колонку')]
    yy=120
    for n in notes:
        d.rounded_rectangle([ax,yy,ax+470,yy+120],8,fill='#eff6ff',outline='#bfdbfe')
        import textwrap
        for i,ln in enumerate(textwrap.wrap(n,52)): tx(d,ax+14,yy+12+i*20,ln,11,False,'#1e40af')
        yy+=150
    im.save(f'{OUT}/lab3/template_wireframe.png')

# ---------------------------------------------------------------- modules arch
def modules_arch():
    W,Hh=1900,1000; im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,60,26,'Архитектура интеграции готовых модулей (ЛР № 6)',20,True)
    d.rounded_rectangle([120,120,640,560],12,fill='#dbeafe',outline=BORDER)
    tx(d,140,140,'CDN: готовые клиентские модули',14,True)
    for i,m in enumerate(['Chart.js 4','FullCalendar 6','DataTables 1.13','SheetJS / jsPDF','CryptoJS (SHA-256)','SweetAlert2 / Toastify','Diff2Html']):
        d.rounded_rectangle([140,180+i*52,620,222+i*52],6,fill='#fff',outline=BORDER); tx(d,156,190+i*52,m,13)
    d.rounded_rectangle([720,120,1240,560],12,fill='#e0e7ff',outline=BORDER)
    tx(d,740,140,'Клиентский уровень портала',14,True)
    for i,m in enumerate(['?page=analytics — диаграммы','?page=calendar — график процедур','?page=plan — поиск/сортировка/экспорт','?page=signatures — штампы ЭЦП, алерты','?page=memos — side-by-side диффы']):
        d.rounded_rectangle([740,180+i*72,1220,240+i*72],6,fill='#fff',outline=BORDER); tx(d,756,198+i*72,m,12)
    d.rounded_rectangle([1320,120,1780,560],12,fill='#dcfce7',outline=BORDER)
    tx(d,1340,140,'Серверный движок (Python/PHP)',14,True)
    for i,m in enumerate(['Router: 15 разделов + /api/*','ValidationEngine ФГОС 3++','WorkflowManager (ЭЦП)','MemoManager (СЗ)','AuditLogger','Prepared Statements → JSON']):
        d.rounded_rectangle([1340,180+i*60,1760,228+i*60],6,fill='#fff',outline=BORDER); tx(d,1356,192+i*60,m,12)
    d.line([(640,340),(720,340)],fill='#475569',width=3); d.line([(1240,340),(1320,340)],fill='#475569',width=3)
    tx(d,650,300,'JS',12,True,'#475569'); tx(d,1250,300,'JSON',12,True,'#475569')
    d.rounded_rectangle([720,640,1240,840],12,fill='#f1f5f9',outline=BORDER)
    tx(d,740,660,'БД anok_portal: 13 таблиц (SQLite / MySQL)',14,True)
    d.line([(1550,560),(1550,740),(1240,740)],fill='#475569',width=3)
    tx(d,1260,700,'SQL',12,True,'#475569')
    im.save(f'{OUT}/lab6/module_architecture_integration.png')

use_case(); db_schema(); class_diagram(); component(); deployment(); sequence(); sitemap(); palette(); wireframe(); modules_arch()
print("diagrams done")
