import sqlite3
import flet as ft

from database.models import (
    cadastrar_usuario,
    listar_usuarios_todos,
    atualizar_usuario,
    atualizar_senha_usuario,
    desativar_usuario,
    reativar_usuario
)

from services.auth import gerar_hash_senha
from services.sessao import sessao
from services.identificadores import codigo_usuario


def tela_consultores(page: ft.Page):

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
                    "gerenciar consultores."
                )
            ]
        )

    # ======================================================
    # CADASTRO
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do consultor",
        width=500
    )

    campo_login = ft.TextField(
        label="Login / E-mail",
        width=500
    )

    campo_senha = ft.TextField(
        label="Senha inicial",
        password=True,
        can_reveal_password=True,
        width=500
    )

    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar consultores inativos",
        value=False
    )

    lista_consultores = ft.Column(
        spacing=12
    )

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar_consultor(e):

        nome = campo_nome.value.strip()
        login = campo_login.value.strip()
        senha = campo_senha.value

        if not nome:
            mensagem.value = "Informe o nome."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        if not login:
            mensagem.value = "Informe o login."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        if not senha or len(senha) < 6:
            mensagem.value = (
                "A senha deve possuir pelo menos 6 caracteres."
            )
            mensagem.color = ft.Colors.RED
            page.update()
            return

        try:

            cadastrar_usuario(
                nome=nome,
                login=login,
                senha_hash=gerar_hash_senha(senha),
                perfil_sistema="CONSULTOR"
            )

        except sqlite3.IntegrityError:

            mensagem.value = (
                "Já existe um usuário com esse login."
            )
            mensagem.color = ft.Colors.RED
            page.update()
            return

        campo_nome.value = ""
        campo_login.value = ""
        campo_senha.value = ""

        mensagem.value = (
            "Consultor cadastrado com sucesso."
        )
        mensagem.color = ft.Colors.GREEN

        carregar_consultores()
        page.update()

    # ======================================================
    # EDITAR
    # ======================================================

    def abrir_edicao(consultor):

        nome = ft.TextField(
            label="Nome",
            value=consultor["nome"],
            width=450
        )

        login = ft.TextField(
            label="Login / E-mail",
            value=consultor["login"],
            width=450
        )

        erro = ft.Text()

        def salvar(e):

            if not nome.value.strip():
                erro.value = "Informe o nome."
                erro.color = ft.Colors.RED
                page.update()
                return

            if not login.value.strip():
                erro.value = "Informe o login."
                erro.color = ft.Colors.RED
                page.update()
                return

            try:

                atualizar_usuario(
                    usuario_id=consultor["id"],
                    nome=nome.value.strip(),
                    login=login.value.strip(),
                    perfil_sistema="CONSULTOR"
                )

            except sqlite3.IntegrityError:

                erro.value = (
                    "Já existe outro usuário com esse login."
                )
                erro.color = ft.Colors.RED
                page.update()
                return

            page.pop_dialog()
            carregar_consultores()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Editar {codigo_usuario(consultor['id'])}"
            ),
            content=ft.Column(
                controls=[
                    nome,
                    login,
                    erro
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
                    content="Salvar alterações",
                    icon=ft.Icons.SAVE,
                    on_click=salvar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # SENHA
    # ======================================================

    def abrir_senha(consultor):

        senha = ft.TextField(
            label="Nova senha",
            password=True,
            can_reveal_password=True,
            width=450
        )

        confirmar = ft.TextField(
            label="Confirmar nova senha",
            password=True,
            can_reveal_password=True,
            width=450
        )

        erro = ft.Text()

        def salvar(e):

            if not senha.value or len(senha.value) < 6:
                erro.value = (
                    "A senha deve possuir pelo menos 6 caracteres."
                )
                erro.color = ft.Colors.RED
                page.update()
                return

            if senha.value != confirmar.value:
                erro.value = "As senhas não coincidem."
                erro.color = ft.Colors.RED
                page.update()
                return

            atualizar_senha_usuario(
                usuario_id=consultor["id"],
                senha_hash=gerar_hash_senha(
                    senha.value
                )
            )

            page.pop_dialog()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Alterar senha — "
                f"{codigo_usuario(consultor['id'])}"
            ),
            content=ft.Column(
                controls=[
                    senha,
                    confirmar,
                    erro
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
                    content="Alterar senha",
                    icon=ft.Icons.LOCK_RESET,
                    on_click=salvar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(consultor):

        def confirmar(e):

            desativar_usuario(
                usuario_id=consultor["id"],
                desativado_por=sessao.usuario_id
            )

            page.pop_dialog()
            carregar_consultores()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Desativar consultor?"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        f'{codigo_usuario(consultor["id"])} '
                        f'— {consultor["nome"]}'
                    ),
                    ft.Text(
                        "O consultor deixará de conseguir "
                        "acessar o sistema."
                    ),
                    ft.Text(
                        "A carteira e o histórico não serão apagados."
                    )
                ],
                tight=True,
                spacing=8
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
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR
    # ======================================================

    def confirmar_reativacao(consultor):

        def confirmar(e):

            reativar_usuario(
                consultor["id"]
            )

            page.pop_dialog()
            carregar_consultores()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Reativar consultor?"
            ),
            content=ft.Text(
                f'{codigo_usuario(consultor["id"])} '
                f'— {consultor["nome"]}'
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
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAGEM
    # ======================================================

    def carregar_consultores(e=None):

        lista_consultores.controls.clear()

        usuarios = listar_usuarios_todos()

        consultores = [
            usuario
            for usuario in usuarios
            if usuario["perfil_sistema"] == "CONSULTOR"
        ]

        if not mostrar_inativos.value:

            consultores = [
                usuario
                for usuario in consultores
                if usuario["ativo"]
            ]

        if not consultores:

            lista_consultores.controls.append(
                ft.Text(
                    "Nenhum consultor cadastrado."
                )
            )
            page.update()
            return

        for consultor in consultores:

            ativo = bool(
                consultor["ativo"]
            )

            controles = [

                ft.Text(
                    codigo_usuario(
                        consultor["id"]
                    ),
                    size=12,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    consultor["nome"],
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    consultor["login"]
                ),

                ft.Text(
                    "● ATIVO"
                    if ativo
                    else "● INATIVO",
                    color=(
                        ft.Colors.GREEN
                        if ativo
                        else ft.Colors.RED
                    ),
                    weight=ft.FontWeight.BOLD
                )
            ]

            botoes = []

            if ativo:

                botoes.extend([

                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        c=consultor:
                        abrir_edicao(c)
                    ),

                    ft.Button(
                        content="Senha",
                        icon=ft.Icons.LOCK_RESET,
                        on_click=lambda e,
                        c=consultor:
                        abrir_senha(c)
                    ),

                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e,
                        c=consultor:
                        confirmar_desativacao(c)
                    )
                ])

            else:

                botoes.append(
                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        c=consultor:
                        confirmar_reativacao(c)
                    )
                )

            controles.append(
                ft.Row(
                    controls=botoes,
                    spacing=8,
                    wrap=True
                )
            )

            lista_consultores.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=controles,
                        spacing=5
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

    mostrar_inativos.on_change = (
        carregar_consultores
    )

    carregar_consultores()

    return ft.Column(
        controls=[

            ft.Text(
                "Consultores",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Gerencie a equipe técnica da consultoria."
            ),

            ft.Divider(),

            ft.Text(
                "Novo consultor",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,
            campo_login,
            campo_senha,

            ft.Button(
                content="Cadastrar consultor",
                icon=ft.Icons.PERSON_ADD,
                on_click=salvar_consultor
            ),

            mensagem,

            ft.Divider(),

            ft.Row(
                controls=[

                    ft.Text(
                        "Consultores cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_inativos
                ]
            ),

            lista_consultores
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )