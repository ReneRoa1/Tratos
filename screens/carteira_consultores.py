import flet as ft

from database.models import (
    listar_consultores,
    listar_fazendas,
    listar_fazendas_consultor,
    vincular_consultor_fazenda,
    encerrar_vinculo_consultor_fazenda
)

from services.sessao import sessao


def tela_carteira_consultores(page: ft.Page):

    # ======================================================
    # SEGURANÇA
    # ======================================================

    if sessao.perfil_sistema != "ADMIN":

        return ft.Column(
            controls=[
                ft.Text(
                    "Acesso não autorizado",
                    size=30,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Somente administradores podem "
                    "gerenciar as carteiras dos consultores."
                )
            ]
        )

    # ======================================================
    # CAMPOS
    # ======================================================

    campo_consultor = ft.Dropdown(
        label="Consultor",
        width=500
    )

    campo_fazenda = ft.Dropdown(
        label="Fazenda",
        width=500
    )

    campo_papel = ft.Dropdown(
        label="Responsabilidade",
        width=500,
        value="PRINCIPAL",
        options=[
            ft.DropdownOption(
                key="PRINCIPAL",
                text="Consultor principal"
            ),
            ft.DropdownOption(
                key="AUXILIAR",
                text="Consultor auxiliar"
            )
        ]
    )

    mensagem = ft.Text()

    lista_carteira = ft.Column(
        spacing=10
    )

    # ======================================================
    # CARREGAR COMBOS
    # ======================================================

    def carregar_dados():

        campo_consultor.options.clear()
        campo_fazenda.options.clear()

        # CONSULTOR
        consultores = listar_consultores()

        for consultor in consultores:

            campo_consultor.options.append(
                ft.DropdownOption(
                    key=str(consultor["id"]),
                    text=(
                        f'{consultor["nome"]} '
                        f'— {consultor["login"]}'
                    )
                )
            )

        # FAZENDA
        fazendas = listar_fazendas()

        for fazenda in fazendas:

            cliente = (
                fazenda["organizacao_nome_fantasia"]
                or fazenda["organizacao_nome"]
                or "Sem cliente"
            )

            campo_fazenda.options.append(
                ft.DropdownOption(
                    key=str(fazenda["id"]),
                    text=(
                        f'{fazenda["nome"]} '
                        f'({cliente})'
                    )
                )
            )

    # ======================================================
    # CARREGAR CARTEIRA DO CONSULTOR
    # ======================================================

    def carregar_carteira(e=None):

        lista_carteira.controls.clear()

        if not campo_consultor.value:

            lista_carteira.controls.append(
                ft.Text(
                    "Selecione um consultor."
                )
            )

            page.update()
            return

        consultor_id = int(
            campo_consultor.value
        )

        fazendas = listar_fazendas_consultor(
            consultor_id
        )

        if not fazendas:

            lista_carteira.controls.append(
                ft.Text(
                    "Nenhuma fazenda atribuída a este consultor."
                )
            )

            page.update()
            return

        for fazenda in fazendas:

            cliente = (
                fazenda["organizacao_nome_fantasia"]
                or fazenda["organizacao_nome"]
                or "Sem cliente"
            )

            lista_carteira.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[

                            ft.Column(
                                controls=[

                                    ft.Text(
                                        fazenda["fazenda_nome"],
                                        size=18,
                                        weight=ft.FontWeight.BOLD
                                    ),

                                    ft.Text(
                                        f"Cliente: {cliente}"
                                    ),

                                    ft.Text(
                                        f'Papel: {fazenda["papel"]}'
                                    )

                                ],
                                spacing=3,
                                expand=True
                            ),

                            ft.Button(
                                content="Remover",
                                icon=ft.Icons.LINK_OFF,
                                on_click=lambda e,
                                fid=fazenda["fazenda_id"]:
                                remover_fazenda(fid)
                            )

                        ]
                    ),

                    padding=15,

                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT
                    ),

                    border_radius=10
                )
            )

        page.update()

    campo_consultor.on_select = carregar_carteira

    # ======================================================
    # ATRIBUIR FAZENDA
    # ======================================================

    def atribuir_fazenda(e):

        if not campo_consultor.value:

            mensagem.value = (
                "Selecione o consultor."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if not campo_fazenda.value:

            mensagem.value = (
                "Selecione a fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        vincular_consultor_fazenda(
            consultor_id=int(
                campo_consultor.value
            ),
            fazenda_id=int(
                campo_fazenda.value
            ),
            papel=campo_papel.value
        )

        mensagem.value = (
            "Fazenda atribuída ao consultor com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_carteira()

        page.update()

    # ======================================================
    # REMOVER FAZENDA DA CARTEIRA
    # ======================================================

    def remover_fazenda(fazenda_id):

        consultor_id = int(
            campo_consultor.value
        )

        encerrar_vinculo_consultor_fazenda(
            consultor_id=consultor_id,
            fazenda_id=fazenda_id
        )

        carregar_carteira()

        page.update()

    # ======================================================
    # INÍCIO
    # ======================================================

    carregar_dados()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[

            ft.Text(
                "Carteira de consultores",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Defina quais fazendas cada consultor "
                "da empresa é responsável por atender."
            ),

            ft.Divider(),

            ft.Text(
                "Selecionar consultor",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_consultor,

            ft.Divider(),

            ft.Text(
                "Atribuir fazenda",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_fazenda,

            campo_papel,

            ft.Button(
                content="Atribuir fazenda",
                icon=ft.Icons.LINK,
                on_click=atribuir_fazenda
            ),

            mensagem,

            ft.Divider(),

            ft.Text(
                "Fazendas do consultor",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            lista_carteira

        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )