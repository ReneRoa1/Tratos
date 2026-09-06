import flet as ft

from database.models import (
    buscar_usuario_ativo_por_login,
    listar_organizacoes_usuario,
    listar_fazendas_usuario,
    listar_fazendas_consultor,
    listar_fazendas
)

from services.auth import verificar_senha
from services.sessao import (
    sessao,
    recarregar_fazendas_sessao,
)


def tela_login(page: ft.Page, ao_entrar):

    campo_login = ft.TextField(
        label="Login / E-mail",
        width=400,
        autofocus=True
    )

    campo_senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        width=400
    )

    mensagem = ft.Text()

    def entrar(e):

        login = campo_login.value.strip()
        senha = campo_senha.value

        if not login:

            mensagem.value = "Informe o login."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        if not senha:

            mensagem.value = "Informe a senha."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        usuario = buscar_usuario_ativo_por_login(
            login
        )

        if usuario is None:

            mensagem.value = (
                "Login ou senha inválidos."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        if not verificar_senha(
            senha,
            usuario["senha_hash"]
        ):

            mensagem.value = (
                "Login ou senha inválidos."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        # ======================================
        # PREENCHE A SESSÃO
        # ======================================

        sessao.usuario_id = usuario["id"]
        sessao.nome = usuario["nome"]
        sessao.login = usuario["login"]
        sessao.perfil_sistema = usuario["perfil_sistema"]


        # ======================================
        # ORGANIZAÇÕES
        # ======================================

        sessao.organizacoes = list(
            listar_organizacoes_usuario(
                usuario["id"]
            )
        )


        # ======================================
        # FAZENDAS DISPONÍVEIS
        # ======================================

        recarregar_fazendas_sessao()


        # ======================================
        # ENTRA NO SISTEMA
        # ======================================

        ao_entrar()
    return ft.Container(

        content=ft.Column(

            controls=[

                ft.Text(
                    "TRATOS",
                    size=38,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    "Gerenciamento de alimentação de ruminantes",
                    size=16
                ),

                ft.Container(
                    height=20
                ),

                ft.Text(
                    "Entrar",
                    size=24,
                    weight=ft.FontWeight.BOLD
                ),

                campo_login,

                campo_senha,

                ft.Button(
                    content="Entrar",
                    icon=ft.Icons.LOGIN,
                    on_click=entrar
                ),

                mensagem

            ],

            horizontal_alignment=(
                ft.CrossAxisAlignment.CENTER
            ),

            spacing=15

        ),

        alignment=ft.Alignment.CENTER,

        expand=True
    )