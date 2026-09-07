import flet as ft
from datetime import datetime
from database.models import (
    cadastrar_misturador,
    listar_misturadores_fazenda,
    listar_misturadores_fazenda_todos,
    atualizar_misturador,
    desativar_misturador,
    reativar_misturador,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
        registrar_calibracao_misturador,
    listar_historico_calibracoes_misturador,
    buscar_calibracao_atual_misturador_dieta,
    listar_dietas_fazenda,
)

from services.sessao import sessao
from services.identificadores import codigo_misturador


def tela_misturadores(page: ft.Page):

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
        # ======================================================
    # DATAS
    # ======================================================

    def aplicar_mascara_data(e):

        numeros = "".join(
            c for c in e.control.value
            if c.isdigit()
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
            return "—"

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
    # ======================================================
    # CAMPOS
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do misturador",
        hint_text="Ex.: Vagão 01",
        width=500
    )

    campo_capacidade = ft.TextField(
        label="Capacidade nominal (m³)",
        hint_text="Ex.: 10",
        width=500,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    campo_capacidade_util = ft.TextField(
        label="Capacidade útil (%)",
        hint_text="Ex.: 80",
        value="100",
        width=500,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    campo_observacoes = ft.TextField(
        label="Observações",
        hint_text="Ex.: Vagão utilizado no confinamento",
        width=500,
        multiline=True,
        min_lines=2,
        max_lines=4
    )

    texto_volume_util = ft.Text(
        "Volume útil: —",
        size=16,
        weight=ft.FontWeight.BOLD
    )

    mensagem = ft.Text()

    mostrar_inativos = ft.Switch(
        label="Mostrar misturadores inativos",
        value=False
    )

    lista_misturadores = ft.Column(
        spacing=12
    )

    # ======================================================
    # PRÉVIA DO VOLUME ÚTIL
    # ======================================================

    def atualizar_volume_util(e=None):

        capacidade = converter_decimal(
            campo_capacidade.value
        )

        percentual = converter_decimal(
            campo_capacidade_util.value
        )

        if (
            capacidade is None
            or percentual is None
            or capacidade <= 0
            or percentual <= 0
            or percentual > 100
        ):

            texto_volume_util.value = (
                "Volume útil: —"
            )

        else:

            volume_util = (
                capacidade
                * percentual
                / 100.0
            )

            texto_volume_util.value = (
                f"Volume útil: "
                f"{volume_util:.2f} m³"
            )

        page.update()

    campo_capacidade.on_change = (
        atualizar_volume_util
    )

    campo_capacidade_util.on_change = (
        atualizar_volume_util
    )

    # ======================================================
    # LIMPAR CAMPOS
    # ======================================================

    def limpar_campos():

        campo_nome.value = ""
        campo_capacidade.value = ""
        campo_capacidade_util.value = "100"
        campo_observacoes.value = ""

        atualizar_volume_util()

    # ======================================================
    # CADASTRAR
    # ======================================================

    def salvar_misturador(e):

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

        capacidade = converter_decimal(
            campo_capacidade.value
        )

        capacidade_util = converter_decimal(
            campo_capacidade_util.value
        )

        observacoes = (
            campo_observacoes.value
            or ""
        ).strip()

        if not nome:

            mensagem.value = (
                "Informe o nome do misturador."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if (
            capacidade is None
            or capacidade <= 0
        ):

            mensagem.value = (
                "Informe uma capacidade nominal válida."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if (
            capacidade_util is None
            or capacidade_util <= 0
            or capacidade_util > 100
        ):

            mensagem.value = (
                "A capacidade útil deve estar "
                "entre 0 e 100%."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        try:

            misturador_id = cadastrar_misturador(
                fazenda_id=fazenda_atual_id(),
                nome=nome,
                capacidade_m3=capacidade,
                capacidade_util_percentual=(
                    capacidade_util
                ),
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

        limpar_campos()

        mensagem.value = (
            f"{codigo_misturador(misturador_id)} "
            "cadastrado com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_misturadores()

    # ======================================================
    # EDITAR
    # ======================================================

    def abrir_edicao(misturador):

        if not pode_acessar_fazenda():
            return

        if (
            misturador["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        editar_nome = ft.TextField(
            label="Nome do misturador",
            value=misturador["nome"],
            width=450
        )

        editar_capacidade = ft.TextField(
            label="Capacidade nominal (m³)",
            value=str(
                misturador["capacidade_m3"]
            ),
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        editar_capacidade_util = ft.TextField(
            label="Capacidade útil (%)",
            value=str(
                misturador[
                    "capacidade_util_percentual"
                ]
            ),
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        editar_observacoes = ft.TextField(
            label="Observações",
            value=(
                misturador["observacoes"]
                or ""
            ),
            width=450,
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        texto_previa = ft.Text(
            weight=ft.FontWeight.BOLD
        )

        mensagem_edicao = ft.Text()

        def atualizar_previa_edicao(e=None):

            capacidade = converter_decimal(
                editar_capacidade.value
            )

            percentual = converter_decimal(
                editar_capacidade_util.value
            )

            if (
                capacidade is None
                or percentual is None
                or capacidade <= 0
                or percentual <= 0
                or percentual > 100
            ):

                texto_previa.value = (
                    "Volume útil: —"
                )

            else:

                volume = (
                    capacidade
                    * percentual
                    / 100.0
                )

                texto_previa.value = (
                    f"Volume útil: {volume:.2f} m³"
                )

            page.update()

        editar_capacidade.on_change = (
            atualizar_previa_edicao
        )

        editar_capacidade_util.on_change = (
            atualizar_previa_edicao
        )

        atualizar_previa_edicao()

        def salvar_alteracoes(e):

            nome = (
                editar_nome.value
                or ""
            ).strip()

            capacidade = converter_decimal(
                editar_capacidade.value
            )

            percentual = converter_decimal(
                editar_capacidade_util.value
            )

            observacoes = (
                editar_observacoes.value
                or ""
            ).strip()

            if not nome:

                mensagem_edicao.value = (
                    "Informe o nome do misturador."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if (
                capacidade is None
                or capacidade <= 0
            ):

                mensagem_edicao.value = (
                    "Capacidade nominal inválida."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if (
                percentual is None
                or percentual <= 0
                or percentual > 100
            ):

                mensagem_edicao.value = (
                    "Capacidade útil inválida."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            try:

                atualizar_misturador(
                    misturador_id=misturador["id"],
                    fazenda_id=fazenda_atual_id(),
                    nome=nome,
                    capacidade_m3=capacidade,
                    capacidade_util_percentual=(
                        percentual
                    ),
                    observacoes=(
                        observacoes
                        if observacoes
                        else None
                    )
                )

            except ValueError as erro:

                mensagem_edicao.value = (
                    str(erro)
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_misturador(misturador['id'])} "
                "atualizado."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_misturadores()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar "
                f"{codigo_misturador(misturador['id'])}"
            ),

            content=ft.Column(
                controls=[
                    editar_nome,
                    editar_capacidade,
                    editar_capacidade_util,
                    texto_previa,
                    editar_observacoes,
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
    # DESATIVAR
    # ======================================================

    def confirmar_desativacao(misturador):

        if (
            misturador["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        def executar(e):

            if not pode_acessar_fazenda():
                return

            desativar_misturador(
                misturador_id=misturador["id"],
                fazenda_id=fazenda_atual_id()
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_misturador(misturador['id'])} "
                "desativado."
            )

            mensagem.color = ft.Colors.ORANGE

            carregar_misturadores()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Desativar misturador"
            ),

            content=ft.Text(
                (
                    f"{codigo_misturador(misturador['id'])}"
                    f" — {misturador['nome']}\n\n"
                    "O histórico de calibrações será "
                    "preservado."
                )
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

    def confirmar_reativacao(misturador):

        def executar(e):

            if not pode_acessar_fazenda():
                return

            reativar_misturador(
                misturador_id=misturador["id"],
                fazenda_id=fazenda_atual_id()
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_misturador(misturador['id'])} "
                "reativado."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_misturadores()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar misturador"
            ),

            content=ft.Text(
                (
                    f"{codigo_misturador(misturador['id'])}"
                    f" — {misturador['nome']}"
                )
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
    # CALIBRAR MISTURADOR
    # ======================================================

    def abrir_calibracao(misturador):

        if not pode_acessar_fazenda():
            return

        if (
            misturador["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        dietas = listar_dietas_fazenda(
            fazenda_id=fazenda_atual_id(),
            incluir_arquivadas=False
        )

        campo_dieta = ft.Dropdown(
            label="Dieta",
            width=460
        )

        for dieta in dietas:

            campo_dieta.options.append(
                ft.DropdownOption(
                    key=str(dieta["id"]),
                    text=(
                        f"{dieta['nome']} "
                        f"— V{dieta['versao']}"
                    )
                )
            )

        campo_densidade = ft.TextField(
            label="Densidade da dieta (kg/m³)",
            hint_text="Ex.: 420",
            width=460,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        campo_data = ft.TextField(
            label="Data da calibração",
            hint_text="DD/MM/AAAA",
            width=460,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=aplicar_mascara_data
        )

        campo_observacoes_calibracao = ft.TextField(
            label="Observações",
            hint_text=(
                "Ex.: calibração realizada "
                "após alteração na dieta"
            ),
            width=460,
            multiline=True,
            min_lines=2,
            max_lines=4
        )

        texto_volume = ft.Text(
            (
                "Volume útil do misturador: "
                f"{misturador['volume_util_m3']:.2f} m³"
            ),
            weight=ft.FontWeight.BOLD
        )

        texto_capacidade = ft.Text(
            "Capacidade operacional: —",
            size=18,
            weight=ft.FontWeight.BOLD
        )

        mensagem_calibracao = ft.Text()

        # --------------------------------------------------
        # Prévia
        # --------------------------------------------------

        def atualizar_capacidade(e=None):

            densidade = converter_decimal(
                campo_densidade.value
            )

            if (
                densidade is None
                or densidade <= 0
            ):

                texto_capacidade.value = (
                    "Capacidade operacional: —"
                )

            else:

                capacidade = (
                    misturador["volume_util_m3"]
                    * densidade
                )

                texto_capacidade.value = (
                    "Capacidade operacional: "
                    f"{capacidade:.2f} kg/carga"
                )

            page.update()

        campo_densidade.on_change = (
            atualizar_capacidade
        )

        # --------------------------------------------------
        # Salvar
        # --------------------------------------------------

        def salvar_calibracao(e):

            if campo_dieta.value is None:

                mensagem_calibracao.value = (
                    "Selecione uma dieta."
                )

                mensagem_calibracao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            densidade = converter_decimal(
                campo_densidade.value
            )

            if (
                densidade is None
                or densidade <= 0
            ):

                mensagem_calibracao.value = (
                    "Informe uma densidade válida."
                )

                mensagem_calibracao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            data_vigencia = (
                data_interface_para_banco(
                    campo_data.value
                )
            )

            if data_vigencia is None:

                mensagem_calibracao.value = (
                    "Informe uma data válida "
                    "no formato DD/MM/AAAA."
                )

                mensagem_calibracao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            observacoes = (
                campo_observacoes_calibracao.value
                or ""
            ).strip()

            try:

                registrar_calibracao_misturador(
                    fazenda_id=fazenda_atual_id(),
                    misturador_id=misturador["id"],
                    dieta_id=int(
                        campo_dieta.value
                    ),
                    densidade_kg_m3=densidade,
                    data_vigencia=data_vigencia,
                    observacoes=(
                        observacoes
                        if observacoes
                        else None
                    )
                )

            except ValueError as erro:

                mensagem_calibracao.value = (
                    str(erro)
                )

                mensagem_calibracao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                "Calibração registrada com sucesso "
                f"para {codigo_misturador(misturador['id'])}."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_misturadores()

        # --------------------------------------------------
        # Sem dietas
        # --------------------------------------------------

        if not dietas:

            conteudo = ft.Column(
                controls=[
                    ft.Text(
                        (
                            f"{codigo_misturador(misturador['id'])}"
                            f" — {misturador['nome']}"
                        ),
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        "Não existem dietas ativas "
                        "nesta fazenda."
                    ),

                    ft.Text(
                        "Cadastre uma dieta antes "
                        "de realizar a calibração."
                    )
                ],
                tight=True,
                spacing=12
            )

            acoes = [
                ft.TextButton(
                    "Fechar",
                    on_click=lambda e:
                    page.pop_dialog()
                )
            ]

        else:

            conteudo = ft.Column(
                controls=[
                    ft.Text(
                        (
                            f"{codigo_misturador(misturador['id'])}"
                            f" — {misturador['nome']}"
                        ),
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),

                    texto_volume,

                    campo_dieta,

                    campo_densidade,

                    texto_capacidade,

                    campo_data,

                    ft.Text(
                        (
                            "Digite somente os números. "
                            "Ex.: 07092026 → 07/09/2026"
                        ),
                        size=12
                    ),

                    campo_observacoes_calibracao,

                    mensagem_calibracao
                ],
                tight=True,
                spacing=12
            )

            acoes = [
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Registrar calibração",
                    icon=ft.Icons.SAVE,
                    on_click=salvar_calibracao
                )
            ]

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Calibrar misturador"
            ),

            content=conteudo,

            actions=acoes,

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)
        # ======================================================
    # HISTÓRICO DE CALIBRAÇÕES
    # ======================================================

    def abrir_historico_calibracoes(
        misturador
    ):

        if (
            misturador["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        historico = (
            listar_historico_calibracoes_misturador(
                misturador_id=misturador["id"],
                fazenda_id=fazenda_atual_id()
            )
        )

        controles = []

        if not historico:

            controles.append(
                ft.Text(
                    "Nenhuma calibração registrada."
                )
            )

        else:

            for calibracao in historico:

                data = (
                    data_banco_para_interface(
                        calibracao["data_vigencia"]
                    )
                )

                controles.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    (
                                        f"{calibracao['dieta_nome']} "
                                        f"— V{calibracao['dieta_versao']}"
                                    ),
                                    weight=ft.FontWeight.BOLD,
                                    size=16
                                ),

                                ft.Text(
                                    f"Data: {data}"
                                ),

                                ft.Text(
                                    (
                                        "Densidade: "
                                        f"{calibracao['densidade_kg_m3']:.2f} "
                                        "kg/m³"
                                    )
                                ),

                                ft.Text(
                                    (
                                        "Volume útil: "
                                        f"{calibracao['volume_util_m3']:.2f} "
                                        "m³"
                                    )
                                ),

                                ft.Text(
                                    (
                                        "Capacidade operacional: "
                                        f"{calibracao['capacidade_operacional_kg']:.2f} "
                                        "kg/carga"
                                    ),
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    (
                                        "Observações: "
                                        f"{calibracao['observacoes']}"
                                    )
                                    if calibracao["observacoes"]
                                    else "Observações: —"
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
                (
                    "Histórico de calibrações — "
                    f"{codigo_misturador(misturador['id'])}"
                )
            ),

            content=ft.Column(
                controls=controles,
                spacing=10,
                width=550,
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
    # LISTAGEM
    # ======================================================

    def carregar_misturadores(e=None):

        lista_misturadores.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            lista_misturadores.controls.append(
                ft.Text(
                    "Selecione uma fazenda."
                )
            )

            page.update()
            return

        if not pode_acessar_fazenda():

            lista_misturadores.controls.append(
                ft.Text(
                    "Você não possui acesso operacional "
                    "a esta fazenda.",
                    color=ft.Colors.RED
                )
            )

            page.update()
            return

        if mostrar_inativos.value:

            misturadores = (
                listar_misturadores_fazenda_todos(
                    fazenda_id
                )
            )

        else:

            misturadores = (
                listar_misturadores_fazenda(
                    fazenda_id
                )
            )

        if not misturadores:

            lista_misturadores.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum misturador cadastrado."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        for misturador in misturadores:

            ativo = bool(
                misturador["ativo"]
            )
            historico_calibracoes = (
                listar_historico_calibracoes_misturador(
                    misturador_id=misturador["id"],
                    fazenda_id=fazenda_id
                )
            )

            quantidade_calibracoes = len(
                historico_calibracoes
            )
            botoes = []

            if ativo:

                botoes.extend([
                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        m=misturador:
                        abrir_edicao(m)
                    ),

                    ft.Button(
                        content="Calibrar",
                        icon=ft.Icons.SCIENCE,
                        on_click=lambda e,
                        m=misturador:
                        abrir_calibracao(m)
                    ),

                    ft.Button(
                        content="Histórico calibração",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda e,
                        m=misturador:
                        abrir_historico_calibracoes(m)
                    ),

                    ft.Button(
                        content="Desativar",
                        icon=ft.Icons.BLOCK,
                        on_click=lambda e,
                        m=misturador:
                        confirmar_desativacao(m)
                    )
                ])
            else:

                botoes.extend([
                    ft.Button(
                        content="Histórico calibração",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda e,
                        m=misturador:
                        abrir_historico_calibracoes(m)
                    ),

                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        m=misturador:
                        confirmar_reativacao(m)
                    )
                ])
            lista_misturadores.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        codigo_misturador(
                                            misturador["id"]
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
                                misturador["nome"],
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                (
                                    "Capacidade nominal: "
                                    f"{misturador['capacidade_m3']:.2f} m³"
                                )
                            ),

                            ft.Text(
                                (
                                    "Capacidade útil: "
                                    f"{misturador['capacidade_util_percentual']:.2f}%"
                                )
                            ),

                            ft.Text(
                                (
                                    "Volume operacional: "
                                    f"{misturador['volume_util_m3']:.2f} m³"
                                ),
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text(
                                (
                                    "Calibrações registradas: "
                                    f"{quantidade_calibracoes}"
                                )
                            ),
                            ft.Text(
                                (
                                    "Observações: "
                                    f"{misturador['observacoes']}"
                                )
                                if misturador["observacoes"]
                                else "Observações: —"
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
    # EVENTOS / INICIALIZAÇÃO
    # ======================================================

    mostrar_inativos.on_change = (
        carregar_misturadores
    )

    carregar_misturadores()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[
            ft.Text(
                "Misturadores",
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
                "Cadastre os vagões ou misturadores "
                "utilizados no fornecimento das dietas."
            ),

            ft.Divider(),

            ft.Text(
                "Novo misturador",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,

            campo_capacidade,

            campo_capacidade_util,

            texto_volume_util,

            campo_observacoes,

            ft.Button(
                content="Cadastrar misturador",
                icon=ft.Icons.ADD,
                on_click=salvar_misturador
            ),

            mensagem,

            ft.Divider(),

            ft.Row(
                controls=[
                    ft.Text(
                        "Misturadores cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_inativos
                ]
            ),

            lista_misturadores
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )