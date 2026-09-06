import flet as ft

from database.migrations import criar_tabelas

from screens.login import tela_login
from screens.layout import layout_principal
from screens.organizacoes import tela_organizacoes
from screens.fazendas import tela_fazendas
from screens.usuarios import tela_usuarios
from screens.consultores import tela_consultores
from screens.carteira_consultores import (
    tela_carteira_consultores
)

from services.sessao import sessao


def main(page: ft.Page):

    criar_tabelas()

    page.title = "Tratos"
    page.padding = 0

    area_conteudo = None

    # ======================================================
    # LOGIN
    # ======================================================

    def mostrar_login():

        sessao.limpar()

        page.clean()

        page.padding = 30

        page.add(
            tela_login(
                page,
                abrir_sistema
            )
        )

        page.update()

    # ======================================================
    # ABRIR SISTEMA
    # ======================================================

    def abrir_sistema():

        nonlocal area_conteudo

        page.clean()

        page.padding = 0

        layout, area_conteudo = layout_principal(
            page=page,
            navegar=navegar,
            sair=mostrar_login
        )

        page.add(layout)

        navegar("inicio")

        page.update()

    # ======================================================
    # NAVEGAÇÃO
    # ======================================================

    def navegar(rota):

        if area_conteudo is None:
            return

        area_conteudo.controls.clear()

        # ==========================================
        # INÍCIO
        # ==========================================

        if rota == "inicio":

            area_conteudo.controls.append(
                tela_inicio()
            )

        # ==========================================
        # CLIENTES
        # ==========================================

        elif rota == "clientes":

            area_conteudo.controls.append(
                tela_organizacoes(page)
            )

        # ==========================================
        # FAZENDAS
        # ==========================================

        elif rota == "fazendas":

            area_conteudo.controls.append(
                tela_fazendas(page)
            )

        # ==========================================
        # USUÁRIOS
        # ==========================================

        elif rota == "usuarios":

            area_conteudo.controls.append(
                tela_usuarios(page)
            )
        elif rota == "consultores":

            area_conteudo.controls.append(
                tela_consultores(page)
            )


        elif rota == "carteira":

            area_conteudo.controls.append(
                tela_carteira_consultores(page)
            )
        # ==========================================
        # TELAS AINDA NÃO IMPLEMENTADAS
        # ==========================================

        else:

            area_conteudo.controls.append(

                ft.Column(
                    controls=[

                        ft.Text(
                            rota.capitalize(),
                            size=30,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            "Módulo em desenvolvimento."
                        )

                    ]
                )

            )

        page.update()

    # ======================================================
    # HOME
    # ======================================================

    def tela_inicio():

        fazenda = (
            sessao.fazenda_atual_nome
            or "Nenhuma fazenda selecionada"
        )

        perfil = (
            sessao.fazenda_atual_perfil
            or sessao.perfil_sistema
        )

        return ft.Column(

            controls=[

                ft.Text(
                    "Início",
                    size=30,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    f"Bem-vindo, {sessao.nome}."
                ),

                ft.Divider(),

                ft.Text(
                    "Fazenda atual",
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    fazenda,
                    size=22
                ),

                ft.Text(
                    f"Perfil: {perfil}"
                )

            ],

            spacing=10
        )

    # ======================================================
    # INÍCIO
    # ======================================================

    mostrar_login()


if __name__ == "__main__":

    ft.run(main)