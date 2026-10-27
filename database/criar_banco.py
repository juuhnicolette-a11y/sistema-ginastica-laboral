import sqlite3

conexao = sqlite3.connect("database/ginastica.db")
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

conexao.commit()
conexao.close()