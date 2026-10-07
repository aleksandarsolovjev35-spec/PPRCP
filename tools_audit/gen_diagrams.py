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
#
# Layout: 5 subsystem bands.  Each band stacks its use cases in one central
# column inside the system boundary; the actor chips live in the outer
# gutters next to the rows they actually connect to.  Every association is
# a single straight segment fanned out from one anchor point on the chip to
# its own entry slot on the ellipse border, which makes crossings
# geometrically impossible for this data set -- and the collision checker
# below asserts it (crossings, line-vs-shape touches, label overlaps) and
# refuses to save if anything is off.
import math, textwrap

ACT={ # key: (name, code, color, tint, outline)
 'HR':('Руководитель выпускающего подразделения','HEAD_RELEASING',BLUE,'#eff6ff','#bfdbfe'),
 'HI':('Руководитель реализующего подразделения','HEAD_IMPLEMENTING',BLUE,'#eff6ff','#bfdbfe'),
 'V' :('Преподаватель / Студент','VIEWER',BLUE,'#eff6ff','#bfdbfe'),
 'CS':('Секретарь Учёного совета','COUNCIL_SEC','#0f766e','#f0fdfa','#99f6e4'),
 'VR':('Проректор по учебной работе','VICE_RECTOR','#0f766e','#f0fdfa','#99f6e4'),
 'RE':('Ректор университета','RECTOR','#0f766e','#f0fdfa','#99f6e4'),
 'E' :('Эксперт Центра АНОК','EXPERT_ANOK','#7c3aed','#f5f3ff','#ddd6fe'),
 'HA':('Начальник Центра АНОК','HEAD_ANOK','#7c3aed','#f5f3ff','#ddd6fe'),
 'A' :('Администратор портала','ADMIN','#7c3aed','#f5f3ff','#ddd6fe'),
}
# band: (title, [ (use case caption, [ (actor, side, association label), ... ]), ... ])
BANDS=[
 ('БЛОК 1 · УЧЕБНЫЕ ПЛАНЫ: ПРОСМОТР И АНАЛИЗ',[
   ('UC-1 Просмотр реестра УП',[('V','L','просмотр'),('HR','L','просмотр')]),
   ('UC-2 Просмотр УП по семестрам (1–8)',[('V','L','навигация по семестрам')]),
   ('UC-3 Анализ нагрузки и СРС',[('V','L','оценка нагрузки'),('E','R','экспертиза нагрузки')]),
 ]),
 ('БЛОК 2 · ЭКСПЕРТИЗА НА СООТВЕТСТВИЕ ФГОС ВО 3++',[
   ('UC-4 Автоматическая валидация УП',[('E','R','запуск валидации'),('HA','L','проверка итогов')]),
   ('UC-5 Контроль лимита экзаменов (≤ 5)',[('E','R','контроль лимита')]),
   ('UC-6 Протокол замечаний',[('E','R','фиксация замечаний'),('HA','L','утверждение протокола')]),
 ]),
 ('БЛОК 3 · СОГЛАСОВАНИЕ И ПОДПИСАНИЕ ЭЦП',[
   ('UC-7 Наложение визы ЭЦП',[('HR','L','виза кафедры'),('HA','R','виза АНОК'),('VR','R','согласование'),('RE','R','виза ректора')]),
   ('UC-8 Просмотр цепочки подписания и SHA-256',[('V','L','просмотр статуса'),('HR','L','контроль подписания')]),
   ('UC-9 Утверждение протокола Учёного совета',[('CS','L','регистрация протокола'),('RE','R','утверждение')]),
 ]),
 ('БЛОК 4 · СЛУЖЕБНЫЕ ЗАПИСКИ (КОРРЕКТИРОВКА УП)',[
   ('UC-10 Создание СЗ на изменение УП',[('HR','L','создание СЗ')]),
   ('UC-11 Сравнение версий «Было → Стало»',[('HR','L','анализ диффа'),('HI','L','сверка часов')]),
   ('UC-12 Согласование обеспечивающей кафедрой',[('HI','L','согласование')]),
   ('UC-13 Применение правок в УП',[('E','R','применение правок')]),
 ]),
 ('БЛОК 5 · СПРАВОЧНИКИ И АДМИНИСТРИРОВАНИЕ',[
   ('UC-14 Матрица компетенций (УК/ОПК/ПК)',[('V','L','просмотр матрицы')]),
   ('UC-15 Справочник подразделений и контактов',[('V','L','поиск контактов'),('A','R','ведение справочника')]),
   ('UC-16 Лента регламентов и объявлений',[('V','L','чтение ленты'),('HA','L','публикация')]),
   ('UC-17 Журнал аудита действий',[('A','R','мониторинг')]),
 ]),
]

def _uc_seg_int(p1,p2,p3,p4,eps=0.0):
    def o(a,b,c):
        v=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        return 0 if abs(v)<=eps else (1 if v>0 else -1)
    o1,o2,o3,o4=o(p1,p2,p3),o(p1,p2,p4),o(p3,p4,p1),o(p3,p4,p2)
    return o1!=o2 and o3!=o4

def _uc_trim(p,q,by):
    dx,dy=q[0]-p[0],q[1]-p[1]; L=math.hypot(dx,dy) or 1
    ux,uy=dx/L,dy/L
    return (p[0]+ux*by,p[1]+uy*by),(q[0]-ux*by,q[1]-uy*by)

def _uc_rect_seg(r,p,q):
    (x0,y0,x1,y1)=r
    if x0<=p[0]<=x1 and y0<=p[1]<=y1: return True
    if x0<=q[0]<=x1 and y0<=q[1]<=y1: return True
    e=[((x0,y0),(x1,y0)),((x1,y0),(x1,y1)),((x1,y1),(x0,y1)),((x0,y1),(x0,y0))]
    return any(_uc_seg_int(p,q,a,b) for a,b in e)

def _uc_rect_rect(a,b,pad=0):
    return not (a[2]+pad<=b[0] or b[2]+pad<=a[0] or a[3]+pad<=b[1] or b[3]+pad<=a[1])

def _uc_seg_ellipse_hit(s0,s1,c,rx,ry,margin=0.02):
    p=((s0[0]-c[0])/rx,(s0[1]-c[1])/ry); q=((s1[0]-c[0])/rx,(s1[1]-c[1])/ry)
    dx,dy=q[0]-p[0],q[1]-p[1]
    L2=dx*dx+dy*dy
    t=0.0 if L2==0 else max(0.0,min(1.0,-(p[0]*dx+p[1]*dy)/L2))
    cx,cy=p[0]+t*dx,p[1]+t*dy
    return math.hypot(cx,cy)<1-margin

def _uc_rect_ellipse_hit(r,c,rx,ry,pad=1.01):
    x0,y0,x1,y1=[(v-c[i%2])/([rx,ry,rx,ry][i]) for i,v in enumerate(r)]
    cx=max(x0,min(0,x1)); cy=max(y0,min(0,y1))
    return math.hypot(cx,cy)<pad

def use_case():
    W=1960; MX=60
    CHIP_W=420; CHIP_X={'L':(MX,MX+CHIP_W),'R':(W-MX-CHIP_W,W-MX)}
    ANCH_X={'L':MX+CHIP_W,'R':W-MX-CHIP_W}
    ECX=980; RX=170; RY=34; ROW=100; HDR=44; PADB=24
    BAND_X0=740; BAND_X1=1220
    BND_X0=700; BND_X1=1260
    TOP=104; GAP=30
    LINEC='#64748b'

    # ---- layout: band boxes, use-case rows, actor chips ----
    bands=[]; y=TOP
    for btitle,rows in BANDS:
        n=len(rows)
        bh=HDR+n*ROW+PADB
        band={'title':btitle,'top':y,'bot':y+bh,'rows':[],'cy':{}}
        for i,(cap,edges) in enumerate(rows):
            cyy=y+HDR+ROW//2+i*ROW
            band['cy'][i]=cyy
            band['rows'].append({'cap':cap,'edges':list(edges),'cx':ECX,'cy':cyy,'idx':i})
        for side in ('L','R'):
            per={}
            for r in band['rows']:
                for (a,s,lab) in r['edges']:
                    if s==side: per.setdefault(a,[]).append(r['cy'])
            items=sorted(per.items(),key=lambda kv:sum(kv[1])/len(kv[1]))
            ys=[sum(v)/len(v) for _,v in items]
            lo,hi=y+HDR//2+18,y+bh-PADB//2-18
            for i in range(len(ys)):
                ys[i]=max(min(ys[i],hi),lo)
                if i>0 and ys[i]-ys[i-1]<96: ys[i]=ys[i-1]+96
            for k in range(len(ys)-2,-1,-1):
                if ys[k+1]-ys[k]<96: ys[k]=ys[k+1]-96
            band['chips_'+side]=[(a,ys[i]) for i,(a,_) in enumerate(items)]
        bands.append(band)
        y+=bh+GAP
    BND_BOT=y-GAP+20
    Hh=BND_BOT+86

    d_=ImageDraw.Draw(Image.new('RGB',(10,10)))
    for band in bands:
        for side in ('L','R'):
            x0,x1=CHIP_X[side]
            for j,(a,cyy) in enumerate(band['chips_'+side]):
                name=ACT[a][0]; code=ACT[a][1]
                lines=textwrap.wrap(name,40)
                h=10+len(lines)*19+15
                band['chips_'+side][j]=(a,cyy,(x0,cyy-h/2,x1,cyy+h/2),lines,code)

    # ---- anchors, entry slots ----
    anchors={}; ellipses=[]; chiprects=[]; headrects=[]
    for bi,band in enumerate(bands):
        hw=max(d_.textlength(band['title'],font=F(12,True))+36,240)
        headrects.append((ECX-hw/2,band['top']+6,ECX+hw/2,band['top']+32))
        for r in band['rows']:
            ellipses.append((r['cx'],r['cy'],r['idx'],bi))
        for side in ('L','R'):
            for (a,cyy,rect,lines,code) in band['chips_'+side]:
                chiprects.append(rect)
                anchors[(bi,a,side)]=(ANCH_X[side],cyy)
        for r in band['rows']:
            for side in ('L','R'):
                es=[(a,lab) for (a,s,lab) in r['edges'] if s==side]
                es.sort(key=lambda al: anchors[(bi,al[0],side)][1])
                m=len(es)
                sp=min(22,(2*(RY-8))/max(m-1,1)) if m>1 else 0
                for j,(a,lab) in enumerate(es):
                    ey=r['cy']+(j-(m-1)/2)*sp
                    ox=math.sqrt(max(0.0,1-((ey-r['cy'])/RY)**2))
                    ex=r['cx']-RX*ox if side=='L' else r['cx']+RX*ox
                    r.setdefault('entry',{})[a]=(ex,ey,side)
    segs=[]
    for bi,band in enumerate(bands):
        for r in band['rows']:
            for (a,s,lab) in r['edges']:
                p=anchors[(bi,a,s)]; q=r['entry'][a]
                segs.append((p,q[:2],bi,s,r['idx'],a,lab,None))

    # ---- collision checker: no crossings, no touches, labels in free space ----
    problems=[]
    T=[_uc_trim(p,q,12) for (p,q,bi,s,ri,a,lab,_x) in segs]
    for i in range(len(segs)):
        for j in range(i+1,len(segs)):
            (p1,q1),(p2,q2)=T[i],T[j]
            if _uc_seg_int(p1,q1,p2,q2,eps=.5): problems.append(('X-seg',i,j))
    for i,(p,q,bi,s,ri,a,lab,_x) in enumerate(segs):
        p2,q2=T[i]
        for (ex,ey,ei,ej) in ellipses:
            if ej==bi and ei==ri: continue
            if _uc_seg_ellipse_hit(p2,q2,(ex,ey),RX,RY,margin=-0.01): problems.append(('seg-ell',i,(ex,ey,ei,ej)))
        for k,rect in enumerate(chiprects):
            if _uc_rect_seg(rect,p2,q2): problems.append(('seg-chip',i,k))
        for hr in headrects:
            if _uc_rect_seg(hr,p2,q2): problems.append(('seg-head',i,hr))
    labrects=[]
    for i,(p,q,bi,s,ri,a,lab,_x) in enumerate(segs):
        band=bands[bi]
        w=d_.textlength(lab,font=F(11))+14; h=24
        lo,hi=((MX+6,BND_X0-6) if s=='L' else (BND_X1+6,W-MX-6))
        best=None; mx,my=p
        for t in (0.5,0.42,0.58,0.34,0.66,0.26,0.74):
            mx,my=p[0]+(q[0]-p[0])*t,p[1]+(q[1]-p[1])*t
            dx,dy=q[0]-p[0],q[1]-p[1]; L=math.hypot(dx,dy) or 1
            nx,ny=-dy/L,dx/L
            for off in (0,22,-22,40,-40,60,-60,84,-84):
                cx2,cy2=mx+nx*off,my+ny*off
                cx2=min(max(cx2,lo+w/2),hi-w/2)
                r=(cx2-w/2,cy2-h/2,cx2+w/2,cy2+h/2)
                if r[1]<band['top']+4 or r[3]>band['bot']-4: continue
                ok=True
                for (ex2,ey2,ei,ej) in ellipses:
                    if _uc_rect_ellipse_hit(r,(ex2,ey2),RX,RY,pad=1.06): ok=False;break
                if ok:
                    for rect in chiprects+headrects:
                        if _uc_rect_rect(r,rect,6): ok=False;break
                if ok:
                    for rr in labrects:
                        if _uc_rect_rect(r,rr,4): ok=False;break
                if ok:
                    for j,(t3,t4) in enumerate(T):
                        if j==i: continue
                        if _uc_rect_seg(r,t3,t4): ok=False;break
                if ok: best=r;break
            if best: break
        if not best:
            best=(mx-w/2,my-12,mx+w/2,my+12); problems.append(('label',i,lab))
        labrects.append(best)
        segs[i]=(p,q,bi,s,ri,a,lab,best)
    if problems:
        raise RuntimeError(f'use case layout problems: {problems[:12]}')

    # ---- render ----
    im=Image.new('RGB',(W,Hh),BG); d=ImageDraw.Draw(im)
    tx(d,MX,26,'Диаграмма вариантов использования — портал Центра АНОК',22,True)
    tx(d,MX,60,'9 акторов · 17 прецедентов · 5 подсистем — каждая ассоциация подписана действием роли',13,False,MUT)
    d.rounded_rectangle([BND_X0,TOP-30,BND_X1,BND_BOT],14,outline=BLUE,width=2)
    cap='ГРАНИЦА СИСТЕМЫ: КОРПОРАТИВНЫЙ ПОРТАЛ УНИВЕРСИТЕТА (МОДУЛЬ АНОК)'
    d.text(((BND_X0+BND_X1)/2-d.textlength(cap,font=F(12,True))/2,TOP-24),cap,font=F(12,True),fill=BLUE)
    for band in bands:
        d.rounded_rectangle([BAND_X0,band['top'],BAND_X1,band['bot']],10,outline='#cbd5e1',width=1)
        hw=max(d.textlength(band['title'],font=F(12,True))+36,240)
        d.rounded_rectangle([ECX-hw/2,band['top']+6,ECX+hw/2,band['top']+32],6,fill='#e2e8f0')
        d.text((ECX-d.textlength(band['title'],font=F(12,True))/2,band['top']+11),band['title'],font=F(12,True),fill='#334155')
    for (p,q,bi,s,ri,a,lab,lr) in segs:
        d.line([p,q],fill=LINEC,width=2)
        d.ellipse([q[0]-4,q[1]-4,q[0]+4,q[1]+4],fill=ACT[a][2])
    for band in bands:
        for r in band['rows']:
            d.ellipse([r['cx']-RX,r['cy']-RY,r['cx']+RX,r['cy']+RY],fill='#ffffff',outline=BLUE,width=2)
            d.text((r['cx']-d.textlength(r['cap'],font=F(12,True))/2,r['cy']-8),r['cap'],font=F(12,True),fill=INK)
    for band in bands:
        for side in ('L','R'):
            for (a,cyy,rect,lines,code) in band['chips_'+side]:
                name,code,color,tint,ol=ACT[a]
                d.rounded_rectangle(rect,10,fill=tint,outline=ol,width=2)
                x0,y0,x1,y1=rect
                for k,ln in enumerate(lines):
                    tx(d,x0+16,y0+9+k*19,ln,12,k==0)
                tx(d,x0+16,y1-22,code,10,False,color)
                dotx=rect[2] if side=='L' else rect[0]
                d.ellipse([dotx-5,cyy-5,dotx+5,cyy+5],fill=color)
    for (p,q,bi,s,ri,a,lab,lr) in segs:
        x0,y0,x1,y1=lr
        d.rounded_rectangle(lr,7,fill='#ffffff',outline=BORDER,width=1)
        d.text(((x0+x1)/2-d.textlength(lab,font=F(11))/2,(y0+y1)/2-7),lab,font=F(11),fill='#334155')
    ly=Hh-52
    tx(d,MX,ly,'Обозначения:',12,True,MUT)
    d.line([(MX+118,ly+8),(MX+168,ly+8)],fill=LINEC,width=2)
    tx(d,MX+176,ly,'ассоциация «актор → прецедент», подпись — действие роли',12,False,MUT)
    for i,(nm,col) in enumerate([('роль университета',BLUE),('роль Центра АНОК','#7c3aed'),('руководство университета','#0f766e')]):
        d.ellipse([MX+i*240+10,ly+28,MX+i*240+22,ly+40],fill=col)
        tx(d,MX+i*240+28,ly+26,nm,12,False,MUT)
    tx(d,W-MX-360,ly+26,'Повтор акторов в блоках — для читаемости',11,False,MUT)
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
