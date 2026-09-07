import flet as ft
from datetime import datetime

from database.models import (
    cadastrar_lote,
    listar_lotes_fazenda,
    listar_lotes_fazenda_todos,
    atualizar_lote,
    encerrar_lote,
    reativar_lote,
    listar_piquetes_fazenda,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
    movimentar_lote_piquete,
    listar_historico_piquetes_lote,
)

from services.sessao import sessao
from services.identificadores import (
    codigo_lote,
    codigo_piquete,
)


def tela_lotes(page: ft.Page):

    # ======================================================
    # CAMPOS
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do lote",
        hint_text="Ex.: Lote Recria 01",
        width=500
    )

    campo_piquete = ft.Dropdown(
        label="Piquete",
        width=500
    )

    campo_numero_animais = ft.TextField(
        label="Número de animais",
        hint_text="Ex.: 100",
        width=500,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    campo_peso_medio = ft.TextField(
        label="Peso médio de entrada (kg)",
        hint_text="Ex.: 320",
        width=500,
        keyboard_type=ft.KeyboardType.NUMBER
    )

    campo_data_entrada = ft.TextField(
        label="Data de entrada",
        hint_text="DD/MM/AAAA",
        width=500,
        max_length=10,
        keyboard_type=ft.KeyboardType.NUMBER,
        on_change=aplicar_mascara_data
    )

    mensagem = ft.Text()

    mostrar_encerrados = ft.Switch(
        label="Mostrar lotes encerrados",
        value=False
    )

    lista_lotes = ft.Column(
        spacing=12
    )

    # ======================================================
    # CONTEXTO DA FAZENDA
    # ======================================================

    def fazenda_atual_id():
        return sessao.fazenda_atual_id

    def fazenda_atual_nome():
        return (
            sessao.fazenda_atual_nome
            or "Nenhuma fazenda selecionada"
        )

    # ======================================================
    # PERMISSÃO
    # ======================================================

    def pode_acessar_fazenda():

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:
            return False

        # ADMIN possui visão administrativa,
        # mas não executa rotina operacional.
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
    # CONVERSÕES / VALIDAÇÕES
    # ======================================================

    def converter_inteiro(valor):

        try:
            numero = int(valor)
            return numero
        except:
            return None

    def converter_decimal(valor):

        if not valor:
            return None

        try:

            valor = valor.replace(",", ".")

            return float(valor)

        except:
            return None

    def aplicar_mascara_data(e):

        somente_numeros = "".join(
            caractere
            for caractere in (e.control.value or "")
            if caractere.isdigit()
        )

        somente_numeros = somente_numeros[:8]

        if len(somente_numeros) <= 2:

            formatado = somente_numeros

        elif len(somente_numeros) <= 4:

            formatado = (
                somente_numeros[:2]
                + "/"
                + somente_numeros[2:]
            )

        else:

            formatado = (
                somente_numeros[:2]
                + "/"
                + somente_numeros[2:4]
                + "/"
                + somente_numeros[4:]
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

    # ======================================================
    # CARREGAR PIQUETES
    # ======================================================

    def carregar_piquetes_dropdown():

        campo_piquete.options.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:
            return

        piquetes = listar_piquetes_fazenda(
            fazenda_id
        )

        for piquete in piquetes:

            campo_piquete.options.append(
                ft.DropdownOption(
                    key=str(
                        piquete["id"]
                    ),
                    text=(
                        f"{codigo_piquete(piquete['id'])} "
                        f"— {piquete['nome']}"
                    )
                )
            )

    # ======================================================
    # LIMPAR FORMULÁRIO
    # ======================================================

    def limpar_campos():

        campo_nome.value = ""
        campo_piquete.value = None
        campo_numero_animais.value = ""
        campo_peso_medio.value = ""
        campo_data_entrada.value = ""

    # ======================================================
    # CADASTRAR LOTE
    # ======================================================

    def salvar_lote(e):

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            mensagem.value = (
                "Selecione uma fazenda."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        if not pode_acessar_fazenda():

            mensagem.value = (
                "Você não possui permissão "
                "para cadastrar lotes nesta fazenda."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        nome = (
            campo_nome.value or ""
        ).strip()

        if not nome:

            mensagem.value = (
                "Informe o nome do lote."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        if campo_piquete.value is None:

            mensagem.value = (
                "Selecione o piquete."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        piquete_id = int(
            campo_piquete.value
        )

        numero_animais = converter_inteiro(
            campo_numero_animais.value
        )

        if (
            numero_animais is None
            or numero_animais <= 0
        ):

            mensagem.value = (
                "Informe um número de animais válido."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        peso_medio = converter_decimal(
            campo_peso_medio.value
        )

        if (
            campo_peso_medio.value
            and (
                peso_medio is None
                or peso_medio <= 0
            )
        ):

            mensagem.value = (
                "Informe um peso médio válido."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        data_entrada_texto = (
            campo_data_entrada.value or ""
        ).strip()

        if not data_entrada_texto:

            mensagem.value = (
                "Informe a data de entrada do lote."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        data_entrada = data_interface_para_banco(
            data_entrada_texto
        )

        if data_entrada is None:

            mensagem.value = (
                "Informe uma data válida "
                "no formato DD/MM/AAAA."
            )
            mensagem.color = ft.Colors.RED

            page.update()
            return

        try:

            lote_id = cadastrar_lote(
                fazenda_id=fazenda_id,
                piquete_id=piquete_id,
                nome=nome,
                numero_animais=numero_animais,
                peso_medio_entrada=peso_medio,
                data_entrada=(
                    data_entrada
                    if data_entrada
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
            f"{codigo_lote(lote_id)} "
            "cadastrado com sucesso."
        )

        mensagem.color = ft.Colors.GREEN

        carregar_lotes()

    # ======================================================
    # EDITAR LOTE
    # ======================================================

    def abrir_edicao(lote):

        if not pode_acessar_fazenda():
            return

        if (
            lote["fazenda_id"]
            != fazenda_atual_id()
        ):
            return

        piquetes = listar_piquetes_fazenda(
            fazenda_atual_id()
        )

        editar_nome = ft.TextField(
            label="Nome do lote",
            value=lote["nome"],
            width=450
        )


        editar_numero_animais = ft.TextField(
            label="Número de animais",
            value=str(
                lote["numero_animais"]
            ),
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        editar_peso = ft.TextField(
            label="Peso médio de entrada (kg)",
            value=(
                str(lote["peso_medio_entrada"])
                if lote["peso_medio_entrada"]
                is not None
                else ""
            ),
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        editar_data = ft.TextField(
            label="Data de entrada",
            value=data_banco_para_interface(
                lote["data_entrada"]
            ),
            hint_text="DD/MM/AAAA",
            width=450,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        editar_data.on_change = aplicar_mascara_data

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
                editar_nome.value or ""
            ).strip()

            if not nome:

                mensagem_edicao.value = (
                    "Informe o nome do lote."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if editar_piquete.value is None:

                mensagem_edicao.value = (
                    "Selecione um piquete."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            numero_animais = converter_inteiro(
                editar_numero_animais.value
            )

            if (
                numero_animais is None
                or numero_animais <= 0
            ):

                mensagem_edicao.value = (
                    "Número de animais inválido."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            peso = converter_decimal(
                editar_peso.value
            )

            if (
                editar_peso.value
                and (
                    peso is None
                    or peso <= 0
                )
            ):

                mensagem_edicao.value = (
                    "Peso médio inválido."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            data = (
                editar_data.value or ""
            ).strip()

            if not data_valida(data):

                mensagem_edicao.value = (
                    "Data inválida. "
                    "Utilize AAAA-MM-DD."
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            try:

                atualizar_lote(
                    lote_id=lote["id"],
                    fazenda_id=(
                        fazenda_atual_id()
                    ),
                    nome=nome,
                    numero_animais=numero_animais,
                    peso_medio_entrada=peso,
                    data_entrada=(
                        data
                        if data
                        else None
                    )
                )

            except ValueError as erro:

                mensagem_edicao.value = str(
                    erro
                )
                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_lote(lote['id'])} "
                "atualizado com sucesso."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_lotes()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Editar "
                f"{codigo_lote(lote['id'])}"
            ),

            content=ft.Column(
                controls=[
                    editar_nome,                   
                    editar_numero_animais,
                    editar_peso,
                    editar_data,
                    mensagem_edicao
                ],
                tight=True,
                spacing=12,
                scroll=ft.ScrollMode.AUTO
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
    # MOVIMENTAR LOTE ENTRE PIQUETES
    # ======================================================

    def abrir_movimentacao(lote):

        if not pode_acessar_fazenda():
            return

        piquetes = listar_piquetes_fazenda(
            fazenda_atual_id()
        )

        novo_piquete = ft.Dropdown(
            label="Novo piquete",
            width=450
        )

        for piquete in piquetes:

            if piquete["id"] != lote["piquete_id"]:

                novo_piquete.options.append(
                    ft.DropdownOption(
                        key=str(piquete["id"]),
                        text=(
                            f"{codigo_piquete(piquete['id'])} "
                            f"— {piquete['nome']}"
                        )
                    )
                )

        campo_data_movimentacao = ft.TextField(
            label="Data da movimentação",
            hint_text="DD/MM/AAAA",
            width=450,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        campo_data_movimentacao.on_change = (
            aplicar_mascara_data
        )

        mensagem_movimentacao = ft.Text()

        def confirmar(e):

            if novo_piquete.value is None:

                mensagem_movimentacao.value = (
                    "Selecione o novo piquete."
                )
                mensagem_movimentacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            data_texto = (
                campo_data_movimentacao.value or ""
            ).strip()

            data_banco = (
                data_interface_para_banco(
                    data_texto
                )
            )

            if data_banco is None:

                mensagem_movimentacao.value = (
                    "Informe uma data válida "
                    "no formato DD/MM/AAAA."
                )
                mensagem_movimentacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            try:

                movimentar_lote_piquete(
                    lote_id=lote["id"],
                    fazenda_id=fazenda_atual_id(),
                    novo_piquete_id=int(
                        novo_piquete.value
                    ),
                    data_movimentacao=data_banco
                )

            except ValueError as erro:

                mensagem_movimentacao.value = (
                    str(erro)
                )
                mensagem_movimentacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_lote(lote['id'])} "
                "movimentado com sucesso."
            )
            mensagem.color = ft.Colors.GREEN

            carregar_lotes()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Movimentar lote"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{codigo_lote(lote['id'])} "
                        f"— {lote['nome']}"
                    ),

                    ft.Text(
                        f"Piquete atual: "
                        f"{lote['piquete_nome']}"
                    ),

                    novo_piquete,

                    campo_data_movimentacao,

                    mensagem_movimentacao
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
                    content="Confirmar movimentação",
                    icon=ft.Icons.SWAP_HORIZ,
                    on_click=confirmar
                )
            ]
        )

        page.show_dialog(dialogo)
        # ======================================================
    # HISTÓRICO DE PIQUETES DO LOTE
    # ======================================================

    def abrir_historico_piquetes(lote):

        historico = (
            listar_historico_piquetes_lote(
                lote["id"]
            )
        )

        itens = []

        if not historico:

            itens.append(
                ft.Text(
                    "Nenhum histórico encontrado."
                )
            )

        else:

            for registro in historico:

                inicio = data_banco_para_interface(
                    registro["data_inicio"]
                )

                fim = (
                    data_banco_para_interface(
                        registro["data_fim"]
                    )
                    if registro["data_fim"]
                    else "Atual"
                )

                itens.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    registro["piquete_nome"],
                                    weight=(
                                        ft.FontWeight.BOLD
                                    )
                                ),

                                ft.Text(
                                    f"{inicio} → {fim}"
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

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                f"Histórico — "
                f"{codigo_lote(lote['id'])}"
            ),

            content=ft.Column(
                controls=itens,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                height=400,
                width=500
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
    # ENCERRAR LOTE
    # ======================================================

    def abrir_encerramento(lote):

        campo_data_saida = ft.TextField(
            label="Data de saída",
            hint_text="AAAA-MM-DD",
            width=400
        )

        mensagem_saida = ft.Text()

        def confirmar(e):

            if not pode_acessar_fazenda():
                return

            if (
                lote["fazenda_id"]
                != fazenda_atual_id()
            ):
                return

            data_saida = (
                campo_data_saida.value or ""
            ).strip()

            if not data_saida:

                mensagem_saida.value = (
                    "Informe a data de saída."
                )
                mensagem_saida.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if not data_valida(data_saida):

                mensagem_saida.value = (
                    "Utilize o formato AAAA-MM-DD."
                )
                mensagem_saida.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            # Impede saída anterior à entrada
            if lote["data_entrada"]:

                data_inicio = datetime.strptime(
                    lote["data_entrada"],
                    "%Y-%m-%d"
                )

                data_fim = datetime.strptime(
                    data_saida,
                    "%Y-%m-%d"
                )

                if data_fim < data_inicio:

                    mensagem_saida.value = (
                        "A data de saída não pode "
                        "ser anterior à data de entrada."
                    )

                    mensagem_saida.color = (
                        ft.Colors.RED
                    )

                    page.update()
                    return

            encerrar_lote(
                lote_id=lote["id"],
                fazenda_id=fazenda_atual_id(),
                data_saida=data_saida
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_lote(lote['id'])} "
                "encerrado com sucesso."
            )

            mensagem.color = ft.Colors.ORANGE

            carregar_lotes()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Encerrar lote"
            ),

            content=ft.Column(
                controls=[
                    ft.Text(
                        f"{codigo_lote(lote['id'])} "
                        f"— {lote['nome']}"
                    ),

                    ft.Text(
                        "O lote será encerrado, "
                        "mas todo o histórico será preservado."
                    ),

                    campo_data_saida,

                    mensagem_saida
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
                    content="Encerrar lote",
                    icon=ft.Icons.CHECK_CIRCLE,
                    on_click=confirmar
                )
            ]
        )

        page.show_dialog(dialogo)

    # ======================================================
    # REATIVAR LOTE
    # ======================================================

    def confirmar_reativacao(lote):

        def executar(e):

            if not pode_acessar_fazenda():
                return

            if (
                lote["fazenda_id"]
                != fazenda_atual_id()
            ):
                return

            reativar_lote(
                lote_id=lote["id"],
                fazenda_id=fazenda_atual_id()
            )

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_lote(lote['id'])} "
                "reativado."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_lotes()

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar lote?"
            ),

            content=ft.Text(
                f"{codigo_lote(lote['id'])} "
                f"— {lote['nome']}"
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

    def carregar_lotes(e=None):

        lista_lotes.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            lista_lotes.controls.append(
                ft.Text(
                    "Selecione uma fazenda."
                )
            )

            page.update()
            return

        if not pode_acessar_fazenda():

            lista_lotes.controls.append(
                ft.Text(
                    "Você não possui acesso "
                    "operacional a esta fazenda.",
                    color=ft.Colors.RED
                )
            )

            page.update()
            return

        if mostrar_encerrados.value:

            lotes = (
                listar_lotes_fazenda_todos(
                    fazenda_id
                )
            )

        else:

            lotes = listar_lotes_fazenda(
                fazenda_id
            )

        if not lotes:

            lista_lotes.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Nenhum lote cadastrado "
                        "nesta fazenda."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        for lote in lotes:

            ativo = (
                lote["status"] == "ATIVO"
            )

            piquete_texto = (
                lote["piquete_nome"]
                or "Não informado"
            )

            peso_texto = (
                f"{lote['peso_medio_entrada']:.2f} kg"
                if lote["peso_medio_entrada"]
                is not None
                else "Não informado"
            )

            entrada_texto = (
                data_banco_para_interface(
                    lote["data_entrada"]
                )
                if lote["data_entrada"]
                else "Não informada"
            )
            data_banco_para_interface(
                lote["data_saida"]
            )
            botoes = []

            if ativo:

                botoes.extend([
                    ft.Button(
                        content="Editar",
                        icon=ft.Icons.EDIT,
                        on_click=lambda e,
                        l=lote:
                        abrir_edicao(l)
                    ),

                    ft.Button(
                        content="Movimentar",
                        icon=ft.Icons.SWAP_HORIZ,
                        on_click=lambda e,
                        l=lote:
                        abrir_movimentacao(l)
                    ),

                    ft.Button(
                        content="Histórico",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda e,
                        l=lote:
                        abrir_historico_piquetes(l)
                    ),

                    ft.Button(
                        content="Encerrar",
                        icon=ft.Icons.CHECK_CIRCLE,
                        on_click=lambda e,
                        l=lote:
                        abrir_encerramento(l)
                    )
                ])

            else:

                botoes.append(
                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        l=lote:
                        confirmar_reativacao(l)
                    )
                )

            controles = [
                ft.Row(
                    controls=[
                        ft.Text(
                            codigo_lote(
                                lote["id"]
                            ),
                            size=13,
                            weight=(
                                ft.FontWeight.BOLD
                            )
                        ),

                        ft.Text(
                            lote["status"],
                            color=(
                                ft.Colors.GREEN
                                if ativo
                                else ft.Colors.ORANGE
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
                    lote["nome"],
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    f"Piquete: {piquete_texto}"
                ),

                ft.Text(
                    f"Animais: "
                    f"{lote['numero_animais']}"
                ),

                ft.Text(
                    f"Peso médio de entrada: "
                    f"{peso_texto}"
                ),

                ft.Text(
                    f"Data de entrada: "
                    f"{entrada_texto}"
                ),
            ]

            if not ativo:

                controles.append(
                    ft.Text(
                        f"Data de saída: "
                        f"{lote['data_saida'] or 'Não informada'}"
                    )
                )

            controles.append(
                ft.Row(
                    controls=botoes,
                    spacing=10
                )
            )

            lista_lotes.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=controles,
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

    mostrar_encerrados.on_change = (
        carregar_lotes
    )

    carregar_piquetes_dropdown()
    carregar_lotes()

    # ======================================================
    # INTERFACE
    # ======================================================

    return ft.Column(
        controls=[
            ft.Text(
                "Lotes",
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
                "Cadastre os grupos de animais "
                "e associe cada lote ao seu piquete atual."
            ),

            ft.Divider(),

            # ==============================================
            # CADASTRO
            # ==============================================

            ft.Text(
                "Novo lote",
                size=20,
                weight=ft.FontWeight.BOLD
            ),

            campo_nome,

            campo_piquete,

            campo_numero_animais,

            campo_peso_medio,

            campo_data_entrada,

            ft.Button(
                content="Cadastrar lote",
                icon=ft.Icons.ADD,
                on_click=salvar_lote
            ),

            mensagem,

            ft.Divider(),

            # ==============================================
            # LISTAGEM
            # ==============================================

            ft.Row(
                controls=[
                    ft.Text(
                        "Lotes cadastrados",
                        size=20,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Container(
                        expand=True
                    ),

                    mostrar_encerrados
                ]
            ),

            lista_lotes
        ],

        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )