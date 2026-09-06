import flet as ft

from database.models import (
    cadastrar_fazenda,
    listar_fazendas,
    listar_fazendas_todas,
    listar_organizacoes,
    atualizar_fazenda,
    desativar_fazenda,
    reativar_fazenda,
    vincular_consultor_fazenda,
    listar_fazendas_consultor,
    listar_fazendas_consultor_todas,
    listar_organizacoes_consultor,
    consultor_tem_acesso_fazenda
)

from services.sessao import (
    sessao,
    recarregar_fazendas_sessao,
)
from services.identificadores import codigo_fazenda


def tela_fazendas(
    page: ft.Page,
    atualizar_seletor_fazendas=None
):

    # ======================================================
    # CAMPOS DE NOVA FAZENDA
    # ======================================================

    campo_organizacao = ft.Dropdown(
        label="Cliente / Organização",
        width=500
    )

    campo_nome = ft.TextField(
        label="Nome da fazenda",
        hint_text="Ex.: Fazenda Santa Clara",
        width=500
    )

    campo_identificacao = ft.TextField(
        label="Identificação",
        hint_text="Ex.: Unidade 01",
        width=500
    )

    mensagem = ft.Text()

    # ======================================================
    # FILTRO
    # ======================================================

    mostrar_inativas = ft.Switch(
        label="Mostrar fazendas inativas",
        value=False
    )

    lista_fazendas = ft.Column(
        spacing=12
    )

    # ======================================================
    # ORGANIZAÇÕES
    # ======================================================

    def carregar_organizacoes():

        campo_organizacao.options.clear()

        organizacoes = listar_organizacoes_consultor(
            sessao.usuario_id
        )

        for organizacao in organizacoes:

            nome_exibicao = (
                organizacao["nome_fantasia"]
                or organizacao["nome"]
            )

            campo_organizacao.options.append(
                ft.DropdownOption(
                    key=str(organizacao["id"]),
                    text=nome_exibicao
                )
            )

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar_fazenda(e):

        if not campo_organizacao.value:

            mensagem.value = (
                "Selecione o cliente da fazenda."
            )

            mensagem.color = ft.Colors.RED
            page.update()
            return

        nome = campo_nome.value.strip()

        if not nome:

            mensagem.value = (
                "Informe o nome da fazenda."
            )

            mensagem.color = ft.Colors.RED
            page.update()
            return

        fazenda_id = cadastrar_fazenda(
            nome=nome,

            identificacao=(
                campo_identificacao.value.strip()
                or None
            ),

            organizacao_id=int(
                campo_organizacao.value
            )
        )

        vincular_consultor_fazenda(
            consultor_id=sessao.usuario_id,
            fazenda_id=fazenda_id,
            papel="PRINCIPAL"
        )
        # Atualiza as fazendas autorizadas da sessão
        recarregar_fazendas_sessao()

        # Atualiza imediatamente o seletor superior
        if atualizar_seletor_fazendas is not None:
            atualizar_seletor_fazendas()

        campo_nome.value = ""
        campo_identificacao.value = ""

        mensagem.value = (
            "Fazenda cadastrada com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_fazendas()

        page.update()

    # ======================================================
    # EDITAR FAZENDA
    # ======================================================

    def abrir_edicao(fazenda):
        if not consultor_tem_acesso_fazenda(
            sessao.usuario_id,
            fazenda["id"]
        ):

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=ft.Text(
                        "Acesso não autorizado"
                    ),
                    content=ft.Text(
                        "Esta fazenda não pertence "
                        "à sua carteira."
                    ),
                    actions=[
                        ft.Button(
                            content="OK",
                            on_click=lambda e:
                            page.pop_dialog()
                        )
                    ]
                )
            )

            return
        editar_organizacao = ft.Dropdown(
            label="Cliente / Organização",
            width=450
        )

        for organizacao in listar_organizacoes():

            nome_exibicao = (
                organizacao["nome_fantasia"]
                or organizacao["nome"]
            )

            editar_organizacao.options.append(
                ft.DropdownOption(
                    key=str(organizacao["id"]),
                    text=nome_exibicao
                )
            )

        if fazenda["organizacao_id"] is not None:
            editar_organizacao.value = str(
                fazenda["organizacao_id"]
            )

        editar_nome = ft.TextField(
            label="Nome da fazenda",
            value=fazenda["nome"],
            width=450
        )

        editar_identificacao = ft.TextField(
            label="Identificação",
            value=fazenda["identificacao"] or "",
            width=450
        )

        mensagem_edicao = ft.Text()

        def salvar_alteracoes(e):

            if not editar_organizacao.value:

                mensagem_edicao.value = (
                    "Selecione o cliente."
                )

                mensagem_edicao.color = ft.Colors.RED
                page.update()
                return

            nome = editar_nome.value.strip()

            if not nome:

                mensagem_edicao.value = (
                    "Informe o nome da fazenda."
                )

                mensagem_edicao.color = ft.Colors.RED
                page.update()
                return

            atualizar_fazenda(
                fazenda_id=fazenda["id"],

                nome=nome,

                identificacao=(
                    editar_identificacao.value.strip()
                    or None
                ),

                organizacao_id=int(
                    editar_organizacao.value
                )
            )

            page.pop_dialog()

            carregar_fazendas()

            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar {codigo_fazenda(fazenda['id'])}"
            ),

            content=ft.Column(
                controls=[
                    editar_organizacao,
                    editar_nome,
                    editar_identificacao,
                    mensagem_edicao
                ],
                tight=True,
                spacing=12
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.Button(
                    content="Salvar alterações",
                    icon=ft.Icons.SAVE,
                    on_click=salvar_alteracoes
                )

            ],

            actions_alignment=ft.MainAxisAlignment.END
        )

        page.show_dialog(dialogo)

    # ======================================================
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(fazenda):

        def confirmar(e):

            desativar_fazenda(
                fazenda_id=fazenda["id"],
                desativado_por=sessao.usuario_id
            )

            page.pop_dialog()

            carregar_fazendas()

            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Desativar fazenda?"
            ),

            content=ft.Column(
                controls=[

                    ft.Text(
                        f'{codigo_fazenda(fazenda["id"])} '
                        f'— {fazenda["nome"]}'
                    ),

                    ft.Text(
                        "A fazenda deixará de aparecer "
                        "nas listas de registros ativos."
                    ),

                    ft.Text(
                        "O histórico continuará armazenado."
                    )

                ],

                tight=True,
                spacing=10
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.Button(
                    content="Desativar",
                    icon=ft.Icons.BLOCK,
                    on_click=confirmar
                )

            ],

            actions_alignment=ft.MainAxisAlignment.END
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR
    # ======================================================

    def confirmar_reativacao(fazenda):

        def confirmar(e):

            reativar_fazenda(
                fazenda["id"]
            )

            page.pop_dialog()

            carregar_fazendas()

            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar fazenda?"
            ),

            content=ft.Text(
                f'{codigo_fazenda(fazenda["id"])} '
                f'— {fazenda["nome"]}'
            ),

            actions=[

                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e: page.pop_dialog()
                ),

                ft.Button(
                    content="Reativar",
                    icon=ft.Icons.REFRESH,
                    on_click=confirmar
                )

            ],

            actions_alignment=ft.MainAxisAlignment.END
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAGEM
    # ======================================================

    def carregar_fazendas(e=None):

        lista_fazendas.controls.clear()

        if mostrar_inativas.value:

            fazendas = listar_fazendas_consultor_todas(
                sessao.usuario_id
            )

        else:

            fazendas = listar_fazendas_consultor(
                sessao.usuario_id
            )

        if not fazendas:

            lista_fazendas.controls.append(
                ft.Text(
                    "Nenhuma fazenda encontrada."
                )
            )

            page.update()
            return

        for fazenda in fazendas:

            codigo = codigo_fazenda(
                fazenda["id"]
            )

            cliente = (
                fazenda["organizacao_nome_fantasia"]
                or fazenda["organizacao_nome"]
                or "Sem cliente"
            )

            identificacao = (
                fazenda["identificacao"]
                or "Não informada"
            )

            ativa = bool(
                fazenda["ativo"]
            )

            # ==============================================
            # DADOS DO CARD
            # ==============================================

            dados = [

                ft.Text(
                    codigo,
                    size=12,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    fazenda["nome"],
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    f"Cliente: {cliente}"
                ),

                ft.Text(
                    f"Identificação: {identificacao}"
                )

            ]

            # ==============================================
            # STATUS
            # ==============================================

            if ativa:

                dados.append(
                    ft.Text(
                        "● ATIVA",
                        color=ft.Colors.GREEN,
                        weight=ft.FontWeight.BOLD
                    )
                )

            else:

                dados.append(
                    ft.Text(
                        "● INATIVA",
                        color=ft.Colors.RED,
                        weight=ft.FontWeight.BOLD
                    )
                )

                if fazenda["desativado_em"]:

                    dados.append(
                        ft.Text(
                            f'Desativada em: '
                            f'{fazenda["desativado_em"]}'
                        )
                    )

            # ==============================================
            # BOTÕES
            # ==============================================

            botoes = []

            if ativa:

                botoes.append(
                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        f=fazenda:
                        abrir_edicao(f)
                    )
                )

                botoes.append(
                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e,
                        f=fazenda:
                        confirmar_desativacao(f)
                    )
                )

            else:

                botoes.append(
                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        f=fazenda:
                        confirmar_reativacao(f)
                    )
                )

            dados.append(
                ft.Row(
                    controls=botoes,
                    spacing=10
                )
            )

            # ==============================================
            # CARD
            # ==============================================

            lista_fazendas.controls.append(

                ft.Container(

                    content=ft.Column(
                        controls=dados,
                        spacing=6
                    ),

                    padding=18,

                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT
                    ),

                    border_radius=12
                )
            )

        page.update()

    mostrar_inativas.on_change = carregar_fazendas

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    carregar_organizacoes()

    carregar_fazendas()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(

        controls=[

            ft.Text(
                "Fazendas",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Cadastre e gerencie as propriedades "
                "dos clientes da consultoria."
            ),

            ft.Divider(),

            # ==============================================
            # NOVA FAZENDA
            # ==============================================

            ft.Text(
                "Nova fazenda",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_organizacao,

            campo_nome,

            campo_identificacao,

            ft.Button(
                content="Cadastrar fazenda",
                icon=ft.Icons.ADD,
                on_click=salvar_fazenda
            ),

            mensagem,

            ft.Divider(),

            # ==============================================
            # LISTAGEM
            # ==============================================

            ft.Row(
                controls=[

                    ft.Text(
                        "Fazendas cadastradas",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_inativas

                ]
            ),

            lista_fazendas

        ],

        spacing=15,

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )