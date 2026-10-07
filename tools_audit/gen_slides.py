# -*- coding: utf-8 -*-
"""Regenerates the 12 defense slides (dark theme) with data consistent with the portal DB."""
import os, sqlite3, re
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD = '/usr/share/fonts/truetype/dejavu/'
def F(sz, bold=False):
    return ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), sz)
BG='#111827'; PANEL='#1f2937'; CARD='#111827'; ACC='#2563eb'; SKY='#38bdf8'; TXT='#f9fafb'; MUT='#9ca3af'
GREEN='#34d399'; PURP='#a78bfa'; AMBER='#fbbf24'; RED='#f87171'
W,H=1920,1080
OUT=f'{ROOT}/diagrams/lab7'

def new_slide(num):
    im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
    d.rectangle([0,0,W,8],fill=ACC); d.rectangle([0,H-8,W,H],fill=ACC)
    def footer():
        pass
    d.text((60,H-52),'Корпоративный портал университета — Модуль Центра АНОК | 2026',font=F(16),fill=MUT)
    d.text((W-260,H-52),f'Слайд {num} из 12',font=F(16,True),fill=SKY)
    return im,d

def head(d,title,sub):
    d.text((60,50),title,font=F(34,True),fill=TXT)
    d.text((60,100),sub,font=F(18),fill=MUT)
    d.rounded_rectangle([W-520,50,W-60,110],10,fill=PANEL)
    d.text((W-500,68),'ПРКП · Вариант 15 · Центр АНОК',font=F(16),fill=MUT)
    d.rectangle([0,130,W,136],fill=ACC)

def card(d,x,y,w,h,border=ACC):
    d.rounded_rectangle([x,y,x+w,y+h],12,fill=PANEL)
    d.rectangle([x,y,x+w,y+6],fill=border)

def bullets(d,x,y,items,sz=20,col=TXT,step=44):
    for t in items:
        d.ellipse([x,y+10,x+10,y+20],fill=SKY)
        d.text((x+26,y),t,font=F(sz),fill=col)
        y+=step
    return y

# S1 title
im,d=new_slide(1)
d.rounded_rectangle([690,150,1230,205],26,fill=ACC)
d.text((724,164),'ИТОГОВАЯ ЗАЩИТА ПРОЕКТА КОРПОРАТИВНОГО ПОРТАЛА',font=F(17,True),fill='#fff')
d.text((370,260),'Проектирование и разработка корпоративного веб-портала',font=F(40,True),fill=TXT)
d.text((430,330),'«Модуль Центра аккредитации и независимой оценки',font=F(36,True),fill=SKY)
d.text((640,395),'качества образования (АНОК)»',font=F(36,True),fill=SKY)
xs=[220,650,1080,1510]
for x,(t,b,c) in zip(xs,[('Нормативная база','ФГОС 3++, матрицы ЗЕТ, лимиты часов и компетенций',ACC),
   ('Сквозной воркфлоу','Согласование УП, служебные записки, протоколы УС',PURP),
   ('Криптография ЭЦП','Хеширование SHA-256, проверка УЦ, штампы',GREEN),
   ('Интерактивный UX','Chart.js, FullCalendar, Diff-трекер версий, SheetJS',SKY)]):
    card(d,x,520,380,200,c)
    d.text((x+22,550),t,font=F(22,True),fill=TXT)
    for i,ln in enumerate(b.split(', ')):
        d.text((x+22,600+i*30),ln,font=F(16),fill=MUT)
d.text((220,880),'Дисциплина: Проектирование и разработка корпоративных порталов (ПРКП)',font=F(18),fill=MUT)
d.text((220,915),'Специализация: Вариант № 15 (Университет — Центр АНОК)',font=F(18,True),fill=SKY)
d.text((1300,880),'Выполнил: студент группы П-41',font=F(22),fill=MUT)
d.text((1300,915),'Год разработки: 2026 · г. Москва',font=F(18),fill=MUT)
im.save(f'{OUT}/slide_01_title.png')

# S2 context & goals
im,d=new_slide(2); head(d,'Контекст и цели проекта','Предметная область, акторы и нормативные требования')
card(d,60,170,900,420,ACC)
d.text((85,200),'Предметная область',font=F(24,True),fill=SKY)
bullets(d,85,250,['Центр АНОК: экспертиза и валидация УП по ФГОС ВО 3++','Объект автоматизации — учебный план (240 з.е., 8 семестров)','Маршрут утверждения: каф. → АНОК → Проректор → Ректор','Служебные записки на корректировку дисциплин («Было → Стало»)'],19)
card(d,990,170,870,420,GREEN)
d.text((1015,200),'Цели разработки',font=F(24,True),fill=GREEN)
bullets(d,1015,250,['Алгоритмическая валидация нормативов (240 / 30 / ≤5 / ≥12 / ≥6)','Исключение ошибок несбалансированности з.е.','Прозрачный жизненный цикл утверждения с ЭЦП (SHA-256)','Единое информационное пространство кафедр'],19)
card(d,60,620,1800,330,PURP)
d.text((85,650),'Основные акторы (9 ролей)',font=F(24,True),fill=PURP)
actors=['Зав. выпускающей каф.','Зав. реализующей каф.','Эксперт АНОК','Начальник АНОК','Проректор по УР','Ректор','Секретарь УС','Преподаватель / студент','Администратор']
x=85
for i,a in enumerate(actors):
    w=d.textlength(a,font=F(17,True))+40
    if x+w>1820: x=85
    d.rounded_rectangle([x,720+(i//5)*70,x+w,760+(i//5)*70],20,fill='#374151')
    d.text((x+20,730+(i//5)*70),a,font=F(17,True),fill=TXT); x+=w+16
im.save(f'{OUT}/slide_02_context_goals.png')

# S3 architecture
im,d=new_slide(3); head(d,'Архитектура и стек технологий','Многоуровневая архитектура без тяжеловесных фреймворков')
layers=[('Web UI: HTML5/CSS3, адаптив, JS-модули (Chart.js, FullCalendar, DataTables, SheetJS, jsPDF, CryptoJS, SweetAlert2/Toastify, Diff2Html)',ACC),
 ('HTTP Router: 15 разделов + REST API (/api/stats, /api/plans, /api/announcements)',SKY),
 ('Service Layer: CurriculumService · ValidationEngine · WorkflowManager · MemoManager · AuditLogger',PURP),
 ('Data Access: PDO MySQL / sqlite3, Prepared Statements; СУБД MySQL 8 / MariaDB / SQLite (13 таблиц, FK)',GREEN)]
y=190
for t,c in layers:
    card(d,240,y,1440,150,c)
    for i,ln in enumerate([t[:95],t[95:]]):
        if ln: d.text((270,y+30+i*44),ln,font=F(20,i==0),fill=TXT)
    y+=180
d.text((240,y+10),'Отклик < 50 мс · потребление RAM < 30 МБ · запуск одной командой (python3 server.py)',font=F(18),fill=MUT)
im.save(f'{OUT}/slide_03_architecture_stack.png')

# S4 data model
im,d=new_slide(4); head(d,'Информационная модель и структура базы данных','13 нормализованных таблиц (3NF) с FOREIGN KEYS')
rows=[('curriculums','Реестр учебных планов','1'),('curriculum_disciplines','Семестровая матрица дисциплин','51'),
 ('standards_fgos','Нормативы ФГОС 3++','3'),('educational_programs','Паспорта ОП','1'),('competencies','Матрица УК/ОПК/ПК','13'),
 ('departments','Подразделения (выпускающие/обеспечивающие/АНОК)','9'),('document_signatures','Этапы визирования + SHA-256','4'),
 ('service_notes','Служебные записки','4'),('service_note_items','Диффы «Было → Стало»','4'),('users','Учетные записи','7'),
 ('roles','Роли доступа','7'),('announcements','Регламенты и объявления','4'),('audit_logs','Журнал аудита с IP','7')]
y=180
for i,(nm,desc,cnt) in enumerate(rows):
    col=i%2; xx=60+col*930; yy=180+(i//2)*112
    card(d,xx,yy,900,100,'#374151')
    d.text((xx+24,yy+16),nm,font=F(20,True),fill=SKY)
    d.text((xx+24,yy+50),desc,font=F(16),fill=MUT)
    d.rounded_rectangle([xx+790,yy+24,xx+870,yy+76],8,fill='#374151',outline=ACC)
    d.text((xx+820-d.textlength(cnt,font=F(24,True))/2,yy+34),cnt,font=F(24,True),fill=TXT)
card(d,60,955,1800,64,GREEN)
d.text((90,972),'Каскадная целостность: FOREIGN KEYS в schema.sql; PRAGMA foreign_key_check = 0 нарушений',font=F(19,True),fill=GREEN)
im.save(f'{OUT}/slide_04_data_model.png')

# S5 structure
im,d=new_slide(5); head(d,'Структура портала и навигация','15 функциональных страниц + сквозная семестровая навигация')
groups=[('Учебные планы',['dashboard','plans','plan (сем. 1–8)','competencies'],ACC),
 ('Качество / ФГОС',['validate','standards','analytics (Chart.js)'],GREEN),
 ('Документооборот',['signatures (ЭЦП)','memos (Diff)','calendar (FullCalendar)'],PURP),
 ('Справочники',['programs','departments','announcements'],SKY),
 ('Служебные',['audit','sitemap','REST API ×3'],AMBER)]
x=60
for g,items,c in groups:
    card(d,x,190,350,560,c)
    d.text((x+22,220),g,font=F(22,True),fill=c)
    yy=280
    for it in items:
        d.rounded_rectangle([x+22,yy,x+328,yy+56],8,fill='#374151')
        d.text((x+38,yy+15),'?page='+it if not it.startswith('REST') else it,font=F(16),fill=TXT)
        yy+=72
    x+=372
d.text((60,800),'Сайдбар: 14 пунктов меню + страница просмотра плана · адаптив ≤ 768px · футер со статусом синхронизации',font=F(19),fill=MUT)
im.save(f'{OUT}/slide_05_portal_structure.png')

# S6 fgos
im,d=new_slide(6); head(d,'Автоматизированная экспертиза ФГОС ВО 3++','Все показатели вычисляются из БД (функция validate_curriculum)')
hdr=['Критерий','Норма','Факт','Статус']
rows=[('Общая трудоемкость','240 з.е.','240 з.е.','СООТВЕТСТВУЕТ'),('Баланс семестров 1–8','30 з.е. / 1080 ч','30 / 1080 в каждом','СООТВЕТСТВУЕТ'),
 ('Экзаменов в сессию','≤ 5','4','СООТВЕТСТВУЕТ'),('Практическая подготовка (Б2)','≥ 12 з.е.','34 з.е.','СООТВЕТСТВУЕТ'),
 ('Блок ГИА (Б3)','≥ 6 з.е.','9 з.е.','СООТВЕТСТВУЕТ')]
y=210
widths=[640,380,420,360]; x0=80
for xx,htxt,wd in zip([80,720,1100,1520],hdr,widths):
    d.text((xx,y),htxt,font=F(20,True),fill=SKY)
y+=50
for r in rows:
    card(d,80,y,1760,90,'#374151')
    for xx,val,wd in zip([100,720,1100,1540],r,widths):
        d.text((xx,y+30),val,font=F(19,val=='СООТВЕТСТВУЕТ'),fill=GREEN if val=='СООТВЕТСТВУЕТ' else TXT)
    y+=110
d.text((80,y+20),'Блоки УП: Б1.О 117 · Б1.В 71 · Б2 34 · Б3 9 · ФТД 9 з.е. = 240',font=F(20,True),fill=AMBER)
im.save(f'{OUT}/slide_06_fgos_validation.png')

# S7 memos
im,d=new_slide(7); head(d,'Управление изменениями УП','Служебные записки с версионными изменениями «Было → Стало»')
rows=[('СЗ-2026/048','Матанализ: 3 → 5 з.е., зачет → экзамен','ПРИМЕНЕНА',GREEN),
 ('СЗ-2026/052','Алгоритмизация: 36 ч практики → 36 ч лабораторных','ПРИМЕНЕНА',GREEN),
 ('СЗ-2026/059','Мобильная разработка → Каф. ИСТ','НА ЭКСПЕРТИЗЕ',PURP),
 ('СЗ-2026/061','График преддипломной практики: сдвиг на 2 недели','ВИЗА ВЫПУСКАЮЩЕЙ',SKY)]
y=200
for nm,desc,st,c in rows:
    card(d,80,y,1760,110,c)
    d.text((110,y+20),nm,font=F(22,True),fill=SKY)
    d.text((380,y+24),desc,font=F(20),fill=TXT)
    d.text((1450,y+24),st,font=F(19,True),fill=c)
    y+=130
card(d,80,y+10,1760,180,RED)
d.text((110,y+40),'Diff2Html (side-by-side):',font=F(20,True),fill=RED)
d.text((110,y+80),'- Семестр 1: Матанализ — 3 з.е. (108 ч.) · Зачет · Каф. ВМ',font=F(18),fill=RED)
d.text((110,y+120),'+ Семестр 1: Матанализ — 5 з.е. (180 ч.) [+2 з.е.] · Экзамен · Каф. ВМ',font=F(18),fill=GREEN)
im.save(f'{OUT}/slide_07_visual_diff.png')

# S8 signatures
im,d=new_slide(8); head(d,'Цифровое визирование и ЭЦП','4 этапа согласования с криптографическими штампами SHA-256')
steps=[('1','Руководитель выпускающего подразделения','Иванов И.И. (Зав. каф. ПИ)','2026-06-15','da15dc1a…ede6'),
 ('2','Начальник Центра АНОК','Кузнецов В.П. (Нач. АНОК)','2026-06-18','2e4aab7…6dc9'),
 ('3','Проректор по учебной работе','Смирнов А.Н. (Проректор по УР)','2026-06-22','67c1ef7…1f2d'),
 ('4','Ректор университета','Михайлов С.В. (Ректор) · протокол УС № 8/26 от 25.06.2026','2026-06-25','36f5e44…184')]
y=200
for n,role,who,dt,hh in steps:
    card(d,140,y,1640,140,GREEN)
    d.ellipse([170,y+40,230,y+100],fill=ACC)
    d.text((192,y+52),n,font=F(26,True),fill='#fff')
    d.text((260,y+22),role,font=F(22,True),fill=TXT)
    d.text((260,y+62),f'{who} · {dt}',font=F(17),fill=MUT)
    d.text((260,y+96),f'SHA-256: {hh} · [MATCH] (пересчет совпадает с хранилищем)',font=F(15),fill=GREEN)
    y+=160
d.text((140,y+20),'Верификация на странице ?page=signatures: CryptoJS пересчитывает payload и сверяет с БД (4 из 4 действительны)',font=F(18),fill=MUT)
im.save(f'{OUT}/slide_08_crypto_signature.png')

# S9 analytics
im,d=new_slide(9); head(d,'Аналитика и сводная панель','Chart.js: структура блоков, компетенции, часы по семестрам')
vals=[('117','Б1.О обязательная',ACC),('71','Б1.В вариативная',SKY),('34','Б2 практики',GREEN),('9','Б3 ГИА',AMBER),('9','ФТД',PURP)]
x=80
for v,lab,c in vals:
    card(d,x,200,330,170,c)
    d.text((x+30,230),v,font=F(44,True),fill=c)
    d.text((x+30,300),lab+' з.е.',font=F(18),fill=MUT)
    x+=360
card(d,80,410,870,300,ACC)
d.text((110,440),'Сводная панель',font=F(22,True),fill=SKY)
bullets(d,110,490,['Учебные планы: 1 · Дисциплины: 51','Стандарты ФГОС: 3 · Служебные записки: 4','Реестр УП с переходом к семестровой сетке','Лента закрепленных регламентов АНОК'],19)
card(d,980,410,860,300,PURP)
d.text((1010,440),'Диаграммы Chart.js',font=F(22,True),fill=PURP)
bullets(d,1010,490,['Doughnut: структура блоков (117/71/34/9/9)','Radar: покрытие компетенций УК 5 · ОПК 4 · ПК 4','Stacked Bar: 1080 ч в каждом семестре'],19)
im.save(f'{OUT}/slide_09_analytics_export.png')

# S10 ux
im,d=new_slide(10); head(d,'Пользовательский интерфейс','Адаптивный дизайн, единая палитра, готовые модули')
tok=[('#0f172a','header'),('#1e293b','sidebar'),('#f8fafc','page'),('#2563eb','primary'),('#15803d','ok'),('#b91c1c','err'),('#7e22ce','anok'),('#b45309','warn')]
x=80
for c,nm in tok:
    d.rounded_rectangle([x,210,x+150,290],10,fill=c)
    d.text((x+10,300),nm,font=F(15),fill=MUT); x+=180
card(d,80,380,870,330,SKY)
d.text((110,410),'Шаблон дизайна',font=F(22,True),fill=SKY)
bullets(d,110,460,['Header 60px sticky + Sidebar 240px + Main 1200px + Footer','Типографика: 24/18/14/12px, системный стек шрифтов','Адаптив ≤ 768px: сайдбар 70px, overflow-x таблиц','14 пунктов меню, подсветка активного раздела'],19)
card(d,980,380,860,330,GREEN)
d.text((1010,410),'Готовые модули (ЛР № 6)',font=F(22,True),fill=GREEN)
bullets(d,1010,460,['DataTables: живой поиск и пагинация плана','SheetJS / jsPDF: экспорт XLSX и PDF','FullCalendar: график процедур АНОК','Diff2Html: сравнение версий УП'],19)
im.save(f'{OUT}/slide_10_interactive_ux.png')

# S11 security
im,d=new_slide(11); head(d,'Тестирование и безопасность','Защита данных и протоколирование действий')
card(d,80,200,870,420,GREEN)
d.text((110,230),'Безопасность',font=F(22,True),fill=GREEN)
bullets(d,110,280,['Prepared Statements — исключены SQL-инъекции','htmlspecialchars / html.escape — защита от XSS','FOREIGN KEYS — ссылочная целостность (0 нарушений)','PRAGMA foreign_key_check — контроль при каждом старте'],19)
card(d,980,200,860,420,ACC)
d.text((1010,230),'Журнал аудита',font=F(22,True),fill=SKY)
bullets(d,1010,280,['7 записей: время, пользователь, роль, действие, статус, IP','Живой поиск по журналу (client-side)','Фиксация валидаций, виз ЭЦП и служебных записок','Статусные бейджи: УСПЕШНО / ОШИБКА / ОБНОВЛЕНО'],19)
d.text((80,660),'Все 15 страниц и 3 REST-эндпоинта отвечают HTTP 200; оффлайн-деградация CDN-модулей без потери данных',font=F(19),fill=MUT)
im.save(f'{OUT}/slide_11_testing_security.png')

# S12 conclusion
im,d=new_slide(12); head(d,'Заключение и результаты','Портал Центра АНОК готов к демонстрации и защите')
bullets(d,80,200,['Полный цикл ЛР № 1–7: требования → проектирование → дизайн → разделы → инфоблоки → модули → защита',
 'Портал: 15 разделов + REST API, 13 таблиц БД с FOREIGN KEYS, 51 дисциплина (240 з.е., баланс 30/1080)',
 'Экспертиза ФГОС 3++: 5/5 критериев соответствуют; маршрут ЭЦП 4 этапа с верификацией SHA-256',
 '9 готовых модулей: Chart.js, FullCalendar, DataTables, SheetJS, jsPDF, CryptoJS, SweetAlert2, Toastify, Diff2Html',
 'Комплект документов: 7 отчетов (MD/DOCX/PDF), пояснительная записка, презентация 12 слайдов'],22,step=64)
card(d,80,640,1760,220,ACC)
d.text((110,680),'Итог: требования варианта № 15 выполнены полностью',font=F(26,True),fill=SKY)
d.text((110,740),'Москва, 2026 · студент группы П-41 Соловьёв А.С.',font=F(20),fill=MUT)
im.save(f'{OUT}/slide_12_conclusion_impact.png')
print('slides done')
