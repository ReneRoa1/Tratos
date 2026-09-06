class SessaoUsuario:

    def __init__(self):
        self.limpar()

    def limpar(self):

        self.usuario_id = None
        self.nome = None
        self.login = None
        self.perfil_sistema = None

        self.organizacoes = []
        self.fazendas = []

        self.fazenda_atual_id = None
        self.fazenda_atual_nome = None
        self.fazenda_atual_perfil = None

    def selecionar_fazenda(
        self,
        fazenda_id,
        fazenda_nome,
        perfil=None
    ):

        self.fazenda_atual_id = fazenda_id
        self.fazenda_atual_nome = fazenda_nome
        self.fazenda_atual_perfil = perfil


sessao = SessaoUsuario()

# ==========================================================
# ATUALIZAÇÃO DAS FAZENDAS DISPONÍVEIS NA SESSÃO
# ==========================================================

def recarregar_fazendas_sessao():
    """
    Atualiza a lista de fazendas disponíveis para o usuário
    logado, preservando a fazenda atual quando ela continuar
    autorizada.
    """

    from database.models import (
        listar_fazendas,
        listar_fazendas_consultor,
        listar_fazendas_usuario,
    )

    if sessao.usuario_id is None:
        sessao.fazendas = []
        sessao.selecionar_fazenda(
            fazenda_id=None,
            fazenda_nome=None,
            perfil=None
        )
        return

    fazenda_anterior_id = sessao.fazenda_atual_id

    novas_fazendas = []

    # ======================================================
    # ADMIN
    # ======================================================

    if sessao.perfil_sistema == "ADMIN":

        fazendas = listar_fazendas()

        for fazenda in fazendas:

            novas_fazendas.append({
                "fazenda_id": fazenda["id"],
                "fazenda_nome": fazenda["nome"],
                "perfil": "LEITURA",
                "organizacao_nome":
                    fazenda["organizacao_nome"],
                "organizacao_nome_fantasia":
                    fazenda["organizacao_nome_fantasia"],
            })

    # ======================================================
    # CONSULTOR
    # ======================================================

    elif sessao.perfil_sistema == "CONSULTOR":

        fazendas = listar_fazendas_consultor(
            sessao.usuario_id
        )

        for fazenda in fazendas:

            novas_fazendas.append({
                "fazenda_id": fazenda["fazenda_id"],
                "fazenda_nome": fazenda["fazenda_nome"],
                "perfil": "CONSULTOR",
                "organizacao_nome":
                    fazenda["organizacao_nome"],
                "organizacao_nome_fantasia":
                    fazenda["organizacao_nome_fantasia"],
            })

    # ======================================================
    # USUÁRIO DA FAZENDA
    # ======================================================

    elif sessao.perfil_sistema == "USUARIO":

        novas_fazendas = list(
            listar_fazendas_usuario(
                sessao.usuario_id
            )
        )

    sessao.fazendas = novas_fazendas

    # ======================================================
    # PRESERVA A FAZENDA QUE JÁ ESTAVA SELECIONADA
    # ======================================================

    fazenda_encontrada = None

    if fazenda_anterior_id is not None:

        for fazenda in sessao.fazendas:

            if (
                fazenda["fazenda_id"]
                == fazenda_anterior_id
            ):
                fazenda_encontrada = fazenda
                break

    if fazenda_encontrada is not None:

        sessao.selecionar_fazenda(
            fazenda_id=(
                fazenda_encontrada["fazenda_id"]
            ),
            fazenda_nome=(
                fazenda_encontrada["fazenda_nome"]
            ),
            perfil=(
                fazenda_encontrada["perfil"]
            )
        )

    # ======================================================
    # SE HOUVER APENAS UMA FAZENDA
    # ======================================================

    elif len(sessao.fazendas) == 1:

        fazenda = sessao.fazendas[0]

        sessao.selecionar_fazenda(
            fazenda_id=fazenda["fazenda_id"],
            fazenda_nome=fazenda["fazenda_nome"],
            perfil=fazenda["perfil"]
        )

    # ======================================================
    # NENHUMA FAZENDA SELECIONADA
    # ======================================================

    else:

        sessao.selecionar_fazenda(
            fazenda_id=None,
            fazenda_nome=None,
            perfil=None
        )