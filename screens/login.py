import flet as ft

from database.models import (
    buscar_usuario_ativo_por_login,
    listar_organizacoes_usuario,
    listar_fazendas_usuario,
    listar_fazendas_consultor,
    listar_fazendas
)

from services.auth import verificar_senha
from services.sessao import sessao


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

        if sessao.perfil_sistema == "ADMIN":

            todas_fazendas = listar_fazendas()

            sessao.fazendas = []

            for fazenda in todas_fazendas:

                sessao.fazendas.append({
                    "fazenda_id": fazenda["id"],
                    "fazenda_nome": fazenda["nome"],
                    "perfil": "LEITURA",

                    "organizacao_nome":
                        fazenda["organizacao_nome"],

                    "organizacao_nome_fantasia":
                        fazenda["organizacao_nome_fantasia"]
                })


        elif sessao.perfil_sistema == "CONSULTOR":

            fazendas_consultor = (
                listar_fazendas_consultor(
                    usuario["id"]
                )
            )

            sessao.fazendas = []

            for fazenda in fazendas_consultor:

                sessao.fazendas.append({
                    "fazenda_id":
                        fazenda["fazenda_id"],

                    "fazenda_nome":
                        fazenda["fazenda_nome"],

                    "perfil":
                        "CONSULTOR",

                    "organizacao_nome":
                        fazenda["organizacao_nome"],

                    "organizacao_nome_fantasia":
                        fazenda["organizacao_nome_fantasia"]
                })


        else:

            sessao.fazendas = list(
                listar_fazendas_usuario(
                    usuario["id"]
                )
            )


        # ======================================
        # SE HOUVER APENAS UMA FAZENDA
        # ======================================

        if len(sessao.fazendas) == 1:

            fazenda = sessao.fazendas[0]

            sessao.selecionar_fazenda(
                fazenda_id=fazenda["fazenda_id"],
                fazenda_nome=fazenda["fazenda_nome"],
                perfil=fazenda["perfil"]
            )


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