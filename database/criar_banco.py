import sqlite3

conexao = sqlite3.connect("database/ginastica.db")
conexao.execute("PRAGMA foreign_keys = ON")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    codigo_cadastro TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'ativa' CHECK (status IN ('ativa', 'inativa')),
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS turnos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    horario TIME NOT NULL,
    dias_semana TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    turno_id INTEGER,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK (perfil IN ('responsavel', 'colaborador')),
    matricula TEXT,
    status TEXT NOT NULL DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo')),
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id),
    FOREIGN KEY (turno_id) REFERENCES turnos (id)
)
""")

conexao.commit()
conexao.close()