import flet as ft

from database.models import (
    cadastrar_organizacao,
    listar_organizacoes,
    listar_organizacoes_todas,
    atualizar_organizacao,
    desativar_organizacao,
    reativar_organizacao,
    vincular_usuario_organizacao,
    listar_organizacoes_consultor,
    listar_organizacoes_consultor_todas,
    consultor_tem_acesso_organizacao
)

from services.sessao import sessao
from services.identificadores import codigo_organizacao


def tela_organizacoes(page: ft.Page):

    campo_nome = ft.TextField(
        label="Nome do cliente / organização",
        width=500
    )

    campo_nome_fantasia = ft.TextField(
        label="Nome fantasia",
        width=500
    )

    campo_documento = ft.TextField(
        label="CPF / CNPJ",
        width=500
    )

    campo_telefone = ft.TextField(
        label="Telefone",
        width=500
    )

    campo_email = ft.TextField(
        label="E-mail",
        width=500
    )

    campo_observacoes = ft.TextField(
        label="Observações",
        multiline=True,
        min_lines=2,
        max_lines=4,
        width=500
    )

    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar clientes inativos",
        value=False
    )

    lista = ft.Column(
        spacing=12
    )

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar(e):

        nome = campo_nome.value.strip()

        if not nome:
            mensagem.value = "Informe o nome do cliente."
            mensagem.color = ft.Colors.RED
            page.update()
            return

        organizacao_id = cadastrar_organizacao(
            nome=nome,
            nome_fantasia=campo_nome_fantasia.value.strip() or None,
            documento=campo_documento.value.strip() or None,
            telefone=campo_telefone.value.strip() or None,
            email=campo_email.value.strip() or None,
            observacoes=campo_observacoes.value.strip() or None
        )

        vincular_usuario_organizacao(
            usuario_id=sessao.usuario_id,
            organizacao_id=organizacao_id,
            perfil="CONSULTOR"
        )

        campo_nome.value = ""
        campo_nome_fantasia.value = ""
        campo_documento.value = ""
        campo_telefone.value = ""
        campo_email.value = ""
        campo_observacoes.value = ""

        mensagem.value = "Cliente cadastrado com sucesso."
        mensagem.color = ft.Colors.GREEN

        carregar()
        page.update()

    # ======================================================
    # EDITAR
    # ======================================================

    def abrir_edicao(org):
        if not consultor_tem_acesso_organizacao(
            sessao.usuario_id,
            org["id"]
        ):
            return
        nome = ft.TextField(
            label="Nome",
            value=org["nome"],
            width=450
        )

        fantasia = ft.TextField(
            label="Nome fantasia",
            value=org["nome_fantasia"] or "",
            width=450
        )

        documento = ft.TextField(
            label="CPF / CNPJ",
            value=org["documento"] or "",
            width=450
        )

        telefone = ft.TextField(
            label="Telefone",
            value=org["telefone"] or "",
            width=450
        )

        email = ft.TextField(
            label="E-mail",
            value=org["email"] or "",
            width=450
        )

        observacoes = ft.TextField(
            label="Observações",
            value=org["observacoes"] or "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=450
        )

        erro = ft.Text()

        def salvar_edicao(e):

            if not nome.value.strip():
                erro.value = "Informe o nome."
                erro.color = ft.Colors.RED
                page.update()
                return

            atualizar_organizacao(
                organizacao_id=org["id"],
                nome=nome.value.strip(),
                nome_fantasia=fantasia.value.strip() or None,
                documento=documento.value.strip() or None,
                telefone=telefone.value.strip() or None,
                email=email.value.strip() or None,
                observacoes=observacoes.value.strip() or None
            )

            page.pop_dialog()
            carregar()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar {codigo_organizacao(org['id'])}"
            ),

            content=ft.Column(
                controls=[
                    nome,
                    fantasia,
                    documento,
                    telefone,
                    email,
                    observacoes,
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
                    on_click=salvar_edicao
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(org):

        def confirmar(e):

            desativar_organizacao(
                organizacao_id=org["id"],
                desativado_por=sessao.usuario_id
            )

            page.pop_dialog()
            carregar()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Desativar cliente?"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        f'{codigo_organizacao(org["id"])} '
                        f'— {org["nome"]}'
                    ),

                    ft.Text(
                        "O cliente será marcado como inativo."
                    ),

                    ft.Text(
                        "O histórico permanecerá armazenado."
                    )
                ],
                tight=True
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

    def confirmar_reativacao(org):

        def confirmar(e):

            reativar_organizacao(
                org["id"]
            )

            page.pop_dialog()
            carregar()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar cliente?"
            ),

            content=ft.Text(
                f'{codigo_organizacao(org["id"])} '
                f'— {org["nome"]}'
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

    def carregar(e=None):

        lista.controls.clear()

        if mostrar_inativos.value:

            organizacoes = listar_organizacoes_consultor_todas(
                sessao.usuario_id
            )

        else:

            organizacoes = listar_organizacoes_consultor(
                sessao.usuario_id
            )

        for org in organizacoes:

            ativa = bool(org["ativo"])

            dados = [
                ft.Text(
                    codigo_organizacao(org["id"]),
                    size=12,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    org["nome"],
                    size=20,
                    weight=ft.FontWeight.BOLD
                )
            ]

            if org["nome_fantasia"]:
                dados.append(
                    ft.Text(
                        f'Nome fantasia: {org["nome_fantasia"]}'
                    )
                )

            if org["documento"]:
                dados.append(
                    ft.Text(
                        f'Documento: {org["documento"]}'
                    )
                )

            if org["email"]:
                dados.append(
                    ft.Text(
                        f'E-mail: {org["email"]}'
                    )
                )

            if org["telefone"]:
                dados.append(
                    ft.Text(
                        f'Telefone: {org["telefone"]}'
                    )
                )

            dados.append(
                ft.Text(
                    "● ATIVO" if ativa else "● INATIVO",
                    color=(
                        ft.Colors.GREEN
                        if ativa
                        else ft.Colors.RED
                    ),
                    weight=ft.FontWeight.BOLD
                )
            )

            botoes = []

            if ativa:

                botoes.append(
                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e, o=org:
                        abrir_edicao(o)
                    )
                )

                botoes.append(
                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e, o=org:
                        confirmar_desativacao(o)
                    )
                )

            else:

                botoes.append(
                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e, o=org:
                        confirmar_reativacao(o)
                    )
                )

            dados.append(
                ft.Row(
                    controls=botoes,
                    spacing=10
                )
            )

            lista.controls.append(
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

    mostrar_inativos.on_change = carregar

    carregar()

    return ft.Column(
        controls=[

            ft.Text(
                "Clientes / Organizações",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Cadastre e gerencie os clientes atendidos pela consultoria."
            ),

            ft.Divider(),

            ft.Text(
                "Novo cliente",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,
            campo_nome_fantasia,
            campo_documento,
            campo_telefone,
            campo_email,
            campo_observacoes,

            ft.Button(
                content="Cadastrar cliente",
                icon=ft.Icons.ADD,
                on_click=salvar
            ),

            mensagem,

            ft.Divider(),

            ft.Row(
                controls=[
                    ft.Text(
                        "Clientes cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(expand=True),

                    mostrar_inativos
                ]
            ),

            lista
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )