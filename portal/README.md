# Портал АНОК

Информационная система Центра аккредитации и независимой оценки качества (АНОК) для автоматизированной настройки и валидации образовательного контента и учебных планов.

## Быстрый запуск (Python / встроенный SQLite)

База данных SQLite автоматически инициализируется из `database/schema.sql` и `database/seed.sql` при первом запуске:

```bash
python3 server.py
# или
python3 portal/server.py
```

Портал будет доступен по адресу `http://localhost:8000` (или `http://0.0.0.0:8000`).

## Запуск на PHP и MySQL/MariaDB

Создать базу и пользователя MySQL/MariaDB, затем выполнить:

```bash
mysql -u root -p -e "CREATE DATABASE anok_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p anok_portal < database/schema.sql
mysql -u root -p anok_portal < database/seed.sql
```

Настроить переменные `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` и запустить встроенный сервер:

```bash
php -S 0.0.0.0:8000 -t portal
```
