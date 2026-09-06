from database.database import get_connection


# ==========================================================
# FUNÇÕES AUXILIARES DE MIGRAÇÃO
# ==========================================================

def coluna_existe(conn, tabela, coluna):
    cursor = conn.execute(f"PRAGMA table_info({tabela})")

    colunas = [
        linha["name"]
        for linha in cursor.fetchall()
    ]

    return coluna in colunas


def adicionar_coluna_se_nao_existir(
    conn,
    tabela,
    coluna,
    definicao
):
    if not coluna_existe(
        conn,
        tabela,
        coluna
    ):
        conn.execute(
            f"""
            ALTER TABLE {tabela}
            ADD COLUMN {coluna} {definicao}
            """
        )


# ==========================================================
# CRIAÇÃO / ATUALIZAÇÃO DO BANCO
# ==========================================================

def criar_tabelas():

    conn = get_connection()

    cursor = conn.cursor()

    # ======================================================
    # ORGANIZAÇÕES / CLIENTES
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS organizacoes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            nome_fantasia TEXT,

            documento TEXT,

            telefone TEXT,

            email TEXT,

            observacoes TEXT,

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP

        );
    """)

    # ======================================================
    # FAZENDAS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fazendas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            identificacao TEXT,

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP

        );
    """)

    # Adiciona vínculo com organização sem apagar dados antigos
    adicionar_coluna_se_nao_existir(
        conn,
        "fazendas",
        "organizacao_id",
        "INTEGER REFERENCES organizacoes(id)"
    )

    # ======================================================
    # USUÁRIOS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nome TEXT NOT NULL,

            login TEXT NOT NULL UNIQUE,

            senha_hash TEXT,

            perfil TEXT NOT NULL DEFAULT 'FUNCIONARIO',

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP

        );
    """)

    # Perfil geral do sistema
    adicionar_coluna_se_nao_existir(
        conn,
        "usuarios",
        "perfil_sistema",
        "TEXT NOT NULL DEFAULT 'USUARIO'"
    )

    # ======================================================
    # USUÁRIOS x ORGANIZAÇÕES
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_organizacoes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario_id INTEGER NOT NULL,

            organizacao_id INTEGER NOT NULL,

            perfil TEXT NOT NULL,

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id),

            FOREIGN KEY (organizacao_id)
                REFERENCES organizacoes(id),

            UNIQUE (
                usuario_id,
                organizacao_id
            )

        );
    """)

    # ======================================================
    # USUÁRIOS x FAZENDAS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_fazendas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            usuario_id INTEGER NOT NULL,

            fazenda_id INTEGER NOT NULL,

            FOREIGN KEY (usuario_id)
                REFERENCES usuarios(id),

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id),

            UNIQUE (
                usuario_id,
                fazenda_id
            )

        );
    """)

    # Permissão específica dentro da fazenda
    adicionar_coluna_se_nao_existir(
        conn,
        "usuarios_fazendas",
        "perfil",
        "TEXT NOT NULL DEFAULT 'FUNCIONARIO'"
    )

    adicionar_coluna_se_nao_existir(
        conn,
        "usuarios_fazendas",
        "ativo",
        "INTEGER NOT NULL DEFAULT 1"
    )

    # ======================================================
    # PIQUETES
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS piquetes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fazenda_id INTEGER NOT NULL,

            nome TEXT NOT NULL,

            identificacao TEXT,

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id)

        );
    """)

    # ======================================================
    # LOTES
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lotes (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fazenda_id INTEGER NOT NULL,

            piquete_id INTEGER,

            nome TEXT NOT NULL,

            numero_animais INTEGER NOT NULL,

            peso_medio_entrada REAL,

            data_entrada TEXT,

            data_saida TEXT,

            status TEXT NOT NULL DEFAULT 'ATIVO',

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id),

            FOREIGN KEY (piquete_id)
                REFERENCES piquetes(id)

        );
    """)
        # ======================================================
    # CAMPOS DE AUDITORIA
    # ======================================================

    adicionar_coluna_se_nao_existir(
        conn,
        "usuarios",
        "desativado_em",
        "TEXT"
    )

    adicionar_coluna_se_nao_existir(
        conn,
        "usuarios",
        "desativado_por",
        "INTEGER REFERENCES usuarios(id)"
    )

    adicionar_coluna_se_nao_existir(
        conn,
        "organizacoes",
        "desativado_em",
        "TEXT"
    )

    adicionar_coluna_se_nao_existir(
        conn,
        "organizacoes",
        "desativado_por",
        "INTEGER REFERENCES usuarios(id)"
    )

    adicionar_coluna_se_nao_existir(
        conn,
        "fazendas",
        "desativado_em",
        "TEXT"
    )

    adicionar_coluna_se_nao_existir(
        conn,
        "fazendas",
        "desativado_por",
        "INTEGER REFERENCES usuarios(id)"
    )

        # ======================================================
    # RESPONSÁVEIS TÉCNICOS PELAS FAZENDAS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsaveis_fazenda (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fazenda_id INTEGER NOT NULL,

            consultor_id INTEGER NOT NULL,

            papel TEXT NOT NULL DEFAULT 'PRINCIPAL',

            data_inicio TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            data_fim TEXT,

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id),

            FOREIGN KEY (consultor_id)
                REFERENCES usuarios(id)

        );
    """)

    conn.commit()

    conn.close()