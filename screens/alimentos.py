import flet as ft
from datetime import datetime
from database.models import (
    cadastrar_alimento,
    listar_alimentos_fazenda,
    listar_alimentos_fazenda_todos,
    atualizar_alimento,
    desativar_alimento,
    reativar_alimento,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
        registrar_ms_alimento,
    listar_historico_ms_alimento,
    buscar_ms_atual_alimento,
)

from services.sessao import sessao
from services.identificadores import codigo_alimento


def tela_alimentos(page: ft.Page):

    # ======================================================
    # CONTEXTO
    # ======================================================

    def fazenda_atual_id():
        return sessao.fazenda_atual_id

    def fazenda_atual_nome():
        return (
            sessao.fazenda_atual_nome
            or "Nenhuma fazenda selecionada"
        )

    # ======================================================
    # PERMISSÕES
    # ======================================================

    def pode_acessar_fazenda():

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:
            return False

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
    # DATAS
    # ======================================================

    def aplicar_mascara_data(e):

        valor = e.control.value or ""

        numeros = "".join(
            caractere
            for caractere in valor
            if caractere.isdigit()
        )

        numeros = numeros[:8]

        if len(numeros) <= 2:

            formatado = numeros

        elif len(numeros) <= 4:

            formatado = (
                numeros[:2]
                + "/"
                + numeros[2:]
            )

        else:

            formatado = (
                numeros[:2]
                + "/"
                + numeros[2:4]
                + "/"
                + numeros[4:]
            )

        e.control.value = formatado
        page.update()


    def data_interface_para_banco(valor):

        if valor is None:
            return None

        valor = str(valor).strip()

        if not valor:
            return None

        try:

            data = datetime.strptime(
                valor,
                "%d/%m/%Y"
            )

            return data.strftime(
                "%Y-%m-%d"
            )

        except ValueError:
            return None


    def data_banco_para_interface(valor):

        if not valor:
            return ""

        try:

            data = datetime.strptime(
                valor,
                "%Y-%m-%d"
            )

            return data.strftime(
                "%d/%m/%Y"
            )

        except ValueError:
            return valor


    def converter_decimal(valor):

        if valor is None:
            return None

        valor = str(valor).strip()

        if not valor:
            return None

        try:

            return float(
                valor.replace(",", ".")
            )

        except ValueError:
            return None
    # ======================================================
    # CAMPOS
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do alimento",
        hint_text="Ex.: Milho moído",
        width=500
    )

    campo_categoria = ft.Dropdown(
        label="Categoria",
        width=500,
        options=[
            ft.DropdownOption(
                key="VOLUMOSO",
                text="Volumoso"
            ),
            ft.DropdownOption(
                key="CONCENTRADO_ENERGETICO",
                text="Concentrado energético"
            ),
            ft.DropdownOption(
                key="CONCENTRADO_PROTEICO",
                text="Concentrado proteico"
            ),
            ft.DropdownOption(
                key="MINERAL",
                text="Mineral"
            ),
            ft.DropdownOption(
                key="NUCLEO",
                text="Núcleo"
            ),
            ft.DropdownOption(
                key="ADITIVO",
                text="Aditivo"
            ),
            ft.DropdownOption(
                key="COPRODUTO",
                text="Coproduto"
            ),
            ft.DropdownOption(
                key="OUTRO",
                text="Outro"
            ),
        ]
    )

    campo_unidade = ft.Dropdown(
        label="Unidade",
        width=500,
        value="kg",
        options=[
            ft.DropdownOption(
                key="kg",
                text="kg"
            ),
            ft.DropdownOption(
                key="ton",
                text="ton"
            ),
            ft.DropdownOption(
                key="L",
                text="L"
            ),
            ft.DropdownOption(
                key="unidade",
                text="unidade"
            ),
        ]
    )

    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar alimentos inativos",
        value=False
    )

    lista_alimentos = ft.Column(
        spacing=12
    )

    # ======================================================
    # LIMPAR CAMPOS
    # ======================================================

    def limpar_campos():

        campo_nome.value = ""
        campo_categoria.value = None
        campo_unidade.value = "kg"

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar_alimento(e):

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            mensagem.value = (
                "Selecione uma fazenda antes "
                "de cadastrar o alimento."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if not pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui acesso operacional "
                "a esta fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        nome = (
            campo_nome.value
            or ""
        ).strip()

        if not nome:

            mensagem.value = (
                "Informe o nome do alimento."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if campo_categoria.value is None:

            mensagem.value = (
                "Selecione a categoria do alimento."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if campo_unidade.value is None:

            mensagem.value = (
                "Selecione a unidade."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        alimento_id = cadastrar_alimento(
            fazenda_id=fazenda_id,
            nome=nome,
            categoria=campo_categoria.value,
            unidade=campo_unidade.value
        )

        limpar_campos()

        mensagem.value = (
            f"{codigo_alimento(alimento_id)} "
            "cadastrado com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_alimentos()

    # ======================================================
    # EDITAR
    # ======================================================

    def abrir_edicao(alimento):

        if not pode_acessar_fazenda():
            return

        if (
            alimento["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        editar_nome = ft.TextField(
            label="Nome do alimento",
            value=alimento["nome"],
            width=450
        )

        editar_categoria = ft.Dropdown(
            label="Categoria",
            width=450,
            value=alimento["categoria"],
            options=[
                ft.DropdownOption(
                    key="VOLUMOSO",
                    text="Volumoso"
                ),
                ft.DropdownOption(
                    key="CONCENTRADO_ENERGETICO",
                    text="Concentrado energético"
                ),
                ft.DropdownOption(
                    key="CONCENTRADO_PROTEICO",
                    text="Concentrado proteico"
                ),
                ft.DropdownOption(
                    key="MINERAL",
                    text="Mineral"
                ),
                ft.DropdownOption(
                    key="NUCLEO",
                    text="Núcleo"
                ),
                ft.DropdownOption(
                    key="ADITIVO",
                    text="Aditivo"
                ),
                ft.DropdownOption(
                    key="COPRODUTO",
                    text="Coproduto"
                ),
                ft.DropdownOption(
                    key="OUTRO",
                    text="Outro"
                ),
            ]
        )

        editar_unidade = ft.Dropdown(
            label="Unidade",
            width=450,
            value=alimento["unidade"],
            options=[
                ft.DropdownOption(
                    key="kg",
                    text="kg"
                ),
                ft.DropdownOption(
                    key="ton",
                    text="ton"
                ),
                ft.DropdownOption(
                    key="L",
                    text="L"
                ),
                ft.DropdownOption(
                    key="unidade",
                    text="unidade"
                ),
            ]
        )

        mensagem_edicao = ft.Text()

        def salvar_alteracoes(e):

            if not pode_acessar_fazenda():

                mensagem_edicao.value = (
                    "Acesso não autorizado."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            nome = (
                editar_nome.value
                or ""
            ).strip()

            if not nome:

                mensagem_edicao.value = (
                    "Informe o nome do alimento."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if editar_categoria.value is None:

                mensagem_edicao.value = (
                    "Selecione a categoria."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if editar_unidade.value is None:

                mensagem_edicao.value = (
                    "Selecione a unidade."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            atualizar_alimento(
                alimento_id=alimento["id"],
                fazenda_id=fazenda_atual_id(),
                nome=nome,
                categoria=editar_categoria.value,
                unidade=editar_unidade.value
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_alimento(alimento['id'])} "
                "atualizado com sucesso."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_alimentos()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar "
                f"{codigo_alimento(alimento['id'])}"
            ),

            content=ft.Column(
                controls=[
                    editar_nome,
                    editar_categoria,
                    editar_unidade,
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
    # REGISTRAR NOVA MATÉRIA SECA
    # ======================================================

    def abrir_registro_ms(alimento):

        if not pode_acessar_fazenda():
            return

        if alimento["fazenda_id"] != fazenda_atual_id():
            return

        campo_ms = ft.TextField(
            label="Matéria seca (%)",
            hint_text="Ex.: 88,0",
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        campo_data_ms = ft.TextField(
            label="Data da análise / vigência",
            hint_text="DD/MM/AAAA",
            width=450,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=aplicar_mascara_data
        )

        campo_observacao = ft.TextField(
            label="Observação",
            hint_text="Ex.: Análise do laboratório",
            width=450,
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        mensagem_ms = ft.Text()

        def registrar(e):

            if not pode_acessar_fazenda():

                mensagem_ms.value = (
                    "Acesso não autorizado."
                )
                mensagem_ms.color = ft.Colors.RED

                page.update()
                return

            materia_seca = converter_decimal(
                campo_ms.value
            )

            if (
                materia_seca is None
                or materia_seca <= 0
                or materia_seca > 100
            ):

                mensagem_ms.value = (
                    "Informe uma matéria seca válida "
                    "entre 0 e 100%."
                )

                mensagem_ms.color = ft.Colors.RED

                page.update()
                return

            data_vigencia = (
                data_interface_para_banco(
                    campo_data_ms.value
                )
            )

            if data_vigencia is None:

                mensagem_ms.value = (
                    "Informe uma data válida "
                    "no formato DD/MM/AAAA."
                )

                mensagem_ms.color = ft.Colors.RED

                page.update()
                return

            observacao = (
                campo_observacao.value
                or ""
            ).strip()

            try:

                registrar_ms_alimento(
                    alimento_id=alimento["id"],
                    fazenda_id=fazenda_atual_id(),
                    materia_seca=materia_seca,
                    data_vigencia=data_vigencia,
                    observacao=(
                        observacao
                        if observacao
                        else None
                    )
                )

            except ValueError as erro:

                mensagem_ms.value = str(erro)
                mensagem_ms.color = ft.Colors.RED

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"Nova MS registrada para "
                f"{alimento['nome']}."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_alimentos()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Registrar MS — "
                f"{codigo_alimento(alimento['id'])}"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        alimento["nome"],
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),

                    campo_ms,

                    campo_data_ms,

                    ft.Text(
                        "Digite apenas os números. "
                        "Ex.: 15092026 → 15/09/2026",
                        size=12
                    ),

                    campo_observacao,

                    mensagem_ms
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
                    content="Registrar",
                    icon=ft.Icons.ADD,
                    on_click=registrar
                )
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)
        # ======================================================
    # HISTÓRICO DE MATÉRIA SECA
    # ======================================================

    def abrir_historico_ms(alimento):

        if alimento["fazenda_id"] != fazenda_atual_id():
            return

        historico = listar_historico_ms_alimento(
            alimento_id=alimento["id"],
            fazenda_id=fazenda_atual_id()
        )

        itens = []

        if not historico:

            itens.append(
                ft.Text(
                    "Nenhum registro de matéria seca "
                    "foi encontrado."
                )
            )

        else:

            for registro in historico:

                data = data_banco_para_interface(
                    registro["data_vigencia"]
                )

                observacao = (
                    registro["observacao"]
                    or "Sem observação"
                )

                itens.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(
                                            data,
                                            weight=(
                                                ft.FontWeight.BOLD
                                            )
                                        ),

                                        ft.Text(
                                            (
                                                f"{registro['materia_seca']:.2f}% MS"
                                            ),
                                            size=18,
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
                                    f"Observação: "
                                    f"{observacao}"
                                )
                            ],
                            spacing=5
                        ),

                        padding=12,

                        border=ft.Border.all(
                            1,
                            ft.Colors.OUTLINE_VARIANT
                        ),

                        border_radius=10
                    )
                )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Histórico de MS — "
                f"{codigo_alimento(alimento['id'])}"
            ),

            content=ft.Column(
                controls=itens,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                height=400,
                width=520
            ),

            actions=[
                ft.TextButton(
                    "Fechar",
                    on_click=lambda e:
                    page.pop_dialog()
                )
            ]
        )

        page.show_dialog(dialogo)
    # ======================================================
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(alimento):

        if (
            alimento["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        def executar(e):

            if not pode_acessar_fazenda():
                return

            desativar_alimento(
                alimento_id=alimento["id"],
                fazenda_id=fazenda_atual_id()
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_alimento(alimento['id'])} "
                "desativado."
            )

            mensagem.color = ft.Colors.ORANGE

            carregar_alimentos()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Desativar alimento"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{codigo_alimento(alimento['id'])}"
                        f" — {alimento['nome']}"
                    ),

                    ft.Text(
                        "O alimento deixará de aparecer "
                        "nas listas operacionais, mas "
                        "seu histórico será preservado."
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
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR
    # ======================================================

    def confirmar_reativacao(alimento):

        if (
            alimento["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        def executar(e):

            if not pode_acessar_fazenda():
                return

            reativar_alimento(
                alimento_id=alimento["id"],
                fazenda_id=fazenda_atual_id()
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_alimento(alimento['id'])} "
                "reativado."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_alimentos()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar alimento"
            ),

            content=ft.Text(
                f"{codigo_alimento(alimento['id'])}"
                f" — {alimento['nome']}"
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
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

    # ======================================================
    # NOMES AMIGÁVEIS
    # ======================================================

    nomes_categorias = {
        "VOLUMOSO": "Volumoso",
        "CONCENTRADO_ENERGETICO":
            "Concentrado energético",
        "CONCENTRADO_PROTEICO":
            "Concentrado proteico",
        "MINERAL": "Mineral",
        "NUCLEO": "Núcleo",
        "ADITIVO": "Aditivo",
        "COPRODUTO": "Coproduto",
        "OUTRO": "Outro",
    }

    # ======================================================
    # LISTAR
    # ======================================================

    def carregar_alimentos(e=None):

        lista_alimentos.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            lista_alimentos.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Selecione uma fazenda "
                        "para visualizar os alimentos."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        if not pode_acessar_fazenda():

            lista_alimentos.controls.append(
                ft.Text(
                    "Você não possui acesso operacional "
                    "a esta fazenda.",
                    color=ft.Colors.RED
                )
            )

            page.update()
            return

        if mostrar_inativos.value:

            alimentos = (
                listar_alimentos_fazenda_todos(
                    fazenda_id
                )
            )

        else:

            alimentos = (
                listar_alimentos_fazenda(
                    fazenda_id
                )
            )

        if not alimentos:

            lista_alimentos.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum alimento cadastrado "
                        "nesta fazenda."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        for alimento in alimentos:

            ativo = bool(
                alimento["ativo"]
            )
            ms_atual = buscar_ms_atual_alimento(
                alimento_id=alimento["id"],
                fazenda_id=fazenda_id
            )

            if ms_atual:

                texto_ms = (
                    f"{ms_atual['materia_seca']:.2f}%"
                )

                texto_data_ms = (
                    data_banco_para_interface(
                        ms_atual["data_vigencia"]
                    )
                )

            else:

                texto_ms = "Não cadastrada"
                texto_data_ms = "—"
            categoria = (
                nomes_categorias.get(
                    alimento["categoria"],
                    alimento["categoria"]
                )
            )

            botoes = []

            if ativo:

                botoes.extend([
                    ft.Button(
                        content="Editar cadastro",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        a=alimento:
                        abrir_edicao(a)
                    ),

                    ft.Button(
                        content="Registrar nova MS",
                        icon=ft.Icons.SCIENCE,
                        on_click=lambda e,
                        a=alimento:
                        abrir_registro_ms(a)
                    ),

                    ft.Button(
                        content="Histórico de MS",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda e,
                        a=alimento:
                        abrir_historico_ms(a)
                    ),

                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e,
                        a=alimento:
                        confirmar_desativacao(a)
                    )
                ])

            else:

                botoes.extend([
                    ft.Button(
                        content="Histórico de MS",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda e,
                        a=alimento:
                        abrir_historico_ms(a)
                    ),

                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        a=alimento:
                        confirmar_reativacao(a)
                    )
                ])

            lista_alimentos.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        codigo_alimento(
                                            alimento["id"]
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
                                alimento["nome"],
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                f"Categoria: {categoria}"
                            ),

                            ft.Text(
                                f"Unidade: "
                                f"{alimento['unidade']}"
                            ),
                            ft.Text(
                                f"MS atual: "
                                f"{texto_ms}",
                                weight=(
                                    ft.FontWeight.BOLD
                                )
                            ),

                            ft.Text(
                                f"Vigente desde: "
                                f"{texto_data_ms}"
                            ),
                            ft.Row(
                                controls=botoes,
                                spacing=10,
                                wrap=True
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

    # ======================================================
    # EVENTOS
    # ======================================================

    mostrar_inativos.on_change = (
        carregar_alimentos
    )

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    carregar_alimentos()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[
            ft.Text(
                "Alimentos",
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
                "Cadastre os ingredientes utilizados "
                "nas dietas da propriedade."
            ),

            ft.Divider(),

            ft.Text(
                "Novo alimento",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,

            campo_categoria,

            campo_unidade,

            ft.Button(
                content="Cadastrar alimento",
                icon=ft.Icons.ADD,
                on_click=salvar_alimento
            ),

            mensagem,

            ft.Divider(),

            ft.Row(
                controls=[
                    ft.Text(
                        "Alimentos cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_inativos
                ]
            ),

            lista_alimentos
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )