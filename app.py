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

        if perfil == "responsavel":
            return redirect(url_for("area_empresa"))

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


@app.route("/empresa")
def area_empresa():
    if "usuario_id" not in session or session.get("perfil") != "responsavel":
        return redirect(url_for("login"))

    conexao = sqlite3.connect("database/ginastica.db")

    empresa = conexao.execute(
        """
        SELECT empresas.nome
        FROM usuarios
        JOIN empresas ON usuarios.empresa_id = empresas.id
        WHERE usuarios.id = ?
          AND usuarios.perfil = 'responsavel'
          AND usuarios.status = 'ativo'
          AND empresas.status = 'ativa'
        """,
        (session["usuario_id"],),
    ).fetchone()

    conexao.close()

    if empresa is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template("empresa.html", empresa=empresa[0])


@app.route("/empresa/colaboradores")
def listar_colaboradores():
    if "usuario_id" not in session or session.get("perfil") != "responsavel":
        return redirect(url_for("login"))

    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row

    responsavel = conexao.execute(
        """
        SELECT usuarios.empresa_id
        FROM usuarios
        JOIN empresas ON empresas.id = usuarios.empresa_id
        WHERE usuarios.id = ?
          AND usuarios.perfil = 'responsavel'
          AND usuarios.status = 'ativo'
          AND empresas.status = 'ativa'
        """,
        (session["usuario_id"],),
    ).fetchone()

    if responsavel is None:
        conexao.close()
        session.clear()
        return redirect(url_for("login"))

    colaboradores = conexao.execute(
        """
        SELECT
            usuarios.id,
            usuarios.nome,
            usuarios.email,
            usuarios.status,
            turnos.nome AS turno
        FROM usuarios
        LEFT JOIN turnos ON usuarios.turno_id = turnos.id
        WHERE usuarios.empresa_id = ?
          AND usuarios.perfil = 'colaborador'
        ORDER BY usuarios.nome
        """,
        (responsavel["empresa_id"],),
    ).fetchall()

    conexao.close()

    return render_template("colaboradores.html", colaboradores=colaboradores)


@app.route(
    "/empresa/colaboradores/<int:colaborador_id>/editar", methods=["GET", "POST"]
)
def editar_colaborador(colaborador_id):
    if "usuario_id" not in session or session.get("perfil") != "responsavel":
        return redirect(url_for("login"))

    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    responsavel = conexao.execute(
        """
        SELECT usuarios.empresa_id
        FROM usuarios
        JOIN empresas ON empresas.id = usuarios.empresa_id
        WHERE usuarios.id = ?
          AND usuarios.perfil = 'responsavel'
          AND usuarios.status = 'ativo'
          AND empresas.status = 'ativa'
        """,
        (session["usuario_id"],),
    ).fetchone()

    if responsavel is None:
        conexao.close()
        session.clear()
        return redirect(url_for("login"))

    empresa_id = responsavel["empresa_id"]

    colaborador = conexao.execute(
        """
        SELECT id, nome, email, turno_id, status
        FROM usuarios
        WHERE id = ?
          AND empresa_id = ?
          AND perfil = 'colaborador'
        """,
        (colaborador_id, empresa_id),
    ).fetchone()

    if colaborador is None:
        conexao.close()
        flash("Colaborador não encontrado.")
        return redirect(url_for("listar_colaboradores"))

    turnos = conexao.execute(
        """
        SELECT id, nome
        FROM turnos
        WHERE empresa_id = ?
          AND (status = 'ativo' OR id = ?)
        ORDER BY nome
        """,
        (empresa_id, colaborador["turno_id"]),
    ).fetchall()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        turno_informado = request.form.get("turno_id", "")
        status = request.form.get("status", "")

        erro = None
        turno_id = None

        if not nome or not email:
            erro = "Preencha o nome e o e-mail."
        elif status not in ("ativo", "inativo"):
            erro = "Selecione um status válido."
        elif turno_informado:
            try:
                turno_id = int(turno_informado)
            except ValueError:
                erro = "Selecione um turno válido."

            if erro is None:
                turno_valido = conexao.execute(
                    """
                    SELECT id
                    FROM turnos
                    WHERE id = ?
                      AND empresa_id = ?
                      AND (status = 'ativo' OR id = ?)
                    """,
                    (turno_id, empresa_id, colaborador["turno_id"]),
                ).fetchone()

                if turno_valido is None:
                    erro = "O turno selecionado não está disponível."

        if erro is None:
            email_existente = conexao.execute(
                "SELECT id FROM usuarios WHERE email = ? AND id != ?",
                (email, colaborador_id),
            ).fetchone()

            if email_existente:
                erro = "Este e-mail já está cadastrado."

        if erro is None:
            conexao.execute(
                """
                UPDATE usuarios
                SET nome = ?,
                    email = ?,
                    turno_id = ?,
                    status = ?,
                    atualizado_em = CURRENT_TIMESTAMP
                WHERE id = ?
                  AND empresa_id = ?
                  AND perfil = 'colaborador'
                """,
                (nome, email, turno_id, status, colaborador_id, empresa_id),
            )
            conexao.commit()
            conexao.close()

            flash("Colaborador atualizado com sucesso! 💜")
            return redirect(url_for("listar_colaboradores"))

        flash(erro)
        dados = {
            "nome": nome,
            "email": email,
            "turno_id": turno_informado,
            "status": status,
        }
    else:
        dados = dict(colaborador)

    conexao.close()

    return render_template(
        "editar_colaborador.html",
        colaborador=dados,
        turnos=turnos,
    )


@app.route("/empresa/colaboradores/adicionar", methods=["GET", "POST"])
def adicionar_colaborador():
    if "usuario_id" not in session or session.get("perfil") != "responsavel":
        return redirect(url_for("login"))

    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    responsavel = conexao.execute(
        """
        SELECT usuarios.empresa_id
        FROM usuarios
        JOIN empresas ON empresas.id = usuarios.empresa_id
        WHERE usuarios.id = ?
          AND usuarios.perfil = 'responsavel'
          AND usuarios.status = 'ativo'
          AND empresas.status = 'ativa'
        """,
        (session["usuario_id"],),
    ).fetchone()

    if responsavel is None:
        conexao.close()
        session.clear()
        return redirect(url_for("login"))

    empresa_id = responsavel["empresa_id"]

    turnos = conexao.execute(
        """
        SELECT id, nome
        FROM turnos
        WHERE empresa_id = ?
          AND status = 'ativo'
        ORDER BY nome
        """,
        (empresa_id,),
    ).fetchall()

    dados = {
        "nome": "",
        "email": "",
        "turno_id": "",
    }

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        turno_informado = request.form.get("turno_id", "")

        dados = {
            "nome": nome,
            "email": email,
            "turno_id": turno_informado,
        }

        erro = None
        turno_id = None

        if not nome or not email or not senha:
            erro = "Preencha nome, e-mail e senha."
        elif len(senha) < 8:
            erro = "A senha precisa ter pelo menos 8 caracteres."

        if erro is None and turno_informado:
            try:
                turno_id = int(turno_informado)
            except ValueError:
                erro = "Selecione um turno válido."

            if erro is None:
                turno_valido = conexao.execute(
                    """
                    SELECT id
                    FROM turnos
                    WHERE id = ?
                      AND empresa_id = ?
                      AND status = 'ativo'
                    """,
                    (turno_id, empresa_id),
                ).fetchone()

                if turno_valido is None:
                    erro = "O turno selecionado não está disponível."

        if erro is None:
            email_existente = conexao.execute(
                "SELECT id FROM usuarios WHERE email = ?",
                (email,),
            ).fetchone()

            if email_existente:
                erro = "Este e-mail já está cadastrado."

        if erro is None:
            try:
                conexao.execute(
                    """
                    INSERT INTO usuarios (
                        empresa_id,
                        turno_id,
                        nome,
                        email,
                        senha_hash,
                        perfil,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?, 'colaborador', 'ativo')
                    """,
                    (
                        empresa_id,
                        turno_id,
                        nome,
                        email,
                        generate_password_hash(senha),
                    ),
                )
                conexao.commit()
            except sqlite3.IntegrityError:
                erro = "Não foi possível cadastrar. Verifique os dados."

        if erro is None:
            conexao.close()
            flash("Colaborador cadastrado com sucesso! 💜")
            return redirect(url_for("listar_colaboradores"))

        flash(erro)

    conexao.close()

    return render_template(
        "adicionar_colaborador.html",
        dados=dados,
        turnos=turnos,
    )


DIAS_SEMANA = [
    ("segunda", "Segunda-feira"),
    ("terca", "Terça-feira"),
    ("quarta", "Quarta-feira"),
    ("quinta", "Quinta-feira"),
    ("sexta", "Sexta-feira"),
    ("sabado", "Sábado"),
    ("domingo", "Domingo"),
]


def obter_empresa_responsavel(conexao):
    if "usuario_id" not in session or session.get("perfil") != "responsavel":
        return None

    resultado = conexao.execute(
        """
        SELECT usuarios.empresa_id
        FROM usuarios
        JOIN empresas ON empresas.id = usuarios.empresa_id
        WHERE usuarios.id = ?
          AND usuarios.perfil = 'responsavel'
          AND usuarios.status = 'ativo'
          AND empresas.status = 'ativa'
        """,
        (session["usuario_id"],),
    ).fetchone()

    return resultado["empresa_id"] if resultado else None


@app.route("/empresa/turnos")
def listar_turnos():
    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row

    empresa_id = obter_empresa_responsavel(conexao)

    if empresa_id is None:
        conexao.close()
        return redirect(url_for("login"))

    turnos = conexao.execute(
        """
        SELECT turnos.*,
               COUNT(usuarios.id) AS total_colaboradores
        FROM turnos
        LEFT JOIN usuarios
          ON usuarios.turno_id = turnos.id
         AND usuarios.empresa_id = turnos.empresa_id
         AND usuarios.perfil = 'colaborador'
        WHERE turnos.empresa_id = ?
        GROUP BY turnos.id
        ORDER BY turnos.nome
        """,
        (empresa_id,),
    ).fetchall()

    conexao.close()

    return render_template("turnos.html", turnos=turnos)


@app.route("/empresa/turnos/adicionar", methods=["GET", "POST"])
def adicionar_turno():
    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row
    empresa_id = obter_empresa_responsavel(conexao)

    if empresa_id is None:
        conexao.close()
        return redirect(url_for("login"))

    dados = {"nome": "", "horario": "", "dias_semana": "", "status": "ativo"}

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        horario = request.form.get("horario", "").strip()
        dias = request.form.getlist("dias_semana")
        status = request.form.get("status", "")

        dados = {
            "nome": nome,
            "horario": horario,
            "dias_semana": ",".join(dias),
            "status": status,
        }

        dias_validos = {dia[0] for dia in DIAS_SEMANA}

        if not nome or not horario or not dias:
            flash("Preencha o nome, horário e selecione pelo menos um dia.")
        elif not set(dias).issubset(dias_validos) or len(dias) != len(set(dias)):
            flash("Selecione dias da semana válidos.")
        elif status not in ("ativo", "inativo"):
            flash("Selecione um status válido.")
        else:
            try:
                datetime.strptime(horario, "%H:%M")

                conexao.execute(
                    """
                    INSERT INTO turnos (
                        empresa_id, nome, horario, dias_semana, status
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (empresa_id, nome, horario, ",".join(dias), status),
                )
                conexao.commit()
                conexao.close()

                flash("Turno cadastrado com sucesso! 💜")
                return redirect(url_for("listar_turnos"))

            except ValueError:
                flash("Informe um horário válido.")
            except sqlite3.IntegrityError:
                flash("Não foi possível cadastrar o turno.")

    conexao.close()

    return render_template(
        "formulario_turno.html",
        dados=dados,
        dias_semana=DIAS_SEMANA,
        titulo="Adicionar turno",
        texto_botao="Cadastrar turno",
    )


@app.route("/empresa/turnos/<int:turno_id>/editar", methods=["GET", "POST"])
def editar_turno(turno_id):
    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row
    empresa_id = obter_empresa_responsavel(conexao)

    if empresa_id is None:
        conexao.close()
        return redirect(url_for("login"))

    turno = conexao.execute(
        "SELECT * FROM turnos WHERE id = ? AND empresa_id = ?",
        (turno_id, empresa_id),
    ).fetchone()

    if turno is None:
        conexao.close()
        flash("Turno não encontrado.")
        return redirect(url_for("listar_turnos"))

    dados = dict(turno)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        horario = request.form.get("horario", "").strip()
        dias = request.form.getlist("dias_semana")
        status = request.form.get("status", "")

        dados = {
            "nome": nome,
            "horario": horario,
            "dias_semana": ",".join(dias),
            "status": status,
        }

        dias_validos = {dia[0] for dia in DIAS_SEMANA}

        if not nome or not horario or not dias:
            flash("Preencha o nome, horário e selecione pelo menos um dia.")
        elif not set(dias).issubset(dias_validos) or len(dias) != len(set(dias)):
            flash("Selecione dias da semana válidos.")
        elif status not in ("ativo", "inativo"):
            flash("Selecione um status válido.")
        else:
            try:
                datetime.strptime(horario, "%H:%M")

                conexao.execute(
                    """
                    UPDATE turnos
                    SET nome = ?, horario = ?, dias_semana = ?, status = ?
                    WHERE id = ? AND empresa_id = ?
                    """,
                    (nome, horario, ",".join(dias), status, turno_id, empresa_id),
                )
                conexao.commit()
                conexao.close()

                flash("Turno atualizado com sucesso! 💜")
                return redirect(url_for("listar_turnos"))

            except ValueError:
                flash("Informe um horário válido.")

    conexao.close()

    return render_template(
        "formulario_turno.html",
        dados=dados,
        dias_semana=DIAS_SEMANA,
        titulo="Editar turno",
        texto_botao="Salvar alterações",
    )


@app.route("/empresa/relatorios")
def relatorios_empresa():
    conexao = sqlite3.connect("database/ginastica.db")
    conexao.row_factory = sqlite3.Row

    empresa_id = obter_empresa_responsavel(conexao)

    if empresa_id is None:
        conexao.close()
        return redirect(url_for("login"))

    hoje = datetime.now(ZoneInfo("America/Sao_Paulo"))
    mes_atual = hoje.strftime("%Y-%m")
    mes = request.args.get("mes", mes_atual)

    try:
        data_mes = datetime.strptime(mes, "%Y-%m")
        if data_mes.strftime("%Y-%m") != mes:
            raise ValueError
    except ValueError:
        mes = mes_atual

    inicio = f"{mes}-01"

    ano, numero_mes = map(int, mes.split("-"))
    if numero_mes == 12:
        fim = f"{ano + 1}-01-01"
    else:
        fim = f"{ano}-{numero_mes + 1:02d}-01"

    total_colaboradores = conexao.execute(
        """
        SELECT COUNT(*)
        FROM usuarios
        WHERE empresa_id = ?
          AND perfil = 'colaborador'
          AND status = 'ativo'
        """,
        (empresa_id,),
    ).fetchone()[0]

    total_turnos = conexao.execute(
        """
        SELECT COUNT(*)
        FROM turnos
        WHERE empresa_id = ?
          AND status = 'ativo'
        """,
        (empresa_id,),
    ).fetchone()[0]

    indicadores = conexao.execute(
        """
        SELECT
            COUNT(*) AS total_presencas,
            COUNT(DISTINCT presencas.usuario_id) AS participantes
        FROM presencas
        JOIN usuarios ON usuarios.id = presencas.usuario_id
        WHERE usuarios.empresa_id = ?
          AND presencas.data_presenca >= ?
          AND presencas.data_presenca < ?
        """,
        (empresa_id, inicio, fim),
    ).fetchone()

    presencas_por_turno = conexao.execute(
        """
        SELECT
            turnos.nome,
            COUNT(presencas.id) AS total_presencas
        FROM turnos
        LEFT JOIN presencas
          ON presencas.turno_id = turnos.id
         AND presencas.data_presenca >= ?
         AND presencas.data_presenca < ?
        WHERE turnos.empresa_id = ?
        GROUP BY turnos.id
        ORDER BY total_presencas DESC, turnos.nome
        """,
        (inicio, fim, empresa_id),
    ).fetchall()

    conexao.close()

    maior_total = max(
        (turno["total_presencas"] for turno in presencas_por_turno),
        default=0,
    )

    return render_template(
        "relatorios.html",
        mes=mes,
        total_colaboradores=total_colaboradores,
        total_turnos=total_turnos,
        total_presencas=indicadores["total_presencas"],
        participantes=indicadores["participantes"],
        presencas_por_turno=presencas_por_turno,
        maior_total=maior_total,
    )


if __name__ == "__main__":
    app.run(debug=True)
