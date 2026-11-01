import sqlite3

from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash


app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        codigo_empresa = request.form["codigo_empresa"]
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        senha_hash = generate_password_hash(senha)

        conexao = sqlite3.connect("database/ginastica.db")
        conexao.execute("PRAGMA foreign_keys = ON")

        empresa = conexao.execute(
            """
            SELECT id, nome
            FROM empresas
            WHERE codigo_cadastro = ? AND status = 'ativa'
            """,
            (codigo_empresa,)
        ).fetchone()

        if empresa is None:
            conexao.close()

            return render_template(
                "cadastro.html",
                erro="Código da empresa não encontrado. Confira o código e tente novamente.",
                codigo_empresa=codigo_empresa,
                nome=nome,
                email=email
            )

        empresa_id = empresa[0]

        try:
            conexao.execute(
                """
                INSERT INTO usuarios (
                    empresa_id,
                    nome,
                    email,
                    senha_hash,
                    perfil
                )
                VALUES (?, ?, ?, ?, 'colaborador')
                """,
                (empresa_id, nome, email, senha_hash)
            )

            conexao.commit()

        except sqlite3.IntegrityError:
            conexao.close()

            return render_template(
                "cadastro.html",
                erro="Já existe uma conta cadastrada com este e-mail.",
                codigo_empresa=codigo_empresa,
                nome=nome,
                email=email
            )

        conexao.close()

        return render_template(
            "cadastro.html",
            sucesso="Cadastro realizado com sucesso! Agora você já pode acessar sua conta."
        )

if __name__ == "__main__":
    app.run(debug=True)