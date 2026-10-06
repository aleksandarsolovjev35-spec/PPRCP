# Портал АНОК на PHP и MySQL/MariaDB

## Запуск

Создать базу и пользователя MySQL/MariaDB, затем выполнить:

```bash
mysql -u root -p -e "CREATE DATABASE anok_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p anok_portal < database/schema.sql
mysql -u root -p anok_portal < database/seed.sql
```

Настроить переменные `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` и запустить встроенный сервер:

```bash
php -S 127.0.0.1:8000 -t portal_php
```
