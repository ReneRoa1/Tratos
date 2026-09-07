import flet as ft

from database.models import (
    cadastrar_dieta,
    listar_dietas_fazenda,
    listar_itens_dieta,
    arquivar_dieta,
    listar_alimentos_fazenda,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
)

from services.sessao import sessao
from services.identificadores import (
    codigo_dieta,
    codigo_alimento,
)


def tela_dietas(page: ft.Page):

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
    # CONVERSÕES
    # ======================================================

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

    def converter_inteiro(valor):

        if valor is None:
            return None

        valor = str(valor).strip()

        if not valor:
            return None

        try:
            return int(valor)

        except ValueError:
            return None

    # ======================================================
    # CAMPOS PRINCIPAIS
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome da dieta",
        hint_text="Ex.: Recria 01",
        width=500
    )

    campo_observacoes = ft.TextField(
        label="Observações",
        hint_text="Informações adicionais sobre a dieta",
        width=500,
        multiline=True,
        min_lines=2,
        max_lines=4
    )

    mensagem = ft.Text()

    mostrar_arquivadas = ft.Switch(
        label="Mostrar versões arquivadas",
        value=False
    )

    lista_dietas = ft.Column(
        spacing=12
    )

    area_ingredientes = ft.Column(
        spacing=10
    )

    texto_soma = ft.Text(
        "Total da dieta: 0,00% MS",
        size=16,
        weight=ft.FontWeight.BOLD
    )

    # ======================================================
    # ALIMENTOS DISPONÍVEIS
    # ======================================================

    def alimentos_disponiveis():

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:
            return []

        return listar_alimentos_fazenda(
            fazenda_id
        )

    # ======================================================
    # LINHAS DE INGREDIENTES
    # ======================================================

    linhas_ingredientes = []

    def atualizar_soma(e=None):

        soma = 0.0

        for linha in linhas_ingredientes:

            inclusao = converter_decimal(
                linha["inclusao"].value
            )

            if inclusao is not None:
                soma += inclusao

        texto_soma.value = (
            f"Total da dieta: {soma:.2f}% MS"
        )

        if abs(soma - 100.0) <= 0.01:

            texto_soma.color = ft.Colors.GREEN

        else:

            texto_soma.color = ft.Colors.ORANGE

        page.update()

    def remover_linha(linha):

        if linha in linhas_ingredientes:
            linhas_ingredientes.remove(linha)

        if linha["container"] in area_ingredientes.controls:
            area_ingredientes.controls.remove(
                linha["container"]
            )

        atualizar_soma()

    def adicionar_linha_ingrediente(
        alimento_id=None,
        inclusao=None,
        ordem=None
    ):

        alimentos = alimentos_disponiveis()

        campo_alimento = ft.Dropdown(
            label="Ingrediente",
            width=330
        )

        for alimento in alimentos:

            campo_alimento.options.append(
                ft.DropdownOption(
                    key=str(alimento["id"]),
                    text=(
                        f"{codigo_alimento(alimento['id'])}"
                        f" — {alimento['nome']}"
                    )
                )
            )

        if alimento_id is not None:
            campo_alimento.value = str(
                alimento_id
            )

        campo_inclusao = ft.TextField(
            label="Inclusão (% MS)",
            width=160,
            value=(
                str(inclusao)
                if inclusao is not None
                else ""
            ),
            keyboard_type=ft.KeyboardType.NUMBER
        )

        campo_ordem = ft.TextField(
            label="Ordem",
            width=100,
            value=(
                str(ordem)
                if ordem is not None
                else ""
            ),
            keyboard_type=ft.KeyboardType.NUMBER
        )

        linha = {}

        botao_remover = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            tooltip="Remover ingrediente",
            on_click=lambda e:
            remover_linha(linha)
        )

        container = ft.Container(
            content=ft.Row(
                controls=[
                    campo_alimento,
                    campo_inclusao,
                    campo_ordem,
                    botao_remover
                ],
                spacing=10,
                wrap=True
            ),
            padding=10,
            border=ft.Border.all(
                1,
                ft.Colors.OUTLINE_VARIANT
            ),
            border_radius=10
        )

        linha.update({
            "alimento": campo_alimento,
            "inclusao": campo_inclusao,
            "ordem": campo_ordem,
            "container": container
        })

        campo_inclusao.on_change = (
            atualizar_soma
        )

        linhas_ingredientes.append(
            linha
        )

        area_ingredientes.controls.append(
            container
        )

        atualizar_soma()

    # ======================================================
    # LIMPAR FORMULÁRIO
    # ======================================================

    def limpar_formulario():

        campo_nome.value = ""
        campo_observacoes.value = ""

        linhas_ingredientes.clear()
        area_ingredientes.controls.clear()

        adicionar_linha_ingrediente()

        atualizar_soma()

    # ======================================================
    # MONTAR ITENS
    # ======================================================

    def obter_itens_formulario():

        itens = []

        alimentos_usados = set()

        for linha in linhas_ingredientes:

            if linha["alimento"].value is None:

                raise ValueError(
                    "Selecione o alimento "
                    "em todas as linhas."
                )

            alimento_id = int(
                linha["alimento"].value
            )

            if alimento_id in alimentos_usados:

                raise ValueError(
                    "O mesmo alimento não pode aparecer "
                    "duas vezes na dieta."
                )

            alimentos_usados.add(
                alimento_id
            )

            inclusao = converter_decimal(
                linha["inclusao"].value
            )

            if (
                inclusao is None
                or inclusao <= 0
            ):

                raise ValueError(
                    "Informe uma inclusão maior que zero "
                    "para todos os ingredientes."
                )

            ordem = converter_inteiro(
                linha["ordem"].value
            )

            if (
                linha["ordem"].value
                and (
                    ordem is None
                    or ordem <= 0
                )
            ):

                raise ValueError(
                    "A ordem de carregamento deve ser "
                    "um número inteiro maior que zero."
                )

            itens.append({
                "alimento_id": alimento_id,
                "inclusao_ms": inclusao,
                "ordem_carregamento": ordem
            })

        return itens

    # ======================================================
    # SALVAR DIETA
    # ======================================================

    def salvar_dieta(e):

        if not pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui acesso operacional "
                "a esta fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        nome = (
            campo_nome.value or ""
        ).strip()

        if not nome:

            mensagem.value = (
                "Informe o nome da dieta."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if not linhas_ingredientes:

            mensagem.value = (
                "Adicione pelo menos um ingrediente."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        try:

            itens = obter_itens_formulario()

            soma = sum(
                item["inclusao_ms"]
                for item in itens
            )

            if abs(soma - 100.0) > 0.01:

                raise ValueError(
                    f"A soma da dieta deve ser 100%. "
                    f"Total atual: {soma:.2f}%."
                )

            observacoes = (
                campo_observacoes.value
                or ""
            ).strip()

            dieta_id = cadastrar_dieta(
                fazenda_id=fazenda_atual_id(),
                nome=nome,
                itens=itens,
                observacoes=(
                    observacoes
                    if observacoes
                    else None
                )
            )

        except ValueError as erro:

            mensagem.value = str(erro)
            mensagem.color = ft.Colors.RED

            page.update()
            return

        mensagem.value = (
            f"{codigo_dieta(dieta_id)} "
            "salva com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        limpar_formulario()
        carregar_dietas()

    # ======================================================
    # VISUALIZAR COMPOSIÇÃO
    # ======================================================

    def abrir_composicao(dieta):

        itens = listar_itens_dieta(
            dieta_id=dieta["id"],
            fazenda_id=fazenda_atual_id()
        )

        controles = []

        total = 0.0

        for item in itens:

            total += item["inclusao_ms"]

            ordem = (
                str(item["ordem_carregamento"])
                if item["ordem_carregamento"]
                is not None
                else "—"
            )

            controles.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                item["alimento_nome"],
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                f"Inclusão: "
                                f"{item['inclusao_ms']:.2f}% MS"
                            ),

                            ft.Text(
                                f"Ordem de carregamento: "
                                f"{ordem}"
                            )
                        ],
                        spacing=4
                    ),

                    padding=12,

                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT
                    ),

                    border_radius=10
                )
            )

        controles.append(
            ft.Text(
                f"Total: {total:.2f}% MS",
                size=17,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREEN
            )
        )

        if dieta["observacoes"]:

            controles.append(
                ft.Text(
                    f"Observações: "
                    f"{dieta['observacoes']}"
                )
            )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"{dieta['nome']} — "
                f"Versão {dieta['versao']}"
            ),

            content=ft.Column(
                controls=controles,
                spacing=10,
                width=520,
                height=430,
                scroll=ft.ScrollMode.AUTO
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
    # NOVA VERSÃO
    # ======================================================

    def criar_nova_versao(dieta):

        if dieta["status"] != "ATIVA":
            return

        itens = listar_itens_dieta(
            dieta_id=dieta["id"],
            fazenda_id=fazenda_atual_id()
        )

        campo_nome.value = dieta["nome"]

        campo_observacoes.value = (
            dieta["observacoes"]
            or ""
        )

        linhas_ingredientes.clear()
        area_ingredientes.controls.clear()

        for item in itens:

            adicionar_linha_ingrediente(
                alimento_id=item["alimento_id"],
                inclusao=item["inclusao_ms"],
                ordem=item["ordem_carregamento"]
            )

        mensagem.value = (
            f"Composição da versão "
            f"{dieta['versao']} carregada. "
            "Ao salvar será criada uma nova versão."
        )

        mensagem.color = ft.Colors.BLUE

        page.update()

    # ======================================================
    # ARQUIVAR
    # ======================================================

    def confirmar_arquivamento(dieta):

        def executar(e):

            if not pode_acessar_fazenda():
                return

            arquivar_dieta(
                dieta_id=dieta["id"],
                fazenda_id=fazenda_atual_id()
            )

            page.pop_dialog()

            mensagem.value = (
                f"{dieta['nome']} — "
                f"V{dieta['versao']} arquivada."
            )

            mensagem.color = ft.Colors.ORANGE

            carregar_dietas()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Arquivar dieta?"
            ),

            content=ft.Text(
                (
                    f"{dieta['nome']} — "
                    f"Versão {dieta['versao']}\n\n"
                    "A composição será preservada "
                    "para consultas históricas."
                )
            ),

            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Arquivar",
                    icon=ft.Icons.ARCHIVE,
                    on_click=executar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAGEM
    # ======================================================

    def carregar_dietas(e=None):

        lista_dietas.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            lista_dietas.controls.append(
                ft.Text(
                    "Selecione uma fazenda."
                )
            )

            page.update()
            return

        if not pode_acessar_fazenda():

            lista_dietas.controls.append(
                ft.Text(
                    "Você não possui acesso operacional "
                    "a esta fazenda.",
                    color=ft.Colors.RED
                )
            )

            page.update()
            return

        dietas = listar_dietas_fazenda(
            fazenda_id=fazenda_id,
            incluir_arquivadas=(
                mostrar_arquivadas.value
            )
        )

        if not dietas:

            lista_dietas.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhuma dieta cadastrada."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        for dieta in dietas:

            ativa = (
                dieta["status"] == "ATIVA"
            )

            botoes = [
                ft.Button(
                    content="Ver composição",
                    icon=ft.Icons.VISIBILITY,
                    on_click=lambda e,
                    d=dieta:
                    abrir_composicao(d)
                )
            ]

            if ativa:

                botoes.extend([
                    ft.Button(
                        content="Criar nova versão",
                        icon=ft.Icons.CONTENT_COPY,
                        on_click=lambda e,
                        d=dieta:
                        criar_nova_versao(d)
                    ),

                    ft.Button(
                        content="Arquivar",
                        icon=ft.Icons.ARCHIVE,
                        on_click=lambda e,
                        d=dieta:
                        confirmar_arquivamento(d)
                    )
                ])

            lista_dietas.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        codigo_dieta(
                                            dieta["id"]
                                        ),
                                        size=13,
                                        weight=ft.FontWeight.BOLD
                                    ),

                                    ft.Text(
                                        dieta["status"],
                                        color=(
                                            ft.Colors.GREEN
                                            if ativa
                                            else ft.Colors.ORANGE
                                        ),
                                        weight=ft.FontWeight.BOLD
                                    )
                                ],

                                alignment=(
                                    ft.MainAxisAlignment
                                    .SPACE_BETWEEN
                                )
                            ),

                            ft.Text(
                                dieta["nome"],
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                f"Versão: "
                                f"{dieta['versao']}"
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

    mostrar_arquivadas.on_change = (
        carregar_dietas
    )

    # Primeira linha do formulário
    adicionar_linha_ingrediente()

    carregar_dietas()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[
            ft.Text(
                "Dietas",
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
                "As inclusões são informadas em "
                "percentual da matéria seca da dieta."
            ),

            ft.Divider(),

            ft.Text(
                "Nova dieta / Nova versão",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,

            campo_observacoes,

            ft.Text(
                "Ingredientes",
                size=18,
                weight=ft.FontWeight.BOLD
            ),

            area_ingredientes,

            ft.Button(
                content="Adicionar ingrediente",
                icon=ft.Icons.ADD,
                on_click=lambda e:
                adicionar_linha_ingrediente()
            ),

            texto_soma,

            ft.Button(
                content="Salvar dieta",
                icon=ft.Icons.SAVE,
                on_click=salvar_dieta
            ),

            mensagem,

            ft.Divider(),

            ft.Row(
                controls=[
                    ft.Text(
                        "Dietas cadastradas",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_arquivadas
                ]
            ),

            lista_dietas
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )