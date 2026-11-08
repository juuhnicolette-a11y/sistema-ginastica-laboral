import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from datetime import datetime
from zoneinfo import ZoneInfo

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
        SELECT usuarios.nome, turnos.nome, turnos.horario, turnos.dias_semana
        FROM usuarios
        LEFT JOIN turnos ON usuarios.turno_id = turnos.id
        WHERE usuarios.id = ?
        """,
        (session["usuario_id"],),
    ).fetchone()

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    data_hoje = agora.date().isoformat()

    presenca_hoje = conexao.execute(
        """
        SELECT id
        FROM presencas
        WHERE usuario_id = ? AND data_presenca = ?
        """,
        (session["usuario_id"], data_hoje),
    ).fetchone()

    conexao.close()

    print("Já registrou presença hoje?", presenca_hoje is not None)

    dia_atual = agora.weekday()

    dias_semana = [
        "segunda",
        "terca",
        "quarta",
        "quinta",
        "sexta",
        "sabado",
        "domingo",
    ]

    nome_dia_atual = dias_semana[dia_atual]

    dias_aula = usuario[3].split(",") if usuario[3] else []

    tem_aula_hoje = nome_dia_atual in dias_aula

    ja_registrou_presenca = presenca_hoje is not None

    pode_fazer_checkin = (
        usuario[1] is not None and tem_aula_hoje and not ja_registrou_presenca
    )

    print("Pode fazer check-in?", pode_fazer_checkin)

    print("Hoje é dia de aula?", tem_aula_hoje)

    return render_template(
        "colaborador.html",
        nome=usuario[0],
        turno=usuario[1],
        horario=usuario[2],
        tem_aula_hoje=tem_aula_hoje,
        pode_fazer_checkin=pode_fazer_checkin,
        ja_registrou_presenca=ja_registrou_presenca,
    )


@app.route("/registrar-presenca", methods=["POST"])
def registrar_presenca():
    if "usuario_id" not in session or session.get("perfil") != "colaborador":
        return redirect(url_for("login"))

    conexao = sqlite3.connect("database/ginastica.db")

    usuario = conexao.execute(
        """
        SELECT turnos.id, turnos.dias_semana
        FROM usuarios
        JOIN turnos ON usuarios.turno_id = turnos.id
        WHERE usuarios.id = ?
            AND usuarios.perfil = 'colaborador'
            AND usuarios.status = 'ativo'
            AND turnos.status = 'ativo'
        """,
        (session["usuario_id"],),
    ).fetchone()

    conexao.close()

    if usuario is None or usuario[0] is None:
        print("Check-in bloqueado: colaborador sem turno ativo ou cadastro válido.")
        return redirect(url_for("area_colaborador"))

    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))

    dias_semana = [
        "segunda",
        "terca",
        "quarta",
        "quinta",
        "sexta",
        "sabado",
        "domingo",
    ]

    nome_dia_atual = dias_semana[agora.weekday()]

    dias_aula = [dia.strip() for dia in usuario[1].split(",")]

    if nome_dia_atual not in dias_aula:
        print("Check-in bloqueado: hoje não é dia de aula.")
        return redirect(url_for("area_colaborador"))

    print("Check-in permitido para o dia de hoje!")

    data_hoje = agora.date().isoformat()

    conexao = sqlite3.connect("database/ginastica.db")

    presenca_existente = conexao.execute(
        """
        SELECT id
        FROM presencas
        WHERE usuario_id = ? AND data_presenca = ?
        """,
        (session["usuario_id"], data_hoje),
    ).fetchone()

    conexao.close()

    if presenca_existente is not None:
        print("Check-in bloqueado: presença já registrada hoje.")
        return redirect(url_for("area_colaborador"))

    print("Colaborador ainda não registrou presença hoje!")

    conexao = sqlite3.connect("database/ginastica.db")

    try:
        conexao.execute(
            """
            INSERT INTO presencas (usuario_id, turno_id, data_presenca)
            VALUES (?, ?, ?)
            """,
            (session["usuario_id"], usuario[0], data_hoje),
        )

        conexao.commit()
        print("Presença registrada com sucesso!")

        flash("Presença registrada com sucesso! 💜")

    except sqlite3.IntegrityError:
        print("Não foi possível registrar: presença duplicada ou dados inválidos.")

    finally:
        conexao.close()

    return redirect(url_for("area_colaborador"))


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
