-- =========================================================================
-- СХЕМА БАЗЫ ДАННЫХ КОРПОРАТИВНОГО ПОРТАЛА (МОДУЛЬ АНОК)
-- СУБД: MariaDB 10.6+ / MySQL 8.0+
-- Вариант № 15: Университет. Центр Аккредитации и независимой оценки качества
-- =========================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Справочник ролей пользователей (RBAC)
DROP TABLE IF EXISTS roles;
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(64) NOT NULL,
    code VARCHAR(32) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Справочник подразделений вуза (кафедры, деканаты, АНОК, ректорат)
DROP TABLE IF EXISTS departments;
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(32) NOT NULL,
    type ENUM('RELEASING', 'IMPLEMENTING', 'EXPERT_ANOK', 'MANAGEMENT') NOT NULL,
    head_user_id INT NULL,
    phone VARCHAR(32),
    email VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Пользователи системы
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    full_name VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    department_id INT NOT NULL,
    position_title VARCHAR(128),
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Стандарты ФГОС ВО (3++)
DROP TABLE IF EXISTS standards_fgos;
CREATE TABLE standards_fgos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(16) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    degree_level ENUM('BACHELOR', 'SPECIALIST', 'MASTER', 'POSTGRADUATE') NOT NULL,
    total_credits INT NOT NULL DEFAULT 240,
    max_exams_per_session INT NOT NULL DEFAULT 5,
    max_credits_per_year INT NOT NULL DEFAULT 60,
    min_practice_credits INT NOT NULL DEFAULT 12,
    min_gia_credits INT NOT NULL DEFAULT 6,
    approval_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Образовательные программы
DROP TABLE IF EXISTS educational_programs;
CREATE TABLE educational_programs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(16) NOT NULL,
    title VARCHAR(255) NOT NULL,
    level ENUM('BACHELOR', 'SPECIALIST', 'MASTER', 'POSTGRADUATE') NOT NULL,
    study_form ENUM('FULL_TIME', 'PART_TIME', 'EXTRAMURAL') NOT NULL DEFAULT 'FULL_TIME',
    fgos_standard_id INT NOT NULL,
    department_id INT NOT NULL,
    head_id INT NULL,
    is_active TINYINT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fgos_standard_id) REFERENCES standards_fgos(id) ON DELETE RESTRICT,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
    FOREIGN KEY (head_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Учебные планы
DROP TABLE IF EXISTS curriculums;
CREATE TABLE curriculums (
    id INT AUTO_INCREMENT PRIMARY KEY,
    program_id INT NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    version VARCHAR(8) NOT NULL DEFAULT '1.0',
    status ENUM(
        'DRAFT', 
        'ON_REVIEW_ANOK', 
        'REJECTED_ANOK', 
        'SIGNING_RELEASING', 
        'SIGNING_ANOK', 
        'SIGNING_VICE_RECTOR', 
        'APPROVED_COUNCIL', 
        'APPROVED_RECTOR', 
        'ARCHIVED'
    ) NOT NULL DEFAULT 'DRAFT',
    total_credits INT NOT NULL DEFAULT 0,
    approved_protocol_num VARCHAR(32) NULL,
    approved_protocol_date DATE NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (program_id) REFERENCES educational_programs(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Дисциплины учебного плана
DROP TABLE IF EXISTS curriculum_disciplines;
CREATE TABLE curriculum_disciplines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curriculum_id INT NOT NULL,
    block_type ENUM('BASE', 'VAR', 'PRACTICE', 'GIA', 'OPTIONAL') NOT NULL DEFAULT 'BASE',
    discipline_name VARCHAR(255) NOT NULL,
    semester_num INT NOT NULL,
    credits_ze INT NOT NULL,
    total_hours INT NOT NULL,
    lecture_hours INT NOT NULL DEFAULT 0,
    lab_hours INT NOT NULL DEFAULT 0,
    practice_hours INT NOT NULL DEFAULT 0,
    self_study_hours INT NOT NULL DEFAULT 0,
    control_form ENUM('EXAM', 'CREDIT', 'GRADED_CREDIT', 'COURSE_WORK', 'GIA') NOT NULL DEFAULT 'EXAM',
    implementing_department_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curriculum_id) REFERENCES curriculums(id) ON DELETE CASCADE,
    FOREIGN KEY (implementing_department_id) REFERENCES departments(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Служебные записки на изменение УП до начала семестра
DROP TABLE IF EXISTS service_notes;
CREATE TABLE service_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curriculum_id INT NOT NULL,
    note_num VARCHAR(32) NOT NULL,
    note_date DATE NOT NULL,
    reason TEXT NOT NULL,
    releasing_dept_id INT NOT NULL,
    implementing_dept_id INT NOT NULL,
    status ENUM('DRAFT', 'SIGNED_RELEASING', 'SIGNED_IMPLEMENTING', 'IN_ANOK', 'APPLIED', 'REJECTED') NOT NULL DEFAULT 'DRAFT',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curriculum_id) REFERENCES curriculums(id) ON DELETE CASCADE,
    FOREIGN KEY (releasing_dept_id) REFERENCES departments(id) ON DELETE RESTRICT,
    FOREIGN KEY (implementing_dept_id) REFERENCES departments(id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Позиции изменений в служебной записке («Было» / «Стало»)
DROP TABLE IF EXISTS service_note_items;
CREATE TABLE service_note_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_note_id INT NOT NULL,
    discipline_id INT NULL,
    change_type ENUM('MODIFY', 'ADD', 'REMOVE') NOT NULL DEFAULT 'MODIFY',
    old_values_json JSON NULL,
    new_values_json JSON NOT NULL,
    status VARCHAR(32) DEFAULT 'PENDING',
    FOREIGN KEY (service_note_id) REFERENCES service_notes(id) ON DELETE CASCADE,
    FOREIGN KEY (discipline_id) REFERENCES curriculum_disciplines(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Электронные подписи и маршруты согласования документов
DROP TABLE IF EXISTS document_signatures;
CREATE TABLE document_signatures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doc_type ENUM('CURRICULUM', 'SERVICE_NOTE') NOT NULL,
    doc_id INT NOT NULL,
    step_order INT NOT NULL DEFAULT 1,
    signer_user_id INT NOT NULL,
    role_title VARCHAR(128) NOT NULL,
    status ENUM('PENDING', 'SIGNED', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    comment TEXT,
    signed_at TIMESTAMP NULL,
    sign_hash VARCHAR(128) NULL,
    FOREIGN KEY (signer_user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Отчеты валидации и журнал аудита ФГОС
DROP TABLE IF EXISTS validation_reports;
CREATE TABLE validation_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    curriculum_id INT NOT NULL,
    validator_user_id INT NOT NULL,
    is_compliant TINYINT NOT NULL DEFAULT 0,
    errors_list JSON,
    warnings_list JSON,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curriculum_id) REFERENCES curriculums(id) ON DELETE CASCADE,
    FOREIGN KEY (validator_user_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
