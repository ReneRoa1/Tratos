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
    # HISTÓRICO DE MOVIMENTAÇÃO DOS LOTES ENTRE PIQUETES
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lotes_piquetes_historico (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            lote_id INTEGER NOT NULL,

            fazenda_id INTEGER NOT NULL,

            piquete_id INTEGER NOT NULL,

            data_inicio TEXT NOT NULL,

            data_fim TEXT,

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (lote_id)
                REFERENCES lotes(id),

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id),

            FOREIGN KEY (piquete_id)
                REFERENCES piquetes(id)

        );
    """)
        # ======================================================
    # CRIA HISTÓRICO INICIAL PARA LOTES JÁ EXISTENTES
    # ======================================================

    cursor.execute("""
        INSERT INTO lotes_piquetes_historico (
            lote_id,
            fazenda_id,
            piquete_id,
            data_inicio,
            ativo
        )

        SELECT
            l.id,
            l.fazenda_id,
            l.piquete_id,
            COALESCE(
                l.data_entrada,
                DATE(l.criado_em),
                DATE('now')
            ),
            CASE
                WHEN l.status = 'ATIVO' THEN 1
                ELSE 0
            END

        FROM lotes AS l

        WHERE
            l.piquete_id IS NOT NULL

            AND NOT EXISTS (
                SELECT 1
                FROM lotes_piquetes_historico AS h
                WHERE h.lote_id = l.id
            );
    """)
    # ======================================================
    # ALIMENTOS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alimentos (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fazenda_id INTEGER NOT NULL,

            nome TEXT NOT NULL,

            categoria TEXT NOT NULL,

            unidade TEXT NOT NULL DEFAULT 'kg',

            ativo INTEGER NOT NULL DEFAULT 1,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id)

        );
    """)
        # ======================================================
    # HISTÓRICO DE MATÉRIA SECA DOS ALIMENTOS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alimento_ms_historico (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            alimento_id INTEGER NOT NULL,

            fazenda_id INTEGER NOT NULL,

            materia_seca REAL NOT NULL,

            data_vigencia TEXT NOT NULL,

            observacao TEXT,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (alimento_id)
                REFERENCES alimentos(id),

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id),

            UNIQUE (
                alimento_id,
                data_vigencia
            )
        );
    """)
        # ======================================================
    # DIETAS
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dietas (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fazenda_id INTEGER NOT NULL,

            nome TEXT NOT NULL,

            versao INTEGER NOT NULL DEFAULT 1,

            status TEXT NOT NULL DEFAULT 'ATIVA',

            observacoes TEXT,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (fazenda_id)
                REFERENCES fazendas(id),

            UNIQUE (
                fazenda_id,
                nome,
                versao
            )
        );
    """)

    # ======================================================
    # ITENS DA DIETA
    # ======================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dieta_itens (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            dieta_id INTEGER NOT NULL,

            alimento_id INTEGER NOT NULL,

            inclusao_ms REAL NOT NULL,

            ordem_carregamento INTEGER,

            criado_em TEXT NOT NULL
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (dieta_id)
                REFERENCES dietas(id),

            FOREIGN KEY (alimento_id)
                REFERENCES alimentos(id),

            UNIQUE (
                dieta_id,
                alimento_id
            )
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