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

cursor.execute("""
CREATE TABLE IF NOT EXISTS presencas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    turno_id INTEGER NOT NULL,
    data_presenca DATE NOT NULL,
    registrado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (turno_id) REFERENCES turnos (id),
    UNIQUE (usuario_id, data_presenca)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS pesquisas_nps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    pergunta TEXT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (empresa_id) REFERENCES empresas (id),
    CHECK (data_fim >= data_inicio)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS respostas_nps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pesquisa_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    turno_id INTEGER NOT NULL,
    nota INTEGER NOT NULL CHECK (nota BETWEEN 0 AND 10),
    comentario TEXT,
    respondido_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pesquisa_id) REFERENCES pesquisas_nps (id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
    FOREIGN KEY (turno_id) REFERENCES turnos (id),
    UNIQUE (pesquisa_id, usuario_id)
)
""")

conexao.commit()
conexao.close()