import sqlite3
import flet as ft

from database.models import (
    cadastrar_usuario,

    listar_usuarios,
    listar_usuarios_todos,
    listar_usuarios_consultor,

    listar_organizacoes,
    listar_organizacoes_consultor,

    listar_fazendas,
    listar_fazendas_consultor,

    listar_organizacoes_usuario,
    listar_fazendas_usuario,

    vincular_usuario_organizacao,
    vincular_usuario_fazenda,

    desativar_vinculo_usuario_organizacao,
    desativar_vinculo_usuario_fazenda,

    atualizar_usuario,
    atualizar_senha_usuario,

    desativar_usuario,
    reativar_usuario,

    consultor_tem_acesso_usuario,
    consultor_tem_acesso_fazenda,
    listar_usuarios_consultor_fazenda,
)

from services.auth import (
    gerar_hash_senha
)

from services.sessao import sessao

from services.identificadores import (
    codigo_usuario
)


def tela_usuarios(page: ft.Page):
    def carregar_fazendas_cadastro():

        campo_fazenda_cadastro.options.clear()

        if sessao.perfil_sistema == "CONSULTOR":

            fazendas = listar_fazendas_consultor(
                sessao.usuario_id
            )

        elif sessao.perfil_sistema == "ADMIN":

            fazendas = listar_fazendas()

        else:

            fazendas = []

        for fazenda in fazendas:

            fazenda_id = (
                fazenda["fazenda_id"]
                if "fazenda_id" in fazenda.keys()
                else fazenda["id"]
            )

            fazenda_nome = (
                fazenda["fazenda_nome"]
                if "fazenda_nome" in fazenda.keys()
                else fazenda["nome"]
            )

            campo_fazenda_cadastro.options.append(
                ft.DropdownOption(
                    key=str(fazenda_id),
                    text=fazenda_nome
                )
            )
    # ======================================================
    # PERMISSÃO PARA GERENCIAR USUÁRIO
    # ======================================================

    def pode_gerenciar_usuario(usuario_id):

        if sessao.perfil_sistema == "ADMIN":

            usuarios = (
                listar_usuarios_todos()
                if mostrar_inativos.value
                else listar_usuarios()
            )

        elif sessao.perfil_sistema == "CONSULTOR":

            if sessao.fazenda_atual_id is None:

                usuarios = []

            else:

                usuarios = listar_usuarios_consultor_fazenda(
                    consultor_id=sessao.usuario_id,
                    fazenda_id=sessao.fazenda_atual_id,
                    incluir_inativos=mostrar_inativos.value
                )

        else:

            usuarios = []
    # ======================================================
    # CADASTRO
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome",
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
    campo_fazenda_cadastro = ft.Dropdown(
    label="Fazenda",
    width=500
)

    campo_perfil_fazenda_cadastro = ft.Dropdown(
        label="Função na fazenda",
        width=500,
        options=[
            ft.DropdownOption(
                key="PROPRIETARIO",
                text="Proprietário"
            ),

            ft.DropdownOption(
                key="GERENTE",
                text="Gerente"
            ),

            ft.DropdownOption(
                key="FUNCIONARIO",
                text="Funcionário / Peão"
            )
        ]
    )
    campo_perfil_sistema = ft.Dropdown(
    label="Tipo de usuário",
    width=500,
    value="USUARIO",
    options=[
        ft.DropdownOption(
            key="USUARIO",
            text="Usuário da fazenda"
        )
    ]
)
    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar usuários inativos",
        value=False
    )

    lista_usuarios = ft.Column(
        spacing=12
    )

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar_usuario(e):

        # ==============================================
        # QUEM PODE CADASTRAR USUÁRIO DE FAZENDA
        # ==============================================

        if sessao.perfil_sistema not in [
            "CONSULTOR",
            "ADMIN"
        ]:

            mensagem.value = (
                "Você não possui permissão para "
                "cadastrar usuários."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        # ==============================================
        # DADOS
        # ==============================================

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
                "A senha deve possuir pelo menos "
                "6 caracteres."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        if not campo_fazenda_cadastro.value:

            mensagem.value = (
                "Selecione a fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        if not campo_perfil_fazenda_cadastro.value:

            mensagem.value = (
                "Selecione a função do usuário "
                "na fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        fazenda_id = int(
            campo_fazenda_cadastro.value
        )

        # ==============================================
        # SEGURANÇA DO CONSULTOR
        # ==============================================

        if sessao.perfil_sistema == "CONSULTOR":

            if not consultor_tem_acesso_fazenda(
                consultor_id=sessao.usuario_id,
                fazenda_id=fazenda_id
            ):

                mensagem.value = (
                    "Você não possui acesso a esta fazenda."
                )

                mensagem.color = ft.Colors.RED

                page.update()

                return

        # ==============================================
        # CRIAR USUÁRIO
        # ==============================================

        try:

            usuario_id = cadastrar_usuario(
                nome=nome,
                login=login,
                senha_hash=gerar_hash_senha(senha),
                perfil_sistema="USUARIO"
            )

        except sqlite3.IntegrityError:

            mensagem.value = (
                "Já existe um usuário com esse login."
            )

            mensagem.color = ft.Colors.RED

            page.update()

            return

        # ==============================================
        # VINCULAR IMEDIATAMENTE À FAZENDA
        # ==============================================

        vincular_usuario_fazenda(
            usuario_id=usuario_id,
            fazenda_id=fazenda_id,
            perfil=campo_perfil_fazenda_cadastro.value
        )

        # ==============================================
        # LIMPAR
        # ==============================================

        campo_nome.value = ""
        campo_login.value = ""
        campo_senha.value = ""

        campo_fazenda_cadastro.value = None

        campo_perfil_fazenda_cadastro.value = None

        mensagem.value = (
            "Usuário cadastrado e vinculado "
            "à fazenda com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_usuarios()

        page.update()

    # ======================================================
    # EDITAR DADOS
    # ======================================================

    def abrir_edicao(usuario):
        if not pode_gerenciar_usuario(
            usuario["id"]
        ):

            page.show_dialog(
                ft.AlertDialog(
                    modal=True,

                    title=ft.Text(
                        "Acesso não autorizado"
                    ),

                    content=ft.Text(
                        "Você não possui permissão para "
                        "editar este usuário."
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
        nome = ft.TextField(
            label="Nome",
            value=usuario["nome"],
            width=450
        )

        login = ft.TextField(
            label="Login / E-mail",
            value=usuario["login"],
            width=450
        )

        perfil = ft.Dropdown(
            label="Tipo de usuário",
            width=450,
            value=usuario["perfil_sistema"],
            options=[
                ft.DropdownOption(
                    key="USUARIO",
                    text="Usuário do cliente"
                ),

                ft.DropdownOption(
                    key="CONSULTOR",
                    text="Consultor"
                )
            ]
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
                    usuario_id=usuario["id"],
                    nome=nome.value.strip(),
                    login=login.value.strip(),
                    perfil_sistema=perfil.value
                )

            except sqlite3.IntegrityError:

                erro.value = (
                    "Já existe outro usuário com esse login."
                )
                erro.color = ft.Colors.RED
                page.update()
                return

            page.pop_dialog()
            carregar_usuarios()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar {codigo_usuario(usuario['id'])}"
            ),

            content=ft.Column(
                controls=[
                    nome,
                    login,
                    perfil,
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
    # ALTERAR SENHA
    # ======================================================

    def abrir_alterar_senha(usuario):
        if not pode_gerenciar_usuario(
            usuario["id"]
        ):
            return
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
                erro.value = (
                    "As senhas não coincidem."
                )
                erro.color = ft.Colors.RED
                page.update()
                return

            atualizar_senha_usuario(
                usuario_id=usuario["id"],
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
                f"{codigo_usuario(usuario['id'])}"
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
    # ACESSOS
    # ======================================================

    def abrir_acessos(usuario):
        if not pode_gerenciar_usuario(
            usuario["id"]
        ):
            return
        lista_acessos = ft.Column(
            spacing=10
        )

        usuario_id = usuario["id"]

        # ----------------------------------------------
        # NOVO ACESSO ORGANIZAÇÃO
        # ----------------------------------------------

        nova_org = ft.Dropdown(
            label="Cliente / Organização",
            width=400
        )

        perfil_org = ft.Dropdown(
            label="Perfil no cliente",
            width=400,
            options=[
                ft.DropdownOption(
                    key="CONSULTOR",
                    text="Consultor"
                ),

                ft.DropdownOption(
                    key="PROPRIETARIO",
                    text="Proprietário"
                ),

                ft.DropdownOption(
                    key="GERENTE",
                    text="Gerente"
                )
            ]
        )

        if sessao.perfil_sistema == "ADMIN":

            organizacoes_disponiveis = (
                listar_organizacoes()
            )

        elif sessao.perfil_sistema == "CONSULTOR":

            organizacoes_disponiveis = (
                listar_organizacoes_consultor(
                    sessao.usuario_id
                )
            )

        else:

            organizacoes_disponiveis = []
        for org in organizacoes_disponiveis:

            nome = (
                org["nome_fantasia"]
                or org["nome"]
            )

            nova_org.options.append(
                ft.DropdownOption(
                    key=str(org["id"]),
                    text=nome
                )
            )

        # ----------------------------------------------
        # NOVO ACESSO FAZENDA
        # ----------------------------------------------

        nova_fazenda = ft.Dropdown(
            label="Fazenda",
            width=400
        )

        perfil_fazenda = ft.Dropdown(
            label="Perfil na fazenda",
            width=400,
            options=[
                ft.DropdownOption(
                    key="PROPRIETARIO",
                    text="Proprietário"
                ),

                ft.DropdownOption(
                    key="GERENTE",
                    text="Gerente"
                ),

                ft.DropdownOption(
                    key="FUNCIONARIO",
                    text="Funcionário / Peão"
                )
            ]
        )
        if sessao.perfil_sistema == "ADMIN":

            fazendas_disponiveis = (
                listar_fazendas()
            )

        elif sessao.perfil_sistema == "CONSULTOR":

            fazendas_disponiveis = (
                listar_fazendas_consultor(
                    sessao.usuario_id
                )
            )

        else:

            fazendas_disponiveis = []

        for fazenda in fazendas_disponiveis:

            fazenda_id = (
                fazenda["fazenda_id"]
                if "fazenda_id" in fazenda.keys()
                else fazenda["id"]
            )

            fazenda_nome = (
                fazenda["fazenda_nome"]
                if "fazenda_nome" in fazenda.keys()
                else fazenda["nome"]
            )

            cliente = (
                fazenda["organizacao_nome_fantasia"]
                or fazenda["organizacao_nome"]
                or "Sem cliente"
            )

            nova_fazenda.options.append(
                ft.DropdownOption(
                    key=str(fazenda_id),
                    text=(
                        f"{fazenda_nome} "
                        f"({cliente})"
                    )
                )
            )

        mensagem_acesso = ft.Text()

        # ----------------------------------------------
        # CARREGAR ACESSOS
        # ----------------------------------------------

        def carregar_acessos():

            lista_acessos.controls.clear()

            organizacoes = (
                listar_organizacoes_usuario(
                    usuario_id
                )
            )

            fazendas = listar_fazendas_usuario(
                usuario_id
            )

            if organizacoes:

                lista_acessos.controls.append(
                    ft.Text(
                        "Clientes / Organizações",
                        weight=ft.FontWeight.BOLD
                    )
                )

                for org in organizacoes:

                    nome = (
                        org["nome_fantasia"]
                        or org["nome"]
                    )

                    lista_acessos.controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f'{nome} '
                                    f'— {org["perfil"]}',
                                    expand=True
                                ),

                                ft.Button(
                                    content="Remover",
                                    icon=ft.Icons.LINK_OFF,
                                    on_click=lambda e,
                                    oid=org["organizacao_id"]:
                                    remover_org(oid)
                                )
                            ]
                        )
                    )

            if fazendas:

                lista_acessos.controls.append(
                    ft.Text(
                        "Fazendas",
                        weight=ft.FontWeight.BOLD
                    )
                )

                for fazenda in fazendas:

                    lista_acessos.controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f'{fazenda["fazenda_nome"]} '
                                    f'— {fazenda["perfil"]}',
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
                        )
                    )

        def remover_org(organizacao_id):

            desativar_vinculo_usuario_organizacao(
                usuario_id=usuario_id,
                organizacao_id=organizacao_id
            )

            carregar_acessos()
            page.update()

        def remover_fazenda(fazenda_id):

            desativar_vinculo_usuario_fazenda(
                usuario_id=usuario_id,
                fazenda_id=fazenda_id
            )

            carregar_acessos()
            page.update()

        # ----------------------------------------------
        # ADICIONAR ORGANIZAÇÃO
        # ----------------------------------------------

        def adicionar_org(e):

            if not nova_org.value:
                mensagem_acesso.value = (
                    "Selecione o cliente."
                )
                mensagem_acesso.color = ft.Colors.RED
                page.update()
                return

            if not perfil_org.value:
                mensagem_acesso.value = (
                    "Selecione o perfil."
                )
                mensagem_acesso.color = ft.Colors.RED
                page.update()
                return

            vincular_usuario_organizacao(
                usuario_id=usuario_id,
                organizacao_id=int(
                    nova_org.value
                ),
                perfil=perfil_org.value
            )

            mensagem_acesso.value = (
                "Acesso ao cliente atualizado."
            )
            mensagem_acesso.color = ft.Colors.GREEN

            carregar_acessos()
            page.update()

        # ----------------------------------------------
        # ADICIONAR FAZENDA
        # ----------------------------------------------

        def adicionar_fazenda(e):

            if not nova_fazenda.value:
                mensagem_acesso.value = (
                    "Selecione a fazenda."
                )
                mensagem_acesso.color = ft.Colors.RED
                page.update()
                return

            if not perfil_fazenda.value:
                mensagem_acesso.value = (
                    "Selecione o perfil."
                )
                mensagem_acesso.color = ft.Colors.RED
                page.update()
                return

            vincular_usuario_fazenda(
                usuario_id=usuario_id,
                fazenda_id=int(
                    nova_fazenda.value
                ),
                perfil=perfil_fazenda.value
            )

            mensagem_acesso.value = (
                "Acesso à fazenda atualizado."
            )
            mensagem_acesso.color = ft.Colors.GREEN

            carregar_acessos()
            page.update()

        carregar_acessos()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Acessos — "
                f"{codigo_usuario(usuario['id'])}"
            ),

            content=ft.Container(
                width=600,
                content=ft.Column(
                    controls=[

                        ft.Text(
                            usuario["nome"],
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Divider(),

                        lista_acessos,

                        ft.Divider(),

                        ft.Text(
                            "Adicionar / alterar acesso ao cliente",
                            weight=ft.FontWeight.BOLD
                        ),

                        nova_org,
                        perfil_org,

                        ft.Button(
                            content="Salvar acesso ao cliente",
                            icon=ft.Icons.LINK,
                            on_click=adicionar_org
                        ),

                        ft.Divider(),

                        ft.Text(
                            "Adicionar / alterar acesso à fazenda",
                            weight=ft.FontWeight.BOLD
                        ),

                        nova_fazenda,
                        perfil_fazenda,

                        ft.Button(
                            content="Salvar acesso à fazenda",
                            icon=ft.Icons.LINK,
                            on_click=adicionar_fazenda
                        ),

                        mensagem_acesso

                    ],
                    tight=True,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                )
            ),

            actions=[
                ft.Button(
                    content="Fechar",
                    on_click=lambda e: (
                        page.pop_dialog()
                    )
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(usuario):
        if not pode_gerenciar_usuario(
            usuario["id"]
        ):
            return
        if usuario["id"] == sessao.usuario_id:

            dialogo = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Operação não permitida"
                ),
                content=ft.Text(
                    "Você não pode desativar o próprio "
                    "usuário enquanto estiver conectado."
                ),
                actions=[
                    ft.Button(
                        content="OK",
                        on_click=lambda e:
                        page.pop_dialog()
                    )
                ]
            )

            page.show_dialog(dialogo)
            return

        def confirmar(e):

            desativar_usuario(
                usuario_id=usuario["id"],
                desativado_por=sessao.usuario_id
            )

            page.pop_dialog()
            carregar_usuarios()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Desativar usuário?"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        f'{codigo_usuario(usuario["id"])} '
                        f'— {usuario["nome"]}'
                    ),

                    ft.Text(
                        "O usuário deixará de conseguir "
                        "acessar o Tratos."
                    ),

                    ft.Text(
                        "O histórico permanecerá preservado."
                    )
                ],
                tight=True,
                spacing=8
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
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR
    # ======================================================

    def confirmar_reativacao(usuario):

        def confirmar(e):

            reativar_usuario(
                usuario["id"]
            )

            page.pop_dialog()
            carregar_usuarios()
            page.update()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar usuário?"
            ),

            content=ft.Text(
                f'{codigo_usuario(usuario["id"])} '
                f'— {usuario["nome"]}'
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
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAGEM
    # ======================================================

    def carregar_usuarios(e=None):

        lista_usuarios.controls.clear()

        # ==============================================
        # ADMIN → TODOS
        # CONSULTOR → SOMENTE SUA CARTEIRA
        # ==============================================

        if sessao.perfil_sistema == "ADMIN":

            usuarios = (
                listar_usuarios_todos()
                if mostrar_inativos.value
                else listar_usuarios()
            )

        elif sessao.perfil_sistema == "CONSULTOR":

            usuarios = listar_usuarios_consultor(
                consultor_id=sessao.usuario_id,
                incluir_inativos=mostrar_inativos.value
            )

        else:

            usuarios = []

        if not usuarios:

            lista_usuarios.controls.append(
                ft.Text(
                    "Nenhum usuário encontrado."
                )
            )

            page.update()
            return

        for usuario in usuarios:

            ativo = bool(
                usuario["ativo"]
            )

            organizacoes = (
                listar_organizacoes_usuario(
                    usuario["id"]
                )
            )

            fazendas = listar_fazendas_usuario(
                usuario["id"]
            )

            controles = [

                ft.Text(
                    codigo_usuario(usuario["id"]),
                    size=12,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    usuario["nome"],
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    usuario["login"]
                ),

                ft.Text(
                    f'Tipo: '
                    f'{usuario["perfil_sistema"]}'
                )

            ]

            if organizacoes:

                controles.append(
                    ft.Text(
                        "Clientes:",
                        weight=ft.FontWeight.BOLD
                    )
                )

                for org in organizacoes:

                    nome = (
                        org["nome_fantasia"]
                        or org["nome"]
                    )

                    controles.append(
                        ft.Text(
                            f'• {nome} '
                            f'— {org["perfil"]}'
                        )
                    )

            if fazendas:

                controles.append(
                    ft.Text(
                        "Fazendas:",
                        weight=ft.FontWeight.BOLD
                    )
                )

                for fazenda in fazendas:

                    controles.append(
                        ft.Text(
                            f'• '
                            f'{fazenda["fazenda_nome"]} '
                            f'— {fazenda["perfil"]}'
                        )
                    )

            controles.append(
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
            )

            botoes = []

            if ativo:

                botoes.extend([

                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        u=usuario:
                        abrir_edicao(u)
                    ),

                    ft.Button(
                        content="Senha",
                        icon=ft.Icons.LOCK_RESET,
                        on_click=lambda e,
                        u=usuario:
                        abrir_alterar_senha(u)
                    ),

                    ft.Button(
                        content="Acessos",
                        icon=ft.Icons.MANAGE_ACCOUNTS,
                        on_click=lambda e,
                        u=usuario:
                        abrir_acessos(u)
                    ),

                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e,
                        u=usuario:
                        confirmar_desativacao(u)
                    )

                ])

            else:

                botoes.append(
                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        u=usuario:
                        confirmar_reativacao(u)
                    )
                )

            controles.append(
                ft.Row(
                    controls=botoes,
                    spacing=8,
                    wrap=True
                )
            )

            lista_usuarios.controls.append(

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
        carregar_usuarios
    )
    carregar_fazendas_cadastro()
    carregar_usuarios()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[

            ft.Text(
                "Usuários",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Cadastre usuários e gerencie seus "
                "acessos ao Tratos."
            ),

            ft.Divider(),

            ft.Text(
                "Novo usuário",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,
            campo_login,
            campo_senha,
            campo_fazenda_cadastro,

            campo_perfil_fazenda_cadastro,

            ft.Button(
                content="Cadastrar usuário",
                icon=ft.Icons.PERSON_ADD,
                on_click=salvar_usuario
            ),

            mensagem,

            ft.Divider(),

            ft.Row(
                controls=[

                    ft.Text(
                        "Usuários cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(expand=True),

                    mostrar_inativos

                ]
            ),

            lista_usuarios

        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )