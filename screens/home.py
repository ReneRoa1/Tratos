import flet as ft

from services.sessao import sessao


def tela_home(page: ft.Page, sair):

    controles = [

        ft.Text(
            f"Bem-vindo, {sessao.nome}",
            size=30,
            weight=ft.FontWeight.BOLD
        ),

        ft.Text(
            f"Perfil do sistema: "
            f"{sessao.perfil_sistema}"
        )

    ]

    # ==========================================
    # ORGANIZAÇÕES
    # ==========================================

    if sessao.organizacoes:

        controles.append(
            ft.Divider()
        )

        controles.append(
            ft.Text(
                "Clientes / Organizações",
                size=20,
                weight=ft.FontWeight.BOLD
            )
        )

        for organizacao in sessao.organizacoes:

            nome = (
                organizacao["nome_fantasia"]
                or organizacao["nome"]
            )

            controles.append(
                ft.Text(
                    f'{nome} '
                    f'— {organizacao["perfil"]}'
                )
            )

    # ==========================================
    # FAZENDAS
    # ==========================================

    if sessao.fazendas:

        controles.append(
            ft.Divider()
        )

        controles.append(
            ft.Text(
                "Fazendas disponíveis",
                size=20,
                weight=ft.FontWeight.BOLD
            )
        )

        for fazenda in sessao.fazendas:

            controles.append(
                ft.Text(
                    f'{fazenda["fazenda_nome"]} '
                    f'— {fazenda["perfil"]}'
                )
            )

    else:

        controles.append(
            ft.Text(
                "Nenhuma fazenda vinculada."
            )
        )

    controles.append(
        ft.Divider()
    )

    controles.append(
        ft.Button(
            content="Sair",
            icon=ft.Icons.LOGOUT,
            on_click=lambda e: sair()
        )
    )

    return ft.Column(
        controls=controles,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )