-- ============================
-- CREACIÓN DE TIPOS ENUM
-- ============================

CREATE TYPE user_role AS ENUM ('ADMIN', 'EMPLOYEE');

CREATE TYPE invoice_status AS ENUM ('PENDING', 'PROCESSED', 'ERROR', 'REJECTED');

CREATE TYPE rpa_status AS ENUM ('SUCCESS', 'FAILED', 'NOT_EXECUTED');

-- ============================
-- TABLA: USERS
-- ============================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'EMPLOYEE',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- TABLA: PROVIDERS
-- ============================

CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    nit VARCHAR(20) UNIQUE NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- TABLA: INVOICES
-- ============================

CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,

    user_id INT REFERENCES users(id),
    provider_id INT REFERENCES providers(id),

    invoice_number VARCHAR(50) NOT NULL,
    date DATE,

    nit VARCHAR(20),

    subtotal NUMERIC(10,2),
    taxes NUMERIC(10,2),
    total NUMERIC(10,2),

    file_path TEXT NOT NULL,

    status invoice_status DEFAULT 'PENDING',

    is_duplicate BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- TABLA: PROCESS LOGS (BITÁCORA)
-- ============================

CREATE TABLE process_logs (
    id SERIAL PRIMARY KEY,

    invoice_id INT REFERENCES invoices(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id),

    process_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    status invoice_status NOT NULL,
    rpa_result rpa_status,

    message TEXT
);

-- ============================
-- TABLA: REPORTS
-- ============================

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,

    invoice_id INT REFERENCES invoices(id) ON DELETE CASCADE,

    file_path TEXT NOT NULL,
    format VARCHAR(20) CHECK (format IN ('PDF', 'EXCEL', 'CSV')),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================
-- ÍNDICES (performance)
-- ============================

CREATE INDEX idx_invoice_user ON invoices(user_id);
CREATE INDEX idx_invoice_provider ON invoices(provider_id);
CREATE INDEX idx_logs_invoice ON process_logs(invoice_id);

-- ============================
-- DATOS INICIALES
-- ============================

INSERT INTO users (username, email, password, role)
VALUES 
('admin', 'admin@gmail.com', '$2b$12$BVWrvou.i1zZqvrqEZ4Sr.XTHuXHQnKFjFAixsRLlt.5qWaTB.Cjm', 'ADMIN'),
('empleado1', 'empl@gamil.com', '$2b$12$BVWrvou.i1zZqvrqEZ4Sr.XTHuXHQnKFjFAixsRLlt.5qWaTB.Cjm', 'EMPLOYEE');