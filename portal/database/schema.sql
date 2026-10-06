SET FOREIGN_KEY_CHECKS=0;
CREATE TABLE `announcements` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` TEXT NOT NULL,
  `category` TEXT NOT NULL,
  `publish_date` TEXT NOT NULL,
  `author_name` TEXT NOT NULL,
  `content` TEXT NOT NULL,
  `is_pinned` INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `audit_logs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `event_time` TEXT NOT NULL,
  `user_name` TEXT NOT NULL,
  `user_role` TEXT NOT NULL,
  `action` TEXT NOT NULL,
  `entity_name` TEXT NOT NULL,
  `status` TEXT NOT NULL,
  `ip_address` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `competencies` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `program_id` INT,
  `code` TEXT NOT NULL,
  `category` TEXT NOT NULL,
  `title` TEXT NOT NULL,
  `description` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `curriculum_disciplines` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `curriculum_id` INT,
  `block_type` TEXT NOT NULL,
  `discipline_name` TEXT NOT NULL,
  `semester_num` INT NOT NULL,
  `credits_ze` INT NOT NULL,
  `total_hours` INT NOT NULL,
  `lecture_hours` INT NOT NULL DEFAULT 0,
  `lab_hours` INT NOT NULL DEFAULT 0,
  `practice_hours` INT NOT NULL DEFAULT 0,
  `self_study_hours` INT NOT NULL DEFAULT 0,
  `control_form` TEXT NOT NULL,
  `implementing_department_id` INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `curriculums` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `program_id` INT,
  `academic_year` TEXT NOT NULL,
  `version` TEXT NOT NULL DEFAULT '1.0',
  `status` TEXT NOT NULL DEFAULT 'DRAFT',
  `total_credits` INT NOT NULL DEFAULT 240,
  `approved_protocol_num` TEXT,
  `approved_protocol_date` TEXT,
  `created_by_user` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `departments` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` TEXT NOT NULL,
  `short_name` TEXT NOT NULL,
  `type` TEXT NOT NULL,
  `phone` TEXT,
  `email` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `document_signatures` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `doc_type` TEXT NOT NULL,
  `doc_id` INT NOT NULL,
  `step_order` INT NOT NULL,
  `role_title` TEXT NOT NULL,
  `signer_name` TEXT,
  `status` TEXT NOT NULL DEFAULT 'PENDING',
  `comment` TEXT,
  `signed_at` TEXT,
  `sign_hash` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `educational_programs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `code` TEXT NOT NULL,
  `title` TEXT NOT NULL,
  `level` TEXT NOT NULL,
  `study_form` TEXT NOT NULL DEFAULT 'Очная',
  `fgos_standard_id` INT,
  `department_id` INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `roles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `role_name` TEXT NOT NULL,
  `code` TEXT NOT NULL,
  `description` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `service_note_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `service_note_id` INT,
  `discipline_id` INT,
  `change_type` TEXT NOT NULL,
  `old_val` TEXT,
  `new_val` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `service_notes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `curriculum_id` INT,
  `note_num` TEXT NOT NULL,
  `note_date` TEXT NOT NULL,
  `reason` TEXT NOT NULL,
  `releasing_dept_id` INT,
  `implementing_dept_id` INT,
  `status` TEXT NOT NULL DEFAULT 'DRAFT',
  `created_by` TEXT,
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `standards_fgos` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `code` TEXT NOT NULL,
  `title` TEXT NOT NULL,
  `degree_level` TEXT NOT NULL,
  `total_credits` INT NOT NULL DEFAULT 240,
  `max_exams_per_session` INT NOT NULL DEFAULT 5,
  `min_practice_credits` INT NOT NULL DEFAULT 12,
  `min_gia_credits` INT NOT NULL DEFAULT 6,
  `approval_date` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` TEXT NOT NULL,
  `full_name` TEXT NOT NULL,
  `email` TEXT NOT NULL,
  `role_id` INT,
  `department_id` INT,
  `position_title` TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS=1;