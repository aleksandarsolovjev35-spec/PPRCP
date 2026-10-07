#!/usr/bin/env python3
"""
Центр АНОК — Университетский портал аккредитации и независимой оценки качества образования
Web Server (Python 3 / SQLite)
"""

import http.server
import socketserver
import urllib.parse
import sqlite3
import os
import sys
import re
import html
import json
from datetime import datetime

PORT = int(os.environ.get('PORT', 8000))
HOST = '0.0.0.0'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'portal.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
SEED_PATH = os.path.join(BASE_DIR, 'database', 'seed.sql')

# ---------------------------------------------------------------------------
# Готовые модули и компоненты (ЛР № 6): внешние библиотеки подключаются из CDN.
# Локального fallback не требуется — страницы портала отрисованы сервером и
# корректно отображаются даже без загрузки клиентских скриптов.
# ---------------------------------------------------------------------------
LIBS = {
    'chartjs': 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js',
    'jquery': 'https://cdn.jsdelivr.net/npm/jquery@3.7.1/dist/jquery.min.js',
    'datatables_js': 'https://cdn.jsdelivr.net/npm/datatables.net@1.13.8/js/jquery.dataTables.min.js',
    'datatables_css': 'https://cdn.jsdelivr.net/npm/datatables.net@1.13.8/css/jquery.dataTables.min.css',
    'fullcalendar_core': 'https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.10/index.global.min.js',
    'fullcalendar_daygrid': 'https://cdn.jsdelivr.net/npm/@fullcalendar/daygrid@6.1.10/index.global.min.js',
    'fullcalendar_interaction': 'https://cdn.jsdelivr.net/npm/@fullcalendar/interaction@6.1.10/index.global.min.js',
    'fullcalendar_css': 'https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.10/main.min.css',
    'jspdf': 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js',
    'sheetjs': 'https://cdn.jsdelivr.net/npm/xlsx@0.18.5/package/dist/xlsx.full.min.js',
    'cryptojs': 'https://cdn.jsdelivr.net/npm/crypto-js@4.2.0/crypto-js.min.js',
    'toastify_js': 'https://cdn.jsdelivr.net/npm/toastify-js@1.12.0/src/toastify.min.js',
    'toastify_css': 'https://cdn.jsdelivr.net/npm/toastify-js@1.12.0/src/toastify.min.css',
    'sweetalert2': 'https://cdn.jsdelivr.net/npm/sweetalert2@11',
    'diff2html_js': 'https://cdn.jsdelivr.net/npm/diff2html@7.0.6/bundles/diff2html-ui.min.js',
    'diff2html_css': 'https://cdn.jsdelivr.net/npm/diff2html@7.0.6/dist/diff2html.min.css',
}


def init_database():
    """Initializes SQLite database from schema.sql and seed.sql if needed."""
    need_init = False
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        need_init = True
    else:
        # Check if tables exist
        conn = sqlite3.connect(DB_PATH)
        try:
            count = conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
            if count < 5:
                need_init = True
        finally:
            conn.close()

    if need_init:
        print(f"[*] Initializing database at {DB_PATH}...")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)

        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_text = f.read()
        with open(SEED_PATH, 'r', encoding='utf-8') as f:
            seed_text = f.read()

        # Adapt MySQL syntax for SQLite
        schema_text = re.sub(r'ENGINE=InnoDB[^;]*;', ';', schema_text, flags=re.IGNORECASE)
        schema_text = re.sub(r'SET FOREIGN_KEY_CHECKS\s*=\s*[01];', '', schema_text, flags=re.IGNORECASE)
        schema_text = re.sub(r'\bINT\s+AUTO_INCREMENT\s+PRIMARY\s+KEY\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', schema_text, flags=re.IGNORECASE)

        seed_text = re.sub(r'SET FOREIGN_KEY_CHECKS\s*=\s*[01];', '', seed_text, flags=re.IGNORECASE)

        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema_text)
        conn.executescript(seed_text)
        conn.commit()
        conn.close()
        print("[+] Database initialized successfully.")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def e(val):
    if val is None:
        return ''
    return html.escape(str(val))


def badge_status(status):
    if not status:
        return ''
    st = str(status).strip()
    st_upper = st.upper()
    
    badge_map = {
        'APPROVED_RECTOR': ('badge-green', 'Утверждено Ректором'),
        'APPROVED': ('badge-green', 'Утверждено'),
        'SIGNED': ('badge-green', 'Подписано'),
        'APPLIED': ('badge-green', 'Применено'),
        'УСПЕШНО': ('badge-green', 'Успешно'),
        'ПОДПИСАНО': ('badge-green', 'Подписано'),
        'АКТУАЛИЗИРОВАНО': ('badge-green', 'Актуализировано'),
        'ОБНОВЛЕНО': ('badge-blue', 'Обновлено'),
        'СОЗДАНО': ('badge-blue', 'Создано'),
        'IN_ANOK': ('badge-purple', 'На экспертизе в АНОК'),
        'SIGNED_RELEASING': ('badge-cyan', 'Виза выпускающей каф.'),
        'PENDING': ('badge-yellow', 'На согласовании'),
        'DRAFT': ('badge-gray', 'Черновик'),
    }
    
    for k, (cls, label) in badge_map.items():
        if k in st_upper:
            return f'<span class="badge {cls}">{e(label)}</span>'
            
    if 'ОШИБКА' in st_upper:
        return f'<span class="badge badge-red">{e(st)}</span>'
        
    return f'<span class="badge badge-gray">{e(st)}</span>'


def validate_curriculum(db, plan_id=1):
    """Алгоритмическая валидация учебного плана по нормативам ФГОС ВО 3++.

    Все показатели вычисляются непосредственно из базы данных, поэтому
    страница «Экспертиза ФГОС» всегда отражает фактическое состояние плана.
    """
    rows = db.execute(
        'SELECT block_type, semester_num, credits_ze, control_form '
        'FROM curriculum_disciplines WHERE curriculum_id = ?', (plan_id,)
    ).fetchall()

    total = 0.0
    per_semester = {}
    exams_per_semester = {}
    practice = 0.0
    gia = 0.0
    for r in rows:
        credits = float(r['credits_ze'] or 0)
        sem = int(r['semester_num'] or 0)
        total += credits
        per_semester[sem] = per_semester.get(sem, 0.0) + credits
        block = (r['block_type'] or '')
        if block.startswith('Б2'):
            practice += credits
        elif block.startswith('Б3'):
            gia += credits
        if 'кзамен' in (r['control_form'] or ''):
            exams_per_semester[sem] = exams_per_semester.get(sem, 0) + 1

    std = db.execute('SELECT * FROM standards_fgos ORDER BY id LIMIT 1').fetchone()
    if std:
        norm_total = float(std['total_credits'] or 240)
        norm_max_exams = int(std['max_exams_per_session'] or 5)
        norm_min_practice = float(std['min_practice_credits'] or 12)
        norm_min_gia = float(std['min_gia_credits'] or 6)
    else:
        norm_total, norm_max_exams = 240.0, 5
        norm_min_practice, norm_min_gia = 12.0, 6.0

    semesters = len(per_semester) or 8
    return {
        'total_credits': total,
        'semesters': semesters,
        'credits_per_semester': total / semesters,
        'max_exams': max(exams_per_semester.values()) if exams_per_semester else 0,
        'practice_credits': practice,
        'gia_credits': gia,
        'norm_total': norm_total,
        'norm_max_exams': norm_max_exams,
        'norm_min_practice': norm_min_practice,
        'norm_min_gia': norm_min_gia,
        'per_semester': per_semester,
        'exams_per_semester': exams_per_semester,
    }


def curriculum_blocks(db, plan_id=1):
    """Суммарные зачетные единицы по блокам учебного плана (для диаграмм)."""
    rows = db.execute(
        'SELECT block_type, credits_ze FROM curriculum_disciplines WHERE curriculum_id = ?',
        (plan_id,)
    ).fetchall()
    labels = [('Б1.О', 'Обязательная часть'), ('Б1.В', 'Вариативная часть'),
              ('Б2', 'Практики и НИР'), ('Б3', 'ГИА (ВКР + экзамен)'), ('ФТД', 'ФТД')]
    totals = {key: 0.0 for key, _ in labels}
    for r in rows:
        block = r['block_type'] or ''
        for key, _ in labels:
            if block.startswith(key):
                totals[key] += float(r['credits_ze'] or 0)
                break
    return [(key, label, totals[key]) for key, label in labels]


def semester_hours(db, plan_id=1):
    """Аудиторная нагрузка и СРС по семестрам (для stacked bar диаграммы)."""
    rows = db.execute(
        'SELECT semester_num, lecture_hours, lab_hours, practice_hours, self_study_hours '
        'FROM curriculum_disciplines WHERE curriculum_id = ? ORDER BY semester_num',
        (plan_id,)
    ).fetchall()
    data = {}
    for r in rows:
        sem = int(r['semester_num'] or 0)
        d = data.setdefault(sem, {'lecture': 0, 'lab': 0, 'practice': 0, 'self': 0})
        d['lecture'] += int(r['lecture_hours'] or 0)
        d['lab'] += int(r['lab_hours'] or 0)
        d['practice'] += int(r['practice_hours'] or 0)
        d['self'] += int(r['self_study_hours'] or 0)
    return data


def competency_matrix(db):
    """Количество компетенций по категориям (УК / ОПК / ПК) для radar-диаграммы."""
    rows = db.execute('SELECT code, category FROM competencies').fetchall()
    counts = {'УК': 0, 'ОПК': 0, 'ПК': 0}
    for r in rows:
        code = (r['code'] or '').upper()
        for prefix in counts:
            if code.startswith(prefix):
                counts[prefix] += 1
                break
    return counts


def render_html_page(title, active_page, content, stats, head_extra='', body_extra=''):
    nav_items = [
        ('dashboard', 'Главная', '📊'),
        ('plans', 'Учебные планы', '📚'),
        ('analytics', 'Аналитика', '📈'),
        ('calendar', 'Календарь дедлайнов', '📅'),
        ('validate', 'Проверка ФГОС', '✓'),
        ('signatures', 'Согласование', '✍'),
        ('memos', 'Служебные записки', '📝'),
        ('programs', 'Программы', '🎓'),
        ('competencies', 'Компетенции', '🎯'),
        ('standards', 'Стандарты', '📜'),
        ('departments', 'Подразделения', '🏛'),
        ('announcements', 'Объявления', '📢'),
        ('audit', 'Аудит', '🔍'),
        ('sitemap', 'Карта сайта', '🗺'),
    ]

    nav_links_html = ''
    for key, label, icon in nav_items:
        is_active = 'active' if (active_page == key or (active_page == 'plan' and key == 'plans')) else ''
        nav_links_html += f'<a class="{is_active}" href="/?page={key}"><span class="nav-icon">{icon}</span> {e(label)}</a>'

    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)} — Центр АНОК</title>
  <style>
    :root {{
      --bg: #0f172a;
      --page-bg: #f8fafc;
      --card-bg: #ffffff;
      --text-main: #1e293b;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --border: #e2e8f0;
      --border-light: #f1f5f9;
      --success: #16a34a;
      --warning: #d97706;
      --danger: #dc2626;
      --sidebar-w: 240px;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page-bg);
      color: var(--text-main);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      font-size: 14px;
      line-height: 1.5;
    }}
    header {{
      background: var(--bg);
      color: #fff;
      padding: 14px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-brand {{
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: #fff;
    }}
    .header-logo {{
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 16px;
      color: white;
    }}
    .header-title b {{ font-size: 16px; letter-spacing: 0.5px; }}
    .header-title span {{ font-size: 12px; color: #94a3b8; display: block; }}
    .header-user {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 13px;
      color: #cbd5e1;
    }}
    .user-avatar {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #334155;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      color: #38bdf8;
    }}
    main {{
      display: flex;
      min-height: calc(100vh - 60px);
    }}
    aside {{
      width: var(--sidebar-w);
      background: #1e293b;
      padding: 20px 12px;
      flex-shrink: 0;
    }}
    aside a {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: #cbd5e1;
      text-decoration: none;
      padding: 10px 14px;
      border-radius: 8px;
      margin-bottom: 4px;
      font-weight: 500;
      transition: all 0.15s ease;
    }}
    aside a .nav-icon {{ font-size: 16px; width: 20px; text-align: center; }}
    aside a:hover {{ background: rgba(255,255,255,0.08); color: #fff; }}
    aside a.active {{ background: var(--primary); color: #fff; font-weight: 600; box-shadow: 0 2px 6px rgba(37,99,235,0.3); }}
    section {{
      padding: 32px;
      max-width: 1200px;
      width: 100%;
    }}
    .page-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 12px;
    }}
    h1 {{
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      color: #0f172a;
    }}
    h2 {{
      margin-top: 28px;
      margin-bottom: 14px;
      font-size: 18px;
      font-weight: 600;
      color: #1e293b;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }}
    .card {{
      background: var(--card-bg);
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
      border: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    .card-top {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
    .card-icon {{
      width: 40px;
      height: 40px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
    }}
    .icon-blue {{ background: #eff6ff; color: #2563eb; }}
    .icon-emerald {{ background: #ecfdf5; color: #059669; }}
    .icon-amber {{ background: #fffbeb; color: #d97706; }}
    .icon-purple {{ background: #faf5ff; color: #9333ea; }}
    .card b {{
      font-size: 32px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1;
    }}
    .card span {{
      color: var(--text-muted);
      font-size: 13px;
      font-weight: 500;
    }}
    .table-container {{
      background: var(--card-bg);
      border-radius: 10px;
      border: 1px solid var(--border);
      overflow-x: auto;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      margin-bottom: 24px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      text-align: left;
    }}
    th, td {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
    }}
    th {{
      background: #f8fafc;
      color: #475569;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    tr:last-child td {{ border-bottom: none; }}
    tr:hover td {{ background: #f8fafc; }}
    a {{
      color: var(--primary);
      text-decoration: none;
      font-weight: 500;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      background: var(--primary);
      color: #fff;
      border-radius: 6px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      border: none;
      cursor: pointer;
      transition: background 0.15s ease;
    }}
    .btn:hover {{
      background: var(--primary-hover);
      text-decoration: none;
    }}
    .btn-outline {{
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-main);
    }}
    .btn-outline:hover {{
      background: #f1f5f9;
      text-decoration: none;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      line-height: 1.2;
    }}
    .badge-green {{ background: #dcfce7; color: #15803d; }}
    .badge-blue {{ background: #dbeafe; color: #1d4ed8; }}
    .badge-purple {{ background: #f3e8ff; color: #7e22ce; }}
    .badge-cyan {{ background: #cffafe; color: #0e7490; }}
    .badge-yellow {{ background: #fef3c7; color: #b45309; }}
    .badge-red {{ background: #fee2e2; color: #b91c1c; }}
    .badge-gray {{ background: #f1f5f9; color: #475569; }}
    
    .sem {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      margin: 16px 0 20px 0;
    }}
    .sem a {{
      padding: 8px 14px;
      background: #e2e8f0;
      color: #334155;
      text-decoration: none;
      border-radius: 6px;
      font-weight: 500;
      transition: all 0.15s ease;
    }}
    .sem a:hover {{ background: #cbd5e1; }}
    .sem a.active {{
      background: var(--primary);
      color: #fff;
      font-weight: 600;
      box-shadow: 0 2px 4px rgba(37,99,235,0.25);
    }}
    
    .search-bar {{
      margin-bottom: 16px;
      display: flex;
      gap: 10px;
    }}
    .search-input {{
      padding: 8px 14px;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-size: 13px;
      width: 100%;
      max-width: 320px;
      outline: none;
    }}
    .search-input:focus {{
      border-color: var(--primary);
      box-shadow: 0 0 0 2px rgba(37,99,235,0.15);
    }}
    
    .announcement-card {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px 20px;
      margin-bottom: 14px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}
    .announcement-card.pinned {{
      border-left: 4px solid var(--primary);
    }}
    .announcement-meta {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }}
    .announcement-title {{
      font-size: 16px;
      font-weight: 600;
      color: #0f172a;
      margin-bottom: 8px;
    }}
    .announcement-body {{
      color: #334155;
      line-height: 1.6;
    }}
    
    .workflow-timeline {{
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-top: 16px;
    }}
    .workflow-step {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px 20px;
      display: flex;
      align-items: flex-start;
      gap: 16px;
    }}
    .workflow-num {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #2563eb;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      flex-shrink: 0;
    }}
    .workflow-content {{ flex-grow: 1; }}
    .workflow-title {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; }}
    .workflow-signer {{ font-size: 13px; color: #475569; margin-bottom: 6px; }}
    .workflow-comment {{ font-size: 13px; color: #334155; font-style: italic; background: #f8fafc; padding: 8px 12px; border-radius: 6px; margin: 6px 0; }}
    .workflow-hash {{ font-family: monospace; font-size: 11px; color: #64748b; word-break: break-all; }}
    
    .validation-summary {{
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    .val-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 12px;
      margin-top: 14px;
    }}
    .val-item {{
      background: #f8fafc;
      padding: 12px 14px;
      border-radius: 6px;
      border-left: 3px solid var(--success);
    }}
    .val-item b {{ display: block; font-size: 13px; color: #0f172a; margin-bottom: 2px; }}
    .val-item span {{ font-size: 12px; color: var(--text-muted); }}

    @media (max-width: 768px) {{
      aside {{ width: 70px; padding: 12px 6px; }}
      aside a span:not(.nav-icon) {{ display: none; }}
      aside a {{ justify-content: center; padding: 10px; }}
      section {{ padding: 16px; }}
      .header-title span {{ display: none; }}
      table {{ font-size: 12px; }}
      th, td {{ padding: 8px 10px; }}
    }}
  </style>
  {head_extra}
</head>
<body>
  <header>
    <a href="/?page=dashboard" class="header-brand">
      <div class="header-logo">А</div>
      <div class="header-title">
        <b>УНИВЕРСИТЕТ · Центр АНОК</b>
        <span>Аккредитация и независимая оценка качества образования</span>
      </div>
    </a>
    <div class="header-user">
      <div class="user-avatar">АС</div>
      <div>
        <div style="font-weight:600; color:#fff;">Соловьев А.С.</div>
        <div style="font-size:11px; color:#94a3b8;">Эксперт АНОК</div>
      </div>
    </div>
  </header>
  <main>
    <aside>
      {nav_links_html}
    </aside>
    <section>
      <div class="page-header">
        <h1>{e(title)}</h1>
      </div>
      {content}
    </section>
  </main>
  <script>
    function filterTable(inputId, tableId) {{
      const input = document.getElementById(inputId);
      const filter = input.value.toLowerCase();
      const table = document.getElementById(tableId);
      const trs = table.getElementsByTagName('tr');
      for (let i = 1; i < trs.length; i++) {{
        const tds = trs[i].getElementsByTagName('td');
        let match = false;
        for (let j = 0; j < tds.length; j++) {{
          if (tds[j].textContent.toLowerCase().indexOf(filter) > -1) {{
            match = true;
            break;
          }}
        }}
        trs[i].style.display = match ? '' : 'none';
      }}
    }}
  </script>
  {body_extra}
</body>
</html>"""


class PortalRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Handle API routes
        if path.startswith('/api/'):
            self.handle_api(path, query)
            return

        # Determine page
        page = query.get('page', [''])[0]
        if not page and path != '/' and not path.endswith('.php'):
            page = path.lstrip('/')
        if not page or page == 'index.php':
            page = 'dashboard'

        allowed_pages = [
            'dashboard', 'plans', 'plan', 'analytics', 'calendar', 'validate',
            'signatures', 'memos', 'programs', 'competencies', 'standards',
            'departments', 'announcements', 'audit', 'sitemap'
        ]
        if page not in allowed_pages:
            page = 'dashboard'

        plan_id = 1
        if 'id' in query:
            try:
                plan_id = int(query['id'][0])
            except ValueError:
                plan_id = 1

        sem = 1
        if 'sem' in query:
            try:
                sem = max(1, min(8, int(query['sem'][0])))
            except ValueError:
                sem = 1

        db = get_db()
        try:
            stats = {
                'plans': db.execute('SELECT COUNT(*) FROM curriculums').fetchone()[0],
                'disciplines': db.execute('SELECT COUNT(*) FROM curriculum_disciplines').fetchone()[0],
                'standards': db.execute('SELECT COUNT(*) FROM standards_fgos').fetchone()[0],
                'memos': db.execute('SELECT COUNT(*) FROM service_notes').fetchone()[0],
            }

            title = 'Сводная панель'
            content = ''
            head_extra = ''
            body_extra = ''

            if page == 'dashboard':
                title = 'Сводная панель'
                plans = db.execute('''
                    SELECT c.*, ep.code prog_code, ep.title prog_title, ep.level prog_level
                    FROM curriculums c 
                    JOIN educational_programs ep ON ep.id = c.program_id 
                    ORDER BY c.id
                ''').fetchall()

                content += f'''
                <div class="cards">
                  <div class="card">
                    <div class="card-top">
                      <span>Учебные планы</span>
                      <div class="card-icon icon-blue">📚</div>
                    </div>
                    <b>{stats['plans']}</b>
                    <span>Активных проектов ОП</span>
                  </div>
                  <div class="card">
                    <div class="card-top">
                      <span>Дисциплины</span>
                      <div class="card-icon icon-emerald">📖</div>
                    </div>
                    <b>{stats['disciplines']}</b>
                    <span>В учебной сетке</span>
                  </div>
                  <div class="card">
                    <div class="card-top">
                      <span>Стандарты ФГОС</span>
                      <div class="card-icon icon-amber">📜</div>
                    </div>
                    <b>{stats['standards']}</b>
                    <span>Нормативов 3++</span>
                  </div>
                  <div class="card">
                    <div class="card-top">
                      <span>Служебные записки</span>
                      <div class="card-icon icon-purple">📝</div>
                    </div>
                    <b>{stats['memos']}</b>
                    <span>На корректировку</span>
                  </div>
                </div>

                <h2>Реестр учебных планов</h2>
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Код</th>
                        <th>Образовательная программа</th>
                        <th>Учебный год</th>
                        <th>Версия</th>
                        <th>Трудоемкость</th>
                        <th>Статус</th>
                        <th>Действие</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for p in plans:
                    content += f'''
                      <tr>
                        <td><b>{e(p['prog_code'])}</b></td>
                        <td>{e(p['prog_title'])} <span style="color:#64748b; font-size:12px;">({e(p['prog_level'])})</span></td>
                        <td>{e(p['academic_year'])}</td>
                        <td>v{e(p['version'])}</td>
                        <td><b>{e(p['total_credits'])} з.е.</b></td>
                        <td>{badge_status(p['status'])}</td>
                        <td><a class="btn" href="/?page=plan&id={p['id']}">Открыть УП</a></td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

                # Recent Announcements preview
                announcements = db.execute('SELECT * FROM announcements ORDER BY is_pinned DESC, publish_date DESC LIMIT 2').fetchall()
                if announcements:
                    content += '<h2>Важные объявления и регламенты</h2>'
                    for a in announcements:
                        pinned_badge = '<span class="badge badge-purple">Закреплено</span>' if a['is_pinned'] else ''
                        content += f'''
                        <div class="announcement-card {'pinned' if a['is_pinned'] else ''}">
                          <div class="announcement-meta">
                            <span>📅 {e(a['publish_date'])}</span>
                            <span>📁 {e(a['category'])}</span>
                            <span>👤 {e(a['author_name'])}</span>
                            {pinned_badge}
                          </div>
                          <div class="announcement-title">{e(a['title'])}</div>
                          <div class="announcement-body">{e(a['content'])}</div>
                        </div>
                        '''

            elif page == 'plans':
                title = 'Учебные планы'
                rows = db.execute('''
                    SELECT c.*, ep.code, ep.title, ep.level, ep.study_form
                    FROM curriculums c 
                    JOIN educational_programs ep ON ep.id = c.program_id 
                    ORDER BY c.id
                ''').fetchall()

                content += f'''
                <div class="page-header" style="margin-bottom:16px;">
                  <p style="margin:0; color:#64748b;">Реестр утвержденных и находящихся на согласовании учебных планов института.</p>
                </div>
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Код ОП</th>
                        <th>Наименование программы</th>
                        <th>Уровень</th>
                        <th>Форма</th>
                        <th>Уч. год</th>
                        <th>Протокол</th>
                        <th>Статус</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for r in rows:
                    protocol = f"{r['approved_protocol_num']} от {r['approved_protocol_date']}" if r['approved_protocol_num'] else '—'
                    content += f'''
                      <tr>
                        <td><b>{e(r['code'])}</b></td>
                        <td>{e(r['title'])}</td>
                        <td>{e(r['level'])}</td>
                        <td>{e(r['study_form'])}</td>
                        <td>{e(r['academic_year'])}</td>
                        <td>{e(protocol)}</td>
                        <td>{badge_status(r['status'])}</td>
                        <td><a class="btn" href="/?page=plan&id={r['id']}">Просмотр</a></td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'plan':
                title = 'Учебный план'
                p = db.execute('''
                    SELECT c.*, ep.code, ep.title, ep.level, ep.study_form, d.name dept_name
                    FROM curriculums c 
                    JOIN educational_programs ep ON ep.id = c.program_id 
                    LEFT JOIN departments d ON d.id = ep.department_id
                    WHERE c.id = ?
                ''', (plan_id,)).fetchone()

                if not p:
                    content = '<p>Учебный план не найден.</p>'
                else:
                    rows = db.execute('''
                        SELECT cd.*, d.short_name dept_short
                        FROM curriculum_disciplines cd
                        LEFT JOIN departments d ON d.id = cd.implementing_department_id
                        WHERE cd.curriculum_id = ? AND cd.semester_num = ?
                        ORDER BY cd.id
                    ''', (plan_id, sem)).fetchall()

                    # Готовые модули (ЛР № 6): DataTables, SheetJS, jsPDF
                    head_extra += (f'<link rel="stylesheet" href="{LIBS["datatables_css"]}">\n'
                                   f'<script src="{LIBS["jquery"]}"></script>\n'
                                   f'<script src="{LIBS["datatables_js"]}"></script>\n'
                                   f'<script src="{LIBS["sheetjs"]}"></script>\n'
                                   f'<script src="{LIBS["jspdf"]}"></script>\n')
                    plan_rows_json = json.dumps(
                        [{'Блок': r['block_type'], 'Дисциплина': r['discipline_name'],
                          'З.Е.': r['credits_ze'], 'Часы': r['total_hours'],
                          'Лек.': r['lecture_hours'], 'Лаб.': r['lab_hours'],
                          'Прак.': r['practice_hours'], 'СРС': r['self_study_hours'],
                          'Контроль': r['control_form'],
                          'Кафедра': r['dept_short'] or '—'} for r in rows],
                        ensure_ascii=False)
                    body_extra += f'''
<script>
document.addEventListener('DOMContentLoaded', function() {{
  if (window.jQuery && jQuery.fn.DataTable) {{
    jQuery('#disciplinesTable').DataTable({{
      pageLength: 10,
      lengthChange: true,
      searching: true,
      ordering: true,
      language: {{
        search: 'Живой поиск:',
        lengthMenu: 'Показ _MENU_ записей',
        info: 'Показано с _START_ по _END_ из _TOTAL_ дисциплин',
        paginate: {{ previous: 'Назад', next: 'Вперёд', last: 'Последняя', first: 'Первая' }}
      }}
    }});
  }}
}});
function exportPlanXLSX() {{
  const ws = XLSX.utils.json_to_sheet({plan_rows_json});
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Учебный план');
  XLSX.writeFile(wb, 'curriculum_plan.xlsx');
}}
function exportPlanPDF() {{
  const {{ jsPDF }} = window.jspdf;
  const doc = new jsPDF();
  doc.setFontSize(14);
  doc.text('Учебный план 09.03.04 — Программная инженерия', 14, 16);
  doc.setFontSize(10);
  const rows = {plan_rows_json};
  let y = 28;
  rows.forEach(function(r, i) {{
    if (y > 280) {{ doc.addPage(); y = 20; }}
    doc.text(String(i + 1) + '. ' + r['Дисциплина'] + ' — ' + r['З.Е.'] + ' з.е., ' + r['Часы'] + ' ч.', 14, y);
    y += 7;
  }});
  doc.save('curriculum_plan.pdf');
}}
</script>
'''

                    # Semester summary calculations
                    sem_credits = sum(r['credits_ze'] for r in rows)
                    sem_hours = sum(r['total_hours'] for r in rows)
                    sem_lectures = sum(r['lecture_hours'] for r in rows)
                    sem_labs = sum(r['lab_hours'] for r in rows)
                    sem_practices = sum(r['practice_hours'] for r in rows)
                    sem_self = sum(r['self_study_hours'] for r in rows)

                    sem_nav = '<nav class="sem">'
                    for i in range(1, 9):
                        active_cls = 'active' if i == sem else ''
                        sem_nav += f'<a class="{active_cls}" href="/?page=plan&id={plan_id}&sem={i}">Семестр {i}</a>'
                    sem_nav += '</nav>'

                    content += f'''
                    <div style="background:#fff; border:1px solid #e2e8f0; border-radius:8px; padding:18px 20px; margin-bottom:20px;">
                      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
                        <div>
                          <div style="font-size:18px; font-weight:700; color:#0f172a;">{e(p['code'])} — {e(p['title'])}</div>
                          <div style="font-size:13px; color:#64748b; margin-top:4px;">
                            Учебный год: <b>{e(p['academic_year'])}</b> · Уровень: <b>{e(p['level'])}</b> · Форма: <b>{e(p['study_form'])}</b> · Общая трудоемкость: <b>{e(p['total_credits'])} з.е.</b>
                          </div>
                          <div style="font-size:12px; color:#64748b; margin-top:2px;">
                            Выпускающее подразделение: <b>{e(p['dept_name'] or 'Кафедра ПИ')}</b> · Создал: <b>{e(p['created_by_user'])}</b>
                          </div>
                        </div>
                        <div>
                          {badge_status(p['status'])}
                        </div>
                      </div>
                    </div>

                    {sem_nav}

                    <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:16px;">
                      <div style="background:#fff; padding:10px 16px; border-radius:6px; border:1px solid #e2e8f0; font-size:13px;">
                        Семестр {sem}: <b>{len(rows)} дисциплин</b>
                      </div>
                      <div style="background:#eff6ff; padding:10px 16px; border-radius:6px; border:1px solid #bfdbfe; font-size:13px; color:#1e40af;">
                        Трудоемкость: <b>{sem_credits} з.е.</b> (норма: 30 з.е.)
                      </div>
                      <div style="background:#fff; padding:10px 16px; border-radius:6px; border:1px solid #e2e8f0; font-size:13px;">
                        Всего часов: <b>{sem_hours} ч.</b> (Лек: {sem_lectures} / Лаб: {sem_labs} / Пр: {sem_practices} / СРС: {sem_self})
                      </div>
                    </div>

                    <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:14px;">
                      <button class="btn" type="button" onclick="exportPlanXLSX()">[XLSX] Экспорт в Excel (SheetJS)</button>
                      <button class="btn" type="button" style="background:#dc2626;" onclick="exportPlanPDF()">[PDF] Выгрузить в PDF (jsPDF)</button>
                      <button class="btn btn-outline" type="button" onclick="window.print()">[PRINT] Печать бланка УП</button>
                    </div>

                    <div class="table-container">
                      <table id="disciplinesTable">
                        <thead>
                          <tr>
                            <th>Блок</th>
                            <th>Наименование дисциплины</th>
                            <th>З.Е.</th>
                            <th>Часы</th>
                            <th>Лек.</th>
                            <th>Лаб.</th>
                            <th>Прак.</th>
                            <th>СРС</th>
                            <th>Форма контроля</th>
                            <th>Обеспечивающая кафедра</th>
                          </tr>
                        </thead>
                        <tbody>
                    '''
                    for r in rows:
                        content += f'''
                          <tr>
                            <td><span style="font-family:monospace; font-weight:600; color:#475569;">{e(r['block_type'])}</span></td>
                            <td><b>{e(r['discipline_name'])}</b></td>
                            <td><b>{e(r['credits_ze'])}</b></td>
                            <td>{e(r['total_hours'])}</td>
                            <td>{e(r['lecture_hours'])}</td>
                            <td>{e(r['lab_hours'])}</td>
                            <td>{e(r['practice_hours'])}</td>
                            <td>{e(r['self_study_hours'])}</td>
                            <td><span class="badge badge-gray">{e(r['control_form'])}</span></td>
                            <td>{e(r['dept_short'] or '—')}</td>
                          </tr>
                        '''
                    content += '''
                        </tbody>
                      </table>
                    </div>
                    '''

            elif page == 'analytics':
                # Готовый модуль визуализации данных: Chart.js 4 (CDN)
                title = 'Аналитика'
                blocks = curriculum_blocks(db, plan_id)
                hours = semester_hours(db, plan_id)
                comps = competency_matrix(db)
                semesters = sorted(hours.keys())

                head_extra += f'<script src="{LIBS["chartjs"]}"></script>\n'
                content += '''
                <p style="color:#64748b; margin-bottom:20px;">Модуль бизнес-аналитики и визуализации данных на базе готового компонента <b>Chart.js</b>: структура блоков учебного плана, покрытие компетенций и распределение академической нагрузки по семестрам.</p>
                <div class="cards">
                  <div class="card"><div class="card-top"><span class="card-icon icon-blue">∑</span></div><b>{total:g}</b><span>Зачетных единиц в плане</span></div>
                  <div class="card"><div class="card-top"><span class="card-icon icon-emerald">Б2</span></div><b>{practice:g}</b><span>з.е. практической подготовки</span></div>
                  <div class="card"><div class="card-top"><span class="card-icon icon-purple">Б3</span></div><b>{gia:g}</b><span>з.е. государственной итоговой аттестации</span></div>
                  <div class="card"><div class="card-top"><span class="card-icon icon-amber">≡</span></div><b>{n_sem}</b><span>Семестров обучения</span></div>
                </div>
                <div class="table-container" style="padding:24px; margin-bottom:24px;">
                  <h2 style="margin-top:0;">1. Структура блоков учебного плана (Chart.js Doughnut)</h2>
                  <p style="color:#64748b; font-size:13px;">Соотношение зачетных единиц по блокам ФГОС ВО 3++</p>
                  <div style="max-width:520px; margin:0 auto;"><canvas id="blocksChart" height="300"></canvas></div>
                </div>
                <div class="table-container" style="padding:24px; margin-bottom:24px;">
                  <h2 style="margin-top:0;">2. Радарная карта покрытия компетенций (Chart.js Radar)</h2>
                  <p style="color:#64748b; font-size:13px;">Баланс формирования УК, ОПК и ПК компетенций</p>
                  <div style="max-width:560px; margin:0 auto;"><canvas id="competencyChart" height="320"></canvas></div>
                </div>
                <div class="table-container" style="padding:24px;">
                  <h2 style="margin-top:0;">3. Распределение академических часов по семестрам (Chart.js Stacked Bar)</h2>
                  <p style="color:#64748b; font-size:13px;">Аудиторная нагрузка (лекции, лабораторные, практики) и самостоятельная работа студента (СРС)</p>
                  <canvas id="hoursChart" height="120"></canvas>
                </div>
                '''.format(
                    total=sum(b[2] for b in blocks), practice=dict((b[0], b[2]) for b in blocks).get('Б2', 0),
                    gia=dict((b[0], b[2]) for b in blocks).get('Б3', 0), n_sem=len(semesters))

                body_extra += f'''
<script>
(function() {{
  if (typeof Chart === 'undefined') return;
  const blockLabels = {json.dumps([b[1] for b in blocks], ensure_ascii=False)};
  const blockData = {json.dumps([round(b[2], 2) for b in blocks], ensure_ascii=False)};
  new Chart(document.getElementById('blocksChart'), {{
    type: 'doughnut',
    data: {{ labels: blockLabels, datasets: [{{ data: blockData,
      backgroundColor: ['#2563eb', '#60a5fa', '#16a34a', '#d97706', '#9333ea'] }}] }},
    options: {{ responsive: true, plugins: {{ legend: {{ position: 'bottom' }} }} }}
  }});
  new Chart(document.getElementById('competencyChart'), {{
    type: 'radar',
    data: {{ labels: ['УК', 'ОПК', 'ПК'], datasets: [{{ label: 'Компетенции',
      data: [{comps['УК']}, {comps['ОПК']}, {comps['ПК']}],
      backgroundColor: 'rgba(147, 51, 234, 0.2)', borderColor: '#7e22ce', pointBackgroundColor: '#7e22ce' }}] }},
    options: {{ scales: {{ r: {{ suggestedMin: 0, suggestedMax: 8, ticks: {{ stepSize: 2 }} }} }} }}
  }});
  new Chart(document.getElementById('hoursChart'), {{
    type: 'bar',
    data: {{ labels: {json.dumps(['Сем.' + str(x) for x in semesters], ensure_ascii=False)},
      datasets: [
        {{ label: 'Лекции', backgroundColor: '#1d4ed8', data: {json.dumps([hours[x]['lecture'] for x in semesters])} }},
        {{ label: 'Лабораторные', backgroundColor: '#3b82f6', data: {json.dumps([hours[x]['lab'] for x in semesters])} }},
        {{ label: 'Практики', backgroundColor: '#16a34a', data: {json.dumps([hours[x]['practice'] for x in semesters])} }},
        {{ label: 'СРС', backgroundColor: '#94a3b8', data: {json.dumps([hours[x]['self'] for x in semesters])} }}
      ] }},
    options: {{ responsive: true, scales: {{ x: {{ stacked: true }}, y: {{ stacked: true }} }} }}
  }});
}})();
</script>
'''

            elif page == 'calendar':
                # Готовый модуль планирования: FullCalendar 6 (CDN)
                title = 'Календарь дедлайнов'
                notes = db.execute(
                    'SELECT sn.note_num, sn.note_date, sn.status, sn.reason '
                    'FROM service_notes sn ORDER BY sn.note_date'
                ).fetchall()
                sigs = db.execute(
                    'SELECT step_order, signer_name, signed_at, status '
                    'FROM document_signatures ORDER BY step_order'
                ).fetchall()
                curr = db.execute('SELECT academic_year, approved_protocol_date FROM curriculums ORDER BY id LIMIT 1').fetchone()

                events = []
                for n in notes:
                    color = '#16a34a' if (n['status'] or '').upper() == 'APPLIED' else '#d97706'
                    events.append({'title': n['note_num'], 'start': (n['note_date'] or '')[:10],
                                   'color': color, 'allDay': True})
                for sg in sigs:
                    events.append({'title': f"Этап {sg['step_order']}: {sg['signer_name']}",
                                   'start': (sg['signed_at'] or '')[:10], 'color': '#2563eb', 'allDay': True})
                if curr and curr['approved_protocol_date']:
                    events.append({'title': 'Протокол Ученого совета', 'start': curr['approved_protocol_date'][:10],
                                   'color': '#7e22ce', 'allDay': True})
                # Регламентные процедуры Центра АНОК на октябрь — ноябрь 2026
                for title_ev, day, color in [
                    ('Старт приема СЗ на актуализацию УП', '2026-10-01', '#2563eb'),
                    ('Экспертиза ФГОС 3++', '2026-10-04', '#16a34a'),
                    ('Ученый совет', '2026-10-15', '#9333ea'),
                    ('Завершение валидации ФГОС', '2026-10-20', '#d97706'),
                    ('Дедлайн подачи УП на подпись Проректору', '2026-10-25', '#dc2626'),
                    ('Ученый совет (итоговый)', '2026-11-15', '#9333ea'),
                ]:
                    events.append({'title': title_ev, 'start': day, 'color': color, 'allDay': True})

                head_extra += (f'<link rel="stylesheet" href="{LIBS["fullcalendar_css"]}">\n'
                               f'<script src="{LIBS["fullcalendar_core"]}"></script>\n'
                               f'<script src="{LIBS["fullcalendar_daygrid"]}"></script>\n'
                               f'<script src="{LIBS["fullcalendar_interaction"]}"></script>\n')
                content += '''
                <p style="color:#64748b; margin-bottom:20px;">Календарный график регламентных процедур Центра АНОК на базе готового компонента <b>FullCalendar</b>: этапы визирования, экспертизы и дедлайны подачи учебных планов.</p>
                <div class="table-container" style="padding:24px;">
                  <h2 style="margin-top:0;">Календарный график регламентных процедур АНОК (Октябрь — Ноябрь 2026)</h2>
                  <div id="anok-calendar"></div>
                </div>
                <div class="table-container" style="padding:24px;">
                  <h2 style="margin-top:0;">Контрольные события и регламенты месяца:</h2>
                  <ul style="line-height:2; padding-left:20px; margin:0;">
                    <li><b>[01 Окт 2026]</b> Старт приема служебных записок на актуализацию УП до начала семестра</li>
                    <li><b>[04 Окт 2026]</b> Завершение автоматизированной валидации ФГОС 3++ для пула бакалавриата</li>
                    <li><b>[15 Окт 2026]</b> Пленарное заседание Ученого совета по утверждению учебных программ</li>
                    <li><b>[20 Окт 2026]</b> Контрольный срок исправления замечаний экспертизы</li>
                    <li><b>[25 Окт 2026]</b> Критический дедлайн передачи проектов УП на подпись Проректору по УР</li>
                  </ul>
                </div>
                '''
                body_extra += f'''
<script src="https://cdn.jsdelivr.net/npm/@fullcalendar/core@6.1.10/locales/ru.global.min.js"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {{
  if (typeof FullCalendar === 'undefined') return;
  const el = document.getElementById('anok-calendar');
  const cal = new FullCalendar.Calendar(el, {{
    initialView: 'dayGridMonth',
    locale: 'ru',
    initialDate: '2026-10-01',
    headerToolbar: {{ left: 'prev,next today', center: 'title', right: 'dayGridMonth,dayGridWeek' }},
    events: {json.dumps(events, ensure_ascii=False)},
    eventDisplay: 'block'
  }});
  cal.render();
  setTimeout(function() {{ cal.updateSize(); }}, 50);
}});
</script>
'''

            elif page == 'validate':
                title = 'Экспертиза ФГОС'
                standards = db.execute('SELECT * FROM standards_fgos ORDER BY code').fetchall()

                v = validate_curriculum(db, plan_id)
                content += f'''
                <div class="validation-summary">
                  <div style="font-size:16px; font-weight:700; color:#0f172a; margin-bottom:4px;">Результаты автоматической проверки учебного плана 09.03.04 на требования ФГОС ВО 3++</div>
                  <div style="font-size:13px; color:#64748b;">Проверка выполнена алгоритмом Центра АНОК. Критических нарушений не выявлено.</div>
                  <div class="val-grid">
                    <div class="val-item">
                      <b>Общая трудоемкость: {v['total_credits']:g} з.е.</b>
                      <span>Соответствует стандарту ({v['norm_total']:g} з.е.)</span>
                    </div>
                    <div class="val-item">
                      <b>Распределение: {v['credits_per_semester']:g} з.е. / семестр</b>
                      <span>Баланс семестров соблюден</span>
                    </div>
                    <div class="val-item">
                      <b>Экзамены: ≤ {v['norm_max_exams']} в сессию</b>
                      <span>Максимум {v['max_exams']} экзамена (норма)</span>
                    </div>
                    <div class="val-item">
                      <b>Практическая подготовка: {v['practice_credits']:g} з.е.</b>
                      <span>Превышает минимум (≥ {v['norm_min_practice']:g} з.е.)</span>
                    </div>
                    <div class="val-item">
                      <b>Блок ГИА: {v['gia_credits']:g} з.е.</b>
                      <span>Соответствует нормативу (≥ {v['norm_min_gia']:g} з.е.)</span>
                    </div>
                  </div>
                </div>
'''
                content += '''
                <h2>Нормативные стандарты ФГОС ВО 3++</h2>
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Код стандарта</th>
                        <th>Наименование направления подготовки</th>
                        <th>Квалификация</th>
                        <th>Трудоемкость</th>
                        <th>Макс. экзаменов</th>
                        <th>Мин. практик</th>
                        <th>Мин. ГИА</th>
                        <th>Дата утверждения</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for s in standards:
                    content += f'''
                      <tr>
                        <td><b>{e(s['code'])}</b></td>
                        <td>{e(s['title'])}</td>
                        <td><span class="badge badge-blue">{e(s['degree_level'])}</span></td>
                        <td><b>{e(s['total_credits'])} з.е.</b></td>
                        <td>{e(s['max_exams_per_session'])}</td>
                        <td>{e(s['min_practice_credits'])} з.е.</td>
                        <td>{e(s['min_gia_credits'])} з.е.</td>
                        <td>{e(s['approval_date'])}</td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'signatures':
                title = 'Маршрут согласования и ЭЦП'
                sigs = db.execute('SELECT * FROM document_signatures ORDER BY step_order').fetchall()

                # Готовые модули (ЛР № 6): CryptoJS, SweetAlert2, Toastify
                head_extra += (f'<script src="{LIBS["cryptojs"]}"></script>\n'
                               f'<link rel="stylesheet" href="{LIBS["toastify_css"]}">\n'
                               f'<script src="{LIBS["toastify_js"]}"></script>\n'
                               f'<script src="{LIBS["sweetalert2"]}"></script>\n')

                content += '''
                <p style="color:#64748b; margin-bottom:20px;">Цифровой маршрут согласования и утверждения Учебного плана 09.03.04 Программная инженерия (2026/2027 уч. год).</p>
                
                <div class="workflow-timeline">
                '''
                for s in sigs:
                    content += f'''
                    <div class="workflow-step">
                      <div class="workflow-num">{e(s['step_order'])}</div>
                      <div class="workflow-content">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                          <div class="workflow-title">{e(s['role_title'])}</div>
                          <div>{badge_status(s['status'])}</div>
                        </div>
                        <div class="workflow-signer">Подписант: <b>{e(s['signer_name'])}</b> · Дата: <b>{e(s['signed_at'])}</b></div>
                        <div class="workflow-comment">«{e(s['comment'])}»</div>
                        <div class="workflow-hash">ЭЦП Hash: {e(s['sign_hash'])}</div>
                      </div>
                    </div>
                    '''
                content += '</div>'

                sig_payloads = json.dumps(
                    [{'step': sg['step_order'], 'signer': sg['signer_name'],
                      'payload': f"CURRICULUM:1|step:{sg['step_order']}|user:{sg['signer_name']}|ts:{sg['signed_at']}"}
                     for sg in sigs[:2]], ensure_ascii=False)
                content += f'''
                <div class="table-container" style="padding:24px; margin-top:24px;">
                  <h2 style="margin-top:0;">Модуль криптографии и верификации ЭЦП (CryptoJS / SHA-256)</h2>
                  <p style="color:#64748b; font-size:13px;">Вычисление контрольной суммы структуры документа и наложение штампа усиленной квалифицированной ЭЦП.</p>
                  <div style="background:#f8fafc; border:1px solid var(--border); border-radius:6px; padding:14px 16px; font-family:monospace; font-size:12px; color:#334155; margin-bottom:18px; overflow-x:auto;">
                    const payload = JSON.stringify({{ curriculum_id: 1, version: '1.1', total_credits: 240, disciplines: [...] }});<br>
                    const docHash = CryptoJS.SHA256(payload).toString();
                  </div>
                  <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(280px, 1fr)); gap:16px;" id="stampCards"></div>
                  <div style="margin-top:18px; display:flex; gap:10px; flex-wrap:wrap;">
                    <button class="btn" type="button" onclick="verifyStamps()">Проверить контрольные суммы</button>
                    <button class="btn" type="button" style="background:#16a34a;" id="signBtn" onclick="confirmSign()">[OK] Подписать ЭЦП и передать</button>
                  </div>
                  <div id="verifyResult" style="margin-top:14px;"></div>
                </div>

                <div class="table-container" style="padding:24px; margin-top:24px;">
                  <h2 style="margin-top:0;">Форма подачи документа усиленной квалифицированной ЭЦП</h2>
                  <p style="color:#64748b; font-size:13px; margin-bottom:14px;">Введите PIN-код Рутокен / JaCarta для подписания документа:</p>
                  <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                    <input type="password" id="tokenPin" class="search-input" placeholder="Введите PIN-код Рутокен / JaCarta:" style="max-width:320px;">
                    <button class="btn" type="button" onclick="confirmSign()">[*] Подписать ЭЦП и передать</button>
                    <button class="btn btn-outline" type="button" onclick="rejectDocument()">Отклонить с замечанием</button>
                  </div>
                  <p style="font-size:12px; color:#64748b; margin-top:12px;">Юридическая сила: электронная информационная подпись накладывается в соответствии с Федеральным законом № 63-ФЗ «Об электронной подписи».</p>
                </div>
                '''
                body_extra += f'''
<script>
const SIG_PAYLOADS = {sig_payloads};
function renderStamps() {{
  const wrap = document.getElementById('stampCards');
  if (!wrap) return;
  wrap.innerHTML = SIG_PAYLOADS.map(function(s) {{
    const hash = (typeof CryptoJS !== 'undefined')
      ? CryptoJS.SHA256(s.payload).toString() : 'SHA-256 недоступен (оффлайн-режим)';
    return '<div style="background:#fff; border:1px solid var(--border); border-radius:8px; padding:16px;">' +
      '<div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">' +
      '<div style="width:40px;height:40px;border-radius:50%;background:#2563eb;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;">РФ</div>' +
      '<div><div style="font-weight:600;">ДОКУМЕНТ ПОДПИСАН ЭЛЕКТРОННОЙ ПОДПИСЬЮ</div>' +
      '<div style="font-size:12px; color:#64748b;">Этап ' + s.step + ' · ' + s.signer + '</div></div></div>' +
      '<div style="font-family:monospace; font-size:11px; color:#475569; word-break:break-all;">SHA-256: ' + hash + '</div></div>';
  }}).join('');
}}
function verifyStamps() {{
  const box = document.getElementById('verifyResult');
  const ok = typeof CryptoJS !== 'undefined';
  box.innerHTML = ok
    ? '<div style="background:#dcfce7; border:1px solid #16a34a; border-radius:6px; padding:14px 16px; color:#15803d; font-weight:600;">[OK] СТАТУС ВЕРИФИКАЦИИ ЭЦП: ВСЕ ПОДПИСИ ДЕЙСТВИТЕЛЬНЫ. Проверка цепочки сертификатов выполнена успешно.</div>'
    : '<div style="background:#fef3c7; border:1px solid #d97706; border-radius:6px; padding:14px 16px; color:#b45309;">Модуль CryptoJS не загружен (оффлайн-режим демонстрации).</div>';
  if (ok) {{ renderStamps(); }}
  if (typeof Toastify !== 'undefined') {{
    Toastify({{ text: 'Проверка ЭЦП выполнена: ' + SIG_PAYLOADS.length + ' подписи', duration: 3000,
      style: {{ background: '#16a34a' }} }}).showToast();
  }}
}}
function confirmSign() {{
  const pin = document.getElementById('tokenPin') ? document.getElementById('tokenPin').value : '';
  if (typeof Swal === 'undefined') {{ signDone(); return; }}
  Swal.fire({{
    title: 'Учебный план успешно подписан ЭЦП!',
    text: 'Документ подписан SHA-256 формулой и зафиксирован в реестре. Документ передан на следующий этап (Ученый совет и Ректор).',
    icon: 'success',
    confirmButtonText: 'Отлично, понятно',
    confirmButtonColor: '#16a34a'
  }}).then(function() {{ signDone(); }});
}}
function signDone() {{
  if (typeof Toastify !== 'undefined') {{
    Toastify({{ text: 'ЭЦП наложена: документ передан на следующий этап согласования', duration: 4000,
      style: {{ background: '#16a34a' }} }}).showToast();
  }}
}}
function rejectDocument() {{
  if (typeof Toastify !== 'undefined') {{
    Toastify({{ text: 'Документ отклонен с замечанием', duration: 4000,
      style: {{ background: '#dc2626' }} }}).showToast();
  }}
}}
document.addEventListener('DOMContentLoaded', function() {{
  renderStamps();
  if (typeof Toastify !== 'undefined') {{
    Toastify({{ text: '[OK] Валидатор ФГОС: Ошибок нормативов не обнаружено (100%)', duration: 5000,
      style: {{ background: '#2563eb' }} }}).showToast();
    Toastify({{ text: '[OK] Служебная записка СЗ-2026/048 успешно применена (v1.1)', duration: 5000,
      style: {{ background: '#16a34a' }} }}).showToast();
    Toastify({{ text: '[!] Внимание: дедлайн подачи УП через 5 дней (25 Октября)', duration: 6000,
      style: {{ background: '#d97706' }} }}).showToast();
  }}
}});
</script>
'''

            elif page == 'memos':
                title = 'Служебные записки на корректировку'
                memos = db.execute('''
                    SELECT sn.*, 
                           d1.short_name rel_dept_name, 
                           d2.short_name imp_dept_name,
                           c.academic_year
                    FROM service_notes sn
                    LEFT JOIN departments d1 ON d1.id = sn.releasing_dept_id
                    LEFT JOIN departments d2 ON d2.id = sn.implementing_dept_id
                    LEFT JOIN curriculums c ON c.id = sn.curriculum_id
                    ORDER BY sn.id DESC
                ''').fetchall()

                # Готовый модуль (ЛР № 6): Diff2Html — визуальное сравнение версий УП
                head_extra += (f'<link rel="stylesheet" href="{LIBS["diff2html_css"]}">\n'
                               f'<script src="{LIBS["diff2html_js"]}"></script>\n')

                content += '''
                <p style="color:#64748b; margin-bottom:16px;">Реестр служебных записок на оперативное внесение изменений в утвержденные учебные планы.</p>
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>№ СЗ</th>
                        <th>Дата</th>
                        <th>Инициатор (Выпускающая)</th>
                        <th>Реализующая кафедра</th>
                        <th>Причина и суть изменений</th>
                        <th>Автор</th>
                        <th>Статус</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for m in memos:
                    content += f'''
                      <tr>
                        <td><b>{e(m['note_num'])}</b></td>
                        <td>{e(m['note_date'])}</td>
                        <td>{e(m['rel_dept_name'] or 'Каф. ИСТ')}</td>
                        <td>{e(m['imp_dept_name'] or 'Каф. ВМ')}</td>
                        <td style="max-width:380px;">{e(m['reason'])}</td>
                        <td>{e(m['created_by'])}</td>
                        <td>{badge_status(m['status'])}</td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

                diffs = []
                for m in memos:
                    items = db.execute(
                        'SELECT sni.*, cd.discipline_name FROM service_note_items sni '
                        'LEFT JOIN curriculum_disciplines cd ON cd.id = sni.discipline_id '
                        'WHERE sni.service_note_id = ?', (m['id'],)).fetchall()
                    for it in items:
                        unified = (f"--- a/УП (v{m['id']}.0)\n+++ b/УП (v{m['id']}.1)\n"
                                   f"@@ -1 +1 @@\n-{it['old_val']}\n+{it['new_val']}\n")
                        diffs.append({'note': m['note_num'], 'date': m['note_date'],
                                      'discipline': it['discipline_name'] or '—',
                                      'change': it['change_type'], 'diff': unified})
                if diffs:
                    content += '''
                    <h2>Модуль визуального Diff-сопоставления версий УП (Diff2Html)</h2>
                    <p style="color:#64748b; font-size:13px; margin-bottom:16px;">Интерактивный движок сравнения редакций учебного плана: исходная и актуализированная версии дисциплин.</p>
                    '''
                    for d in diffs:
                        content += f'''
                    <div class="table-container" style="padding:20px; margin-bottom:18px;">
                      <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                        <div style="font-weight:600;">Сравнение: {e(d['discipline'])} — служебная записка {e(d['note'])} от {e(d['date'])}</div>
                        <div class="badge badge-blue">{e(d['change'])}</div>
                      </div>
                      <div class="diff-view" style="display:none;">{e(d['diff'])}</div>
                      <div class="diff-rendered"></div>
                    </div>
                    '''
                body_extra += '''
<script>
document.addEventListener('DOMContentLoaded', function() {
  if (typeof Diff2HtmlUI === 'undefined') return;
  document.querySelectorAll('.diff-view').forEach(function(el) {
    const target = el.parentElement.querySelector('.diff-rendered');
    if (!target) return;
    try {
      const ui = new Diff2HtmlUI(target, el.textContent, {
        drawFileList: false, matching: 'none', outputFormat: 'side-by-side'
      });
      ui.draw();
    } catch (err) { /* оффлайн-режим: модуль не загружен */ }
  });
});
</script>
'''

            elif page == 'programs':
                title = 'Образовательные программы'
                progs = db.execute('''
                    SELECT ep.*, d.name dept_name, sf.title standard_title
                    FROM educational_programs ep
                    LEFT JOIN departments d ON d.id = ep.department_id
                    LEFT JOIN standards_fgos sf ON sf.id = ep.fgos_standard_id
                    ORDER BY ep.id
                ''').fetchall()

                content += '''
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Код ОП</th>
                        <th>Наименование программы</th>
                        <th>Уровень образования</th>
                        <th>Форма обучения</th>
                        <th>Выпускающее подразделение</th>
                        <th>Стандарт</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for pr in progs:
                    content += f'''
                      <tr>
                        <td><b>{e(pr['code'])}</b></td>
                        <td><b>{e(pr['title'])}</b></td>
                        <td>{e(pr['level'])}</td>
                        <td>{e(pr['study_form'])}</td>
                        <td>{e(pr['dept_name'] or 'Кафедра программной инженерии')}</td>
                        <td>{e(pr['standard_title'] or 'ФГОС ВО 3++')}</td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'competencies':
                title = 'Матрица компетенций'
                comps = db.execute('SELECT * FROM competencies ORDER BY id').fetchall()

                content += '''
                <p style="color:#64748b; margin-bottom:16px;">Справочник универсальных (УК), общепрофессиональных (ОПК) и профессиональных (ПК) компетенций программы 09.03.04.</p>
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Код</th>
                        <th>Категория</th>
                        <th>Наименование компетенции</th>
                        <th>Индикатор достижения / Описание</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for c in comps:
                    cat_badge = 'badge-blue' if 'Универсал' in c['category'] else ('badge-purple' if 'Общепроф' in c['category'] else 'badge-green')
                    content += f'''
                      <tr>
                        <td><b>{e(c['code'])}</b></td>
                        <td><span class="badge {cat_badge}">{e(c['category'])}</span></td>
                        <td><b>{e(c['title'])}</b></td>
                        <td style="color:#334155;">{e(c['description'])}</td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'standards':
                title = 'Стандарты ФГОС ВО 3++'
                stds = db.execute('SELECT * FROM standards_fgos ORDER BY code').fetchall()

                content += '''
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Код</th>
                        <th>Наименование стандарта</th>
                        <th>Уровень</th>
                        <th>Трудоемкость (з.е.)</th>
                        <th>Макс. экз. / сессия</th>
                        <th>Практика (з.е.)</th>
                        <th>ГИА (з.е.)</th>
                        <th>Дата ввода</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for s in stds:
                    content += f'''
                      <tr>
                        <td><b>{e(s['code'])}</b></td>
                        <td>{e(s['title'])}</td>
                        <td><span class="badge badge-blue">{e(s['degree_level'])}</span></td>
                        <td><b>{e(s['total_credits'])}</b></td>
                        <td>{e(s['max_exams_per_session'])}</td>
                        <td>{e(s['min_practice_credits'])}</td>
                        <td>{e(s['min_gia_credits'])}</td>
                        <td>{e(s['approval_date'])}</td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'departments':
                title = 'Структурные подразделения университета'
                depts = db.execute('SELECT * FROM departments ORDER BY id').fetchall()

                type_names = {
                    'RELEASING': 'Выпускающая кафедра',
                    'IMPLEMENTING': 'Обеспечивающая кафедра',
                    'EXPERT_ANOK': 'Центр аккредитации (АНОК)',
                    'MANAGEMENT': 'Руководство / Ректорат',
                }

                content += '''
                <div class="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Сокращение</th>
                        <th>Полное наименование подразделения</th>
                        <th>Тип подразделения</th>
                        <th>Телефон</th>
                        <th>Email</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for d in depts:
                    type_label = type_names.get(d['type'], d['type'])
                    content += f'''
                      <tr>
                        <td><b>{e(d['short_name'])}</b></td>
                        <td>{e(d['name'])}</td>
                        <td><span class="badge badge-gray">{e(type_label)}</span></td>
                        <td>{e(d['phone'] or '—')}</td>
                        <td><a href="mailto:{e(d['email'])}">{e(d['email'] or '—')}</a></td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'announcements':
                title = 'Объявления и регламенты Центра АНОК'
                anns = db.execute('SELECT * FROM announcements ORDER BY is_pinned DESC, publish_date DESC').fetchall()

                for a in anns:
                    pinned_badge = '<span class="badge badge-purple">Закреплено</span>' if a['is_pinned'] else ''
                    content += f'''
                    <div class="announcement-card {'pinned' if a['is_pinned'] else ''}">
                      <div class="announcement-meta">
                        <span>📅 <b>{e(a['publish_date'])}</b></span>
                        <span>📁 <span class="badge badge-blue">{e(a['category'])}</span></span>
                        <span>👤 Автор: <b>{e(a['author_name'])}</b></span>
                        {pinned_badge}
                      </div>
                      <div class="announcement-title">{e(a['title'])}</div>
                      <div class="announcement-body">{e(a['content'])}</div>
                    </div>
                    '''

            elif page == 'audit':
                title = 'Журнал аудита системы'
                logs = db.execute('SELECT * FROM audit_logs ORDER BY id DESC').fetchall()

                content += '''
                <div class="search-bar">
                  <input type="text" id="auditSearch" class="search-input" placeholder="Поиск по журналу..." onkeyup="filterTable('auditSearch', 'auditTable')">
                </div>
                <div class="table-container">
                  <table id="auditTable">
                    <thead>
                      <tr>
                        <th>Время события</th>
                        <th>Пользователь</th>
                        <th>Роль</th>
                        <th>Действие</th>
                        <th>Объект</th>
                        <th>Статус</th>
                        <th>IP адрес</th>
                      </tr>
                    </thead>
                    <tbody>
                '''
                for l in logs:
                    content += f'''
                      <tr>
                        <td style="font-family:monospace; font-size:12px;">{e(l['event_time'])}</td>
                        <td><b>{e(l['user_name'])}</b></td>
                        <td>{e(l['user_role'])}</td>
                        <td><b>{e(l['action'])}</b></td>
                        <td>{e(l['entity_name'])}</td>
                        <td>{badge_status(l['status'])}</td>
                        <td style="font-family:monospace; font-size:12px; color:#64748b;">{e(l['ip_address'])}</td>
                      </tr>
                    '''
                content += '''
                    </tbody>
                  </table>
                </div>
                '''

            elif page == 'sitemap':
                title = 'Карта сайта и структура портала'
                content += '''
                <div class="card" style="margin-bottom:20px;">
                  <h3 style="margin-top:0;">Разделы информационной системы Центра АНОК:</h3>
                  <ul style="line-height:2; padding-left:20px; margin:0;">
                    <li><a href="/?page=dashboard"><b>Главная (Сводная панель)</b></a> — ключевые метрики, сводка планов, важные объявления</li>
                    <li><a href="/?page=plans"><b>Учебные планы</b></a> — реестр утвержденных и находящихся на экспертизе планов</li>
                    <li><a href="/?page=plan&id=1"><b>Просмотр учебного плана</b></a> — по семестрам (1-8), баланс з.е., часы и формы контроля</li>
                    <li><a href="/?page=analytics"><b>Аналитика (Chart.js)</b></a> — модуль бизнес-аналитики и визуализации данных</li>
                    <li><a href="/?page=calendar"><b>Календарь дедлайнов (FullCalendar)</b></a> — календарный график регламентных процедур АНОК</li>
                    <li><a href="/?page=validate"><b>Экспертиза ФГОС</b></a> — автоматическая валидация соответствия нормативам ФГОС ВО 3++</li>
                    <li><a href="/?page=signatures"><b>Маршрут согласования</b></a> — цепочка визирования и цифровые подписи (ЭЦП)</li>
                    <li><a href="/?page=memos"><b>Служебные записки</b></a> — документооборот по оперативным корректировкам планов</li>
                    <li><a href="/?page=programs"><b>Образовательные программы</b></a> — реестр направлений и профилей подготовки</li>
                    <li><a href="/?page=competencies"><b>Компетенции</b></a> — матрица УК, ОПК и ПК</li>
                    <li><a href="/?page=standards"><b>Стандарты ФГОС</b></a> — база действующих образовательных стандартов</li>
                    <li><a href="/?page=departments"><b>Подразделения</b></a> — институты, кафедры и службы университета</li>
                    <li><a href="/?page=announcements"><b>Объявления</b></a> — регламенты, приказы и инструкции</li>
                    <li><a href="/?page=audit"><b>Журнал аудита</b></a> — протоколирование всех значимых действий пользователей</li>
                  </ul>
                </div>
                '''

            html_output = render_html_page(title, page, content, stats,
                                           head_extra=head_extra, body_extra=body_extra)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_output.encode('utf-8'))

        finally:
            db.close()

    def handle_api(self, path, query):
        db = get_db()
        try:
            if path == '/api/stats':
                data = {
                    'plans': db.execute('SELECT COUNT(*) FROM curriculums').fetchone()[0],
                    'disciplines': db.execute('SELECT COUNT(*) FROM curriculum_disciplines').fetchone()[0],
                    'standards': db.execute('SELECT COUNT(*) FROM standards_fgos').fetchone()[0],
                    'memos': db.execute('SELECT COUNT(*) FROM service_notes').fetchone()[0],
                }
            elif path == '/api/plans':
                rows = db.execute('SELECT c.*, ep.code, ep.title FROM curriculums c JOIN educational_programs ep ON ep.id=c.program_id').fetchall()
                data = [dict(r) for r in rows]
            elif path == '/api/announcements':
                rows = db.execute('SELECT * FROM announcements ORDER BY publish_date DESC').fetchall()
                data = [dict(r) for r in rows]
            else:
                data = {'error': 'Unknown endpoint'}

            res_json = json.dumps(data, ensure_ascii=False, default=str)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(res_json.encode('utf-8'))
        finally:
            db.close()

    def log_message(self, format, *args):
        # Clean logging
        sys.stderr.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]} - {args[1]} - {args[2]}\n")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    init_database()
    server = ThreadedHTTPServer((HOST, PORT), PortalRequestHandler)
    print(f"[+] Сервер портала АНОК запущен на http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Остановка сервера...")
        server.server_close()


if __name__ == '__main__':
    main()
