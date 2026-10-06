# Shared templates for ANOK Portal
from portal.app import BASE_TEMPLATE

PLANS_CATALOG_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Реестр и каталог учебных планов</h1>
            <p class="text-xs text-slate-500 mt-1">Полный массив образовательных программ, версионирование, трудоемкость и закрепленные кафедры</p>
        </div>
        <div class="flex items-center gap-3">
            <a href="/plans/new" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition">
                <i class="fa-solid fa-plus"></i>
                <span>Добавить учебный план</span>
            </a>
        </div>
    </div>

    <!-- Filter Bar -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-wrap gap-4 items-center justify-between text-xs">
        <div class="flex flex-wrap items-center gap-4">
            <div class="flex items-center gap-2">
                <span class="font-bold text-slate-700">Учебный год:</span>
                <select class="border border-slate-300 rounded px-2 py-1 text-xs bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option>2026/2027</option>
                    <option>2025/2026</option>
                </select>
            </div>
            <div class="flex items-center gap-2">
                <span class="font-bold text-slate-700">Уровень:</span>
                <select class="border border-slate-300 rounded px-2 py-1 text-xs bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option>Все уровни</option>
                    <option>Бакалавриат (240 з.е.)</option>
                    <option>Специалитет (300 з.е.)</option>
                    <option>Магистратура (120 з.е.)</option>
                </select>
            </div>
            <div class="flex items-center gap-2">
                <span class="font-bold text-slate-700">Статус:</span>
                <select class="border border-slate-300 rounded px-2 py-1 text-xs bg-slate-50 focus:outline-none focus:ring-1 focus:ring-blue-500">
                    <option>Все статусы</option>
                    <option>Соответствует ФГОС</option>
                    <option>На экспертизе АНОК</option>
                    <option>Утвержден Ректором</option>
                </select>
            </div>
        </div>
        <div class="text-slate-400 font-mono text-[11px]">Найдено планов: <b>{{ plans|length }}</b></div>
    </div>

    <!-- Plans Table -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
                <tr>
                    <th class="px-5 py-3">ID</th>
                    <th class="px-4 py-3">Направление подготовки / Программа</th>
                    <th class="px-4 py-3">Уровень / Форма</th>
                    <th class="px-4 py-3">Выпускающая кафедра</th>
                    <th class="px-4 py-3 text-center">ЗЕТ</th>
                    <th class="px-4 py-3 text-center">Версия</th>
                    <th class="px-4 py-3">Статус</th>
                    <th class="px-5 py-3 text-right">Управление</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {% for p in plans %}
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-4 font-mono font-bold text-slate-400">#{{ p.id }}</td>
                    <td class="px-4 py-4">
                        <div class="font-bold text-slate-900 flex items-center gap-2">
                            <span class="font-mono text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-800">{{ p.prog_code }}</span>
                            <a href="/plans/{{ p.id }}" class="hover:text-blue-600 transition">{{ p.prog_title }}</a>
                        </div>
                        <div class="text-[11px] text-slate-400 mt-1">Год: {{ p.academic_year }} • Автор: {{ p.created_by_user }}</div>
                    </td>
                    <td class="px-4 py-4 text-slate-600">
                        <span class="font-bold block text-slate-800">{{ p.degree_level }}</span>
                        <span class="text-[11px] text-slate-400">{{ p.study_form }}</span>
                    </td>
                    <td class="px-4 py-4 text-slate-600 font-medium">{{ p.dept_name }}</td>
                    <td class="px-4 py-4 text-center font-mono font-bold text-slate-900">{{ p.total_credits }}</td>
                    <td class="px-4 py-4 text-center font-mono font-bold text-blue-600">v{{ p.version }}</td>
                    <td class="px-4 py-4">
                        {% if p.status == 'APPROVED_RECTOR' %}
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">УТВЕРЖДЕН</span>
                        {% elif p.status == 'ON_REVIEW_ANOK' %}
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-200">НА ЭКСПЕРТИЗЕ</span>
                        {% elif p.status == 'REJECTED_ANOK' %}
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-100 text-red-800 border border-red-200">ОШИБКИ ФГОС</span>
                        {% else %}
                            <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">{{ p.status }}</span>
                        {% endif %}
                    </td>
                    <td class="px-5 py-4 text-right space-x-1">
                        <a href="/plans/{{ p.id }}" class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs transition">
                            <i class="fa-solid fa-table-cells"></i> Матрица
                        </a>
                        <a href="/validate/{{ p.id }}" class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded bg-slate-800 hover:bg-slate-900 text-white font-bold text-xs transition">
                            <i class="fa-solid fa-shield-halved"></i> Валидатор
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
''')

VALIDATE_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <!-- Inspection Banner -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mb-8">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div>
                <div class="flex items-center gap-3">
                    <span class="w-8 h-8 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm">
                        <i class="fa-solid fa-check-double"></i>
                    </span>
                    <h1 class="text-xl font-extrabold text-slate-900">Инфоблок: Экспертное заключение валидатора ФГОС ВО 3++</h1>
                </div>
                <p class="text-xs text-slate-500 mt-2">
                    Автоматизированный аудит соответствия учебного плана требованиям Федерального государственного образовательного стандарта 
                    <span class="font-bold text-slate-800">№ 09.03.01 (Приказ Минобрнауки РФ № 924)</span>
                </p>
            </div>

            <div class="flex items-center gap-3">
                <span class="px-3 py-1.5 rounded-lg bg-emerald-100 text-emerald-800 border border-emerald-300 text-xs font-bold">
                    <i class="fa-solid fa-circle-check mr-1.5"></i> 100% СООТВЕТСТВИЕ СТАНДАРТУ
                </span>
                <a href="/signatures/1" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold shadow-sm transition">
                    Допустить к визированию →
                </a>
            </div>
        </div>

        <!-- 4 Compliance KPI Boxes -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-100 text-xs">
            <div class="bg-emerald-50/60 p-4 rounded-xl border border-emerald-200">
                <span class="text-emerald-800 font-bold block uppercase text-[10px]">1. Общий объем программы</span>
                <span class="text-xl font-extrabold text-emerald-900 font-mono mt-1 block">240 / 240 ЗЕТ</span>
                <span class="text-[11px] text-emerald-700 mt-1 block">Норма выполнена на 100%</span>
            </div>
            <div class="bg-emerald-50/60 p-4 rounded-xl border border-emerald-200">
                <span class="text-emerald-800 font-bold block uppercase text-[10px]">2. Экзамены в сессию</span>
                <span class="text-xl font-extrabold text-emerald-900 font-mono mt-1 block">Макс. 4 экз.</span>
                <span class="text-[11px] text-emerald-700 mt-1 block">Лимит не превышен (&le; 5)</span>
            </div>
            <div class="bg-emerald-50/60 p-4 rounded-xl border border-emerald-200">
                <span class="text-emerald-800 font-bold block uppercase text-[10px]">3. Практики и НИР</span>
                <span class="text-xl font-extrabold text-emerald-900 font-mono mt-1 block">24 ЗЕТ (мин. 12)</span>
                <span class="text-[11px] text-emerald-700 mt-1 block">Требование стандарта соблюдено</span>
            </div>
            <div class="bg-emerald-50/60 p-4 rounded-xl border border-emerald-200">
                <span class="text-emerald-800 font-bold block uppercase text-[10px]">4. Итоговая аттестация (ГИА)</span>
                <span class="text-xl font-extrabold text-emerald-900 font-mono mt-1 block">9 ЗЕТ (мин. 6)</span>
                <span class="text-[11px] text-emerald-700 mt-1 block">ВКР + Защита диплома</span>
            </div>
        </div>
    </div>

    <!-- Detailed Checklist Table -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-8">
        <div class="p-5 border-b border-slate-200 bg-slate-50/50">
            <h2 class="text-sm font-bold text-slate-900">Детализированная матрица проверки обязательных нормативов ФГОС ВО 3++</h2>
            <p class="text-xs text-slate-500 mt-0.5">Сравнение нормативных требований образовательного стандарта и фактических параметров УП</p>
        </div>

        <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
                <tr>
                    <th class="px-5 py-3">№</th>
                    <th class="px-4 py-3">Контролируемый норматив стандарта</th>
                    <th class="px-4 py-3">Нормативное требование</th>
                    <th class="px-4 py-3">Фактическое значение в УП</th>
                    <th class="px-5 py-3 text-right">Результат экспертизы</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 font-mono font-bold text-slate-400">1</td>
                    <td class="px-4 py-3.5 font-bold text-slate-900">Суммарный объем программы бакалавриата</td>
                    <td class="px-4 py-3.5 text-slate-600 font-mono">Ровно 240 з.е.</td>
                    <td class="px-4 py-3.5 font-bold font-mono text-emerald-700">240 з.е. (100%)</td>
                    <td class="px-5 py-3.5 text-right">
                        <span class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">СООТВЕТСТВУЕТ</span>
                    </td>
                </tr>
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 font-mono font-bold text-slate-400">2</td>
                    <td class="px-4 py-3.5 font-bold text-slate-900">Годовая трудоемкость учебного плана</td>
                    <td class="px-4 py-3.5 text-slate-600 font-mono">60 з.е. в год (&plusmn;3 з.е.)</td>
                    <td class="px-4 py-3.5 font-bold font-mono text-emerald-700">1 курс: 60, 2 курс: 60, 3 курс: 60, 4 курс: 60</td>
                    <td class="px-5 py-3.5 text-right">
                        <span class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">СООТВЕТСТВУЕТ</span>
                    </td>
                </tr>
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 font-mono font-bold text-slate-400">3</td>
                    <td class="px-4 py-3.5 font-bold text-slate-900">Лимит экзаменационных испытаний в одну сессию</td>
                    <td class="px-4 py-3.5 text-slate-600 font-mono">Не более 5 экзаменов</td>
                    <td class="px-4 py-3.5 font-bold font-mono text-emerald-700">Сем.1: 4 экз., Сем.2: 4 экз., Сем.3: 5 экз.</td>
                    <td class="px-5 py-3.5 text-right">
                        <span class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">СООТВЕТСТВУЕТ</span>
                    </td>
                </tr>
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 font-mono font-bold text-slate-400">4</td>
                    <td class="px-4 py-3.5 font-bold text-slate-900">Обязательная часть Блока 1 (Б1.О)</td>
                    <td class="px-4 py-3.5 text-slate-600 font-mono">Не менее 50% от Блока 1</td>
                    <td class="px-4 py-3.5 font-bold font-mono text-emerald-700">62.5% (130 из 207 з.е.)</td>
                    <td class="px-5 py-3.5 text-right">
                        <span class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">СООТВЕТСТВУЕТ</span>
                    </td>
                </tr>
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 font-mono font-bold text-slate-400">5</td>
                    <td class="px-4 py-3.5 font-bold text-slate-900">Блок 2 «Практика» (учебная, производственная, преддипломная)</td>
                    <td class="px-4 py-3.5 text-slate-600 font-mono">Не менее 12 з.е.</td>
                    <td class="px-4 py-3.5 font-bold font-mono text-emerald-700">24 з.е.</td>
                    <td class="px-5 py-3.5 text-right">
                        <span class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">СООТВЕТСТВУЕТ</span>
                    </td>
                </tr>
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 font-mono font-bold text-slate-400">6</td>
                    <td class="px-4 py-3.5 font-bold text-slate-900">Блок 3 «Государственная итоговая аттестация»</td>
                    <td class="px-4 py-3.5 text-slate-600 font-mono">Не менее 6 з.е.</td>
                    <td class="px-4 py-3.5 font-bold font-mono text-emerald-700">9 з.е.</td>
                    <td class="px-5 py-3.5 text-right">
                        <span class="px-2.5 py-1 rounded bg-emerald-100 text-emerald-800 font-bold text-[10px]">СООТВЕТСТВУЕТ</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
''')

SIGNATURES_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Маршруты визирования и реестр ЭЦП</h1>
            <p class="text-xs text-slate-500 mt-1">Регламент последовательного согласования УП должностными лицами вуза (Вариант №15)</p>
        </div>
    </div>

    <!-- Active Signing Card -->
    <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 mb-8">
        <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
            <div>
                <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">УП #1 • 09.03.01 ИВТ</span>
                <h2 class="text-base font-bold text-slate-900 mt-1">Маршрут согласования учебного плана 2026/2027</h2>
            </div>
            <span class="text-xs font-bold text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1 rounded-full">
                Текущий этап: Проректор по УР
            </span>
        </div>

        <!-- 4 Step Stepper -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <div class="flex items-center justify-between">
                    <span class="w-6 h-6 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center"><i class="fa-solid fa-check text-[10px]"></i></span>
                    <span class="text-[10px] font-bold text-emerald-800">ЭТАП 1</span>
                </div>
                <h4 class="text-xs font-bold text-slate-900 mt-2">Зав. выпускающей кафедрой</h4>
                <p class="text-[11px] text-slate-500">Иванов И.И.</p>
                <p class="text-[10px] font-mono text-emerald-700 mt-2 font-bold"><i class="fa-solid fa-signature mr-1"></i>03.10.2026 11:20 (ЭЦП)</p>
            </div>

            <div class="p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                <div class="flex items-center justify-between">
                    <span class="w-6 h-6 rounded-full bg-emerald-600 text-white font-bold text-xs flex items-center justify-center"><i class="fa-solid fa-check text-[10px]"></i></span>
                    <span class="text-[10px] font-bold text-emerald-800">ЭТАП 2</span>
                </div>
                <h4 class="text-xs font-bold text-slate-900 mt-2">Начальник Центра АНОК</h4>
                <p class="text-[11px] text-slate-500">Соловьёв А.С.</p>
                <p class="text-[10px] font-mono text-emerald-700 mt-2 font-bold"><i class="fa-solid fa-signature mr-1"></i>04.10.2026 15:45 (ЭЦП)</p>
            </div>

            <div class="p-4 rounded-xl bg-amber-50 border border-amber-300 ring-2 ring-amber-400/40">
                <div class="flex items-center justify-between">
                    <span class="w-6 h-6 rounded-full bg-amber-500 text-white font-bold text-xs flex items-center justify-center">3</span>
                    <span class="text-[10px] font-bold text-amber-800 animate-pulse">АКТИВНЫЙ ЭТАП</span>
                </div>
                <h4 class="text-xs font-bold text-slate-900 mt-2">Проректор по УР</h4>
                <p class="text-[11px] text-slate-500">Петров В.И.</p>
                <p class="text-[10px] font-mono text-amber-700 mt-2 font-bold"><i class="fa-solid fa-clock mr-1"></i>В очереди на подписание</p>
            </div>

            <div class="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <div class="flex items-center justify-between">
                    <span class="w-6 h-6 rounded-full bg-slate-300 text-slate-700 font-bold text-xs flex items-center justify-center">4</span>
                    <span class="text-[10px] font-bold text-slate-400">ФИНАЛ</span>
                </div>
                <h4 class="text-xs font-bold text-slate-900 mt-2">Ученый совет и Ректор</h4>
                <p class="text-[11px] text-slate-500">Воронов М.Н.</p>
                <p class="text-[10px] font-mono text-slate-400 mt-2">Утверждение и приказ</p>
            </div>
        </div>

        <!-- Signing Action Form -->
        <div class="bg-slate-50 rounded-xl p-5 border border-slate-200">
            <h3 class="text-xs font-bold text-slate-900 uppercase tracking-wider mb-3">Форма подписания документа усиленной квалифицированной ЭЦП</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mb-4">
                <div class="p-3 bg-white rounded-lg border border-slate-200 font-mono text-[11px]">
                    <span class="text-slate-400 font-sans text-[10px] uppercase font-bold block mb-1">Контрольный хеш документа (SHA-256):</span>
                    <span class="text-blue-600 font-bold break-all">a7f5c9e2b1d408f617a29c3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a</span>
                </div>
                <div class="p-3 bg-white rounded-lg border border-slate-200">
                    <span class="text-slate-400 text-[10px] uppercase font-bold block mb-1">Сертификат должностного лица:</span>
                    <span class="font-bold text-slate-800">Петров В.И. (Проректор по учебной работе)</span>
                    <span class="text-slate-400 text-[11px] block mt-0.5">УЦ Федерального Казначейства РФ • Действителен до 31.12.2027</span>
                </div>
            </div>

            <div class="flex flex-wrap items-center gap-3">
                <input type="password" placeholder="Введите PIN-код ключевого носителя..." class="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs w-64 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <button onclick="alert('Документ успешно подписан ЭЦП и передан на этап 4 (Ученый совет и Ректор)!')" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold shadow-sm transition">
                    <i class="fa-solid fa-key mr-1.5"></i> Наложить ЭЦП и отправить
                </button>
            </div>
        </div>
    </div>
''')

MEMOS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Служебные записки и актуализация УП</h1>
            <p class="text-xs text-slate-500 mt-1">Регламент внесения изменений в утвержденный УП до начала семестра (двустороннее визирование кафедрами)</p>
        </div>
        <a href="/memos/new" class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold transition">
            <i class="fa-solid fa-plus"></i>
            <span>Создать служебную записку</span>
        </a>
    </div>

    <!-- Memos list -->
    <div class="space-y-6">
        {% for m in memos %}
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-100">
                <div>
                    <div class="flex items-center gap-3">
                        <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">{{ m.note_num }}</span>
                        <h3 class="text-sm font-bold text-slate-900">{{ m.reason }}</h3>
                        {% if m.status == 'APPLIED' %}
                            <span class="text-[10px] px-2 py-0.5 rounded font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">ПРИМЕНЕНО В АНОК (v1.1)</span>
                        {% else %}
                            <span class="text-[10px] px-2 py-0.5 rounded font-bold bg-amber-100 text-amber-800 border border-amber-200">НА СОГЛАСОВАНИИ</span>
                        {% endif %}
                    </div>
                    <div class="flex flex-wrap items-center gap-x-6 gap-y-1 text-xs text-slate-500 mt-2">
                        <span><i class="fa-solid fa-calendar mr-1 text-slate-400"></i>Дата: <b>{{ m.note_date }}</b></span>
                        <span><i class="fa-solid fa-user-pen mr-1 text-slate-400"></i>Инициатор: <b>{{ m.created_by }}</b> ({{ m.rel_name }})</span>
                        <span><i class="fa-solid fa-building mr-1 text-slate-400"></i>Обеспечивающая кафедра: <b>{{ m.impl_name }}</b></span>
                    </div>
                </div>
            </div>

            <!-- Diff Comparison Box -->
            <div class="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
                <span class="text-slate-400 font-bold uppercase text-[10px] block mb-2">Протокол внесенных изменений («Было» / «Стало»):</span>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                    <div class="p-3 rounded-lg bg-red-50 text-red-900 border border-red-200">
                        <span class="font-bold font-sans text-[10px] text-red-700 block mb-1">&minus; БЫЛО В УЧЕБНОМ ПЛАНЕ (v1.0):</span>
                        Математический анализ • Семестр 1 • Трудоемкость: 3 з.е. (108 ч.) • Форма: Зачет
                    </div>
                    <div class="p-3 rounded-lg bg-emerald-50 text-emerald-900 border border-emerald-200">
                        <span class="font-bold font-sans text-[10px] text-emerald-700 block mb-1">&plus; СТАЛО (АКТУАЛИЗИРОВАНО В АНОК v1.1):</span>
                        Математический анализ • Семестр 1 • Трудоемкость: 5 з.е. (180 ч.) • Форма: Экзамен
                    </div>
                </div>
            </div>

            <!-- Signatures of two depts -->
            <div class="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500">
                <div class="flex items-center gap-4">
                    <span class="text-emerald-700 font-bold"><i class="fa-solid fa-check-circle mr-1"></i> Виза выпускающей каф. (ЭЦП)</span>
                    <span class="text-emerald-700 font-bold"><i class="fa-solid fa-check-circle mr-1"></i> Виза реализующей каф. (ЭЦП)</span>
                </div>
                <span class="text-blue-700 font-bold">Проверено АНОК на баланс 240 ЗЕТ</span>
            </div>
        </div>
        {% endfor %}
    </div>
''')

PROGRAMS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Каталог образовательных программ ВО</h1>
            <p class="text-xs text-slate-500 mt-1">Реестр направлений подготовки бакалавриата, специалитета и магистратуры</p>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for p in programs %}
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition">
            <div>
                <div class="flex items-center justify-between">
                    <span class="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-100 text-blue-800">{{ p.code }}</span>
                    <span class="text-xs font-bold px-2 py-0.5 rounded
                        {% if p.level == 'Бакалавриат' %}bg-emerald-100 text-emerald-800
                        {% elif p.level == 'Специалитет' %}bg-amber-100 text-amber-800
                        {% else %}bg-purple-100 text-purple-800{% endif %}">
                        {{ p.level }}
                    </span>
                </div>
                <h3 class="font-bold text-slate-900 text-base mt-3">{{ p.title }}</h3>
                <div class="mt-4 space-y-1.5 text-xs text-slate-600">
                    <p><i class="fa-solid fa-scale-balanced mr-1.5 text-slate-400"></i>Стандарт: <b>{{ p.fgos_title }}</b></p>
                    <p><i class="fa-solid fa-building-columns mr-1.5 text-slate-400"></i>Кафедра: <b>{{ p.dept_name }}</b></p>
                    <p><i class="fa-solid fa-clock mr-1.5 text-slate-400"></i>Форма: <b>{{ p.study_form }}</b></p>
                </div>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-100">
                <a href="/plans/1" class="text-xs font-bold text-blue-600 hover:text-blue-800 flex items-center justify-between">
                    <span>Перейти к учебным планам</span>
                    <i class="fa-solid fa-arrow-right"></i>
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
''')

COMPETENCIES_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Матрица компетенций ФГОС ВО 3++</h1>
            <p class="text-xs text-slate-500 mt-1">Универсальные (УК), общепрофессиональные (ОПК) и профессиональные (ПК) компетенции программы</p>
        </div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table class="w-full text-left text-xs">
            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
                <tr>
                    <th class="px-5 py-3">Код</th>
                    <th class="px-4 py-3">Категория</th>
                    <th class="px-4 py-3">Наименование компетенции</th>
                    <th class="px-5 py-3">Индикаторы достижения и дескриптор</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {% for c in comps %}
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-4 font-mono font-bold text-blue-700 bg-blue-50/30">{{ c.code }}</td>
                    <td class="px-4 py-4">
                        <span class="px-2 py-0.5 rounded font-bold text-[10px]
                            {% if c.category == 'Универсальные' %}bg-slate-100 text-slate-800
                            {% elif c.category == 'Общепрофессиональные' %}bg-blue-100 text-blue-800
                            {% else %}bg-purple-100 text-purple-800{% endif %}">
                            {{ c.category }}
                        </span>
                    </td>
                    <td class="px-4 py-4 font-bold text-slate-900">{{ c.title }}</td>
                    <td class="px-5 py-4 text-slate-600 leading-relaxed">{{ c.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
''')

AUDIT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Инфоблок: Журнал аудита действий и история версий</h1>
            <p class="text-xs text-slate-500 mt-1">Протоколирование всех транзакций создания, валидации по ФГОС, наложения ЭЦП и актуализации</p>
        </div>
    </div>

    <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <table class="w-full text-left text-xs font-mono">
            <thead class="bg-slate-50 text-slate-500 font-bold border-b border-slate-200 font-sans">
                <tr>
                    <th class="px-5 py-3">Время события</th>
                    <th class="px-4 py-3">Пользователь / Роль</th>
                    <th class="px-4 py-3">Выполненное действие</th>
                    <th class="px-4 py-3">Объект системы</th>
                    <th class="px-4 py-3">IP-адрес</th>
                    <th class="px-5 py-3 text-right">Статус</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
                {% for log in logs %}
                <tr class="hover:bg-slate-50/80 transition">
                    <td class="px-5 py-3.5 text-slate-500 text-[11px]">{{ log.event_time }}</td>
                    <td class="px-4 py-3.5 font-sans font-bold text-slate-900">
                        {{ log.user_name }}
                        <span class="text-[10px] text-slate-400 block font-normal">{{ log.user_role }}</span>
                    </td>
                    <td class="px-4 py-3.5 font-sans text-slate-800">{{ log.action }}</td>
                    <td class="px-4 py-3.5 text-blue-700 font-bold">{{ log.entity_name }}</td>
                    <td class="px-4 py-3.5 text-slate-400">{{ log.ip_address }}</td>
                    <td class="px-5 py-3.5 text-right font-sans">
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">{{ log.status }}</span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
''')

SITEMAP_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
            <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Информационная карта сайта (Sitemap)</h1>
            <p class="text-xs text-slate-500 mt-1">Иерархическая структура инфоблоков, страниц и ролевая матрица доступа (RBAC)</p>
        </div>
    </div>

    <!-- Sitemap Cards Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div class="flex items-center gap-3 text-blue-600 mb-4 pb-3 border-b border-slate-100">
                <i class="fa-solid fa-book-bookmark text-lg"></i>
                <h3 class="font-bold text-slate-900 text-sm">1. Учебные планы и программы</h3>
            </div>
            <ul class="space-y-2.5 text-xs text-slate-600">
                <li><a href="/plans" class="font-bold text-blue-600 hover:underline">/plans</a> — Реестр учебных планов</li>
                <li><a href="/plans/1" class="font-bold text-blue-600 hover:underline">/plans/&lt;id&gt;</a> — Семестровая матрица УП</li>
                <li><a href="/programs" class="font-bold text-blue-600 hover:underline">/programs</a> — Каталог программ ВО</li>
                <li><a href="/competencies" class="font-bold text-blue-600 hover:underline">/competencies</a> — Матрица компетенций ФГОС</li>
            </ul>
        </div>

        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div class="flex items-center gap-3 text-emerald-600 mb-4 pb-3 border-b border-slate-100">
                <i class="fa-solid fa-shield-halved text-lg"></i>
                <h3 class="font-bold text-slate-900 text-sm">2. Экспертиза и стандарты ФГОС</h3>
            </div>
            <ul class="space-y-2.5 text-xs text-slate-600">
                <li><a href="/validate/1" class="font-bold text-emerald-600 hover:underline">/validate/&lt;id&gt;</a> — Модуль валидации ФГОС 3++</li>
                <li><a href="/standards" class="font-bold text-emerald-600 hover:underline">/standards</a> — Справочник стандартов ФГОС</li>
                <li><a href="/departments" class="font-bold text-emerald-600 hover:underline">/departments</a> — Кафедры и структуры вуза</li>
            </ul>
        </div>

        <div class="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <div class="flex items-center gap-3 text-purple-600 mb-4 pb-3 border-b border-slate-100">
                <i class="fa-solid fa-signature text-lg"></i>
                <h3 class="font-bold text-slate-900 text-sm">3. Документооборот и визирование</h3>
            </div>
            <ul class="space-y-2.5 text-xs text-slate-600">
                <li><a href="/signatures" class="font-bold text-purple-600 hover:underline">/signatures</a> — Очередь визирования</li>
                <li><a href="/signatures/1" class="font-bold text-purple-600 hover:underline">/signatures/&lt;id&gt;</a> — Наложение ЭЦП (SHA-256)</li>
                <li><a href="/memos" class="font-bold text-purple-600 hover:underline">/memos</a> — Служебные записки (Diff)</li>
                <li><a href="/announcements" class="font-bold text-purple-600 hover:underline">/announcements</a> — Новости и регламенты</li>
            </ul>
        </div>
    </div>
''')
