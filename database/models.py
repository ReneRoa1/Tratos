from database.database import get_connection


# ==========================================================
# FAZENDAS
# ==========================================================

def cadastrar_fazenda(
    nome,
    identificacao=None,
    organizacao_id=None
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO fazendas (
                nome,
                identificacao,
                organizacao_id
            )
            VALUES (?, ?, ?)
            """,
            (
                nome,
                identificacao,
                organizacao_id
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def listar_fazendas():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                f.id,
                f.nome,
                f.identificacao,
                f.ativo,
                f.criado_em,
                f.organizacao_id,

                o.nome AS organizacao_nome,
                o.nome_fantasia AS organizacao_nome_fantasia

            FROM fazendas AS f

            LEFT JOIN organizacoes AS o
                ON o.id = f.organizacao_id

            WHERE f.ativo = 1

            ORDER BY f.nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()


def atualizar_organizacao_fazenda(
    fazenda_id,
    organizacao_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE fazendas

            SET organizacao_id = ?

            WHERE id = ?
            """,
            (
                organizacao_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()
# ==========================================================
# ORGANIZAÇÕES / CLIENTES
# ==========================================================

def cadastrar_organizacao(
    nome,
    nome_fantasia=None,
    documento=None,
    telefone=None,
    email=None,
    observacoes=None
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO organizacoes (
                nome,
                nome_fantasia,
                documento,
                telefone,
                email,
                observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                nome,
                nome_fantasia,
                documento,
                telefone,
                email,
                observacoes
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def listar_organizacoes():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome,
                nome_fantasia,
                documento,
                telefone,
                email,
                observacoes,
                ativo,
                criado_em
            FROM organizacoes
            WHERE ativo = 1
            ORDER BY nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()

# ==========================================================
# USUÁRIOS
# ==========================================================

def cadastrar_usuario(
    nome,
    login,
    senha_hash,
    perfil_sistema="USUARIO"
):
    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO usuarios (
                nome,
                login,
                senha_hash,
                perfil,
                perfil_sistema
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                nome,
                login,
                senha_hash,
                "FUNCIONARIO",
                perfil_sistema
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def listar_usuarios():

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome,
                login,
                perfil_sistema,
                ativo,
                criado_em
            FROM usuarios

            WHERE ativo = 1

            ORDER BY nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()


def buscar_usuario_por_login(login):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM usuarios
            WHERE login = ?
            LIMIT 1
            """,
            (login,)
        )

        return cursor.fetchone()

    finally:
        conn.close()


# ==========================================================
# USUÁRIO x ORGANIZAÇÃO
# ==========================================================

def vincular_usuario_organizacao(
    usuario_id,
    organizacao_id,
    perfil
):
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO usuarios_organizacoes (
                usuario_id,
                organizacao_id,
                perfil,
                ativo
            )
            VALUES (?, ?, ?, 1)

            ON CONFLICT(usuario_id, organizacao_id)
            DO UPDATE SET
                perfil = excluded.perfil,
                ativo = 1
            """,
            (
                usuario_id,
                organizacao_id,
                perfil
            )
        )

        conn.commit()

    finally:
        conn.close()


def listar_organizacoes_usuario(usuario_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                uo.id,
                uo.perfil,

                o.id AS organizacao_id,
                o.nome,
                o.nome_fantasia

            FROM usuarios_organizacoes AS uo

            INNER JOIN organizacoes AS o
                ON o.id = uo.organizacao_id

            WHERE
                uo.usuario_id = ?
                AND uo.ativo = 1
                AND o.ativo = 1

            ORDER BY o.nome
            """,
            (usuario_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ==========================================================
# USUÁRIO x FAZENDA
# ==========================================================

def vincular_usuario_fazenda(
    usuario_id,
    fazenda_id,
    perfil
):
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT INTO usuarios_fazendas (
                usuario_id,
                fazenda_id,
                perfil,
                ativo
            )
            VALUES (?, ?, ?, 1)

            ON CONFLICT(usuario_id, fazenda_id)
            DO UPDATE SET
                perfil = excluded.perfil,
                ativo = 1
            """,
            (
                usuario_id,
                fazenda_id,
                perfil
            )
        )

        conn.commit()

    finally:
        conn.close()


def listar_fazendas_usuario(usuario_id):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                uf.id,
                uf.perfil,

                f.id AS fazenda_id,
                f.nome AS fazenda_nome,

                o.nome AS organizacao_nome,
                o.nome_fantasia
                    AS organizacao_nome_fantasia

            FROM usuarios_fazendas AS uf

            INNER JOIN fazendas AS f
                ON f.id = uf.fazenda_id

            LEFT JOIN organizacoes AS o
                ON o.id = f.organizacao_id

            WHERE
                uf.usuario_id = ?
                AND uf.ativo = 1
                AND f.ativo = 1

            ORDER BY f.nome
            """,
            (usuario_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()

# ==========================================================
# AUTENTICAÇÃO
# ==========================================================

def buscar_usuario_ativo_por_login(login):

    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome,
                login,
                senha_hash,
                perfil_sistema,
                ativo
            FROM usuarios

            WHERE
                login = ?
                AND ativo = 1

            LIMIT 1
            """,
            (login,)
        )

        return cursor.fetchone()

    finally:
        conn.close()

# ==========================================================
# EDIÇÃO / DESATIVAÇÃO DE VÍNCULOS
# ==========================================================

def atualizar_perfil_usuario_fazenda(
    usuario_id,
    fazenda_id,
    perfil
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios_fazendas
            SET
                perfil = ?,
                ativo = 1
            WHERE
                usuario_id = ?
                AND fazenda_id = ?
            """,
            (
                perfil,
                usuario_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_vinculo_usuario_fazenda(
    usuario_id,
    fazenda_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios_fazendas
            SET ativo = 0
            WHERE
                usuario_id = ?
                AND fazenda_id = ?
            """,
            (
                usuario_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_vinculo_usuario_organizacao(
    usuario_id,
    organizacao_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios_organizacoes
            SET ativo = 0
            WHERE
                usuario_id = ?
                AND organizacao_id = ?
            """,
            (
                usuario_id,
                organizacao_id
            )
        )

        conn.commit()

    finally:
        conn.close()

# ==========================================================
# EDITAR / DESATIVAR FAZENDA
# ==========================================================

def atualizar_fazenda(
    fazenda_id,
    nome,
    identificacao,
    organizacao_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE fazendas

            SET
                nome = ?,
                identificacao = ?,
                organizacao_id = ?

            WHERE id = ?
            """,
            (
                nome,
                identificacao,
                organizacao_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_fazenda(
    fazenda_id,
    desativado_por=None
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE fazendas

            SET
                ativo = 0,
                desativado_em = CURRENT_TIMESTAMP,
                desativado_por = ?

            WHERE id = ?
            """,
            (
                desativado_por,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()

# ==========================================================
# EDITAR / DESATIVAR USUÁRIO
# ==========================================================

def atualizar_usuario(
    usuario_id,
    nome,
    login,
    perfil_sistema
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios

            SET
                nome = ?,
                login = ?,
                perfil_sistema = ?

            WHERE id = ?
            """,
            (
                nome,
                login,
                perfil_sistema,
                usuario_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def atualizar_senha_usuario(
    usuario_id,
    senha_hash
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios
            SET senha_hash = ?
            WHERE id = ?
            """,
            (
                senha_hash,
                usuario_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_usuario(
    usuario_id,
    desativado_por=None
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios

            SET
                ativo = 0,
                desativado_em = CURRENT_TIMESTAMP,
                desativado_por = ?

            WHERE id = ?
            """,
            (
                desativado_por,
                usuario_id
            )
        )

        conn.commit()

    finally:
        conn.close()

# ==========================================================
# EDITAR / DESATIVAR ORGANIZAÇÃO
# ==========================================================

def atualizar_organizacao(
    organizacao_id,
    nome,
    nome_fantasia=None,
    documento=None,
    telefone=None,
    email=None,
    observacoes=None
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE organizacoes

            SET
                nome = ?,
                nome_fantasia = ?,
                documento = ?,
                telefone = ?,
                email = ?,
                observacoes = ?

            WHERE id = ?
            """,
            (
                nome,
                nome_fantasia,
                documento,
                telefone,
                email,
                observacoes,
                organizacao_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_organizacao(
    organizacao_id,
    desativado_por=None
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE organizacoes

            SET
                ativo = 0,
                desativado_em = CURRENT_TIMESTAMP,
                desativado_por = ?

            WHERE id = ?
            """,
            (
                desativado_por,
                organizacao_id
            )
        )

        conn.commit()

    finally:
        conn.close()

def listar_usuarios_todos():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome,
                login,
                perfil_sistema,
                ativo,
                criado_em,
                desativado_em,
                desativado_por
            FROM usuarios
            ORDER BY nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()
def listar_organizacoes_todas():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome,
                nome_fantasia,
                documento,
                telefone,
                email,
                observacoes,
                ativo,
                criado_em,
                desativado_em,
                desativado_por
            FROM organizacoes
            ORDER BY nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()

def listar_fazendas_todas():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                f.id,
                f.nome,
                f.identificacao,
                f.organizacao_id,
                f.ativo,
                f.criado_em,
                f.desativado_em,
                f.desativado_por,

                o.nome AS organizacao_nome,
                o.nome_fantasia
                    AS organizacao_nome_fantasia

            FROM fazendas AS f

            LEFT JOIN organizacoes AS o
                ON o.id = f.organizacao_id

            ORDER BY f.nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()
def reativar_usuario(usuario_id):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios

            SET
                ativo = 1,
                desativado_em = NULL,
                desativado_por = NULL

            WHERE id = ?
            """,
            (usuario_id,)
        )

        conn.commit()

    finally:
        conn.close()
def reativar_fazenda(fazenda_id):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE fazendas

            SET
                ativo = 1,
                desativado_em = NULL,
                desativado_por = NULL

            WHERE id = ?
            """,
            (fazenda_id,)
        )

        conn.commit()

    finally:
        conn.close()
def reativar_organizacao(
    organizacao_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE organizacoes

            SET
                ativo = 1,
                desativado_em = NULL,
                desativado_por = NULL

            WHERE id = ?
            """,
            (organizacao_id,)
        )

        conn.commit()

    finally:
        conn.close()
# ==========================================================
# ACESSOS DO USUÁRIO
# ==========================================================

def desativar_vinculo_usuario_fazenda(
    usuario_id,
    fazenda_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios_fazendas

            SET ativo = 0

            WHERE
                usuario_id = ?
                AND fazenda_id = ?
            """,
            (
                usuario_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_vinculo_usuario_organizacao(
    usuario_id,
    organizacao_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE usuarios_organizacoes

            SET ativo = 0

            WHERE
                usuario_id = ?
                AND organizacao_id = ?
            """,
            (
                usuario_id,
                organizacao_id
            )
        )

        conn.commit()

    finally:
        conn.close()

# ==========================================================
# CONSULTORES RESPONSÁVEIS POR FAZENDAS
# ==========================================================

def vincular_consultor_fazenda(
    consultor_id,
    fazenda_id,
    papel="PRINCIPAL"
):
    conn = get_connection()

    try:

        # Verifica se já existe vínculo ativo
        existente = conn.execute(
            """
            SELECT id
            FROM responsaveis_fazenda

            WHERE
                consultor_id = ?
                AND fazenda_id = ?
                AND ativo = 1

            LIMIT 1
            """,
            (
                consultor_id,
                fazenda_id
            )
        ).fetchone()

        if existente:

            conn.execute(
                """
                UPDATE responsaveis_fazenda

                SET papel = ?

                WHERE id = ?
                """,
                (
                    papel,
                    existente["id"]
                )
            )

        else:

            conn.execute(
                """
                INSERT INTO responsaveis_fazenda (
                    consultor_id,
                    fazenda_id,
                    papel
                )
                VALUES (?, ?, ?)
                """,
                (
                    consultor_id,
                    fazenda_id,
                    papel
                )
            )

        conn.commit()

    finally:
        conn.close()


def encerrar_vinculo_consultor_fazenda(
    consultor_id,
    fazenda_id
):
    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE responsaveis_fazenda

            SET
                ativo = 0,
                data_fim = CURRENT_TIMESTAMP

            WHERE
                consultor_id = ?
                AND fazenda_id = ?
                AND ativo = 1
            """,
            (
                consultor_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def listar_fazendas_consultor(
    consultor_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                rf.id AS responsavel_id,
                rf.papel,
                rf.data_inicio,

                f.id,
                f.id AS fazenda_id,

                f.nome,
                f.nome AS fazenda_nome,

                f.identificacao,
                f.organizacao_id,
                f.ativo,
                f.criado_em,
                f.desativado_em,
                f.desativado_por,

                o.id AS organizacao_id_cliente,

                o.nome AS organizacao_nome,

                o.nome_fantasia
                    AS organizacao_nome_fantasia

            FROM responsaveis_fazenda AS rf

            INNER JOIN fazendas AS f
                ON f.id = rf.fazenda_id

            LEFT JOIN organizacoes AS o
                ON o.id = f.organizacao_id

            WHERE
                rf.consultor_id = ?
                AND rf.ativo = 1
                AND f.ativo = 1

            ORDER BY f.nome
            """,
            (consultor_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def listar_consultores_fazenda(
    fazenda_id
):
    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                rf.id AS responsavel_id,
                rf.papel,
                rf.data_inicio,

                u.id AS consultor_id,
                u.nome,
                u.login

            FROM responsaveis_fazenda AS rf

            INNER JOIN usuarios AS u
                ON u.id = rf.consultor_id

            WHERE
                rf.fazenda_id = ?
                AND rf.ativo = 1
                AND u.ativo = 1
                AND u.perfil_sistema = 'CONSULTOR'

            ORDER BY
                rf.papel,
                u.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def listar_consultores():
    conn = get_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                nome,
                login,
                perfil_sistema,
                ativo,
                criado_em
            FROM usuarios

            WHERE
                ativo = 1
                AND perfil_sistema = 'CONSULTOR'

            ORDER BY nome
            """
        )

        return cursor.fetchall()

    finally:
        conn.close()

def definir_perfil_sistema(
    usuario_id,
    perfil
):
    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE usuarios

            SET perfil_sistema = ?

            WHERE id = ?
            """,
            (
                perfil,
                usuario_id
            )
        )

        conn.commit()

    finally:
        conn.close()

def listar_organizacoes_consultor(consultor_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                o.id,
                o.nome,
                o.nome_fantasia,
                o.documento,
                o.telefone,
                o.email,
                o.observacoes,
                o.ativo,
                o.criado_em,
                o.desativado_em,
                o.desativado_por

            FROM usuarios_organizacoes AS uo

            INNER JOIN organizacoes AS o
                ON o.id = uo.organizacao_id

            WHERE
                uo.usuario_id = ?
                AND uo.ativo = 1
                AND o.ativo = 1

            ORDER BY o.nome
            """,
            (consultor_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()
def listar_organizacoes_consultor_todas(consultor_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                o.id,
                o.nome,
                o.nome_fantasia,
                o.documento,
                o.telefone,
                o.email,
                o.observacoes,
                o.ativo,
                o.criado_em,
                o.desativado_em,
                o.desativado_por

            FROM usuarios_organizacoes AS uo

            INNER JOIN organizacoes AS o
                ON o.id = uo.organizacao_id

            WHERE
                uo.usuario_id = ?
                AND uo.ativo = 1

            ORDER BY o.nome
            """,
            (consultor_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()
def listar_fazendas_consultor_todas(
    consultor_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                rf.id AS responsavel_id,
                rf.papel,
                rf.data_inicio,
                rf.data_fim,
                rf.ativo AS vinculo_ativo,

                f.id AS fazenda_id,
                f.id AS id,
                f.nome,
                f.nome AS fazenda_nome,
                f.identificacao,
                f.organizacao_id,
                f.ativo,
                f.criado_em,
                f.desativado_em,
                f.desativado_por,

                o.nome AS organizacao_nome,
                o.nome_fantasia
                    AS organizacao_nome_fantasia

            FROM responsaveis_fazenda AS rf

            INNER JOIN fazendas AS f
                ON f.id = rf.fazenda_id

            LEFT JOIN organizacoes AS o
                ON o.id = f.organizacao_id

            WHERE
                rf.consultor_id = ?
                AND rf.ativo = 1

            ORDER BY f.nome
            """,
            (consultor_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()

def consultor_tem_acesso_fazenda(
    consultor_id,
    fazenda_id
):
    conn = get_connection()

    try:
        registro = conn.execute(
            """
            SELECT 1

            FROM responsaveis_fazenda

            WHERE
                consultor_id = ?
                AND fazenda_id = ?
                AND ativo = 1

            LIMIT 1
            """,
            (
                consultor_id,
                fazenda_id
            )
        ).fetchone()

        return registro is not None

    finally:
        conn.close()
def consultor_tem_acesso_organizacao(
    consultor_id,
    organizacao_id
):
    conn = get_connection()

    try:
        registro = conn.execute(
            """
            SELECT 1

            FROM usuarios_organizacoes

            WHERE
                usuario_id = ?
                AND organizacao_id = ?
                AND ativo = 1

            LIMIT 1
            """,
            (
                consultor_id,
                organizacao_id
            )
        ).fetchone()

        return registro is not None

    finally:
        conn.close()

# ==========================================================
# USUÁRIOS DA CARTEIRA DO CONSULTOR
# ==========================================================

def listar_usuarios_consultor(
    consultor_id,
    incluir_inativos=False
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        filtro_ativo = ""

        if not incluir_inativos:
            filtro_ativo = "AND u.ativo = 1"

        cursor.execute(
            f"""
            SELECT DISTINCT
                u.id,
                u.nome,
                u.login,
                u.perfil_sistema,
                u.ativo,
                u.criado_em,
                u.desativado_em,
                u.desativado_por

            FROM usuarios AS u

            INNER JOIN usuarios_fazendas AS uf
                ON uf.usuario_id = u.id

            INNER JOIN responsaveis_fazenda AS rf
                ON rf.fazenda_id = uf.fazenda_id

            WHERE
                rf.consultor_id = ?
                AND rf.ativo = 1
                AND uf.ativo = 1
                AND u.perfil_sistema = 'USUARIO'
                {filtro_ativo}

            ORDER BY u.nome
            """,
            (consultor_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


# ==========================================================
# VERIFICAR SE CONSULTOR PODE GERENCIAR USUÁRIO
# ==========================================================

def consultor_tem_acesso_usuario(
    consultor_id,
    usuario_id
):
    conn = get_connection()

    try:
        registro = conn.execute(
            """
            SELECT 1

            FROM usuarios_fazendas AS uf

            INNER JOIN responsaveis_fazenda AS rf
                ON rf.fazenda_id = uf.fazenda_id

            WHERE
                rf.consultor_id = ?
                AND uf.usuario_id = ?
                AND rf.ativo = 1
                AND uf.ativo = 1

            LIMIT 1
            """,
            (
                consultor_id,
                usuario_id
            )
        ).fetchone()

        return registro is not None

    finally:
        conn.close()


# ==========================================================
# VERIFICAR SE CONSULTOR TEM ACESSO À FAZENDA
# ==========================================================

def consultor_tem_acesso_fazenda(
    consultor_id,
    fazenda_id
):
    conn = get_connection()

    try:
        registro = conn.execute(
            """
            SELECT 1

            FROM responsaveis_fazenda

            WHERE
                consultor_id = ?
                AND fazenda_id = ?
                AND ativo = 1

            LIMIT 1
            """,
            (
                consultor_id,
                fazenda_id
            )
        ).fetchone()

        return registro is not None

    finally:
        conn.close()


# ==========================================================
# VERIFICAR SE CONSULTOR TEM ACESSO AO CLIENTE
# ==========================================================

def consultor_tem_acesso_organizacao(
    consultor_id,
    organizacao_id
):
    conn = get_connection()

    try:
        registro = conn.execute(
            """
            SELECT 1

            FROM usuarios_organizacoes

            WHERE
                usuario_id = ?
                AND organizacao_id = ?
                AND ativo = 1

            LIMIT 1
            """,
            (
                consultor_id,
                organizacao_id
            )
        ).fetchone()

        return registro is not None

    finally:
        conn.close()


# ==========================================================
# CLIENTES DO CONSULTOR
# ==========================================================

def listar_organizacoes_consultor(
    consultor_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                o.id,
                o.nome,
                o.nome_fantasia,
                o.documento,
                o.telefone,
                o.email,
                o.observacoes,
                o.ativo,
                o.criado_em,
                o.desativado_em,
                o.desativado_por

            FROM usuarios_organizacoes AS uo

            INNER JOIN organizacoes AS o
                ON o.id = uo.organizacao_id

            WHERE
                uo.usuario_id = ?
                AND uo.ativo = 1
                AND o.ativo = 1

            ORDER BY o.nome
            """,
            (consultor_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()
# ==========================================================
# PIQUETES
# ==========================================================

def cadastrar_piquete(
    fazenda_id,
    nome,
    identificacao=None
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO piquetes (
                fazenda_id,
                nome,
                identificacao
            )
            VALUES (?, ?, ?)
            """,
            (
                fazenda_id,
                nome,
                identificacao
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def listar_piquetes_fazenda(
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.id,
                p.fazenda_id,
                p.nome,
                p.identificacao,
                p.ativo,
                p.criado_em,

                f.nome AS fazenda_nome

            FROM piquetes AS p

            INNER JOIN fazendas AS f
                ON f.id = p.fazenda_id

            WHERE
                p.fazenda_id = ?
                AND p.ativo = 1
                AND f.ativo = 1

            ORDER BY p.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def listar_piquetes_fazenda_todos(
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.id,
                p.fazenda_id,
                p.nome,
                p.identificacao,
                p.ativo,
                p.criado_em,

                f.nome AS fazenda_nome

            FROM piquetes AS p

            INNER JOIN fazendas AS f
                ON f.id = p.fazenda_id

            WHERE
                p.fazenda_id = ?

            ORDER BY p.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def atualizar_piquete(
    piquete_id,
    fazenda_id,
    nome,
    identificacao=None
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE piquetes

            SET
                fazenda_id = ?,
                nome = ?,
                identificacao = ?

            WHERE id = ?
            """,
            (
                fazenda_id,
                nome,
                identificacao,
                piquete_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_piquete(
    piquete_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE piquetes
            SET ativo = 0
            WHERE id = ?
            """,
            (piquete_id,)
        )

        conn.commit()

    finally:
        conn.close()


def reativar_piquete(
    piquete_id
):
    conn = get_connection()

    try:
        conn.execute(
            """
            UPDATE piquetes
            SET ativo = 1
            WHERE id = ?
            """,
            (piquete_id,)
        )

        conn.commit()

    finally:
        conn.close()


def buscar_piquete_por_id(
    piquete_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.id,
                p.fazenda_id,
                p.nome,
                p.identificacao,
                p.ativo,
                p.criado_em,

                f.nome AS fazenda_nome

            FROM piquetes AS p

            INNER JOIN fazendas AS f
                ON f.id = p.fazenda_id

            WHERE p.id = ?

            LIMIT 1
            """,
            (piquete_id,)
        )

        return cursor.fetchone()

    finally:
        conn.close()


def usuario_tem_acesso_fazenda(
    usuario_id,
    fazenda_id
):
    conn = get_connection()

    try:
        registro = conn.execute(
            """
            SELECT 1

            FROM usuarios_fazendas

            WHERE
                usuario_id = ?
                AND fazenda_id = ?
                AND ativo = 1

            LIMIT 1
            """,
            (
                usuario_id,
                fazenda_id
            )
        ).fetchone()

        return registro is not None

    finally:
        conn.close()

# ==========================================================
# USUÁRIOS DE UMA FAZENDA DA CARTEIRA DO CONSULTOR
# ==========================================================

def listar_usuarios_consultor_fazenda(
    consultor_id,
    fazenda_id,
    incluir_inativos=False
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        filtro_ativo = ""

        if not incluir_inativos:
            filtro_ativo = "AND u.ativo = 1"

        cursor.execute(
            f"""
            SELECT DISTINCT
                u.id,
                u.nome,
                u.login,
                u.perfil_sistema,
                u.ativo,
                u.criado_em,
                u.desativado_em,
                u.desativado_por

            FROM usuarios AS u

            INNER JOIN usuarios_fazendas AS uf
                ON uf.usuario_id = u.id

            INNER JOIN responsaveis_fazenda AS rf
                ON rf.fazenda_id = uf.fazenda_id

            WHERE
                rf.consultor_id = ?
                AND rf.fazenda_id = ?
                AND uf.fazenda_id = ?
                AND rf.ativo = 1
                AND uf.ativo = 1
                AND u.perfil_sistema = 'USUARIO'
                {filtro_ativo}

            ORDER BY u.nome
            """,
            (
                consultor_id,
                fazenda_id,
                fazenda_id
            )
        )

        return cursor.fetchall()

    finally:
        conn.close()

# ==========================================================
# LOTES
# ==========================================================

def cadastrar_lote(
    fazenda_id,
    piquete_id,
    nome,
    numero_animais,
    peso_medio_entrada=None,
    data_entrada=None
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Segurança:
        # o piquete precisa pertencer à mesma fazenda
        piquete = cursor.execute(
            """
            SELECT id
            FROM piquetes
            WHERE
                id = ?
                AND fazenda_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (
                piquete_id,
                fazenda_id
            )
        ).fetchone()

        if piquete is None:
            raise ValueError(
                "O piquete informado não pertence "
                "à fazenda selecionada ou está inativo."
            )

        cursor.execute(
            """
            INSERT INTO lotes (
                fazenda_id,
                piquete_id,
                nome,
                numero_animais,
                peso_medio_entrada,
                data_entrada,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'ATIVO')
            """,
            (
                fazenda_id,
                piquete_id,
                nome,
                numero_animais,
                peso_medio_entrada,
                data_entrada
            )
        )

        lote_id = cursor.lastrowid

        # --------------------------------------------------
        # Cria o primeiro vínculo histórico do lote
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO lotes_piquetes_historico (
                lote_id,
                fazenda_id,
                piquete_id,
                data_inicio,
                ativo
            )
            VALUES (?, ?, ?, ?, 1)
            """,
            (
                lote_id,
                fazenda_id,
                piquete_id,
                data_entrada
            )
        )

        conn.commit()

        return lote_id

    finally:
        conn.close()


def listar_lotes_fazenda(
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                l.id,
                l.fazenda_id,
                l.piquete_id,
                l.nome,
                l.numero_animais,
                l.peso_medio_entrada,
                l.data_entrada,
                l.data_saida,
                l.status,
                l.criado_em,

                p.nome AS piquete_nome,
                p.identificacao AS piquete_identificacao,

                f.nome AS fazenda_nome

            FROM lotes AS l

            LEFT JOIN piquetes AS p
                ON p.id = l.piquete_id

            INNER JOIN fazendas AS f
                ON f.id = l.fazenda_id

            WHERE
                l.fazenda_id = ?
                AND l.status = 'ATIVO'

            ORDER BY l.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def listar_lotes_fazenda_todos(
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                l.id,
                l.fazenda_id,
                l.piquete_id,
                l.nome,
                l.numero_animais,
                l.peso_medio_entrada,
                l.data_entrada,
                l.data_saida,
                l.status,
                l.criado_em,

                p.nome AS piquete_nome,
                p.identificacao AS piquete_identificacao,

                f.nome AS fazenda_nome

            FROM lotes AS l

            LEFT JOIN piquetes AS p
                ON p.id = l.piquete_id

            INNER JOIN fazendas AS f
                ON f.id = l.fazenda_id

            WHERE
                l.fazenda_id = ?

            ORDER BY l.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def buscar_lote_por_id(
    lote_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                l.id,
                l.fazenda_id,
                l.piquete_id,
                l.nome,
                l.numero_animais,
                l.peso_medio_entrada,
                l.data_entrada,
                l.data_saida,
                l.status,
                l.criado_em,

                p.nome AS piquete_nome,
                f.nome AS fazenda_nome

            FROM lotes AS l

            LEFT JOIN piquetes AS p
                ON p.id = l.piquete_id

            INNER JOIN fazendas AS f
                ON f.id = l.fazenda_id

            WHERE l.id = ?

            LIMIT 1
            """,
            (lote_id,)
        )

        return cursor.fetchone()

    finally:
        conn.close()


def atualizar_lote(
    lote_id,
    fazenda_id,
    nome,
    numero_animais,
    peso_medio_entrada=None,
    data_entrada=None
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE lotes

            SET
                nome = ?,
                numero_animais = ?,
                peso_medio_entrada = ?,
                data_entrada = ?

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                nome,
                numero_animais,
                peso_medio_entrada,
                data_entrada,
                lote_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def encerrar_lote(
    lote_id,
    fazenda_id,
    data_saida
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        lote = cursor.execute(
            """
            SELECT
                id,
                status,
                data_entrada
            FROM lotes
            WHERE
                id = ?
                AND fazenda_id = ?
            LIMIT 1
            """,
            (
                lote_id,
                fazenda_id
            )
        ).fetchone()

        if lote is None:
            raise ValueError(
                "Lote não encontrado."
            )

        if lote["status"] != "ATIVO":
            raise ValueError(
                "Este lote já está encerrado."
            )

        if (
            lote["data_entrada"]
            and data_saida < lote["data_entrada"]
        ):
            raise ValueError(
                "A data de saída não pode ser "
                "anterior à data de entrada."
            )

        vinculo_atual = cursor.execute(
            """
            SELECT
                id,
                data_inicio
            FROM lotes_piquetes_historico
            WHERE
                lote_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (lote_id,)
        ).fetchone()

        if vinculo_atual is not None:

            if (
                vinculo_atual["data_inicio"]
                and data_saida
                < vinculo_atual["data_inicio"]
            ):
                raise ValueError(
                    "A data de saída não pode ser "
                    "anterior à entrada no piquete atual."
                )

            cursor.execute(
                """
                UPDATE lotes_piquetes_historico

                SET
                    data_fim = ?,
                    ativo = 0

                WHERE id = ?
                """,
                (
                    data_saida,
                    vinculo_atual["id"]
                )
            )

        cursor.execute(
            """
            UPDATE lotes

            SET
                status = 'ENCERRADO',
                data_saida = ?

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                data_saida,
                lote_id,
                fazenda_id
            )
        )

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        conn.close()


def reativar_lote(
    lote_id,
    fazenda_id,
    piquete_id,
    data_retorno
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # --------------------------------------------------
        # Confere o lote
        # --------------------------------------------------

        lote = cursor.execute(
            """
            SELECT
                id,
                status,
                data_saida
            FROM lotes
            WHERE
                id = ?
                AND fazenda_id = ?
            LIMIT 1
            """,
            (
                lote_id,
                fazenda_id
            )
        ).fetchone()

        if lote is None:
            raise ValueError(
                "Lote não encontrado."
            )

        if lote["status"] == "ATIVO":
            raise ValueError(
                "Este lote já está ativo."
            )

        # --------------------------------------------------
        # Confere o piquete escolhido
        # --------------------------------------------------

        piquete = cursor.execute(
            """
            SELECT id
            FROM piquetes
            WHERE
                id = ?
                AND fazenda_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (
                piquete_id,
                fazenda_id
            )
        ).fetchone()

        if piquete is None:
            raise ValueError(
                "O piquete selecionado não pertence "
                "à fazenda ou está inativo."
            )

        # --------------------------------------------------
        # A reativação não pode ocorrer antes
        # do encerramento anterior
        # --------------------------------------------------

        if (
            lote["data_saida"]
            and data_retorno < lote["data_saida"]
        ):
            raise ValueError(
                "A data de retorno não pode ser "
                "anterior à data de saída do lote."
            )

        # --------------------------------------------------
        # Segurança: não pode existir vínculo ativo
        # --------------------------------------------------

        vinculo_ativo = cursor.execute(
            """
            SELECT id
            FROM lotes_piquetes_historico
            WHERE
                lote_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (lote_id,)
        ).fetchone()

        if vinculo_ativo is not None:
            raise ValueError(
                "O lote já possui um piquete ativo "
                "no histórico."
            )

        # --------------------------------------------------
        # Novo período histórico
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO lotes_piquetes_historico (
                lote_id,
                fazenda_id,
                piquete_id,
                data_inicio,
                ativo
            )
            VALUES (?, ?, ?, ?, 1)
            """,
            (
                lote_id,
                fazenda_id,
                piquete_id,
                data_retorno
            )
        )

        # --------------------------------------------------
        # Reativa o lote e define a nova localização
        # --------------------------------------------------

        cursor.execute(
            """
            UPDATE lotes

            SET
                status = 'ATIVO',
                piquete_id = ?,
                data_saida = NULL

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                piquete_id,
                lote_id,
                fazenda_id
            )
        )

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        conn.close()

# ==========================================================
# HISTÓRICO DE MOVIMENTAÇÃO DOS LOTES ENTRE PIQUETES
# ==========================================================

def registrar_entrada_lote_piquete(
    lote_id,
    fazenda_id,
    piquete_id,
    data_inicio
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # --------------------------------------------------
        # Valida se o lote pertence à fazenda
        # --------------------------------------------------

        lote = cursor.execute(
            """
            SELECT id
            FROM lotes
            WHERE
                id = ?
                AND fazenda_id = ?
            LIMIT 1
            """,
            (
                lote_id,
                fazenda_id
            )
        ).fetchone()

        if lote is None:
            raise ValueError(
                "O lote não pertence à fazenda selecionada."
            )

        # --------------------------------------------------
        # Valida se o piquete pertence à fazenda
        # --------------------------------------------------

        piquete = cursor.execute(
            """
            SELECT id
            FROM piquetes
            WHERE
                id = ?
                AND fazenda_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (
                piquete_id,
                fazenda_id
            )
        ).fetchone()

        if piquete is None:
            raise ValueError(
                "O piquete não pertence à fazenda "
                "selecionada ou está inativo."
            )

        # --------------------------------------------------
        # Impede dois vínculos atuais simultâneos
        # --------------------------------------------------

        vinculo_atual = cursor.execute(
            """
            SELECT id
            FROM lotes_piquetes_historico
            WHERE
                lote_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (lote_id,)
        ).fetchone()

        if vinculo_atual is not None:
            raise ValueError(
                "O lote já possui um piquete atual."
            )

        cursor.execute(
            """
            INSERT INTO lotes_piquetes_historico (
                lote_id,
                fazenda_id,
                piquete_id,
                data_inicio,
                ativo
            )
            VALUES (?, ?, ?, ?, 1)
            """,
            (
                lote_id,
                fazenda_id,
                piquete_id,
                data_inicio
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def buscar_piquete_atual_lote(
    lote_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                h.id,
                h.lote_id,
                h.fazenda_id,
                h.piquete_id,
                h.data_inicio,
                h.data_fim,
                h.ativo,

                p.nome AS piquete_nome,
                p.identificacao
                    AS piquete_identificacao

            FROM lotes_piquetes_historico AS h

            INNER JOIN piquetes AS p
                ON p.id = h.piquete_id

            WHERE
                h.lote_id = ?
                AND h.ativo = 1

            LIMIT 1
            """,
            (lote_id,)
        )

        return cursor.fetchone()

    finally:
        conn.close()


def listar_historico_piquetes_lote(
    lote_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                h.id,
                h.lote_id,
                h.fazenda_id,
                h.piquete_id,
                h.data_inicio,
                h.data_fim,
                h.ativo,
                h.criado_em,

                p.nome AS piquete_nome,
                p.identificacao
                    AS piquete_identificacao

            FROM lotes_piquetes_historico AS h

            INNER JOIN piquetes AS p
                ON p.id = h.piquete_id

            WHERE h.lote_id = ?

            ORDER BY
                h.data_inicio DESC,
                h.id DESC
            """,
            (lote_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def movimentar_lote_piquete(
    lote_id,
    fazenda_id,
    novo_piquete_id,
    data_movimentacao
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # --------------------------------------------------
        # Confere o lote
        # --------------------------------------------------

        lote = cursor.execute(
            """
            SELECT
                id,
                piquete_id
            FROM lotes
            WHERE
                id = ?
                AND fazenda_id = ?
                AND status = 'ATIVO'
            LIMIT 1
            """,
            (
                lote_id,
                fazenda_id
            )
        ).fetchone()

        if lote is None:
            raise ValueError(
                "Lote não encontrado ou encerrado."
            )

        # --------------------------------------------------
        # Confere o novo piquete
        # --------------------------------------------------

        piquete = cursor.execute(
            """
            SELECT id
            FROM piquetes
            WHERE
                id = ?
                AND fazenda_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (
                novo_piquete_id,
                fazenda_id
            )
        ).fetchone()

        if piquete is None:
            raise ValueError(
                "O novo piquete não pertence à fazenda "
                "selecionada ou está inativo."
            )

        if lote["piquete_id"] == novo_piquete_id:
            raise ValueError(
                "O lote já está neste piquete."
            )

        # --------------------------------------------------
        # Busca o vínculo atual
        # --------------------------------------------------

        atual = cursor.execute(
            """
            SELECT
                id,
                data_inicio
            FROM lotes_piquetes_historico
            WHERE
                lote_id = ?
                AND ativo = 1
            LIMIT 1
            """,
            (lote_id,)
        ).fetchone()

        if atual is None:
            raise ValueError(
                "O lote não possui histórico de "
                "piquete atual."
            )
        # --------------------------------------------------
        # Impede movimentação anterior à entrada atual
        # --------------------------------------------------

        if (
            atual["data_inicio"] is not None
            and data_movimentacao < atual["data_inicio"]
        ):
            raise ValueError(
                "A data da movimentação não pode ser "
                "anterior à entrada do lote no piquete atual."
            )
        # --------------------------------------------------
        # Fecha o vínculo anterior
        # --------------------------------------------------

        cursor.execute(
            """
            UPDATE lotes_piquetes_historico

            SET
                data_fim = ?,
                ativo = 0

            WHERE id = ?
            """,
            (
                data_movimentacao,
                atual["id"]
            )
        )

        # --------------------------------------------------
        # Abre o novo vínculo
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO lotes_piquetes_historico (
                lote_id,
                fazenda_id,
                piquete_id,
                data_inicio,
                ativo
            )
            VALUES (?, ?, ?, ?, 1)
            """,
            (
                lote_id,
                fazenda_id,
                novo_piquete_id,
                data_movimentacao
            )
        )

        # --------------------------------------------------
        # Atualiza o piquete atual do lote
        # --------------------------------------------------

        cursor.execute(
            """
            UPDATE lotes

            SET piquete_id = ?

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                novo_piquete_id,
                lote_id,
                fazenda_id
            )
        )

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        conn.close()
        # ==========================================================
# ALIMENTOS
# ==========================================================

def cadastrar_alimento(
    fazenda_id,
    nome,
    categoria,
    unidade="kg"
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO alimentos (
                fazenda_id,
                nome,
                categoria,
                unidade
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                fazenda_id,
                nome,
                categoria,
                unidade
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def listar_alimentos_fazenda(
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.id,
                a.fazenda_id,
                a.nome,
                a.categoria,
                a.unidade,
                a.ativo,
                a.criado_em,

                f.nome AS fazenda_nome

            FROM alimentos AS a

            INNER JOIN fazendas AS f
                ON f.id = a.fazenda_id

            WHERE
                a.fazenda_id = ?
                AND a.ativo = 1

            ORDER BY
                a.categoria,
                a.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def listar_alimentos_fazenda_todos(
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.id,
                a.fazenda_id,
                a.nome,
                a.categoria,
                a.unidade,
                a.ativo,
                a.criado_em,

                f.nome AS fazenda_nome

            FROM alimentos AS a

            INNER JOIN fazendas AS f
                ON f.id = a.fazenda_id

            WHERE
                a.fazenda_id = ?

            ORDER BY
                a.categoria,
                a.nome
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def buscar_alimento_por_id(
    alimento_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                a.id,
                a.fazenda_id,
                a.nome,
                a.categoria,
                a.unidade,
                a.ativo,
                a.criado_em,

                f.nome AS fazenda_nome

            FROM alimentos AS a

            INNER JOIN fazendas AS f
                ON f.id = a.fazenda_id

            WHERE a.id = ?

            LIMIT 1
            """,
            (alimento_id,)
        )

        return cursor.fetchone()

    finally:
        conn.close()


def atualizar_alimento(
    alimento_id,
    fazenda_id,
    nome,
    categoria,
    unidade
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE alimentos

            SET
                nome = ?,
                categoria = ?,
                unidade = ?

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                nome,
                categoria,
                unidade,
                alimento_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def desativar_alimento(
    alimento_id,
    fazenda_id
):
    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE alimentos

            SET ativo = 0

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                alimento_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()


def reativar_alimento(
    alimento_id,
    fazenda_id
):
    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE alimentos

            SET ativo = 1

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                alimento_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()
# ==========================================================
# HISTÓRICO DE MATÉRIA SECA DOS ALIMENTOS
# ==========================================================

def registrar_ms_alimento(
    alimento_id,
    fazenda_id,
    materia_seca,
    data_vigencia,
    observacao=None
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # --------------------------------------------------
        # Confere se o alimento pertence à fazenda
        # --------------------------------------------------

        alimento = cursor.execute(
            """
            SELECT
                id,
                ativo
            FROM alimentos
            WHERE
                id = ?
                AND fazenda_id = ?
            LIMIT 1
            """,
            (
                alimento_id,
                fazenda_id
            )
        ).fetchone()

        if alimento is None:
            raise ValueError(
                "O alimento não pertence "
                "à fazenda selecionada."
            )

        if not alimento["ativo"]:
            raise ValueError(
                "Não é possível registrar matéria seca "
                "para um alimento inativo."
            )

        # --------------------------------------------------
        # Validação da MS
        # --------------------------------------------------

        try:
            materia_seca = float(
                materia_seca
            )

        except (TypeError, ValueError):
            raise ValueError(
                "Informe uma matéria seca válida."
            )

        if (
            materia_seca <= 0
            or materia_seca > 100
        ):
            raise ValueError(
                "A matéria seca deve ser maior que 0 "
                "e menor ou igual a 100%."
            )

        # --------------------------------------------------
        # Impede dois valores para o mesmo alimento/data
        # --------------------------------------------------

        existente = cursor.execute(
            """
            SELECT id
            FROM alimento_ms_historico
            WHERE
                alimento_id = ?
                AND data_vigencia = ?
            LIMIT 1
            """,
            (
                alimento_id,
                data_vigencia
            )
        ).fetchone()

        if existente is not None:
            raise ValueError(
                "Já existe um registro de matéria seca "
                "para este alimento nesta data."
            )

        cursor.execute(
            """
            INSERT INTO alimento_ms_historico (
                alimento_id,
                fazenda_id,
                materia_seca,
                data_vigencia,
                observacao
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                alimento_id,
                fazenda_id,
                materia_seca,
                data_vigencia,
                observacao
            )
        )

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def listar_historico_ms_alimento(
    alimento_id,
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                h.id,
                h.alimento_id,
                h.fazenda_id,
                h.materia_seca,
                h.data_vigencia,
                h.observacao,
                h.criado_em,

                a.nome AS alimento_nome

            FROM alimento_ms_historico AS h

            INNER JOIN alimentos AS a
                ON a.id = h.alimento_id

            WHERE
                h.alimento_id = ?
                AND h.fazenda_id = ?
                AND a.fazenda_id = ?

            ORDER BY
                h.data_vigencia DESC,
                h.id DESC
            """,
            (
                alimento_id,
                fazenda_id,
                fazenda_id
            )
        )

        return cursor.fetchall()

    finally:
        conn.close()


def buscar_ms_atual_alimento(
    alimento_id,
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                h.id,
                h.alimento_id,
                h.fazenda_id,
                h.materia_seca,
                h.data_vigencia,
                h.observacao,
                h.criado_em

            FROM alimento_ms_historico AS h

            WHERE
                h.alimento_id = ?
                AND h.fazenda_id = ?

            ORDER BY
                h.data_vigencia DESC,
                h.id DESC

            LIMIT 1
            """,
            (
                alimento_id,
                fazenda_id
            )
        )

        return cursor.fetchone()

    finally:
        conn.close()


def buscar_ms_alimento_na_data(
    alimento_id,
    fazenda_id,
    data_referencia
):
    """
    Retorna a MS vigente para o alimento
    na data informada.

    Exemplo:
        01/09 -> 88%
        15/09 -> 86%

        consulta em 20/09 -> 86%
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                h.id,
                h.alimento_id,
                h.fazenda_id,
                h.materia_seca,
                h.data_vigencia,
                h.observacao,
                h.criado_em

            FROM alimento_ms_historico AS h

            WHERE
                h.alimento_id = ?
                AND h.fazenda_id = ?
                AND h.data_vigencia <= ?

            ORDER BY
                h.data_vigencia DESC,
                h.id DESC

            LIMIT 1
            """,
            (
                alimento_id,
                fazenda_id,
                data_referencia
            )
        )

        return cursor.fetchone()

    finally:
        conn.close()
# ==========================================================
# DIETAS
# ==========================================================

def cadastrar_dieta(
    fazenda_id,
    nome,
    itens,
    observacoes=None
):
    """
    itens:
    [
        {
            "alimento_id": 1,
            "inclusao_ms": 50.0,
            "ordem_carregamento": 1
        },
        ...
    ]
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

        nome = (nome or "").strip()

        if not nome:
            raise ValueError(
                "Informe o nome da dieta."
            )

        if not itens:
            raise ValueError(
                "A dieta precisa possuir "
                "pelo menos um ingrediente."
            )

        # --------------------------------------------------
        # Valida soma das inclusões
        # --------------------------------------------------

        soma = sum(
            float(item["inclusao_ms"])
            for item in itens
        )

        if abs(soma - 100.0) > 0.01:

            raise ValueError(
                f"A soma das inclusões deve ser 100%. "
                f"Valor atual: {soma:.2f}%."
            )

        # --------------------------------------------------
        # Determina a próxima versão
        # --------------------------------------------------

        registro = cursor.execute(
            """
            SELECT MAX(versao) AS ultima_versao

            FROM dietas

            WHERE
                fazenda_id = ?
                AND LOWER(nome) = LOWER(?)
            """,
            (
                fazenda_id,
                nome
            )
        ).fetchone()

        ultima_versao = (
            registro["ultima_versao"]
            if registro
            and registro["ultima_versao"]
            is not None
            else 0
        )

        nova_versao = ultima_versao + 1

        # --------------------------------------------------
        # Ao criar nova versão, arquiva anteriores
        # --------------------------------------------------

        cursor.execute(
            """
            UPDATE dietas

            SET status = 'ARQUIVADA'

            WHERE
                fazenda_id = ?
                AND LOWER(nome) = LOWER(?)
                AND status = 'ATIVA'
            """,
            (
                fazenda_id,
                nome
            )
        )

        # --------------------------------------------------
        # Cria a dieta
        # --------------------------------------------------

        cursor.execute(
            """
            INSERT INTO dietas (
                fazenda_id,
                nome,
                versao,
                status,
                observacoes
            )

            VALUES (?, ?, ?, 'ATIVA', ?)
            """,
            (
                fazenda_id,
                nome,
                nova_versao,
                observacoes
            )
        )

        dieta_id = cursor.lastrowid

        # --------------------------------------------------
        # Cria os ingredientes
        # --------------------------------------------------

        alimentos_usados = set()

        for item in itens:

            alimento_id = int(
                item["alimento_id"]
            )

            inclusao = float(
                item["inclusao_ms"]
            )

            ordem = item.get(
                "ordem_carregamento"
            )

            if alimento_id in alimentos_usados:

                raise ValueError(
                    "Um alimento não pode aparecer "
                    "duas vezes na mesma dieta."
                )

            alimentos_usados.add(
                alimento_id
            )

            alimento = cursor.execute(
                """
                SELECT id

                FROM alimentos

                WHERE
                    id = ?
                    AND fazenda_id = ?
                    AND ativo = 1

                LIMIT 1
                """,
                (
                    alimento_id,
                    fazenda_id
                )
            ).fetchone()

            if alimento is None:

                raise ValueError(
                    "Um dos alimentos selecionados "
                    "não pertence à fazenda ou está inativo."
                )

            if inclusao <= 0:

                raise ValueError(
                    "A inclusão dos ingredientes "
                    "deve ser maior que zero."
                )

            cursor.execute(
                """
                INSERT INTO dieta_itens (
                    dieta_id,
                    alimento_id,
                    inclusao_ms,
                    ordem_carregamento
                )

                VALUES (?, ?, ?, ?)
                """,
                (
                    dieta_id,
                    alimento_id,
                    inclusao,
                    ordem
                )
            )

        conn.commit()

        return dieta_id

    except:
        conn.rollback()
        raise

    finally:
        conn.close()


def listar_dietas_fazenda(
    fazenda_id,
    incluir_arquivadas=False
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        filtro = ""

        if not incluir_arquivadas:
            filtro = (
                "AND d.status = 'ATIVA'"
            )

        cursor.execute(
            f"""
            SELECT
                d.id,
                d.fazenda_id,
                d.nome,
                d.versao,
                d.status,
                d.observacoes,
                d.criado_em,

                f.nome AS fazenda_nome

            FROM dietas AS d

            INNER JOIN fazendas AS f
                ON f.id = d.fazenda_id

            WHERE
                d.fazenda_id = ?
                {filtro}

            ORDER BY
                d.nome,
                d.versao DESC
            """,
            (fazenda_id,)
        )

        return cursor.fetchall()

    finally:
        conn.close()


def listar_itens_dieta(
    dieta_id,
    fazenda_id
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                di.id,
                di.dieta_id,
                di.alimento_id,
                di.inclusao_ms,
                di.ordem_carregamento,

                a.nome AS alimento_nome,
                a.categoria AS alimento_categoria,
                a.unidade AS alimento_unidade

            FROM dieta_itens AS di

            INNER JOIN dietas AS d
                ON d.id = di.dieta_id

            INNER JOIN alimentos AS a
                ON a.id = di.alimento_id

            WHERE
                di.dieta_id = ?
                AND d.fazenda_id = ?

            ORDER BY
                CASE
                    WHEN di.ordem_carregamento IS NULL
                    THEN 999999
                    ELSE di.ordem_carregamento
                END,
                di.id
            """,
            (
                dieta_id,
                fazenda_id
            )
        )

        return cursor.fetchall()

    finally:
        conn.close()


def buscar_dieta_por_id(
    dieta_id,
    fazenda_id
):
    conn = get_connection()

    try:
        return conn.execute(
            """
            SELECT
                id,
                fazenda_id,
                nome,
                versao,
                status,
                observacoes,
                criado_em

            FROM dietas

            WHERE
                id = ?
                AND fazenda_id = ?

            LIMIT 1
            """,
            (
                dieta_id,
                fazenda_id
            )
        ).fetchone()

    finally:
        conn.close()


def arquivar_dieta(
    dieta_id,
    fazenda_id
):
    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE dietas

            SET status = 'ARQUIVADA'

            WHERE
                id = ?
                AND fazenda_id = ?
            """,
            (
                dieta_id,
                fazenda_id
            )
        )

        conn.commit()

    finally:
        conn.close()