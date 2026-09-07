from datetime import datetime

import flet as ft

from database.models import (
    listar_lotes_fazenda,
    registrar_leitura_cocho,
    listar_leituras_cocho_lote,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
)

from services.calculos import (
    calcular_quantidade_padrao_lote,
    calcular_ajuste_cocho,
)

from services.identificadores import (
    codigo_lote,
    codigo_leitura_cocho,
)

from services.sessao import sessao


def tela_cocho(page: ft.Page):

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
        )[:8]

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

        try:

            return datetime.strptime(
                valor,
                "%d/%m/%Y"
            ).strftime(
                "%Y-%m-%d"
            )

        except (TypeError, ValueError):

            return None

    def data_banco_para_interface(valor):

        try:

            return datetime.strptime(
                valor,
                "%Y-%m-%d"
            ).strftime(
                "%d/%m/%Y"
            )

        except (TypeError, ValueError):

            return valor or "—"

    # ======================================================
    # CAMPOS
    # ======================================================

    campo_lote = ft.Dropdown(
        label="Lote",
        width=500
    )

    campo_data = ft.TextField(
        label="Data da leitura",
        hint_text="DD/MM/AAAA",
        width=500,
        max_length=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=aplicar_mascara_data
    )

    campo_observacoes = ft.TextField(
        label="Observações",
        width=500,
        multiline=True,
        min_lines=2,
        max_lines=4
    )

    mensagem = ft.Text()

    area_resultado = ft.Column(
        spacing=10
    )

    area_historico = ft.Column(
        spacing=10
    )

    leitura_atual = {
        "nota": None,
        "padrao": None,
        "ajuste": None,
    }

    # ======================================================
    # LOTES
    # ======================================================

    def carregar_lotes():

        campo_lote.options.clear()

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

    # ======================================================
    # SELECIONAR NOTA
    # ======================================================

    def selecionar_nota(nota):

        if campo_lote.value is None:

            mensagem.value = (
                "Selecione um lote."
            )

            mensagem.color = ft.Colors.RED
            page.update()
            return

        data_banco = (
            data_interface_para_banco(
                campo_data.value
            )
        )

        if data_banco is None:

            mensagem.value = (
                "Informe uma data válida."
            )

            mensagem.color = ft.Colors.RED
            page.update()
            return

        try:

            padrao = (
                calcular_quantidade_padrao_lote(
                    fazenda_id=fazenda_atual_id(),
                    lote_id=int(
                        campo_lote.value
                    ),
                    data_referencia=data_banco
                )
            )

            ajuste = calcular_ajuste_cocho(
                quantidade_padrao_mn_kg=(
                    padrao[
                        "quantidade_padrao_mn_kg"
                    ]
                ),
                nota=nota
            )

        except ValueError as erro:

            mensagem.value = str(erro)
            mensagem.color = ft.Colors.RED

            page.update()
            return

        leitura_atual["nota"] = nota
        leitura_atual["padrao"] = padrao
        leitura_atual["ajuste"] = ajuste

        montar_resultado()

    # ======================================================
    # RESULTADO
    # ======================================================

    def montar_resultado():

        area_resultado.controls.clear()

        padrao = leitura_atual["padrao"]
        ajuste = leitura_atual["ajuste"]

        if padrao is None:
            page.update()
            return

        percentual = ajuste[
            "ajuste_percentual"
        ]

        area_resultado.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            (
                                f"{padrao['dieta_nome']} "
                                f"— V{padrao['dieta_versao']}"
                            ),
                            size=18,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            (
                                f"Animais: "
                                f"{padrao['numero_animais']}"
                            )
                        ),

                        ft.Text(
                            (
                                "Consumo padrão: "
                                f"{padrao['consumo_ms_animal_dia']:.2f} "
                                "kg MS/animal/dia"
                            )
                        ),

                        ft.Divider(),

                        ft.Text(
                            (
                                "Quantidade padrão: "
                                f"{ajuste['quantidade_padrao_mn_kg']:.2f} "
                                "kg MN/dia"
                            )
                        ),

                        ft.Text(
                            (
                                f"Nota de cocho: "
                                f"{ajuste['nota']:+d}"
                            ),
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Text(
                            (
                                f"Ajuste: "
                                f"{percentual:+.0f}%"
                            )
                        ),

                        ft.Text(
                            (
                                "Quantidade recomendada: "
                                f"{ajuste['quantidade_recomendada_mn_kg']:.2f} "
                                "kg MN/dia"
                            ),
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),

                        ft.Button(
                            content="Salvar leitura",
                            icon=ft.Icons.SAVE,
                            on_click=salvar_leitura
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

        mensagem.value = (
            "Recomendação calculada."
        )

        mensagem.color = ft.Colors.GREEN

        page.update()

    # ======================================================
    # SALVAR
    # ======================================================

    def salvar_leitura(e):

        if leitura_atual["ajuste"] is None:
            return

        data_banco = (
            data_interface_para_banco(
                campo_data.value
            )
        )

        ajuste = leitura_atual["ajuste"]

        observacoes = (
            campo_observacoes.value
            or ""
        ).strip()

        try:

            leitura_id = registrar_leitura_cocho(
                fazenda_id=fazenda_atual_id(),
                lote_id=int(
                    campo_lote.value
                ),
                usuario_id=sessao.usuario_id,
                data_leitura=data_banco,

                nota=ajuste["nota"],

                ajuste_percentual=(
                    ajuste["ajuste_percentual"]
                ),

                quantidade_padrao_mn_kg=(
                    ajuste[
                        "quantidade_padrao_mn_kg"
                    ]
                ),

                quantidade_recomendada_mn_kg=(
                    ajuste[
                        "quantidade_recomendada_mn_kg"
                    ]
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

        mensagem.value = (
            f"{codigo_leitura_cocho(leitura_id)} "
            "salva com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        leitura_atual["nota"] = None
        leitura_atual["padrao"] = None
        leitura_atual["ajuste"] = None

        area_resultado.controls.clear()

        campo_observacoes.value = ""

        carregar_historico()

    # ======================================================
    # HISTÓRICO
    # ======================================================

    def carregar_historico(e=None):

        area_historico.controls.clear()

        if campo_lote.value is None:

            area_historico.controls.append(
                ft.Text(
                    "Selecione um lote para visualizar "
                    "o histórico."
                )
            )

            page.update()
            return

        historico = (
            listar_leituras_cocho_lote(
                lote_id=int(
                    campo_lote.value
                ),
                fazenda_id=fazenda_atual_id()
            )
        )

        if not historico:

            area_historico.controls.append(
                ft.Text(
                    "Nenhuma leitura registrada."
                )
            )

        for leitura in historico:

            area_historico.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        codigo_leitura_cocho(
                                            leitura["id"]
                                        ),
                                        weight=ft.FontWeight.BOLD
                                    ),

                                    ft.Text(
                                        (
                                            f"Nota "
                                            f"{leitura['nota']:+d}"
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
                                (
                                    "Data: "
                                    f"{data_banco_para_interface(leitura['data_leitura'])}"
                                )
                            ),

                            ft.Text(
                                (
                                    "Ajuste aplicado: "
                                    f"{leitura['ajuste_percentual']:+.0f}%"
                                )
                            ),

                            ft.Text(
                                (
                                    "Padrão: "
                                    f"{leitura['quantidade_padrao_mn_kg']:.2f} "
                                    "kg MN"
                                )
                            ),

                            ft.Text(
                                (
                                    "Recomendado: "
                                    f"{leitura['quantidade_recomendada_mn_kg']:.2f} "
                                    "kg MN"
                                ),
                                weight=ft.FontWeight.BOLD
                            ),

                            ft.Text(
                                (
                                    f"Registrado por: "
                                    f"{leitura['usuario_nome']}"
                                )
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

        page.update()

    campo_lote.on_change = carregar_historico

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

    carregar_lotes()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[
            ft.Text(
                "Leitura de Cocho",
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

            ft.Divider(),

            campo_lote,

            campo_data,

            ft.Text(
                "Selecione a nota do cocho:",
                size=18,
                weight=ft.FontWeight.BOLD
            ),

            ft.Row(
                controls=[
                    ft.Button(
                        content="-2",
                        on_click=lambda e:
                        selecionar_nota(-2)
                    ),

                    ft.Button(
                        content="-1",
                        on_click=lambda e:
                        selecionar_nota(-1)
                    ),

                    ft.Button(
                        content="0",
                        on_click=lambda e:
                        selecionar_nota(0)
                    ),

                    ft.Button(
                        content="+1",
                        on_click=lambda e:
                        selecionar_nota(1)
                    ),

                    ft.Button(
                        content="+2",
                        on_click=lambda e:
                        selecionar_nota(2)
                    ),
                ],
                spacing=10,
                wrap=True
            ),

            ft.Text(
                (
                    "-2 = +20% | "
                    "-1 = +10% | "
                    "0 = manter | "
                    "+1 = -10% | "
                    "+2 = -20%"
                )
            ),

            campo_observacoes,

            mensagem,

            area_resultado,

            ft.Divider(),

            ft.Text(
                "Histórico do lote",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            area_historico
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )