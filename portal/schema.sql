-- SQLite-схема учебного прототипа портала АНОК.
-- База данных приложения: portal/anok_portal.db

PRAGMA foreign_keys = ON;

CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    type TEXT NOT NULL,
    phone TEXT,
    email TEXT
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role_id INTEGER,
    department_id INTEGER,
    position_title TEXT,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE standards_fgos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    degree_level TEXT NOT NULL,
    total_credits INTEGER NOT NULL DEFAULT 240,
    max_exams_per_session INTEGER NOT NULL DEFAULT 5,
    min_practice_credits INTEGER NOT NULL DEFAULT 12,
    min_gia_credits INTEGER NOT NULL DEFAULT 6,
    approval_date TEXT NOT NULL
);

CREATE TABLE educational_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    title TEXT NOT NULL,
    level TEXT NOT NULL,
    study_form TEXT NOT NULL DEFAULT 'Очная',
    fgos_standard_id INTEGER,
    department_id INTEGER,
    FOREIGN KEY (fgos_standard_id) REFERENCES standards_fgos(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE curriculums (
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
);

CREATE TABLE curriculum_disciplines (
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
);

CREATE TABLE service_notes (
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
);

CREATE TABLE service_note_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_note_id INTEGER,
    discipline_id INTEGER,
    change_type TEXT NOT NULL,
    old_val TEXT,
    new_val TEXT,
    FOREIGN KEY (service_note_id) REFERENCES service_notes(id),
    FOREIGN KEY (discipline_id) REFERENCES curriculum_disciplines(id)
);

CREATE TABLE document_signatures (
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
);

CREATE TABLE validation_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curriculum_id INTEGER,
    validator_name TEXT,
    is_compliant INTEGER NOT NULL DEFAULT 0,
    errors_json TEXT,
    warnings_json TEXT,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curriculum_id) REFERENCES curriculums(id)
);

CREATE TABLE competencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    program_id INTEGER,
    code TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (program_id) REFERENCES educational_programs(id)
);

CREATE TABLE announcements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    publish_date TEXT NOT NULL,
    author_name TEXT NOT NULL,
    content TEXT NOT NULL,
    is_pinned INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_time TEXT NOT NULL,
    user_name TEXT NOT NULL,
    user_role TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    status TEXT NOT NULL,
    ip_address TEXT NOT NULL
);
