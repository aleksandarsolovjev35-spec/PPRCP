# Лабораторная работа № 5
## Работа с инфоблоками

**Вариант 15:** Университет. Центр АНОК

Информационные блоки портала связаны с таблицами MySQL/MariaDB:

| Блок | Таблица |
|---|---|
| Учебные планы | `curriculums` |
| Дисциплины | `curriculum_disciplines` |
| Стандарты ФГОС | `standards_fgos` |
| Программы | `educational_programs` |
| Подразделения | `departments` |
| Компетенции | `competencies` |
| Служебные записки | `service_notes` |
| Согласование | `document_signatures` |
| Объявления | `announcements` |
| Аудит | `audit_logs` |

Демонстрационные записи загружаются из `portal/database/seed.sql`. Страницы приложения выводят их в таблицах и карточках.

![Учебные планы](../../diagrams/lab5/infoblock_curriculums_filled.png)
![Проверка ФГОС](../../diagrams/lab5/infoblock_fgos_validation_filled.png)
![Служебные записки](../../diagrams/lab5/infoblock_memos_diff_filled.png)
![Программы и стандарты](../../diagrams/lab5/infoblock_programs_standards_filled.png)
![Компетенции](../../diagrams/lab5/infoblock_competencies_matrix_filled.png)
![Подразделения](../../diagrams/lab5/infoblock_departments_structure_filled.png)
![Объявления](../../diagrams/lab5/infoblock_news_announcements_filled.png)
![Согласование](../../diagrams/lab5/infoblock_signatures_workflow_filled.png)

## Заключение

Страницы портала наполнены связанными демонстрационными данными из MySQL/MariaDB.
