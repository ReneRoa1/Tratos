from datetime import datetime

import flet as ft

from database.models import (
    listar_lotes_fazenda,
    listar_misturadores_fazenda,
    registrar_trato_planejado,
    listar_tratos_planejados_fazenda,
    buscar_trato_planejado,
    listar_itens_trato_planejado,
    cancelar_trato_planejado,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
)

from services.calculos import calcular_trato_planejado
from screens.tratos import tela_tratos
from services.identificadores import (
    codigo_lote,
    codigo_misturador,
    codigo_trato_planejado,
)

from services.sessao import sessao


def tela_tratos(page: ft.Page):

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

    campo_lote = ft.Dropdown(
        label="Lote",
        width=500
    )

    campo_misturador = ft.Dropdown(
        label="Misturador",
        width=500
    )

    campo_data = ft.TextField(
        label="Data do trato",
        hint_text="DD/MM/AAAA",
        width=500,
        max_length=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=aplicar_mascara_data
    )

    campo_observacoes = ft.TextField(
        label="Observações",
        hint_text="Observações sobre este planejamento",
        width=500,
        multiline=True,
        min_lines=2,
        max_lines=4
    )

    mensagem = ft.Text()

    area_resultado = ft.Column(
        spacing=12
    )

    lista_planejamentos = ft.Column(
        spacing=12
    )

    resultado_atual = {
        "dados": None
    }

    # ======================================================
    # CARREGAR LOTE / MISTURADOR
    # ======================================================

    def carregar_opcoes():

        campo_lote.options.clear()
        campo_misturador.options.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:
            return

        lotes = listar_lotes_fazenda(
            fazenda_id
        )

        for lote in lotes:

            campo_lote.options.append(
                ft.DropdownOption(
                    key=str(lote["id"]),
                    text=(
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}"
                    )
                )
            )

        misturadores = (
            listar_misturadores_fazenda(
                fazenda_id
            )
        )

        for misturador in misturadores:

            campo_misturador.options.append(
                ft.DropdownOption(
                    key=str(misturador["id"]),
                    text=(
                        f"{codigo_misturador(misturador['id'])}"
                        f" — {misturador['nome']}"
                    )
                )
            )

    # ======================================================
    # LIMPAR RESULTADO
    # ======================================================

    def limpar_resultado():

        resultado_atual["dados"] = None

        area_resultado.controls.clear()

        page.update()

    # ======================================================
    # CALCULAR TRATO
    # ======================================================

    def calcular(e):

        limpar_resultado()

        if not pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui acesso operacional "
                "a esta fazenda."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if campo_lote.value is None:

            mensagem.value = (
                "Selecione um lote."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if campo_misturador.value is None:

            mensagem.value = (
                "Selecione um misturador."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        data_trato = (
            data_interface_para_banco(
                campo_data.value
            )
        )

        if data_trato is None:

            mensagem.value = (
                "Informe uma data válida "
                "no formato DD/MM/AAAA."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        try:

            resultado = calcular_trato_planejado(
                fazenda_id=fazenda_atual_id(),
                lote_id=int(
                    campo_lote.value
                ),
                misturador_id=int(
                    campo_misturador.value
                ),
                data_referencia=data_trato
            )

        except ValueError as erro:

            mensagem.value = str(erro)

            mensagem.color = ft.Colors.RED

            page.update()
            return

        resultado_atual["dados"] = resultado

        mensagem.value = (
            "Cálculo realizado com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        montar_resultado(resultado)

    # ======================================================
    # RESULTADO DO CÁLCULO
    # ======================================================

    def montar_resultado(resultado):

        area_resultado.controls.clear()

        # --------------------------------------------------
        # Resumo
        # --------------------------------------------------

        area_resultado.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Resumo do planejamento",
                            size=22,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            (
                                "Dieta: "
                                f"{resultado['dieta_nome']} "
                                f"— V{resultado['dieta_versao']}"
                            )
                        ),

                        ft.Text(
                            (
                                "Animais: "
                                f"{resultado['numero_animais']}"
                            )
                        ),

                        ft.Text(
                            (
                                "Consumo: "
                                f"{resultado['consumo_ms_animal_dia']:.2f} "
                                "kg MS/animal/dia"
                            )
                        ),

                        ft.Text(
                            (
                                "Necessidade total: "
                                f"{resultado['necessidade_ms_lote_kg']:.2f} "
                                "kg MS/dia"
                            )
                        ),

                        ft.Text(
                            (
                                "Matéria natural total: "
                                f"{resultado['total_materia_natural_kg']:.2f} "
                                "kg/dia"
                            ),
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Divider(),

                        ft.Text(
                            (
                                "Densidade utilizada: "
                                f"{resultado['densidade_kg_m3']:.2f} "
                                "kg/m³"
                            )
                        ),

                        ft.Text(
                            (
                                "Volume útil: "
                                f"{resultado['volume_util_m3']:.2f} "
                                "m³"
                            )
                        ),

                        ft.Text(
                            (
                                "Capacidade por carga: "
                                f"{resultado['capacidade_misturador_kg']:.2f} "
                                "kg"
                            )
                        ),

                        ft.Text(
                            (
                                "Número de cargas: "
                                f"{resultado['numero_cargas']}"
                            ),
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            (
                                "Peso médio por carga: "
                                f"{resultado['quantidade_media_por_carga_kg']:.2f} "
                                "kg"
                            )
                        )
                    ],
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

        # --------------------------------------------------
        # Ingredientes
        # --------------------------------------------------

        area_resultado.controls.append(
            ft.Text(
                "Ingredientes do dia",
                size=20,
                weight=ft.FontWeight.BOLD
            )
        )

        ingredientes = sorted(
            resultado["ingredientes"],
            key=lambda x: (
                x["ordem_carregamento"]
                if x["ordem_carregamento"]
                is not None
                else 999999
            )
        )

        for ingrediente in ingredientes:

            ordem = (
                ingrediente["ordem_carregamento"]
                if ingrediente[
                    "ordem_carregamento"
                ] is not None
                else "—"
            )

            data_ms = (
                data_banco_para_interface(
                    ingrediente["data_ms"]
                )
            )

            area_resultado.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                ingrediente[
                                    "alimento_nome"
                                ],
                                size=17,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                f"Ordem de carregamento: "
                                f"{ordem}"
                            ),

                            ft.Text(
                                (
                                    "Inclusão na MS: "
                                    f"{ingrediente['inclusao_ms_percentual']:.2f}%"
                                )
                            ),

                            ft.Text(
                                (
                                    "MS utilizada: "
                                    f"{ingrediente['materia_seca_percentual']:.2f}%"
                                    f" — vigente desde {data_ms}"
                                )
                            ),

                            ft.Text(
                                (
                                    "Quantidade total em MS: "
                                    f"{ingrediente['quantidade_ms_kg']:.2f} kg"
                                )
                            ),

                            ft.Text(
                                (
                                    "Quantidade total para pesar: "
                                    f"{ingrediente['quantidade_mn_kg']:.2f} kg MN"
                                ),
                                weight=ft.FontWeight.BOLD
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

        # --------------------------------------------------
        # Quantidade por carga
        # --------------------------------------------------

        area_resultado.controls.append(
            ft.Text(
                "Carregamento do misturador",
                size=20,
                weight=ft.FontWeight.BOLD
            )
        )

        for numero_carga in range(
            1,
            resultado["numero_cargas"] + 1
        ):

            controles_carga = [
                ft.Text(
                    f"Carga {numero_carga}",
                    size=18,
                    weight=ft.FontWeight.BOLD
                )
            ]

            for ingrediente in ingredientes:

                ordem = (
                    ingrediente[
                        "ordem_carregamento"
                    ]
                    if ingrediente[
                        "ordem_carregamento"
                    ] is not None
                    else "—"
                )

                controles_carga.append(
                    ft.Text(
                        (
                            f"{ordem}. "
                            f"{ingrediente['alimento_nome']}: "
                            f"{ingrediente['quantidade_mn_por_carga_kg']:.2f} kg"
                        )
                    )
                )

            controles_carga.append(
                ft.Divider()
            )

            controles_carga.append(
                ft.Text(
                    (
                        "Peso total da carga: "
                        f"{resultado['quantidade_media_por_carga_kg']:.2f} kg"
                    ),
                    weight=ft.FontWeight.BOLD
                )
            )

            area_resultado.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=controles_carga,
                        spacing=6
                    ),

                    padding=15,

                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT
                    ),

                    border_radius=10
                )
            )

        # --------------------------------------------------
        # Botão salvar
        # --------------------------------------------------

        area_resultado.controls.append(
            ft.Button(
                content="Salvar planejamento",
                icon=ft.Icons.SAVE,
                on_click=salvar_planejamento
            )
        )

        page.update()

    # ======================================================
    # SALVAR PLANEJAMENTO
    # ======================================================

    def salvar_planejamento(e):

        resultado = resultado_atual[
            "dados"
        ]

        if resultado is None:

            mensagem.value = (
                "Realize o cálculo antes de salvar."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        observacoes = (
            campo_observacoes.value
            or ""
        ).strip()

        try:

            trato_id = registrar_trato_planejado(
                resultado_calculo=resultado,
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
            f"{codigo_trato_planejado(trato_id)} "
            "salvo com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        resultado_atual["dados"] = None

        area_resultado.controls.clear()

        campo_observacoes.value = ""

        carregar_planejamentos()

    # ======================================================
    # VISUALIZAR PLANEJAMENTO SALVO
    # ======================================================

    def abrir_planejamento(trato):

        registro = buscar_trato_planejado(
            trato_id=trato["id"],
            fazenda_id=fazenda_atual_id()
        )

        if registro is None:
            return

        itens = listar_itens_trato_planejado(
            trato_id=trato["id"],
            fazenda_id=fazenda_atual_id()
        )

        controles = [
            ft.Text(
                (
                    f"Lote: "
                    f"{registro['lote_nome']}"
                )
            ),

            ft.Text(
                (
                    f"Dieta: "
                    f"{registro['dieta_nome']} "
                    f"— V{registro['dieta_versao']}"
                )
            ),

            ft.Text(
                (
                    f"Misturador: "
                    f"{registro['misturador_nome']}"
                )
            ),

            ft.Text(
                (
                    "Data: "
                    f"{data_banco_para_interface(registro['data_trato'])}"
                )
            ),

            ft.Text(
                (
                    "Animais: "
                    f"{registro['numero_animais']}"
                )
            ),

            ft.Text(
                (
                    "Consumo: "
                    f"{registro['consumo_ms_animal_dia']:.2f} "
                    "kg MS/animal/dia"
                )
            ),

            ft.Text(
                (
                    "Total em MS: "
                    f"{registro['necessidade_ms_lote_kg']:.2f} kg"
                )
            ),

            ft.Text(
                (
                    "Total em MN: "
                    f"{registro['total_materia_natural_kg']:.2f} kg"
                ),
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                (
                    "Número de cargas: "
                    f"{registro['numero_cargas']}"
                ),
                weight=ft.FontWeight.BOLD
            ),

            ft.Divider()
        ]

        for item in itens:

            controles.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                item["alimento_nome"],
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                (
                                    "MS usada: "
                                    f"{item['materia_seca_percentual']:.2f}%"
                                )
                            ),

                            ft.Text(
                                (
                                    "Total: "
                                    f"{item['quantidade_mn_kg']:.2f} kg MN"
                                )
                            ),

                            ft.Text(
                                (
                                    "Por carga: "
                                    f"{item['quantidade_mn_por_carga_kg']:.2f} kg"
                                )
                            )
                        ],
                        spacing=4
                    ),

                    padding=10,

                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT
                    ),

                    border_radius=8
                )
            )

        if registro["observacoes"]:

            controles.append(
                ft.Text(
                    (
                        "Observações: "
                        f"{registro['observacoes']}"
                    )
                )
            )

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                codigo_trato_planejado(
                    registro["id"]
                )
            ),

            content=ft.Column(
                controls=controles,
                spacing=8,
                width=560,
                height=500,
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
    # CANCELAR
    # ======================================================

    def confirmar_cancelamento(trato):

        def executar(e):

            try:

                cancelar_trato_planejado(
                    trato_id=trato["id"],
                    fazenda_id=fazenda_atual_id()
                )

            except ValueError as erro:

                page.pop_dialog()

                mensagem.value = str(erro)

                mensagem.color = ft.Colors.RED

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_trato_planejado(trato['id'])} "
                "cancelado."
            )

            mensagem.color = ft.Colors.ORANGE

            carregar_planejamentos()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Cancelar planejamento?"
            ),

            content=ft.Text(
                (
                    f"{codigo_trato_planejado(trato['id'])}\n\n"
                    "O registro não será excluído. "
                    "Ele permanecerá no histórico "
                    "com status CANCELADO."
                )
            ),

            actions=[
                ft.TextButton(
                    "Voltar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Cancelar planejamento",
                    icon=ft.Icons.CANCEL,
                    on_click=executar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # LISTAR PLANEJAMENTOS
    # ======================================================

    def carregar_planejamentos(e=None):

        lista_planejamentos.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            page.update()
            return

        tratos = (
            listar_tratos_planejados_fazenda(
                fazenda_id
            )
        )

        if not tratos:

            lista_planejamentos.controls.append(
                ft.Text(
                    "Nenhum trato planejado."
                )
            )

            page.update()
            return

        for trato in tratos:

            planejado = (
                trato["status"]
                == "PLANEJADO"
            )

            botoes = [
                ft.Button(
                    content="Visualizar",
                    icon=ft.Icons.VISIBILITY,
                    on_click=lambda e,
                    t=trato:
                    abrir_planejamento(t)
                )
            ]

            if planejado:

                botoes.append(
                    ft.Button(
                        content="Cancelar",
                        icon=ft.Icons.CANCEL,
                        on_click=lambda e,
                        t=trato:
                        confirmar_cancelamento(t)
                    )
                )

            lista_planejamentos.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        codigo_trato_planejado(
                                            trato["id"]
                                        ),
                                        weight=ft.FontWeight.BOLD
                                    ),

                                    ft.Text(
                                        trato["status"],
                                        weight=ft.FontWeight.BOLD,
                                        color=(
                                            ft.Colors.GREEN
                                            if planejado
                                            else ft.Colors.ORANGE
                                        )
                                    )
                                ],

                                alignment=(
                                    ft.MainAxisAlignment
                                    .SPACE_BETWEEN
                                )
                            ),

                            ft.Text(
                                trato["lote_nome"],
                                size=18,
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                (
                                    "Data: "
                                    f"{data_banco_para_interface(trato['data_trato'])}"
                                )
                            ),

                            ft.Text(
                                (
                                    "Dieta: "
                                    f"{trato['dieta_nome']} "
                                    f"— V{trato['dieta_versao']}"
                                )
                            ),

                            ft.Text(
                                (
                                    "Misturador: "
                                    f"{trato['misturador_nome']}"
                                )
                            ),

                            ft.Text(
                                (
                                    "Total: "
                                    f"{trato['total_materia_natural_kg']:.2f} "
                                    "kg MN"
                                )
                            ),

                            ft.Text(
                                (
                                    "Cargas: "
                                    f"{trato['numero_cargas']}"
                                )
                            ),

                            ft.Row(
                                controls=botoes,
                                wrap=True,
                                spacing=10
                            )
                        ],
                        spacing=6
                    ),

                    padding=15,

                    border=ft.Border.all(
                        1,
                        ft.Colors.OUTLINE_VARIANT
                    ),

                    border_radius=10
                )
            )

        page.update()

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    carregar_opcoes()
    carregar_planejamentos()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[
            ft.Text(
                "Tratos",
                size=30,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                (
                    "Fazenda atual: "
                    f"{fazenda_atual_nome()}"
                ),
                size=18,
                weight=ft.FontWeight.BOLD
            ),

            ft.Text(
                "Planeje o fornecimento diário "
                "com base na dieta, consumo, "
                "matéria seca e calibração vigentes."
            ),

            ft.Divider(),

            ft.Text(
                "Novo planejamento",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_lote,

            campo_misturador,

            campo_data,

            ft.Text(
                (
                    "Digite somente os números da data. "
                    "Ex.: 07092026 → 07/09/2026"
                ),
                size=12
            ),

            campo_observacoes,

            ft.Button(
                content="Calcular trato",
                icon=ft.Icons.CALCULATE,
                on_click=calcular
            ),

            mensagem,

            area_resultado,

            ft.Divider(),

            ft.Text(
                "Planejamentos salvos",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            lista_planejamentos
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )