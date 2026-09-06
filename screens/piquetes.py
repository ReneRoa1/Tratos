import flet as ft

from database.models import (
    cadastrar_piquete,
    listar_piquetes_fazenda,
    listar_piquetes_fazenda_todos,
    atualizar_piquete,
    desativar_piquete,
    reativar_piquete,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
)

from services.sessao import sessao
from services.identificadores import codigo_piquete


def tela_piquetes(page: ft.Page):

    # ======================================================
    # CONTEXTO DA FAZENDA
    # ======================================================

    fazenda_id = sessao.fazenda_atual_id
    fazenda_nome = sessao.fazenda_atual_nome

    # ======================================================
    # CAMPOS
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do piquete",
        hint_text="Ex.: Piquete 01",
        width=500
    )

    campo_identificacao = ft.TextField(
        label="Identificação",
        hint_text="Ex.: Retiro Norte, Área 01, P-01",
        width=500
    )

    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar piquetes inativos",
        value=False
    )

    lista_piquetes = ft.Column(
        spacing=12
    )

    # ======================================================
    # VALIDAÇÃO DE ACESSO
    # ======================================================

    def usuario_pode_acessar_fazenda():

        if fazenda_id is None:
            return False

        if sessao.perfil_sistema == "ADMIN":
            return True

        if sessao.perfil_sistema == "CONSULTOR":

            return consultor_tem_acesso_fazenda(
                sessao.usuario_id,
                fazenda_id
            )

        if sessao.perfil_sistema == "USUARIO":

            return usuario_tem_acesso_fazenda(
                sessao.usuario_id,
                fazenda_id
            )

        return False

    # ======================================================
    # CADASTRAR PIQUETE
    # ======================================================

    def salvar_piquete(e):

        if not usuario_pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui acesso a esta fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        nome = campo_nome.value.strip()

        if not nome:

            mensagem.value = (
                "Informe o nome do piquete."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        piquete_id = cadastrar_piquete(
            fazenda_id=fazenda_id,
            nome=nome,
            identificacao=(
                campo_identificacao.value.strip()
                or None
            )
        )

        campo_nome.value = ""
        campo_identificacao.value = ""

        mensagem.value = (
            f"Piquete {codigo_piquete(piquete_id)} "
            f"cadastrado com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_piquetes()

        page.update()

    # ======================================================
    # EDITAR PIQUETE
    # ======================================================

    def abrir_edicao(piquete):

        if not usuario_pode_acessar_fazenda():

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,
                    title=ft.Text(
                        "Acesso não autorizado"
                    ),
                    content=ft.Text(
                        "Você não possui acesso "
                        "a esta fazenda."
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

        editar_nome = ft.TextField(
            label="Nome do piquete",
            value=piquete["nome"],
            width=450
        )

        editar_identificacao = ft.TextField(
            label="Identificação",
            value=(
                piquete["identificacao"]
                or ""
            ),
            width=450
        )

        mensagem_edicao = ft.Text()

        def salvar_alteracoes(e):

            if not usuario_pode_acessar_fazenda():

                mensagem_edicao.value = (
                    "Acesso não autorizado."
                )

                mensagem_edicao.color = ft.Colors.RED

                page.update()
                return

            nome = editar_nome.value.strip()

            if not nome:

                mensagem_edicao.value = (
                    "Informe o nome do piquete."
                )

                mensagem_edicao.color = ft.Colors.RED

                page.update()
                return

            atualizar_piquete(
                piquete_id=piquete["id"],
                fazenda_id=fazenda_id,
                nome=nome,
                identificacao=(
                    editar_identificacao.value.strip()
                    or None
                )
            )

            page.pop_dialog()

            carregar_piquetes()

            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar "
                f"{codigo_piquete(piquete['id'])}"
            ),

            content=ft.Column(
                controls=[
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
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Salvar alterações",
                    icon=ft.Icons.SAVE,
                    on_click=salvar_alteracoes
                )
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

    # ======================================================
    # DESATIVAR PIQUETE
    # ======================================================

    def confirmar_desativacao(piquete):

        def confirmar(e):

            if not usuario_pode_acessar_fazenda():

                page.pop_dialog()

                mensagem.value = (
                    "Acesso não autorizado."
                )

                mensagem.color = ft.Colors.RED

                page.update()
                return

            desativar_piquete(
                piquete["id"]
            )

            page.pop_dialog()

            carregar_piquetes()

            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Desativar piquete?"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        f'{codigo_piquete(piquete["id"])} '
                        f'— {piquete["nome"]}'
                    ),

                    ft.Text(
                        "O piquete deixará de aparecer "
                        "nas listas de registros ativos."
                    ),

                    ft.Text(
                        "O histórico continuará "
                        "armazenado."
                    )
                ],

                tight=True,
                spacing=10
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Desativar",
                    icon=ft.Icons.BLOCK,
                    on_click=confirmar
                )
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR PIQUETE
    # ======================================================

    def confirmar_reativacao(piquete):

        def confirmar(e):

            if not usuario_pode_acessar_fazenda():

                page.pop_dialog()

                mensagem.value = (
                    "Acesso não autorizado."
                )

                mensagem.color = ft.Colors.RED

                page.update()
                return

            reativar_piquete(
                piquete["id"]
            )

            page.pop_dialog()

            carregar_piquetes()

            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar piquete?"
            ),

            content=ft.Text(
                f'{codigo_piquete(piquete["id"])} '
                f'— {piquete["nome"]}'
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Reativar",
                    icon=ft.Icons.REFRESH,
                    on_click=confirmar
                )
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAGEM
    # ======================================================

    def carregar_piquetes(e=None):

        lista_piquetes.controls.clear()

        if fazenda_id is None:

            lista_piquetes.controls.append(
                ft.Text(
                    "Selecione uma fazenda para "
                    "visualizar os piquetes."
                )
            )

            page.update()
            return

        if not usuario_pode_acessar_fazenda():

            lista_piquetes.controls.append(
                ft.Text(
                    "Você não possui acesso "
                    "a esta fazenda.",
                    color=ft.Colors.RED
                )
            )

            page.update()
            return

        if mostrar_inativos.value:

            piquetes = (
                listar_piquetes_fazenda_todos(
                    fazenda_id
                )
            )

        else:

            piquetes = (
                listar_piquetes_fazenda(
                    fazenda_id
                )
            )

        if not piquetes:

            lista_piquetes.controls.append(
                ft.Text(
                    "Nenhum piquete cadastrado "
                    "nesta fazenda."
                )
            )

            page.update()
            return

        for piquete in piquetes:

            codigo = codigo_piquete(
                piquete["id"]
            )

            identificacao = (
                piquete["identificacao"]
                or "Não informada"
            )

            ativo = bool(
                piquete["ativo"]
            )

            dados = [

                ft.Text(
                    codigo,
                    size=12,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    piquete["nome"],
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    f"Fazenda: "
                    f"{piquete['fazenda_nome']}"
                ),

                ft.Text(
                    f"Identificação: "
                    f"{identificacao}"
                )
            ]

            if ativo:

                dados.append(
                    ft.Text(
                        "● ATIVO",
                        color=ft.Colors.GREEN,
                        weight=ft.FontWeight.BOLD
                    )
                )

            else:

                dados.append(
                    ft.Text(
                        "● INATIVO",
                        color=ft.Colors.RED,
                        weight=ft.FontWeight.BOLD
                    )
                )

            botoes = []

            if ativo:

                botoes.append(
                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,

                        on_click=lambda e,
                        p=piquete:
                        abrir_edicao(p)
                    )
                )

                botoes.append(
                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,

                        on_click=lambda e,
                        p=piquete:
                        confirmar_desativacao(p)
                    )
                )

            else:

                botoes.append(
                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,

                        on_click=lambda e,
                        p=piquete:
                        confirmar_reativacao(p)
                    )
                )

            dados.append(
                ft.Row(
                    controls=botoes,
                    spacing=10
                )
            )

            lista_piquetes.controls.append(

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

    mostrar_inativos.on_change = (
        carregar_piquetes
    )

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    carregar_piquetes()

    # ======================================================
    # INTERFACE
    # ======================================================

    if fazenda_id is None:

        return ft.Column(
            controls=[

                ft.Text(
                    "Piquetes",
                    size=30,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    "Selecione uma fazenda no topo "
                    "do aplicativo para gerenciar "
                    "os piquetes."
                )

            ],

            spacing=15
        )

    return ft.Column(

        controls=[

            ft.Text(
                "Piquetes",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                f"Fazenda atual: {fazenda_nome}",
                size=18,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Cadastre e gerencie os locais "
                "físicos onde os lotes de animais "
                "serão mantidos."
            ),

            ft.Divider(),

            # ==============================================
            # NOVO PIQUETE
            # ==============================================

            ft.Text(
                "Novo piquete",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,

            campo_identificacao,

            ft.Button(
                content="Cadastrar piquete",
                icon=ft.Icons.ADD,
                on_click=salvar_piquete
            ),

            mensagem,

            ft.Divider(),

            # ==============================================
            # LISTAGEM
            # ==============================================

            ft.Row(
                controls=[

                    ft.Text(
                        "Piquetes cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_inativos

                ]
            ),

            lista_piquetes

        ],

        spacing=15,

        scroll=ft.ScrollMode.AUTO,

        expand=True
    )                                                                                    