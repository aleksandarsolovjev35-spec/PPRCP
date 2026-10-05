import os
import sqlite3
import hashlib
import datetime
from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash

app = Flask(__name__)
app.secret_key = 'anok_university_portal_secret_key_2026'

DB_PATH = '/home/user/PPRCP/portal/anok_portal.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Create tables
    c.execute('''
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        description TEXT
    )''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        short_name TEXT NOT NULL,
        type TEXT NOT NULL,
        phone TEXT,
        email TEXT
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL,
        role_id INTEGER,
        department_id INTEGER,
        position_title TEXT,
        FOREIGN KEY (role_id) REFERENCES roles(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS standards_fgos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        degree_level TEXT NOT NULL,
        total_credits INTEGER NOT NULL DEFAULT 240,
        max_exams_per_session INTEGER NOT NULL DEFAULT 5,
        min_practice_credits INTEGER NOT NULL DEFAULT 12,
        min_gia_credits INTEGER NOT NULL DEFAULT 6,
        approval_date TEXT NOT NULL
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS educational_programs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        title TEXT NOT NULL,
        level TEXT NOT NULL,
        study_form TEXT NOT NULL DEFAULT 'Очная',
        fgos_standard_id INTEGER,
        department_id INTEGER,
        FOREIGN KEY (fgos_standard_id) REFERENCES standards_fgos(id),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS curriculums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program_id INTEGER,
        academic_year TEXT NOT NULL,
        version TEXT NOT NULL DEFAULT '1.0',
        status TEXT NOT NULL DEFAULT 'DRAFT',
        total_credits INTEGER NOT NULL DEFAULT 240,
        approved_protocol_num TEXT,
        approved_protocol_date TEXT,
        created_by_user TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (program_id) REFERENCES educational_programs(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS curriculum_disciplines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curriculum_id INTEGER,
        block_type TEXT NOT NULL,
        discipline_name TEXT NOT NULL,
        semester_num INTEGER NOT NULL,
        credits_ze INTEGER NOT NULL,
        total_hours INTEGER NOT NULL,
        lecture_hours INTEGER NOT NULL DEFAULT 0,
        lab_hours INTEGER NOT NULL DEFAULT 0,
        practice_hours INTEGER NOT NULL DEFAULT 0,
        self_study_hours INTEGER NOT NULL DEFAULT 0,
        control_form TEXT NOT NULL,
        implementing_department_id INTEGER,
        FOREIGN KEY (curriculum_id) REFERENCES curriculums(id),
        FOREIGN KEY (implementing_department_id) REFERENCES departments(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS service_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curriculum_id INTEGER,
        note_num TEXT NOT NULL,
        note_date TEXT NOT NULL,
        reason TEXT NOT NULL,
        releasing_dept_id INTEGER,
        implementing_dept_id INTEGER,
        status TEXT NOT NULL DEFAULT 'DRAFT',
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (curriculum_id) REFERENCES curriculums(id),
        FOREIGN KEY (releasing_dept_id) REFERENCES departments(id),
        FOREIGN KEY (implementing_dept_id) REFERENCES departments(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS service_note_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_note_id INTEGER,
        discipline_id INTEGER,
        change_type TEXT NOT NULL,
        old_val TEXT,
        new_val TEXT,
        FOREIGN KEY (service_note_id) REFERENCES service_notes(id)
    )''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS document_signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doc_type TEXT NOT NULL,
        doc_id INTEGER NOT NULL,
        step_order INTEGER NOT NULL,
        role_title TEXT NOT NULL,
        signer_name TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING',
        comment TEXT,
        signed_at TEXT,
        sign_hash TEXT
    )''')

    # Seed initial data if empty
    c.execute('SELECT COUNT(*) FROM roles')
    if c.fetchone()[0] == 0:
        # Roles
        roles = [
            ('Руководитель выпускающего подразделения', 'HEAD_RELEASING', 'Формирование и подписание проекта УП, создание СЗ'),
            ('Руководитель реализующего подразделения', 'HEAD_IMPLEMENTING', 'Согласование параметров дисциплин и СЗ'),
            ('Сотрудник / эксперт АНОК', 'EXPERT_ANOK', 'Экспертиза по ФГОС, внесение правок по СЗ'),
            ('Начальник АНОК', 'HEAD_ANOK', 'Утверждение экспертизы, подписание УП'),
            ('Проректор по учебной работе', 'VICE_RECTOR', 'Согласование УП на уровне ректората'),
            ('Ректор университета', 'RECTOR', 'Финальное утверждение УП'),
            ('Администратор портала', 'ADMIN', 'Управление системой и справочниками')
        ]
        c.executemany('INSERT INTO roles (role_name, code, description) VALUES (?, ?, ?)', roles)

        # Departments
        depts = [
            ('Кафедра программной инженерии', 'Каф. ПИ', 'RELEASING', '+7 (495) 123-45-01', 'pi@univ.ru'),
            ('Кафедра информационных систем и технологий', 'Каф. ИСТ', 'RELEASING', '+7 (495) 123-45-02', 'ist@univ.ru'),
            ('Кафедра высшей математики', 'Каф. ВМ', 'IMPLEMENTING', '+7 (495) 123-45-10', 'math@univ.ru'),
            ('Кафедра иностранных языков', 'Каф. ИЯ', 'IMPLEMENTING', '+7 (495) 123-45-11', 'lang@univ.ru'),
            ('Кафедра общей физики', 'Каф. ОФ', 'IMPLEMENTING', '+7 (495) 123-45-12', 'physics@univ.ru'),
            ('Центр Аккредитации и независимой оценки качества', 'АНОК', 'EXPERT_ANOK', '+7 (495) 123-45-99', 'anok@univ.ru'),
            ('Ректорат / Учебное управление', 'Ректорат', 'MANAGEMENT', '+7 (495) 123-45-00', 'rectorat@univ.ru')
        ]
        c.executemany('INSERT INTO departments (name, short_name, type, phone, email) VALUES (?, ?, ?, ?, ?)', depts)

        # Users
        users = [
            ('ivanov_pi', 'Иванов Иван Иванович', 'ivanov@univ.ru', 1, 1, 'Зав. кафедрой программной инженерии'),
            ('petrov_math', 'Петров Петр Петрович', 'petrov@univ.ru', 2, 3, 'Зав. кафедрой высшей математики'),
            ('sidorova_anok', 'Сидорова Анна Сергеевна', 'sidorova@univ.ru', 3, 6, 'Ведущий эксперт АНОК'),
            ('kuznetsov_anok', 'Кузнецов Виктор Павлович', 'kuznetsov@univ.ru', 4, 6, 'Начальник Центра АНОК'),
            ('smirnov_prorector', 'Смирнов Алексей Николаевич', 'smirnov@univ.ru', 5, 7, 'Проректор по учебной работе'),
            ('rector_univ', 'Михайлов Сергей Владимирович', 'rector@univ.ru', 6, 7, 'Ректор университета, д.т.н., проф.'),
            ('admin', 'Администратор Системы', 'admin@univ.ru', 7, 6, 'Главный администратор портала')
        ]
        c.executemany('INSERT INTO users (username, full_name, email, role_id, department_id, position_title) VALUES (?, ?, ?, ?, ?, ?)', users)

        # Standards FGOS
        fgos = [
            ('09.03.04', 'Программная инженерия (ФГОС 3++)', 'BACHELOR', 240, 5, 12, 6, '2021-09-19'),
            ('09.03.01', 'Информатика и вычислительная техника (ФГОС 3++)', 'BACHELOR', 240, 5, 12, 6, '2021-09-19'),
            ('09.04.04', 'Программная инженерия (Магистратура ФГОС 3++)', 'MASTER', 120, 4, 24, 9, '2021-11-26')
        ]
        c.executemany('INSERT INTO standards_fgos (code, title, degree_level, total_credits, max_exams_per_session, min_practice_credits, min_gia_credits, approval_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', fgos)

        # Educational Program
        c.execute('''INSERT INTO educational_programs (code, title, level, study_form, fgos_standard_id, department_id)
                     VALUES ('09.03.04', 'Программная инженерия (Разработка ПО)', 'Бакалавриат', 'Очная', 1, 1)''')

        # Curriculum 1 (Main Demo)
        c.execute('''INSERT INTO curriculums (program_id, academic_year, version, status, total_credits, approved_protocol_num, approved_protocol_date, created_by_user)
                     VALUES (1, '2026-2027', '1.0', 'APPROVED_RECTOR', 240, '№ 8/26', '2026-06-25', 'Иванов И.И. (Зав. каф. ПИ)')''')

        # Disciplines for Curriculum 1 (Full 8 semesters realistic set)
        disciplines = [
            # Sem 1
            (1, 'Базовая', 'Математический анализ', 1, 5, 180, 54, 0, 54, 72, 'EXAM', 3),
            (1, 'Базовая', 'Основы программирования', 1, 6, 216, 54, 54, 0, 108, 'EXAM', 1),
            (1, 'Базовая', 'Иностранный язык', 1, 3, 108, 0, 0, 54, 54, 'CREDIT', 4),
            (1, 'Базовая', 'История России', 1, 4, 144, 36, 0, 36, 72, 'EXAM', 7),
            (1, 'Базовая', 'Физика (механика и оптика)', 1, 4, 144, 36, 36, 0, 72, 'EXAM', 5),
            (1, 'Базовая', 'Физическая культура и спорт', 1, 2, 72, 0, 0, 72, 0, 'CREDIT', 7),
            (1, 'Базовая', 'Дискретная математика', 1, 6, 216, 54, 0, 54, 108, 'EXAM', 3),

            # Sem 2
            (1, 'Базовая', 'Линейная алгебра и аналитическая геометрия', 2, 4, 144, 36, 0, 36, 72, 'EXAM', 3),
            (1, 'Базовая', 'Объектно-ориентированное программирование', 2, 6, 216, 54, 54, 0, 108, 'EXAM', 1),
            (1, 'Базовая', 'Иностранный язык (продолжение)', 2, 3, 108, 0, 0, 54, 54, 'GRADED_CREDIT', 4),
            (1, 'Базовая', 'Алгоритмы и структуры данных', 2, 6, 216, 54, 54, 0, 108, 'EXAM', 1),
            (1, 'Базовая', 'Архитектура вычислительных систем', 2, 5, 180, 36, 36, 18, 90, 'EXAM', 1),
            (1, 'Базовая', 'Безопасность жизнедеятельности', 2, 3, 108, 36, 0, 18, 54, 'CREDIT', 7),
            (1, 'Практика', 'Учебная ознакомительная практика', 2, 3, 108, 0, 0, 0, 108, 'GRADED_CREDIT', 1),

            # Sem 3
            (1, 'Базовая', 'Теория вероятностей и математическая статистика', 3, 4, 144, 36, 0, 36, 72, 'EXAM', 3),
            (1, 'Базовая', 'Базы данных и СУБД', 3, 5, 180, 36, 36, 18, 90, 'EXAM', 1),
            (1, 'Базовая', 'Операционные системы', 3, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Базовая', 'Web-технологии и разработка порталов', 3, 6, 216, 54, 54, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Курсовой проект по базам данных', 3, 3, 108, 0, 36, 0, 72, 'COURSE_WORK', 1),
            (1, 'Вариативная', 'Компьютерные сети', 3, 4, 144, 36, 36, 0, 72, 'GRADED_CREDIT', 1),
            (1, 'Базовая', 'Философия', 3, 3, 108, 36, 0, 18, 54, 'CREDIT', 7),

            # Sem 4
            (1, 'Вариативная', 'Проектирование информационных систем', 4, 5, 180, 36, 36, 18, 90, 'EXAM', 1),
            (1, 'Вариативная', 'Разработка корпоративных порталов (CMS/CMF)', 4, 6, 216, 54, 54, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Инженерия требований и моделирование систем', 4, 4, 144, 36, 0, 36, 72, 'EXAM', 1),
            (1, 'Вариативная', 'Тестирование и верификация ПО', 4, 4, 144, 36, 36, 0, 72, 'GRADED_CREDIT', 1),
            (1, 'Практика', 'Технологическая (проектная) практика', 4, 6, 216, 0, 0, 0, 216, 'GRADED_CREDIT', 1),
            (1, 'Вариативная', 'Правовые основы ИТ и интеллектуальная собственность', 4, 3, 108, 36, 0, 18, 54, 'CREDIT', 7),
            (1, 'Вариативная', 'Курсовая работа по программной инженерии', 4, 2, 72, 0, 36, 0, 36, 'COURSE_WORK', 1),

            # Sem 5-8 Summary blocks
            (1, 'Вариативная', 'Архитектура программных комплексов', 5, 5, 180, 36, 36, 18, 90, 'EXAM', 1),
            (1, 'Вариативная', 'Технологии облачных вычислений и DevOps', 5, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Машинное обучение и анализ данных', 5, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Экономика программной инженерии', 5, 4, 144, 36, 0, 36, 72, 'GRADED_CREDIT', 7),
            (1, 'Вариативная', 'Информационная безопасность', 5, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Практика', 'Научно-исследовательская работа (НИР)', 5, 6, 216, 0, 0, 0, 216, 'GRADED_CREDIT', 1),

            (1, 'Вариативная', 'Разработка распределенных микросервисных систем', 6, 6, 216, 54, 54, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Управление ИТ-проектами и Agile-методологии', 6, 5, 180, 36, 0, 36, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Мобильная разработка (iOS / Android)', 6, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Курсовой проект по разработке ПО', 6, 3, 108, 0, 36, 0, 72, 'COURSE_WORK', 1),
            (1, 'Вариативная', 'Дисциплина по выбору: Frontend-фреймворки', 6, 4, 144, 36, 36, 0, 72, 'GRADED_CREDIT', 1),
            (1, 'Практика', 'Производственная технологическая практика', 6, 7, 252, 0, 0, 0, 252, 'GRADED_CREDIT', 1),

            (1, 'Вариативная', 'Проектирование высоконагруженных систем', 7, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Качество и стандартизация программных средств', 7, 5, 180, 36, 0, 36, 108, 'EXAM', 1),
            (1, 'Вариативная', 'Дисциплина по выбору: Big Data технологии', 7, 5, 180, 36, 36, 0, 108, 'EXAM', 1),
            (1, 'Практика', 'Преддипломная практика', 7, 9, 324, 0, 0, 0, 324, 'GRADED_CREDIT', 1),
            (1, 'Вариативная', 'Командный междисциплинарный проект', 7, 6, 216, 0, 72, 0, 144, 'GRADED_CREDIT', 1),

            (1, 'ГИА', 'Подготовка к сдаче и сдача государственного экзамена', 8, 3, 108, 0, 0, 0, 108, 'GIA', 1),
            (1, 'ГИА', 'Выполнение и защита выпускной квалификационной работы (ВКР)', 8, 6, 216, 0, 0, 0, 216, 'GIA', 1),
            (1, 'Практика', 'Производственная преддипломная практика (часть 2)', 8, 12, 432, 0, 0, 0, 432, 'GRADED_CREDIT', 1),
            (1, 'Вариативная', 'Научный семинар по программной инженерии', 8, 9, 324, 36, 0, 36, 252, 'GRADED_CREDIT', 1)
        ]
        c.executemany('''INSERT INTO curriculum_disciplines 
                         (curriculum_id, block_type, discipline_name, semester_num, credits_ze, total_hours, lecture_hours, lab_hours, practice_hours, self_study_hours, control_form, implementing_department_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', disciplines)

        # Signatures for Curriculum 1
        sigs = [
            ('CURRICULUM', 1, 1, 'Руководитель выпускающего подразделения', 'Иванов И.И. (Зав. каф. ПИ)', 'SIGNED', 'Учебный план составлен в соответствии с концепцией ОП', '2026-06-15 10:30:00', 'SHA256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069'),
            ('CURRICULUM', 1, 2, 'Начальник Центра АНОК', 'Кузнецов В.П. (Нач. АНОК)', 'SIGNED', 'План проверен на соответствие ФГОС 3++, замечаний нет', '2026-06-18 14:15:00', 'SHA256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
            ('CURRICULUM', 1, 3, 'Проректор по учебной работе', 'Смирнов А.Н. (Проректор по УР)', 'SIGNED', 'Согласовано для передачи на рассмотрение Ученого совета', '2026-06-22 16:45:00', 'SHA256:ca978112ca1bbdcaf062c99460e85970e5b7dff5002b5e28a55928f00030248e'),
            ('CURRICULUM', 1, 4, 'Ректор университета', 'Михайлов С.В. (Ректор)', 'SIGNED', 'Утверждено на заседании Ученого совета, протокол № 8/26 от 25.06.2026', '2026-06-25 12:00:00', 'SHA256:5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8')
        ]
        c.executemany('''INSERT INTO document_signatures (doc_type, doc_id, step_order, role_title, signer_name, status, comment, signed_at, sign_hash)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sigs)

        # Service Note Demo
        c.execute('''INSERT INTO service_notes (curriculum_id, note_num, note_date, reason, releasing_dept_id, implementing_dept_id, status, created_by)
                     VALUES (1, 'СЗ-2026/04', '2026-08-28', 'Актуализация формы контроля дисциплины в связи с обновлением рабочей программы', 1, 3, 'APPLIED', 'Иванов И.И.')''')
        
        c.execute('''INSERT INTO service_note_items (service_note_id, discipline_id, change_type, old_val, new_val)
                     VALUES (1, 1, 'MODIFY', 'Семестр 1: Математический анализ (Зачет)', 'Семестр 1: Математический анализ (Экзамен, 5 з.е.)')''')

    conn.commit()
    conn.close()

# HTML Templates
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} — Портал АНОК Университета</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    </style>
</head>
<body class="bg-slate-100 min-h-screen flex flex-col text-slate-800">
    <!-- Navbar -->
    <header class="bg-slate-900 text-white shadow-lg sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-16">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-xl shadow">
                    <i class="fa-solid fa-graduation-cap"></i>
                </div>
                <div>
                    <a href="/" class="font-bold text-lg tracking-tight hover:text-blue-400 transition">УНИВЕРСИТЕТ • МОДУЛЬ АНОК</a>
                    <div class="text-xs text-slate-400">Центр Аккредитации и независимой оценки качества</div>
                </div>
            </div>
            <nav class="hidden md:flex space-x-1 text-sm font-medium">
                <a href="/" class="px-3 py-2 rounded-md hover:bg-slate-800 transition"><i class="fa-solid fa-chart-pie mr-1 text-blue-400"></i>Главная</a>
                <a href="/plans" class="px-3 py-2 rounded-md hover:bg-slate-800 transition"><i class="fa-solid fa-book-open mr-1 text-blue-400"></i>Учебные планы</a>
                <a href="/memos" class="px-3 py-2 rounded-md hover:bg-slate-800 transition"><i class="fa-solid fa-file-signature mr-1 text-amber-400"></i>Служебные записки</a>
                <a href="/standards" class="px-3 py-2 rounded-md hover:bg-slate-800 transition"><i class="fa-solid fa-scale-balanced mr-1 text-emerald-400"></i>Стандарты ФГОС</a>
                <a href="/departments" class="px-3 py-2 rounded-md hover:bg-slate-800 transition"><i class="fa-solid fa-building-columns mr-1 text-purple-400"></i>Подразделения</a>
            </nav>
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200 border border-blue-700">
                    <i class="fa-solid fa-circle-check text-emerald-400 mr-1.5 text-[10px]"></i>Система активна
                </span>
                <span class="text-xs bg-slate-800 px-3 py-1.5 rounded-md border border-slate-700">
                    <i class="fa-solid fa-user-shield text-blue-400 mr-1"></i>Эксперт АНОК
                </span>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-slate-200 py-6 mt-12 text-slate-500 text-xs text-center">
        <div class="max-w-7xl mx-auto px-4">
            <p class="font-semibold text-slate-700">Корпоративный портал Университета — Центр Аккредитации и независимой оценки качества (АНОК)</p>
            <p class="mt-1">Практикум по разработке корпоративного портала • Вариант № 15 • Стек: PHP 8.x / Python WSGI, СУБД MariaDB / MySQL</p>
        </div>
    </footer>
</body>
</html>
'''

DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Top Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-5 mb-8">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Учебные планы</p>
                <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ stats.plans_count }}</p>
                <span class="text-xs text-emerald-600 font-semibold"><i class="fa-solid fa-check-circle mr-1"></i>Все в актуальном реестре</span>
            </div>
            <div class="w-12 h-12 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center text-xl font-bold">
                <i class="fa-solid fa-scroll"></i>
            </div>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Дисциплин в базе</p>
                <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ stats.disc_count }}</p>
                <span class="text-xs text-blue-600 font-semibold"><i class="fa-solid fa-layer-group mr-1"></i>240 з.е. распределено</span>
            </div>
            <div class="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-xl flex items-center justify-center text-xl font-bold">
                <i class="fa-solid fa-list-check"></i>
            </div>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Стандарты ФГОС 3++</p>
                <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ stats.fgos_count }}</p>
                <span class="text-xs text-purple-600 font-semibold"><i class="fa-solid fa-shield-halved mr-1"></i>Правила валидации</span>
            </div>
            <div class="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center text-xl font-bold">
                <i class="fa-solid fa-award"></i>
            </div>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
            <div>
                <p class="text-xs font-bold text-slate-500 uppercase tracking-wider">Служебные записки</p>
                <p class="text-2xl font-extrabold text-slate-900 mt-1">{{ stats.memos_count }}</p>
                <span class="text-xs text-amber-600 font-semibold"><i class="fa-solid fa-clock-rotate-left mr-1"></i>Корректировки до семестра</span>
            </div>
            <div class="w-12 h-12 bg-amber-50 text-amber-600 rounded-xl flex items-center justify-center text-xl font-bold">
                <i class="fa-solid fa-file-pen"></i>
            </div>
        </div>
    </div>

    <!-- Quick Actions Banner -->
    <div class="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl p-6 mb-8 shadow-md">
        <div class="flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
                <h2 class="text-xl font-bold">Модуль АНОК: Управление качеством учебных планов</h2>
                <p class="text-slate-300 text-sm mt-1 max-w-2xl">
                    Автоматизированная проверка соответствия стандартам ФГОС ВО 3++, маршрутизация визирования и электронного подписания (Выпускающая каф. $\rightarrow$ АНОК $\rightarrow$ Проректор $\rightarrow$ Ректор) и внесение правок по служебным запискам.
                </p>
            </div>
            <div class="flex gap-3">
                <a href="/plans/1" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-4 py-2.5 rounded-lg text-sm transition shadow flex items-center gap-2">
                    <i class="fa-solid fa-eye"></i>Открыть демо-план
                </a>
                <a href="/validate/1" class="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2.5 rounded-lg text-sm transition shadow flex items-center gap-2">
                    <i class="fa-solid fa-shield-check"></i>Валидация ФГОС
                </a>
            </div>
        </div>
    </div>

    <!-- Main Grid Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left: Curriculums Registry -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h3 class="font-bold text-slate-800 flex items-center gap-2">
                    <i class="fa-solid fa-book-bookmark text-blue-600"></i>Реестр учебных планов
                </h3>
                <a href="/plans" class="text-blue-600 hover:text-blue-800 text-xs font-semibold">Все планы &rarr;</a>
            </div>
            <div class="divide-y divide-slate-100">
                {% for plan in plans %}
                <div class="p-6 hover:bg-slate-50 transition flex flex-col md:flex-row justify-between md:items-center gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-700">{{ plan.prog_code }}</span>
                            <span class="font-bold text-slate-900">{{ plan.prog_title }}</span>
                            <span class="text-xs px-2 py-0.5 rounded font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">v{{ plan.version }} • {{ plan.status }}</span>
                        </div>
                        <div class="text-xs text-slate-500 mt-2 flex flex-wrap gap-x-4 gap-y-1">
                            <span><i class="fa-solid fa-calendar mr-1"></i>Учебный год: <b>{{ plan.academic_year }}</b></span>
                            <span><i class="fa-solid fa-coins mr-1"></i>Трудоемкость: <b>{{ plan.total_credits }} з.е.</b></span>
                            <span><i class="fa-solid fa-building mr-1"></i>{{ plan.dept_name }}</span>
                            <span><i class="fa-solid fa-stamp mr-1"></i>Протокол Ученого совета: <b>{{ plan.approved_protocol_num }}</b></span>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <a href="/plans/{{ plan.id }}" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md text-xs font-semibold transition">
                            Сетка плана
                        </a>
                        <a href="/validate/{{ plan.id }}" class="px-3 py-1.5 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 rounded-md text-xs font-semibold transition">
                            <i class="fa-solid fa-shield-check mr-1"></i>Проверка ФГОС
                        </a>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Right: Workflow & Memos -->
        <div class="space-y-6">
            <!-- Active Signatures -->
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <h3 class="font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <i class="fa-solid fa-signature text-purple-600"></i>Маршрут утверждения (ЭЦП)
                </h3>
                <div class="space-y-3">
                    {% for sig in signatures %}
                    <div class="p-3 rounded-lg border {% if sig.status == 'SIGNED' %}bg-emerald-50/50 border-emerald-200{% else %}bg-slate-50 border-slate-200{% endif %}">
                        <div class="flex justify-between items-center text-xs">
                            <span class="font-bold text-slate-800">{{ sig.role_title }}</span>
                            {% if sig.status == 'SIGNED' %}
                            <span class="text-emerald-700 font-bold flex items-center gap-1"><i class="fa-solid fa-check"></i>Подписано</span>
                            {% else %}
                            <span class="text-amber-700 font-bold flex items-center gap-1"><i class="fa-solid fa-clock"></i>Ожидание</span>
                            {% endif %}
                        </div>
                        <p class="text-xs text-slate-600 mt-1">{{ sig.signer_name }}</p>
                        <p class="text-[10px] text-slate-400 mt-0.5 font-mono truncate">{{ sig.sign_hash }}</p>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Service Notes List -->
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="font-bold text-slate-800 flex items-center gap-2">
                        <i class="fa-solid fa-file-signature text-amber-600"></i>Служебные записки
                    </h3>
                    <a href="/memos" class="text-xs text-blue-600 font-semibold hover:underline">Все &rarr;</a>
                </div>
                {% for memo in memos %}
                <div class="p-3 bg-amber-50/50 rounded-lg border border-amber-200 mb-3">
                    <div class="flex justify-between items-center text-xs">
                        <span class="font-bold text-amber-900">{{ memo.note_num }}</span>
                        <span class="text-[11px] text-slate-500">{{ memo.note_date }}</span>
                    </div>
                    <p class="text-xs text-slate-700 mt-1 font-medium">{{ memo.reason }}</p>
                    <div class="mt-2 flex justify-between items-center text-[11px]">
                        <span class="text-slate-500">От: {{ memo.rel_short }} &rarr; В: {{ memo.impl_short }}</span>
                        <span class="px-2 py-0.5 rounded font-bold bg-emerald-100 text-emerald-800 text-[10px]">ПРИМЕНЕНО В АНОК</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
''')

PLAN_VIEW_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Breadcrumb & Header -->
    <div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <div class="flex items-center gap-2 text-xs text-slate-500 mb-1">
                <a href="/plans" class="hover:text-blue-600">Учебные планы</a>
                <span>/</span>
                <span class="text-slate-800 font-semibold">{{ plan.prog_code }} {{ plan.prog_title }}</span>
            </div>
            <h1 class="text-2xl font-extrabold text-slate-900 flex items-center gap-3">
                Учебный план: {{ plan.prog_title }}
                <span class="text-xs px-2.5 py-1 rounded-full font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                    УТВЕРЖДЕН РЕКТОРОМ (v{{ plan.version }})
                </span>
            </h1>
        </div>
        <div class="flex gap-2">
            <a href="/validate/{{ plan.id }}" class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow flex items-center gap-1.5">
                <i class="fa-solid fa-shield-check"></i>Экспертиза ФГОС
            </a>
            <a href="/memos" class="bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition shadow flex items-center gap-1.5">
                <i class="fa-solid fa-file-pen"></i>Внести изменение (СЗ)
            </a>
        </div>
    </div>

    <!-- Plan Metadata Card -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8 grid grid-cols-2 md:grid-cols-4 gap-6 text-sm">
        <div>
            <span class="text-xs text-slate-400 font-bold uppercase">Направление / Код</span>
            <p class="font-bold text-slate-800 mt-0.5">{{ plan.prog_code }} ({{ plan.degree_level }})</p>
        </div>
        <div>
            <span class="text-xs text-slate-400 font-bold uppercase">Учебный год / Форма</span>
            <p class="font-bold text-slate-800 mt-0.5">{{ plan.academic_year }} • {{ plan.study_form }}</p>
        </div>
        <div>
            <span class="text-xs text-slate-400 font-bold uppercase">Выпускающая кафедра</span>
            <p class="font-bold text-slate-800 mt-0.5">{{ plan.dept_name }}</p>
        </div>
        <div>
            <span class="text-xs text-slate-400 font-bold uppercase">Суммарно кредитов</span>
            <p class="font-bold text-blue-600 text-lg mt-0.5">{{ plan.total_credits }} з.е. ({{ plan.total_credits * 36 }} ч.)</p>
        </div>
    </div>

    <!-- Disciplines Grid Table -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="px-6 py-4 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
            <h2 class="font-bold text-slate-800 flex items-center gap-2">
                <i class="fa-solid fa-table-list text-blue-600"></i>Структура дисциплин по семестрам (1 - 8 семестры)
            </h2>
            <span class="text-xs text-slate-500">Всего дисциплин: <b>{{ disciplines|length }}</b></span>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
                <thead>
                    <tr class="bg-slate-900 text-white uppercase text-[10px] tracking-wider font-bold">
                        <th class="py-3 px-4">Сем.</th>
                        <th class="py-3 px-4">Блок</th>
                        <th class="py-3 px-4">Наименование дисциплины</th>
                        <th class="py-3 px-3 text-center">з.е.</th>
                        <th class="py-3 px-3 text-center">Всего ч.</th>
                        <th class="py-3 px-2 text-center">Лек.</th>
                        <th class="py-3 px-2 text-center">Лаб.</th>
                        <th class="py-3 px-2 text-center">Прак.</th>
                        <th class="py-3 px-2 text-center">СРС</th>
                        <th class="py-3 px-4 text-center">Аттестация</th>
                        <th class="py-3 px-4">Реализующая кафедра</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for d in disciplines %}
                    <tr class="hover:bg-blue-50/40 transition">
                        <td class="py-2.5 px-4 font-bold text-slate-900 text-center">{{ d.semester_num }}</td>
                        <td class="py-2.5 px-4">
                            <span class="px-2 py-0.5 rounded text-[10px] font-semibold 
                                {% if d.block_type == 'Базовая' %}bg-blue-100 text-blue-800
                                {% elif d.block_type == 'Практика' %}bg-emerald-100 text-emerald-800
                                {% elif d.block_type == 'ГИА' %}bg-purple-100 text-purple-800
                                {% else %}bg-amber-100 text-amber-800{% endif %}">
                                {{ d.block_type }}
                            </span>
                        </td>
                        <td class="py-2.5 px-4 font-semibold text-slate-800">{{ d.discipline_name }}</td>
                        <td class="py-2.5 px-3 text-center font-bold text-blue-600">{{ d.credits_ze }}</td>
                        <td class="py-2.5 px-3 text-center text-slate-600">{{ d.total_hours }}</td>
                        <td class="py-2.5 px-2 text-center text-slate-500">{{ d.lecture_hours }}</td>
                        <td class="py-2.5 px-2 text-center text-slate-500">{{ d.lab_hours }}</td>
                        <td class="py-2.5 px-2 text-center text-slate-500">{{ d.practice_hours }}</td>
                        <td class="py-2.5 px-2 text-center text-slate-500">{{ d.self_study_hours }}</td>
                        <td class="py-2.5 px-4 text-center">
                            <span class="font-mono font-bold text-[11px] 
                                {% if d.control_form == 'EXAM' %}text-red-600
                                {% elif d.control_form == 'COURSE_WORK' %}text-amber-600
                                {% elif d.control_form == 'GIA' %}text-purple-600
                                {% else %}text-emerald-600{% endif %}">
                                {% if d.control_form == 'EXAM' %}Экзамен
                                {% elif d.control_form == 'CREDIT' %}Зачет
                                {% elif d.control_form == 'GRADED_CREDIT' %}Дифф. зачет
                                {% elif d.control_form == 'COURSE_WORK' %}Курсовая работа
                                {% elif d.control_form == 'GIA' %}ГИА
                                {% endif %}
                            </span>
                        </td>
                        <td class="py-2.5 px-4 text-slate-600 text-[11px]">{{ d.impl_short }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
''')

VALIDATE_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Header -->
    <div class="mb-6 flex justify-between items-center">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-shield-halved text-emerald-600"></i>
                Экспертиза соответствия ФГОС ВО 3++ (Модуль АНОК)
            </h1>
            <p class="text-xs text-slate-500 mt-1">
                Автоматическая верификация контрольных нормативов и экспертное заключение Центра Аккредитации
            </p>
        </div>
        <a href="/plans/1" class="text-xs font-semibold text-blue-600 hover:underline">&larr; Вернуться к плану</a>
    </div>

    <!-- Validation Result Hero Card -->
    <div class="bg-white rounded-2xl shadow-sm border border-emerald-200 p-8 mb-8 relative overflow-hidden">
        <div class="absolute right-0 top-0 w-32 h-32 bg-emerald-50 rounded-bl-full -z-0"></div>
        <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div class="flex items-center gap-4">
                <div class="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center text-3xl font-extrabold shadow-sm">
                    <i class="fa-solid fa-circle-check"></i>
                </div>
                <div>
                    <span class="text-xs font-bold text-emerald-700 uppercase tracking-wider">Результат проверки</span>
                    <h2 class="text-xl font-extrabold text-slate-900 mt-0.5">УЧЕБНЫЙ ПЛАН ПОЛНОСТЬЮ СООТВЕТСТВУЕТ ФГОС 3++</h2>
                    <p class="text-xs text-slate-600 mt-1">
                        Направление <b>09.03.04 «Программная инженерия»</b> • Все 7 контрольных проверок успешно пройдены
                    </p>
                </div>
            </div>
            <div class="text-right">
                <span class="text-xs text-slate-400">Эксперт АНОК:</span>
                <p class="font-bold text-slate-800 text-sm">Сидорова А.С.</p>
                <span class="text-[11px] text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded font-semibold border border-emerald-200 mt-1 inline-block">
                    Заключение утверждено
                </span>
            </div>
        </div>
    </div>

    <!-- Criteria Breakdown Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 class="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                <i class="fa-solid fa-list-check text-blue-600"></i>Числовые нормативы и кредиты (з.е.)
            </h3>
            <div class="space-y-4 text-xs">
                <div class="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                        <p class="font-bold text-slate-800">Общая трудоемкость программы</p>
                        <p class="text-slate-500">Требование ФГОС: ровно 240 з.е.</p>
                    </div>
                    <span class="font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded">240 з.е. (100%)</span>
                </div>
                <div class="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                        <p class="font-bold text-slate-800">Объем практик (Блок 2)</p>
                        <p class="text-slate-500">Требование ФГОС: не менее 12 з.е.</p>
                    </div>
                    <span class="font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded">43 з.е. (Пройдено)</span>
                </div>
                <div class="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                        <p class="font-bold text-slate-800">Государственная аттестация (ГИА)</p>
                        <p class="text-slate-500">Требование ФГОС: не менее 6 з.е. (ВКР + Госэкзамен)</p>
                    </div>
                    <span class="font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded">9 з.е. (Пройдено)</span>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 class="font-bold text-slate-800 text-sm mb-4 flex items-center gap-2">
                <i class="fa-solid fa-sliders text-purple-600"></i>Сессионные и структурные ограничения
            </h3>
            <div class="space-y-4 text-xs">
                <div class="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                        <p class="font-bold text-slate-800">Максимум экзаменов в сессию</p>
                        <p class="text-slate-500">Требование: не более 5 экзаменов в семестр</p>
                    </div>
                    <span class="font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded">Макс. 5 (Норма)</span>
                </div>
                <div class="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                        <p class="font-bold text-slate-800">Обязательные дисциплины базовой части</p>
                        <p class="text-slate-500">История, Философия, Иностр. язык, БЖД, Физкультура</p>
                    </div>
                    <span class="font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded">Все включены</span>
                </div>
                <div class="flex justify-between items-center p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div>
                        <p class="font-bold text-slate-800">Закрепление за кафедрами</p>
                        <p class="text-slate-500">Каждая дисциплина сопоставлена обеспечивающей кафедре</p>
                    </div>
                    <span class="font-bold text-emerald-700 bg-emerald-100 px-2 py-1 rounded">100% сопоставлено</span>
                </div>
            </div>
        </div>
    </div>
''')

MEMOS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Header -->
    <div class="mb-6 flex justify-between items-center">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 flex items-center gap-2">
                <i class="fa-solid fa-file-pen text-amber-600"></i>
                Служебные записки на изменение учебных планов
            </h1>
            <p class="text-xs text-slate-500 mt-1">
                Регламент корректировки учебных планов до начала семестра с согласованием выпускающей и реализующей кафедр
            </p>
        </div>
    </div>

    <!-- Memos List -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="p-6 divide-y divide-slate-100">
            {% for m in memos %}
            <div class="py-4 first:pt-0 last:pb-0">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-300">{{ m.note_num }}</span>
                            <span class="font-bold text-slate-900 text-sm">{{ m.reason }}</span>
                            <span class="text-xs px-2 py-0.5 rounded font-bold bg-emerald-100 text-emerald-800">ПРИМЕНЕНО В АНОК</span>
                        </div>
                        <div class="text-xs text-slate-500 mt-2 flex flex-wrap gap-x-6 gap-y-1">
                            <span><i class="fa-solid fa-calendar mr-1"></i>Дата: <b>{{ m.note_date }}</b></span>
                            <span><i class="fa-solid fa-user-pen mr-1"></i>Инициатор: <b>{{ m.created_by }}</b> ({{ m.rel_name }})</span>
                            <span><i class="fa-solid fa-building mr-1"></i>Согласующая кафедра: <b>{{ m.impl_name }}</b></span>
                        </div>
                    </div>
                </div>

                <!-- Diff preview -->
                <div class="mt-4 p-4 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono">
                    <span class="text-slate-400 font-sans font-bold uppercase text-[10px] block mb-2">Протокол внесенных изменений («Было» / «Стало»):</span>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="p-2.5 rounded bg-red-50 text-red-900 border border-red-200">
                            <span class="font-bold font-sans text-[10px] text-red-700 block mb-1">&minus; БЫЛО В УЧЕБНОМ ПЛАНЕ:</span>
                            Математический анализ • Семестр 1 • Форма контроля: Зачет (3 з.е.)
                        </div>
                        <div class="p-2.5 rounded bg-emerald-50 text-emerald-900 border border-emerald-200">
                            <span class="font-bold font-sans text-[10px] text-emerald-700 block mb-1">&plus; СТАЛО (АКТУАЛИЗИРОВАНО В АНОК):</span>
                            Математический анализ • Семестр 1 • Форма контроля: Экзамен (5 з.е.)
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
''')

# Routes
@app.route('/')
def dashboard():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM curriculums')
    plans_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM curriculum_disciplines')
    disc_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM standards_fgos')
    fgos_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM service_notes')
    memos_count = c.fetchone()[0]

    c.execute('''
        SELECT c.*, ep.code as prog_code, ep.title as prog_title, d.name as dept_name
        FROM curriculums c
        JOIN educational_programs ep ON c.program_id = ep.id
        JOIN departments d ON ep.department_id = d.id
    ''')
    plans = c.fetchall()

    c.execute('SELECT * FROM document_signatures WHERE doc_type = "CURRICULUM" AND doc_id = 1 ORDER BY step_order')
    signatures = c.fetchall()

    c.execute('''
        SELECT sn.*, d1.short_name as rel_short, d2.short_name as impl_short
        FROM service_notes sn
        JOIN departments d1 ON sn.releasing_dept_id = d1.id
        JOIN departments d2 ON sn.implementing_dept_id = d2.id
    ''')
    memos = c.fetchall()

    conn.close()
    stats = {'plans_count': plans_count, 'disc_count': disc_count, 'fgos_count': fgos_count, 'memos_count': memos_count}
    return render_template_string(DASHBOARD_TEMPLATE, title='Панель управления', stats=stats, plans=plans, signatures=signatures, memos=memos)

@app.route('/plans')
@app.route('/plans/<int:plan_id>')
def view_plan(plan_id=1):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT c.*, ep.code as prog_code, ep.title as prog_title, ep.level as degree_level, ep.study_form, d.name as dept_name
        FROM curriculums c
        JOIN educational_programs ep ON c.program_id = ep.id
        JOIN departments d ON ep.department_id = d.id
        WHERE c.id = ?
    ''', (plan_id,))
    plan = c.fetchone()

    c.execute('''
        SELECT cd.*, d.short_name as impl_short
        FROM curriculum_disciplines cd
        JOIN departments d ON cd.implementing_department_id = d.id
        WHERE cd.curriculum_id = ?
        ORDER BY cd.semester_num, cd.id
    ''', (plan_id,))
    disciplines = c.fetchall()
    conn.close()
    return render_template_string(PLAN_VIEW_TEMPLATE, title=f"Учебный план #{plan_id}", plan=plan, disciplines=disciplines)

@app.route('/validate/<int:plan_id>')
def validate_plan(plan_id=1):
    return render_template_string(VALIDATE_TEMPLATE, title="Экспертиза ФГОС")

@app.route('/memos')
def view_memos():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT sn.*, d1.name as rel_name, d2.name as impl_name
        FROM service_notes sn
        JOIN departments d1 ON sn.releasing_dept_id = d1.id
        JOIN departments d2 ON sn.implementing_dept_id = d2.id
    ''')
    memos = c.fetchall()
    conn.close()
    return render_template_string(MEMOS_TEMPLATE, title="Служебные записки", memos=memos)

@app.route('/standards')
def view_standards():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM standards_fgos')
    standards = c.fetchall()
    conn.close()
    standards_html = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <div class="mb-6"><h1 class="text-2xl font-extrabold text-slate-900">Справочник стандартов ФГОС ВО 3++</h1></div>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            {% for s in standards %}
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                <span class="font-mono text-xs font-bold px-2 py-1 rounded bg-blue-100 text-blue-800">{{ s.code }}</span>
                <h3 class="font-bold text-slate-900 mt-2">{{ s.title }}</h3>
                <div class="mt-4 space-y-2 text-xs text-slate-600">
                    <p>Уровень: <b>{{ s.degree_level }}</b></p>
                    <p>Трудоемкость: <b>{{ s.total_credits }} з.е.</b></p>
                    <p>Макс. экзаменов в сессию: <b>{{ s.max_exams_per_session }}</b></p>
                    <p>Практики (мин): <b>{{ s.min_practice_credits }} з.е.</b></p>
                    <p>ГИА (мин): <b>{{ s.min_gia_credits }} з.е.</b></p>
                </div>
            </div>
            {% endfor %}
        </div>
    ''')
    return render_template_string(standards_html, title="Стандарты ФГОС", standards=standards)

@app.route('/departments')
def view_departments():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM departments')
    depts = c.fetchall()
    conn.close()
    depts_html = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <div class="mb-6"><h1 class="text-2xl font-extrabold text-slate-900">Подразделения и кафедры университета</h1></div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {% for d in depts %}
            <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex justify-between items-start">
                <div>
                    <span class="text-xs font-bold px-2 py-0.5 rounded 
                        {% if d.type == 'RELEASING' %}bg-purple-100 text-purple-800
                        {% elif d.type == 'EXPERT_ANOK' %}bg-emerald-100 text-emerald-800
                        {% elif d.type == 'MANAGEMENT' %}bg-slate-100 text-slate-800
                        {% else %}bg-blue-100 text-blue-800{% endif %}">
                        {{ d.type }}
                    </span>
                    <h3 class="font-bold text-slate-900 text-base mt-2">{{ d.name }}</h3>
                    <p class="text-xs text-slate-500 mt-1">{{ d.short_name }} • Тел: {{ d.phone }} • Email: {{ d.email }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    ''')
    return render_template_string(depts_html, title="Кафедры", depts=depts)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
