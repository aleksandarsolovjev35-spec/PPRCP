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

# Base layout template
BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="ru" class="h-full bg-slate-50">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Портал АНОК Университета</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace'],
                    },
                    colors: {
                        brand: {
                            50: '#eff6ff',
                            100: '#dbeafe',
                            500: '#2563eb',
                            600: '#1d4ed8',
                            700: '#1e40af',
                            900: '#1e3a8a',
                        },
                        navy: {
                            800: '#1e293b',
                            900: '#0f172a',
                            950: '#020617',
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="h-full flex flex-col font-sans text-slate-800 antialiased selection:bg-blue-600 selection:text-white">

    <!-- Topbar Header -->
    <header class="h-16 bg-slate-900 border-b border-slate-800 text-white flex items-center justify-between px-6 shrink-0 z-30 sticky top-0">
        <div class="flex items-center gap-4">
            <a href="/" class="flex items-center gap-3 group">
                <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20 group-hover:bg-blue-500 transition">
                    <i class="fa-solid fa-graduation-cap text-lg"></i>
                </div>
                <div>
                    <span class="font-extrabold text-base tracking-tight text-white block leading-tight">УНИВЕРСИТЕТ</span>
                    <span class="text-[11px] font-medium text-blue-400 block tracking-wide">Центр Аккредитации и оценки качества (АНОК)</span>
                </div>
            </a>
            <span class="hidden md:inline-block px-2.5 py-1 rounded bg-slate-800 text-[10px] font-mono text-slate-400 border border-slate-700">Вариант №15</span>
        </div>

        <div class="hidden lg:flex items-center flex-1 max-w-md mx-8">
            <div class="relative w-full">
                <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 text-xs"></i>
                <input type="text" placeholder="Быстрый поиск по инфоблокам, дисциплинам, ФГОС..." class="w-full pl-9 pr-4 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-slate-800">
            </div>
        </div>

        <div class="flex items-center gap-4">
            <a href="/announcements" class="hidden sm:flex items-center gap-1.5 text-xs text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition">
                <i class="fa-solid fa-bullhorn text-amber-400"></i>
                <span>Объявления АНОК</span>
            </a>
            
            <a href="/signatures" class="relative p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition" title="Задачи на согласование">
                <i class="fa-solid fa-bell text-sm"></i>
                <span class="absolute top-1 right-1 w-2.5 h-2.5 bg-amber-500 rounded-full ring-2 ring-slate-900"></span>
            </a>

            <div class="flex items-center gap-3 pl-3 border-l border-slate-800">
                <div class="w-8 h-8 rounded-full bg-blue-700 flex items-center justify-center font-bold text-xs text-white">
                    АС
                </div>
                <div class="hidden md:block text-left leading-tight">
                    <p class="text-xs font-bold text-slate-200">Соловьёв А.С.</p>
                    <p class="text-[10px] text-blue-400 font-medium">Эксперт Центра АНОК</p>
                </div>
            </div>
        </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
        
        <!-- Sidebar Navigation -->
        <aside class="w-64 bg-navy-900 border-r border-slate-800 text-slate-300 flex flex-col shrink-0 overflow-y-auto">
            <div class="p-4">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3">Инфоблоки процессов</span>
                <nav class="mt-2 space-y-1 text-xs">
                    <a href="/" class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'dashboard' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-chart-pie w-4 text-center"></i>
                        <span>Сводная панель</span>
                    </a>
                    <a href="/plans" class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'plans' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-book-bookmark w-4 text-center"></i>
                        <span>Реестр учебных планов</span>
                    </a>
                    <a href="/validate/1" class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'validate' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-shield-halved w-4 text-center"></i>
                        <span>Экспертиза ФГОС 3++</span>
                    </a>
                    <a href="/signatures" class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'signatures' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-signature w-4 text-center"></i>
                        <span>Маршруты визирования</span>
                    </a>
                    <a href="/memos" class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'memos' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-file-pen w-4 text-center"></i>
                        <span>Служебные записки (Diff)</span>
                    </a>
                </nav>

                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3 mt-6 block">Справочники и структура</span>
                <nav class="mt-2 space-y-1 text-xs">
                    <a href="/programs" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'programs' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-layer-group w-4 text-center"></i>
                        <span>Программы подготовки</span>
                    </a>
                    <a href="/standards" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'standards' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-scale-balanced w-4 text-center"></i>
                        <span>Стандарты ФГОС</span>
                    </a>
                    <a href="/departments" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'departments' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-building-columns w-4 text-center"></i>
                        <span>Кафедры и структуры</span>
                    </a>
                    <a href="/competencies" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'competencies' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-list-check w-4 text-center"></i>
                        <span>Матрица компетенций</span>
                    </a>
                    <a href="/announcements" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'announcements' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-bullhorn w-4 text-center"></i>
                        <span>Новости и регламенты</span>
                    </a>
                </nav>

                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3 mt-6 block">Система</span>
                <nav class="mt-2 space-y-1 text-xs">
                    <a href="/audit" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'audit' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-clock-rotate-left w-4 text-center"></i>
                        <span>Журнал аудита и логов</span>
                    </a>
                    <a href="/sitemap" class="flex items-center gap-3 px-3 py-2 rounded-lg font-medium hover:bg-slate-800/80 hover:text-white transition {% if active_page == 'sitemap' %}bg-blue-600 text-white shadow-sm font-semibold{% endif %}">
                        <i class="fa-solid fa-network-wired w-4 text-center"></i>
                        <span>Информационная карта</span>
                    </a>
                </nav>
            </div>

            <!-- Sidebar footer info -->
            <div class="mt-auto p-4 border-t border-slate-800 text-[11px] text-slate-400 bg-slate-950/40">
                <div class="flex items-center justify-between font-mono text-[10px]">
                    <span class="text-emerald-400"><i class="fa-solid fa-circle text-[8px] mr-1"></i> Инфоблоки активны</span>
                    <span>MariaDB 10.6</span>
                </div>
                <p class="mt-1 text-slate-500">Университет АНОК © 2026</p>
            </div>
        </aside>

        <!-- Main Content Area -->
        <main class="flex-1 bg-slate-50 overflow-y-auto flex flex-col justify-between">
            <div class="p-8 max-w-7xl mx-auto w-full">
                
                <!-- Breadcrumbs -->
                <div class="flex items-center gap-2 text-xs text-slate-500 mb-4 font-medium">
                    <a href="/" class="hover:text-blue-600 transition"><i class="fa-solid fa-house"></i></a>
                    <i class="fa-solid fa-chevron-right text-[10px] text-slate-400"></i>
                    <span class="text-slate-800 font-semibold">{{ title }}</span>
                </div>

                {% block content %}{% endblock %}
            </div>

            <!-- Page Footer -->
            <footer class="h-12 bg-white border-t border-slate-200 px-8 flex items-center justify-between text-xs text-slate-500 shrink-0">
                <div class="flex items-center gap-4">
                    <span>© 2026 Центр Аккредитации и независимой оценки качества (АНОК)</span>
                    <span class="text-slate-300">•</span>
                    <span class="text-slate-400">Дисциплина: Практикум по разработке корпоративного портала (ПРКП)</span>
                </div>
                <div class="flex items-center gap-4">
                    <span class="font-mono text-[11px] text-slate-400">Инфоблоки: 8 модулей</span>
                    <span class="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-mono text-[11px] font-bold border border-blue-200">Вариант 15</span>
                </div>
            </footer>
        </main>
    </div>
</body>
</html>
'''

# 1. Dashboard Template
DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Сводная панель оперативного мониторинга</h1>
            <p class="text-xs text-slate-500 mt-1">Информационные блоки экспертного контроля учебных планов, стандартов ФГОС 3++ и документооборота</p>
        </div>
        <div class="flex items-center gap-3">
            <a href="/plans/new" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm shadow-blue-500/20 transition">
                <i class="fa-solid fa-plus"></i>
                <span>Создать проект УП</span>
            </a>
            <a href="/memos/new" class="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition">
                <i class="fa-solid fa-file-signature"></i>
                <span>Подать служебную записку</span>
            </a>
        </div>
    </div>

    <!-- 4 KPI Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div class="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Учебных планов</span>
                <span class="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center text-sm"><i class="fa-solid fa-book-open"></i></span>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
                <span class="text-2xl font-extrabold text-slate-900">{{ stats.plans_count }}</span>
                <span class="text-xs text-emerald-600 font-bold"><i class="fa-solid fa-arrow-trend-up"></i> База 2026/27</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">5 направлений ВО (240-300 з.е.)</p>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Дисциплин в каталоге</span>
                <span class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center text-sm"><i class="fa-solid fa-list-check"></i></span>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
                <span class="text-2xl font-extrabold text-slate-900">{{ stats.disc_count }}</span>
                <span class="text-xs text-emerald-600 font-bold">1–8 семестры</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">С распределением аудиторных часов</p>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Стандарты ФГОС 3++</span>
                <span class="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center text-sm"><i class="fa-solid fa-scale-balanced"></i></span>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
                <span class="text-2xl font-extrabold text-slate-900">{{ stats.fgos_count }}</span>
                <span class="text-xs text-blue-600 font-bold">100% валидация</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Контрольные нормативы Минобрнауки</p>
        </div>

        <div class="bg-white p-5 rounded-xl border border-slate-200/80 shadow-sm relative overflow-hidden">
            <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-slate-500 uppercase tracking-wider">Служебные записки</span>
                <span class="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center text-sm"><i class="fa-solid fa-file-pen"></i></span>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
                <span class="text-2xl font-extrabold text-slate-900">{{ stats.memos_count }}</span>
                <span class="text-xs text-purple-600 font-bold">Diff-протоколы</span>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">Актуализация УП до начала семестра</p>
        </div>
    </div>

    <!-- Pinned Announcements Infoblock -->
    <div class="bg-gradient-to-r from-blue-900 to-slate-900 text-white rounded-xl p-5 mb-8 shadow-md border border-slate-800">
        <div class="flex items-center justify-between mb-3 pb-2 border-b border-blue-800/60">
            <div class="flex items-center gap-2.5">
                <span class="px-2 py-0.5 rounded bg-amber-500 text-slate-950 font-bold text-[10px] uppercase tracking-wider">Инфоблок АНОК</span>
                <h3 class="text-sm font-bold">Регламент аккредитационной экспертизы и дедлайны согласования</h3>
            </div>
            <a href="/announcements" class="text-xs text-blue-300 hover:text-white transition font-medium">Все регламенты ({{ announcements|length }}) →</a>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {% for a in announcements[:2] %}
            <div class="p-3 rounded-lg bg-slate-800/60 border border-slate-700/60">
                <span class="text-[10px] font-mono text-blue-300 font-bold block">{{ a.publish_date }} • {{ a.category }}</span>
                <h4 class="font-bold text-white mt-1">{{ a.title }}</h4>
                <p class="text-[11px] text-slate-300 mt-1 line-clamp-2">{{ a.content }}</p>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Main Grid: Queue of Plans + Signatures -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        
        <!-- Left Table: Plans Queue -->
        <div class="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
            <div class="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
                <div>
                    <h2 class="text-sm font-bold text-slate-900">Инфоблок: Реестр учебных планов и статусы экспертизы АНОК</h2>
                    <p class="text-xs text-slate-500 mt-0.5">Учебный год 2026/2027 • Вариант №15</p>
                </div>
                <a href="/plans" class="text-xs font-bold text-blue-600 hover:text-blue-800 transition">Все планы →</a>
            </div>

            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs">
                    <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
                        <tr>
                            <th class="px-5 py-3">Шифр и программа</th>
                            <th class="px-4 py-3">Выпускающая каф.</th>
                            <th class="px-4 py-3 text-center">Версия</th>
                            <th class="px-4 py-3">Статус экспертизы</th>
                            <th class="px-5 py-3 text-right">Действия</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {% for p in plans %}
                        <tr class="hover:bg-slate-50/80 transition">
                            <td class="px-5 py-3.5">
                                <div class="font-bold text-slate-900 flex items-center gap-2">
                                    <span class="font-mono text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-800">{{ p.prog_code }}</span>
                                    <span>{{ p.prog_title }}</span>
                                </div>
                                <div class="text-[11px] text-slate-400 mt-0.5">Автор: {{ p.created_by_user }} • Трудоемкость: {{ p.total_credits }} з.е.</div>
                            </td>
                            <td class="px-4 py-3.5 text-slate-600 font-medium">{{ p.dept_name }}</td>
                            <td class="px-4 py-3.5 text-center font-mono font-bold text-slate-700">v{{ p.version }}</td>
                            <td class="px-4 py-3.5">
                                {% if p.status == 'APPROVED_RECTOR' %}
                                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                                        <i class="fa-solid fa-check-double text-[8px]"></i> УТВЕРЖДЕН РЕКТОРОМ
                                    </span>
                                {% elif p.status == 'ON_REVIEW_ANOK' %}
                                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">
                                        <i class="fa-solid fa-magnifying-glass text-[8px]"></i> ЭКСПЕРТИЗА АНОК
                                    </span>
                                {% elif p.status == 'REJECTED_ANOK' %}
                                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">
                                        <i class="fa-solid fa-xmark text-[8px]"></i> ЗАМЕЧАНИЯ ФГОС (238 з.е.)
                                    </span>
                                {% elif p.status == 'SIGNING_VICE_RECTOR' %}
                                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                                        <i class="fa-solid fa-pen-fancy text-[8px]"></i> ВИЗИРОВАНИЕ ПРОРЕКТОРА
                                    </span>
                                {% else %}
                                    <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                                        <i class="fa-solid fa-file text-[8px]"></i> ПРОЕКТ (ЧЕРНОВИК)
                                    </span>
                                {% endif %}
                            </td>
                            <td class="px-5 py-3.5 text-right space-x-2">
                                <a href="/plans/{{ p.id }}" class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs transition">
                                    <i class="fa-solid fa-table-cells text-[10px]"></i> Матрица
                                </a>
                                <a href="/validate/{{ p.id }}" class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs transition">
                                    <i class="fa-solid fa-shield-check text-[10px]"></i> ФГОС
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Right Column: Status & Signatures timeline -->
        <div class="space-y-6">
            
            <!-- Digital Signatures Timeline -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-sm font-bold text-slate-900">Инфоблок визирования УП #1</h3>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-bold">09.03.01 ИВТ</span>
                </div>

                <div class="space-y-4">
                    {% for s in signatures %}
                    <div class="flex items-start gap-3">
                        <div class="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5
                            {% if s.status == 'SIGNED' %}bg-emerald-100 text-emerald-600 font-bold text-xs border border-emerald-300
                            {% elif s.status == 'PENDING' and loop.index == 3 %}bg-amber-100 text-amber-600 font-bold text-xs border border-amber-300 animate-pulse
                            {% else %}bg-slate-100 text-slate-400 font-bold text-xs border border-slate-200{% endif %}">
                            {% if s.status == 'SIGNED' %}<i class="fa-solid fa-check text-[10px]"></i>
                            {% elif s.status == 'PENDING' %}{{ s.step_order }}
                            {% else %}<i class="fa-solid fa-clock text-[10px]"></i>{% endif %}
                        </div>
                        <div class="flex-1">
                            <div class="flex items-center justify-between">
                                <p class="text-xs font-bold text-slate-900">{{ s.role_title }}</p>
                                {% if s.status == 'SIGNED' %}
                                    <span class="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">ПОДПИСАНО</span>
                                {% else %}
                                    <span class="text-[10px] font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded">ОЖИДАНИЕ</span>
                                {% endif %}
                            </div>
                            <p class="text-[11px] text-slate-500">{{ s.signer_name }}</p>
                            {% if s.signed_at %}
                                <p class="text-[10px] font-mono text-slate-400 mt-1"><i class="fa-solid fa-calendar mr-1"></i>{{ s.signed_at }}</p>
                                <p class="text-[9px] font-mono text-blue-600 truncate mt-0.5">SHA: {{ s.sign_hash[:20] }}...</p>
                            {% endif %}
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <div class="mt-5 pt-4 border-t border-slate-100">
                    <a href="/signatures/1" class="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition">
                        <i class="fa-solid fa-key"></i>
                        <span>Перейти к наложению ЭЦП</span>
                    </a>
                </div>
            </div>

            <!-- Quick FGOS Stat Card -->
            <div class="bg-gradient-to-br from-blue-900 to-indigo-950 rounded-xl p-5 text-white shadow-md">
                <div class="flex items-center justify-between">
                    <span class="text-xs font-mono text-blue-300 font-bold uppercase tracking-wider">ФГОС ВО 3++ Контроль</span>
                    <i class="fa-solid fa-certificate text-blue-400 text-lg"></i>
                </div>
                <h3 class="text-lg font-bold mt-2">Автоматический аудит нормативов</h3>
                <p class="text-xs text-blue-200 mt-1">Проверка 100% учебных планов на соответствие контрольным показателям Минобрнауки РФ.</p>
                <div class="mt-4 pt-3 border-t border-blue-800/80 flex items-center justify-between text-xs">
                    <span class="text-blue-300">Пройдено успешно:</span>
                    <span class="font-bold text-emerald-400 font-mono">90.1% (4 / 5 планов)</span>
                </div>
            </div>

        </div>
    </div>
''')

# 2. Plan View / Semester Matrix Template (Supports semester selector)
PLAN_VIEW_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Plan Header Card -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mb-8">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
                <div class="flex items-center gap-3">
                    <span class="font-mono text-sm font-bold px-2.5 py-1 rounded bg-blue-100 text-blue-800 border border-blue-200">{{ plan.prog_code }}</span>
                    <h1 class="text-xl font-extrabold text-slate-900">{{ plan.prog_title }}</h1>
                    <span class="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-bold border border-slate-200">v{{ plan.version }}</span>
                </div>
                <div class="flex flex-wrap items-center gap-x-6 gap-y-2 mt-3 text-xs text-slate-500">
                    <span><i class="fa-solid fa-building-columns mr-1.5 text-slate-400"></i>Выпускающая кафедра: <b class="text-slate-800">{{ plan.dept_name }}</b></span>
                    <span><i class="fa-solid fa-graduation-cap mr-1.5 text-slate-400"></i>Уровень: <b class="text-slate-800">{{ plan.degree_level }}</b></span>
                    <span><i class="fa-solid fa-calendar mr-1.5 text-slate-400"></i>Учебный год: <b class="text-slate-800">{{ plan.academic_year }}</b></span>
                    <span><i class="fa-solid fa-user-pen mr-1.5 text-slate-400"></i>Разработчик: <b class="text-slate-800">{{ plan.created_by_user }}</b></span>
                </div>
            </div>

            <div class="flex flex-wrap items-center gap-3">
                <a href="/validate/{{ plan.id }}" class="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm transition">
                    <i class="fa-solid fa-shield-check"></i>
                    <span>Экспертиза ФГОС 3++</span>
                </a>
                <a href="/signatures/{{ plan.id }}" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm transition">
                    <i class="fa-solid fa-signature"></i>
                    <span>Маршрут визирования</span>
                </a>
                <a href="/memos/new" class="inline-flex items-center gap-2 px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-bold transition">
                    <i class="fa-solid fa-file-pen"></i>
                    <span>Служебная записка</span>
                </a>
            </div>
        </div>

        <!-- Metric badges -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-100 text-xs">
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/60">
                <span class="text-slate-400 font-bold block">Суммарная трудоемкость</span>
                <span class="text-lg font-extrabold text-blue-600 font-mono mt-0.5 block">{{ plan.total_credits }} з.е. (8640 ч.)</span>
            </div>
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/60">
                <span class="text-slate-400 font-bold block">Срок обучения</span>
                <span class="text-lg font-extrabold text-slate-900 font-mono mt-0.5 block">4 года (8 семестров)</span>
            </div>
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/60">
                <span class="text-slate-400 font-bold block">Всего дисциплин в УП</span>
                <span class="text-lg font-extrabold text-slate-900 font-mono mt-0.5 block">{{ all_disciplines_count }} дисциплин</span>
            </div>
            <div class="bg-slate-50 p-3 rounded-lg border border-slate-200/60">
                <span class="text-slate-400 font-bold block">Статус согласования</span>
                <span class="text-xs font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded inline-block mt-1">НА ЭКСПЕРТИЗЕ АНОК</span>
            </div>
        </div>
    </div>

    <!-- Semester Matrix Section -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-8">
        <div class="p-5 border-b border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
                <h2 class="text-sm font-bold text-slate-900">Инфоблок: Семестровая матрица дисциплин и учебных поручений</h2>
                <p class="text-xs text-slate-500 mt-0.5">Детализация часов (Л/Лаб/Пр/СРС), зачетных единиц и обеспечивающих кафедр</p>
            </div>
            
            <!-- Semester Switcher tabs -->
            <div class="flex items-center flex-wrap gap-1 bg-slate-200 p-1 rounded-lg text-xs font-bold">
                {% for s_num in range(1, 9) %}
                <a href="/plans/{{ plan.id }}?sem={{ s_num }}" class="px-3 py-1 rounded-md transition {% if selected_sem == s_num %}bg-white text-blue-700 shadow-sm font-bold{% else %}text-slate-600 hover:text-slate-900{% endif %}">
                    Сем. {{ s_num }}
                </a>
                {% endfor %}
            </div>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left text-xs">
                <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
                    <tr>
                        <th class="px-4 py-3">Блок / Шифр</th>
                        <th class="px-4 py-3">Наименование дисциплины</th>
                        <th class="px-3 py-3 text-center">Сем.</th>
                        <th class="px-3 py-3 text-center">ЗЕТ</th>
                        <th class="px-3 py-3 text-center">Всего ч.</th>
                        <th class="px-3 py-3 text-center">Лек.</th>
                        <th class="px-3 py-3 text-center">Лаб.</th>
                        <th class="px-3 py-3 text-center">Прак.</th>
                        <th class="px-3 py-3 text-center">СРС</th>
                        <th class="px-4 py-3">Форма контроля</th>
                        <th class="px-4 py-3">Кафедра-исполнитель</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    {% for d in disciplines %}
                    <tr class="hover:bg-slate-50/80 transition">
                        <td class="px-4 py-3.5 font-mono text-[11px] font-bold text-slate-500">{{ d.block_type }}</td>
                        <td class="px-4 py-3.5">
                            <span class="font-bold text-slate-900 block">{{ d.discipline_name }}</span>
                            <span class="text-[10px] text-slate-400">Компетенции: УК-1, ОПК-1, ПК-1</span>
                        </td>
                        <td class="px-3 py-3.5 text-center font-bold text-slate-700">{{ d.semester_num }}</td>
                        <td class="px-3 py-3.5 text-center font-mono font-bold text-blue-600 bg-blue-50/50">{{ d.credits_ze }}</td>
                        <td class="px-3 py-3.5 text-center font-mono text-slate-700">{{ d.total_hours }}</td>
                        <td class="px-3 py-3.5 text-center font-mono text-slate-600">{{ d.lecture_hours }}</td>
                        <td class="px-3 py-3.5 text-center font-mono text-slate-600">{{ d.lab_hours }}</td>
                        <td class="px-3 py-3.5 text-center font-mono text-slate-600">{{ d.practice_hours }}</td>
                        <td class="px-3 py-3.5 text-center font-mono text-slate-600">{{ d.self_study_hours }}</td>
                        <td class="px-4 py-3.5">
                            {% if 'Экзамен' in d.control_form %}
                                <span class="px-2 py-0.5 rounded font-bold text-[10px] bg-blue-100 text-blue-800 border border-blue-200">{{ d.control_form }}</span>
                            {% elif 'Зачет с оценкой' in d.control_form %}
                                <span class="px-2 py-0.5 rounded font-bold text-[10px] bg-purple-100 text-purple-800 border border-purple-200">{{ d.control_form }}</span>
                            {% elif 'ГИА' in d.control_form %}
                                <span class="px-2 py-0.5 rounded font-bold text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200">{{ d.control_form }}</span>
                            {% else %}
                                <span class="px-2 py-0.5 rounded font-bold text-[10px] bg-slate-100 text-slate-800 border border-slate-200">{{ d.control_form }}</span>
                            {% endif %}
                        </td>
                        <td class="px-4 py-3.5 text-slate-700 font-medium">{{ d.impl_short }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
                <tfoot class="bg-slate-100 text-slate-900 font-bold border-t border-slate-300">
                    <tr>
                        <td colspan="3" class="px-4 py-3 text-right">ИТОГО ЗА {{ selected_sem }} СЕМЕСТР:</td>
                        <td class="px-3 py-3 text-center font-mono text-blue-700 text-sm">{{ sem_stats.total_ze }} з.е.</td>
                        <td class="px-3 py-3 text-center font-mono">{{ sem_stats.total_hrs }} ч.</td>
                        <td class="px-3 py-3 text-center font-mono">{{ sem_stats.total_lec }} ч.</td>
                        <td class="px-3 py-3 text-center font-mono">{{ sem_stats.total_lab }} ч.</td>
                        <td class="px-3 py-3 text-center font-mono">{{ sem_stats.total_pr }} ч.</td>
                        <td class="px-3 py-3 text-center font-mono">{{ sem_stats.total_srs }} ч.</td>
                        <td colspan="2" class="px-4 py-3 text-xs text-slate-600">Экзаменов: {{ sem_stats.exams_count }} (норма <= 5) • Зачетов: {{ sem_stats.credits_count }}</td>
                    </tr>
                </tfoot>
            </table>
        </div>
    </div>
''')

# 3. Announcements Template
ANNOUNCEMENTS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Новости, объявления и регламенты АНОК</h1>
            <p class="text-xs text-slate-500 mt-1">Нормативно-методическая информация, график заседаний Ученого совета и приказы</p>
        </div>
    </div>

    <div class="space-y-6">
        {% for a in announcements %}
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 hover:shadow-md transition">
            <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div class="flex items-center gap-2">
                    <span class="px-2.5 py-0.5 rounded font-bold text-xs bg-blue-100 text-blue-800">{{ a.category }}</span>
                    {% if a.is_pinned %}
                    <span class="px-2 py-0.5 rounded font-bold text-[10px] bg-amber-100 text-amber-800 border border-amber-200"><i class="fa-solid fa-thumbtack mr-1"></i> ЗАКРЕПЛЕНО</span>
                    {% endif %}
                </div>
                <span class="text-xs font-mono text-slate-400"><i class="fa-solid fa-calendar mr-1"></i>{{ a.publish_date }}</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 mt-3">{{ a.title }}</h3>
            <p class="text-xs text-slate-600 mt-2 leading-relaxed">{{ a.content }}</p>
            <div class="mt-4 pt-3 border-t border-slate-100 text-[11px] text-slate-400 flex items-center justify-between">
                <span>Автор публикации: <b>{{ a.author_name }}</b></span>
                <span class="text-blue-600 font-bold">Официальный регламент Центра АНОК</span>
            </div>
        </div>
        {% endfor %}
    </div>
''')

# --- Routes ---

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

    c.execute('SELECT * FROM announcements ORDER BY is_pinned DESC, publish_date DESC')
    announcements = c.fetchall()

    conn.close()
    stats = {'plans_count': plans_count, 'disc_count': disc_count, 'fgos_count': fgos_count, 'memos_count': memos_count}
    return render_template_string(DASHBOARD_TEMPLATE, title='Сводная панель', stats=stats, plans=plans, signatures=signatures, announcements=announcements, active_page='dashboard')

@app.route('/plans')
def view_plans():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT c.*, ep.code as prog_code, ep.title as prog_title, ep.level as degree_level, ep.study_form, d.name as dept_name
        FROM curriculums c
        JOIN educational_programs ep ON c.program_id = ep.id
        JOIN departments d ON ep.department_id = d.id
    ''')
    plans = c.fetchall()
    conn.close()
    
    # We use the catalog template from earlier
    from portal.app_templates import PLANS_CATALOG_TEMPLATE
    return render_template_string(PLANS_CATALOG_TEMPLATE, title='Реестр учебных планов', plans=plans, active_page='plans')

@app.route('/plans/<int:plan_id>')
def view_plan(plan_id=1):
    sem = request.args.get('sem', 1, type=int)
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

    # Total disciplines count
    c.execute('SELECT COUNT(*) FROM curriculum_disciplines WHERE curriculum_id = ?', (plan_id,))
    all_disciplines_count = c.fetchone()[0]

    # Filter disciplines by selected semester
    c.execute('''
        SELECT cd.*, d.short_name as impl_short
        FROM curriculum_disciplines cd
        JOIN departments d ON cd.implementing_department_id = d.id
        WHERE cd.curriculum_id = ? AND cd.semester_num = ?
        ORDER BY cd.id
    ''', (plan_id, sem))
    disciplines = c.fetchall()

    # Calculate semester stats
    total_ze = sum(d['credits_ze'] for d in disciplines)
    total_hrs = sum(d['total_hours'] for d in disciplines)
    total_lec = sum(d['lecture_hours'] for d in disciplines)
    total_lab = sum(d['lab_hours'] for d in disciplines)
    total_pr = sum(d['practice_hours'] for d in disciplines)
    total_srs = sum(d['self_study_hours'] for d in disciplines)
    exams_count = sum(1 for d in disciplines if 'Экзамен' in d['control_form'])
    credits_count = sum(1 for d in disciplines if 'Зачет' in d['control_form'])

    sem_stats = {
        'total_ze': total_ze,
        'total_hrs': total_hrs,
        'total_lec': total_lec,
        'total_lab': total_lab,
        'total_pr': total_pr,
        'total_srs': total_srs,
        'exams_count': exams_count,
        'credits_count': credits_count
    }

    conn.close()
    return render_template_string(PLAN_VIEW_TEMPLATE, title=f"Учебный план #{plan_id} (Сем. {sem})", plan=plan, disciplines=disciplines, all_disciplines_count=all_disciplines_count, selected_sem=sem, sem_stats=sem_stats, active_page='plans')

@app.route('/plans/new')
def new_plan():
    return redirect(url_for('view_plan', plan_id=1))

@app.route('/validate/<int:plan_id>')
def validate_plan(plan_id=1):
    from portal.app_templates import VALIDATE_TEMPLATE
    return render_template_string(VALIDATE_TEMPLATE, title="Экспертиза ФГОС 3++", active_page='validate')

@app.route('/signatures')
@app.route('/signatures/<int:plan_id>')
def signatures_view(plan_id=1):
    from portal.app_templates import SIGNATURES_TEMPLATE
    return render_template_string(SIGNATURES_TEMPLATE, title="Маршруты визирования и ЭЦП", active_page='signatures')

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
    from portal.app_templates import MEMOS_TEMPLATE
    return render_template_string(MEMOS_TEMPLATE, title="Служебные записки", memos=memos, active_page='memos')

@app.route('/memos/new')
def new_memo():
    return redirect(url_for('view_memos'))

@app.route('/programs')
def view_programs():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT ep.*, sf.title as fgos_title, d.name as dept_name
        FROM educational_programs ep
        JOIN standards_fgos sf ON ep.fgos_standard_id = sf.id
        JOIN departments d ON ep.department_id = d.id
    ''')
    programs = c.fetchall()
    conn.close()
    from portal.app_templates import PROGRAMS_TEMPLATE
    return render_template_string(PROGRAMS_TEMPLATE, title="Образовательные программы", programs=programs, active_page='programs')

@app.route('/competencies')
def view_competencies():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM competencies')
    comps = c.fetchall()
    conn.close()
    from portal.app_templates import COMPETENCIES_TEMPLATE
    return render_template_string(COMPETENCIES_TEMPLATE, title="Матрица компетенций", comps=comps, active_page='competencies')

@app.route('/standards')
def view_standards():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM standards_fgos')
    standards = c.fetchall()
    conn.close()
    standards_html = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <div class="mb-6"><h1 class="text-2xl font-extrabold text-slate-900">Инфоблок: Справочник стандартов ФГОС ВО 3++</h1></div>
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
    return render_template_string(standards_html, title="Стандарты ФГОС", standards=standards, active_page='standards')

@app.route('/departments')
def view_departments():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM departments')
    depts = c.fetchall()
    conn.close()
    depts_html = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
        <div class="mb-6"><h1 class="text-2xl font-extrabold text-slate-900">Инфоблок: Организационная структура и кафедры университета</h1></div>
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
    return render_template_string(depts_html, title="Кафедры и структуры", depts=depts, active_page='departments')

@app.route('/announcements')
def view_announcements():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM announcements ORDER BY is_pinned DESC, publish_date DESC')
    announcements = c.fetchall()
    conn.close()
    return render_template_string(ANNOUNCEMENTS_TEMPLATE, title="Новости и регламенты АНОК", announcements=announcements, active_page='announcements')

@app.route('/audit')
def view_audit():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM audit_logs ORDER BY id DESC')
    logs = c.fetchall()
    conn.close()
    from portal.app_templates import AUDIT_TEMPLATE
    return render_template_string(AUDIT_TEMPLATE, title="Журнал аудита", logs=logs, active_page='audit')

@app.route('/sitemap')
def view_sitemap():
    from portal.app_templates import SITEMAP_TEMPLATE
    return render_template_string(SITEMAP_TEMPLATE, title="Карта сайта и архитектура", active_page='sitemap')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
