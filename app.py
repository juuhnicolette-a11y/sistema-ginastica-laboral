import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "chave-temporaria-ginastica-em-dia"


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conexao = sqlite3.connect("database/ginastica.db")
        conexao.execute("PRAGMA foreign_keys = ON")

        usuario = conexao.execute(
            """
            SELECT id, nome, email, senha_hash, perfil, status
            FROM usuarios
            WHERE email = ?
            """,
            (email,),
        ).fetchone()

        conexao.close()

        if usuario is None or not check_password_hash(usuario[3], senha):
            return render_template(
                "login.html",
                erro="E-mail ou senha incorretos.",
                email=email,
            )
        perfil = usuario[4]

        session["usuario_id"] = usuario[0]
        session["perfil"] = usuario[4]

        if perfil == "colaborador":
            return redirect(url_for("area_colaborador"))

    return render_template("login.html")


@app.route("/colaborador")
def area_colaborador():
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    if session["perfil"] != "colaborador":
        return redirect(url_for("login"))

    conexao = sqlite3.connect("database/ginastica.db")

    usuario = conexao.execute(
        """
        SELECT usuarios.nome, turnos.nome, turnos.horario
        FROM usuarios
        LEFT JOIN turnos ON usuarios.turno_id = turnos.id
        WHERE usuarios.id = ?
        """,
        (session["usuario_id"],),
    ).fetchone()

    conexao.close()

    return render_template(
        "colaborador.html",
        nome=usuario[0],
        turno=usuario[1],
        horario=usuario[2],
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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
            (codigo_empresa,),
        ).fetchone()

        if empresa is None:
            conexao.close()

            return render_template(
                "cadastro.html",
                erro="Código da empresa não encontrado. Confira o código e tente novamente.",
                codigo_empresa=codigo_empresa,
                nome=nome,
                email=email,
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
                (empresa_id, nome, email, senha_hash),
            )

            conexao.commit()

        except sqlite3.IntegrityError:
            conexao.close()

            return render_template(
                "cadastro.html",
                erro="Já existe uma conta cadastrada com este e-mail.",
                codigo_empresa=codigo_empresa,
                nome=nome,
                email=email,
            )

        conexao.close()

        return render_template(
            "cadastro.html",
            sucesso="Cadastro realizado com sucesso! Agora você já pode acessar sua conta.",
        )


if __name__ == "__main__":
    app.run(debug=True)
