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
    # CAMPOS
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do piquete",
        hint_text="Ex.: Piquete 01",
        width=500
    )

    campo_identificacao = ft.TextField(
        label="Identificação",
        hint_text="Ex.: Retiro Norte, P-01, Área 03",
        width=500
    )

    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar inativos",
        value=False
    )

    lista_piquetes = ft.Column(
        spacing=12
    )

    # ======================================================
    # FAZENDA ATUAL
    # ======================================================

    def fazenda_atual_id():
        return sessao.fazenda_atual_id

    def fazenda_atual_nome():
        return (
            sessao.fazenda_atual_nome
            or "Nenhuma fazenda selecionada"
        )

    # ======================================================
    # VALIDAÇÃO DE ACESSO
    # ======================================================

    def pode_acessar_fazenda():

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:
            return False

        # ADMIN não opera rotina de fazenda
        if sessao.perfil_sistema == "ADMIN":
            return False

        if sessao.perfil_sistema == "CONSULTOR":

            return consultor_tem_acesso_fazenda(
                consultor_id=sessao.usuario_id,
                fazenda_id=fazenda_id
            )

        if sessao.perfil_sistema == "USUARIO":

            return usuario_tem_acesso_fazenda(
                usuario_id=sessao.usuario_id,
                fazenda_id=fazenda_id
            )

        return False

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar_piquete(e):

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            mensagem.value = (
                "Selecione uma fazenda antes "
                "de cadastrar um piquete."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        if not pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui permissão "
                "para cadastrar piquetes nesta fazenda."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        nome = (
            campo_nome.value or ""
        ).strip()

        identificacao = (
            campo_identificacao.value or ""
        ).strip()

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
                identificacao
                if identificacao
                else None
            )
        )

        campo_nome.value = ""
        campo_identificacao.value = ""

        mensagem.value = (
            f"{codigo_piquete(piquete_id)} "
            "cadastrado com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_piquetes()

    # ======================================================
    # EDITAR
    # ======================================================

    def abrir_edicao(piquete):

        if not pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui permissão "
                "para editar este piquete."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        # Segurança adicional:
        # o piquete precisa pertencer à fazenda atual
        if (
            piquete["fazenda_id"]
            != fazenda_atual_id()
        ):

            mensagem.value = (
                "Este piquete não pertence "
                "à fazenda selecionada."
            )
            mensagem.color = ft.Colors.RED

            page.update()
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

            nome = (
                editar_nome.value or ""
            ).strip()

            identificacao = (
                editar_identificacao.value
                or ""
            ).strip()

            if not nome:

                mensagem_edicao.value = (
                    "Informe o nome do piquete."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if not pode_acessar_fazenda():

                mensagem_edicao.value = (
                    "Acesso não autorizado."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            atualizar_piquete(
                piquete_id=piquete["id"],
                fazenda_id=fazenda_atual_id(),
                nome=nome,
                identificacao=(
                    identificacao
                    if identificacao
                    else None
                )
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_piquete(piquete['id'])} "
                "atualizado com sucesso."
            )
            mensagem.color = ft.Colors.GREEN

            carregar_piquetes()

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
                    content="Salvar",
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
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(piquete):

        if (
            piquete["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        def executar(e):

            if not pode_acessar_fazenda():

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

            mensagem.value = (
                f"{codigo_piquete(piquete['id'])} "
                "desativado."
            )

            mensagem.color = ft.Colors.ORANGE

            carregar_piquetes()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Desativar piquete"
            ),
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{codigo_piquete(piquete['id'])} "
                        f"— {piquete['nome']}"
                    ),
                    ft.Text(
                        "O piquete será desativado, "
                        "mas seu histórico será preservado."
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
                    on_click=executar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR
    # ======================================================

    def confirmar_reativacao(piquete):

        if (
            piquete["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        def executar(e):

            if not pode_acessar_fazenda():

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

            mensagem.value = (
                f"{codigo_piquete(piquete['id'])} "
                "reativado."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_piquetes()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Reativar piquete"
            ),
            content=ft.Text(
                f"{codigo_piquete(piquete['id'])} "
                f"— {piquete['nome']}"
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
                    on_click=executar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAGEM
    # ======================================================

    def carregar_piquetes(e=None):

        lista_piquetes.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            lista_piquetes.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Selecione uma fazenda no topo "
                        "para visualizar os piquetes."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        if not pode_acessar_fazenda():

            lista_piquetes.controls.append(
                ft.Text(
                    "Você não possui acesso operacional "
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
                ft.Container(
                    content=ft.Text(
                        "Nenhum piquete cadastrado "
                        "nesta fazenda."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        for piquete in piquetes:

            ativo = bool(
                piquete["ativo"]
            )

            identificacao = (
                piquete["identificacao"]
                or "Não informada"
            )

            botoes = []

            if ativo:

                botoes.extend([
                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        p=piquete:
                        abrir_edicao(p)
                    ),
                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e,
                        p=piquete:
                        confirmar_desativacao(p)
                    )
                ])

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

            lista_piquetes.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        codigo_piquete(
                                            piquete["id"]
                                        ),
                                        size=13,
                                        weight=(
                                            ft.FontWeight.BOLD
                                        )
                                    ),
                                    ft.Text(
                                        (
                                            "ATIVO"
                                            if ativo
                                            else "INATIVO"
                                        ),
                                        color=(
                                            ft.Colors.GREEN
                                            if ativo
                                            else ft.Colors.RED
                                        ),
                                        weight=(
                                            ft.FontWeight.BOLD
                                        )
                                    )
                                ],
                                alignment=(
                                    ft.MainAxisAlignment
                                    .SPACE_BETWEEN
                                )
                            ),

                            ft.Text(
                                piquete["nome"],
                                size=20,
                                weight=(
                                    ft.FontWeight.BOLD
                                )
                            ),

                            ft.Text(
                                f"Identificação: "
                                f"{identificacao}"
                            ),

                            ft.Text(
                                f"Fazenda: "
                                f"{piquete['fazenda_nome']}"
                            ),

                            ft.Row(
                                controls=botoes,
                                spacing=10
                            )
                        ],
                        spacing=7
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
    # INTERFACE
    # ======================================================

    carregar_piquetes()

    return ft.Column(
        controls=[
            ft.Text(
                "Piquetes",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                f"Fazenda atual: "
                f"{fazenda_atual_nome()}",
                size=18,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Cadastre os locais físicos onde "
                "os lotes de animais permanecerão."
            ),

            ft.Divider(),

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