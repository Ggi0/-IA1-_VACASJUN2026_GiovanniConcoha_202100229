-- CREATE DATABASE smartbot;


-- TABLA: usuarios
-- Administradores y clientes del sistema

CREATE TABLE usuarios (

    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol VARCHAR(20) NOT NULL
        CHECK (rol IN ('admin', 'cliente')),

    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- TABLA: categorias
-- Clasificación de preguntas frecuentes
CREATE TABLE categorias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);


-- TABLA: preguntas_frecuentes
-- Base de conocimiento del bot
CREATE TABLE preguntas_frecuentes (

    id SERIAL PRIMARY KEY,
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    categoria_id INTEGER NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pregunta_categoria
        FOREIGN KEY (categoria_id)
        REFERENCES categorias(id)
        ON DELETE RESTRICT
);


CREATE TABLE palabras_clave (

    id SERIAL PRIMARY KEY,
    pregunta_id INTEGER NOT NULL,
    palabra VARCHAR(100) NOT NULL,

    CONSTRAINT fk_palabra_pregunta
        FOREIGN KEY (pregunta_id)
        REFERENCES preguntas_frecuentes(id)
        ON DELETE CASCADE
);


-- TABLA: telegram_chats
-- Chats/grupos autorizados

CREATE TABLE telegram_chats (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL UNIQUE,
    nombre_chat VARCHAR(255),
    tipo_chat VARCHAR(50),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- TABLA: consultas
-- Historial de preguntas realizadas


CREATE TABLE consultas (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    pregunta_realizada TEXT NOT NULL,
    respuesta_entregada TEXT,
    fecha_consulta TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ÍNDICES


CREATE INDEX idx_preguntas_categoria
ON preguntas_frecuentes(categoria_id);

CREATE INDEX idx_consultas_chat
ON consultas(chat_id);

CREATE INDEX idx_consultas_fecha
ON consultas(fecha_consulta);

CREATE INDEX idx_palabras_clave
ON palabras_clave(palabra);