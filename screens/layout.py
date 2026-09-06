import flet as ft

from services.sessao import sessao


def layout_principal(
    page: ft.Page,
    navegar,
    sair
):

    # ======================================================
    # SELETOR DE FAZENDA
    # ======================================================

    titulo_seletor = (
        "Visualizar fazenda"
        if sessao.perfil_sistema == "ADMIN"
        else "Fazenda atual"
    )

    seletor_fazenda = ft.Dropdown(
        label=titulo_seletor,
        width=300
    )

    def atualizar_seletor_fazendas():

        seletor_fazenda.options.clear()

        for fazenda in sessao.fazendas:

            seletor_fazenda.options.append(
                ft.DropdownOption(
                    key=str(
                        fazenda["fazenda_id"]
                    ),
                    text=(
                        fazenda["fazenda_nome"]
                    )
                )
            )

        if sessao.fazenda_atual_id is not None:

            seletor_fazenda.value = str(
                sessao.fazenda_atual_id
            )

        else:

            seletor_fazenda.value = None

        page.update()


    atualizar_seletor_fazendas()

    def alterar_fazenda(e):

        if not seletor_fazenda.value:
            return

        fazenda_id = int(
            seletor_fazenda.value
        )

        for fazenda in sessao.fazendas:

            if fazenda["fazenda_id"] == fazenda_id:

                sessao.selecionar_fazenda(
                    fazenda_id=fazenda["fazenda_id"],
                    fazenda_nome=fazenda["fazenda_nome"],
                    perfil=fazenda["perfil"]
                )

                break

        navegar("inicio")

    seletor_fazenda.on_select = alterar_fazenda

    # ======================================================
    # MENU
    # ======================================================

    itens_menu = []

    def adicionar_item(
        titulo,
        icone,
        rota
    ):

        itens_menu.append(
            ft.Button(
                content=titulo,
                icon=icone,
                on_click=lambda e, r=rota: navegar(r)
            )
        )

     # ======================================================
    # INÍCIO - TODOS
    # ======================================================

    adicionar_item(
        "Início",
        ft.Icons.HOME,
        "inicio"
    )

    # ======================================================
    # ADMIN
    # ======================================================

    if sessao.perfil_sistema == "ADMIN":

        adicionar_item(
            "Consultores",
            ft.Icons.SUPERVISOR_ACCOUNT,
            "consultores"
        )

        adicionar_item(
            "Carteiras",
            ft.Icons.ACCOUNT_TREE,
            "carteira"
        )

        adicionar_item(
            "Usuários",
            ft.Icons.PEOPLE,
            "usuarios"
        )

    # ======================================================
    # CONSULTOR
    # ======================================================

    elif sessao.perfil_sistema == "CONSULTOR":

        adicionar_item(
            "Clientes",
            ft.Icons.BUSINESS,
            "clientes"
        )

        adicionar_item(
            "Fazendas",
            ft.Icons.AGRICULTURE,
            "fazendas"
        )

        adicionar_item(
            "Usuários",
            ft.Icons.PEOPLE,
            "usuarios"
        )

        adicionar_item(
            "Piquetes",
            ft.Icons.LANDSCAPE,
            "piquetes"
        )

        adicionar_item(
            "Lotes",
            ft.Icons.PETS,
            "lotes"
        )

        adicionar_item(
            "Alimentos",
            ft.Icons.GRASS,
            "alimentos"
        )

        adicionar_item(
            "Dietas",
            ft.Icons.RESTAURANT,
            "dietas"
        )

        adicionar_item(
            "Misturadores",
            ft.Icons.LOCAL_SHIPPING,
            "misturadores"
        )

        adicionar_item(
            "Cocho",
            ft.Icons.ASSIGNMENT,
            "cocho"
        )

        adicionar_item(
            "Tratos",
            ft.Icons.CHECKLIST,
            "tratos"
        )

    # ======================================================
    # USUÁRIO DA FAZENDA
    # ======================================================

    elif sessao.perfil_sistema == "USUARIO":

        # ==============================================
        # PROPRIETÁRIO OU GERENTE
        # ==============================================

        if sessao.fazenda_atual_perfil in [
            "PROPRIETARIO",
            "GERENTE"
        ]:

            adicionar_item(
                "Piquetes",
                ft.Icons.LANDSCAPE,
                "piquetes"
            )

            adicionar_item(
                "Lotes",
                ft.Icons.PETS,
                "lotes"
            )

            adicionar_item(
                "Alimentos",
                ft.Icons.GRASS,
                "alimentos"
            )

            adicionar_item(
                "Dietas",
                ft.Icons.RESTAURANT,
                "dietas"
            )

            adicionar_item(
                "Misturadores",
                ft.Icons.LOCAL_SHIPPING,
                "misturadores"
            )

            adicionar_item(
                "Cocho",
                ft.Icons.ASSIGNMENT,
                "cocho"
            )

            adicionar_item(
                "Tratos",
                ft.Icons.CHECKLIST,
                "tratos"
            )

        # ==============================================
        # FUNCIONÁRIO / PEÃO
        # ==============================================

        elif sessao.fazenda_atual_perfil == "FUNCIONARIO":

            adicionar_item(
                "Cocho",
                ft.Icons.ASSIGNMENT,
                "cocho"
            )

            adicionar_item(
                "Tratos",
                ft.Icons.CHECKLIST,
                "tratos"
            )

    # ======================================================
    # CONTEÚDO DA PÁGINA
    # ======================================================

    area_conteudo = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )

    # ======================================================
    # TOPO
    # ======================================================

    topo = ft.Container(

        content=ft.Row(

            controls=[

                ft.Column(
                    controls=[

                        ft.Text(
                            "TRATOS",
                            size=24,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            f"Olá, {sessao.nome}"
                        )

                    ],

                    spacing=2
                ),

                ft.Container(expand=True),

                seletor_fazenda,

                ft.Button(
                    content="Sair",
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda e: sair()
                )

            ],

            vertical_alignment=(
                ft.CrossAxisAlignment.CENTER
            )

        ),

        padding=15
    )

    # ======================================================
    # MENU LATERAL
    # ======================================================

    menu = ft.Container(

        content=ft.Column(

            controls=itens_menu,

            spacing=8,

            scroll=ft.ScrollMode.AUTO

        ),

        width=220,

        padding=15,

        border=ft.Border.all(
            1,
            ft.Colors.OUTLINE_VARIANT
        )

    )

    # ======================================================
    # CORPO
    # ======================================================

    corpo = ft.Row(

        controls=[

            menu,

            ft.Container(
                content=area_conteudo,
                padding=25,
                expand=True
            )

        ],

        expand=True,

        vertical_alignment=(
            ft.CrossAxisAlignment.START
        )

    )

    return (
        ft.Column(
            controls=[
                topo,
                ft.Divider(height=1),
                corpo
            ],
            expand=True
        ),
        area_conteudo,
        atualizar_seletor_fazendas
    )