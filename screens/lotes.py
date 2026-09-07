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
    movimentar_lote_piquete,
    listar_historico_piquetes_lote,
    consultor_tem_acesso_fazenda,
    usuario_tem_acesso_fazenda,
        definir_consumo_lote,
    buscar_consumo_atual_lote,
    listar_historico_consumo_lote,
    listar_dietas_fazenda,
)

from services.sessao import sessao

from services.identificadores import (
    codigo_lote,
    codigo_piquete,
)


def tela_lotes(page: ft.Page):

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

        # ADMIN possui visão administrativa,
        # mas não executa a rotina operacional.
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

    def converter_inteiro(valor):

        try:
            return int(valor)

        except (TypeError, ValueError):
            return None

    def converter_decimal(valor):

        if valor is None:
            return None

        valor = str(valor).strip()

        if not valor:
            return None

        try:

            valor = valor.replace(",", ".")

            return float(valor)

        except ValueError:
            return None

    # ======================================================
    # DATAS
    # Interface: DD/MM/AAAA
    # Banco:     AAAA-MM-DD
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

        if valor is None:
            return ""

        valor = str(valor).strip()

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

            # Evita quebrar a interface caso
            # exista algum dado antigo inesperado.
            return valor

    # ======================================================
    # CAMPOS DO CADASTRO
    # ======================================================

    campo_nome = ft.TextField(
        label="Nome do lote",
        hint_text="Ex.: Lote Recria 01",
        width=500
    )

    campo_piquete = ft.Dropdown(
        label="Piquete inicial",
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
    # PIQUETES DISPONÍVEIS
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
                    key=str(piquete["id"]),
                    text=(
                        f"{codigo_piquete(piquete['id'])}"
                        f" — {piquete['nome']}"
                    )
                )
            )

    # ======================================================
    # LIMPAR CADASTRO
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
                "Selecione uma fazenda antes "
                "de cadastrar o lote."
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
                "Informe o nome do lote."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        if campo_piquete.value is None:

            mensagem.value = (
                "Selecione o piquete inicial."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

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

        data_entrada = (
            data_interface_para_banco(
                campo_data_entrada.value
            )
        )

        if data_entrada is None:

            mensagem.value = (
                "Informe uma data de entrada válida "
                "no formato DD/MM/AAAA."
            )

            mensagem.color = ft.Colors.RED

            page.update()
            return

        try:

            lote_id = cadastrar_lote(
                fazenda_id=fazenda_id,
                piquete_id=int(
                    campo_piquete.value
                ),
                nome=nome,
                numero_animais=numero_animais,
                peso_medio_entrada=peso_medio,
                data_entrada=data_entrada
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
    # EDITAR DADOS DO LOTE
    #
    # IMPORTANTE:
    # O piquete NÃO é alterado aqui.
    # Para isso existe a função Movimentar.
    # ======================================================

    def abrir_edicao(lote):

        if not pode_acessar_fazenda():
            return

        if lote["fazenda_id"] != fazenda_atual_id():
            return

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
                str(
                    lote["peso_medio_entrada"]
                )
                if lote["peso_medio_entrada"]
                is not None
                else ""
            ),
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        # Mantemos a data original protegida.
        # Alterá-la exigiria atualizar também
        # o primeiro registro histórico.
        editar_data_entrada = ft.TextField(
            label="Data de entrada",
            value=data_banco_para_interface(
                lote["data_entrada"]
            ),
            width=450,
            read_only=True
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
                    "Informe o nome do lote."
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
                    "Informe um número de animais válido."
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
                    "Informe um peso médio válido."
                )

                mensagem_edicao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            atualizar_lote(
                lote_id=lote["id"],
                fazenda_id=fazenda_atual_id(),
                nome=nome,
                numero_animais=numero_animais,
                peso_medio_entrada=peso,
                data_entrada=lote["data_entrada"]
            )

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
                f"Editar {codigo_lote(lote['id'])}"
            ),

            content=ft.Column(
                controls=[
                    editar_nome,
                    editar_numero_animais,
                    editar_peso,
                    editar_data_entrada,
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
    # MOVIMENTAR LOTE
    # ======================================================

    def abrir_movimentacao(lote):

        if not pode_acessar_fazenda():
            return

        if lote["fazenda_id"] != fazenda_atual_id():
            return

        piquetes = listar_piquetes_fazenda(
            fazenda_atual_id()
        )

        novo_piquete = ft.Dropdown(
            label="Novo piquete",
            width=450
        )

        for piquete in piquetes:

            # Não mostra o próprio piquete atual
            if piquete["id"] == lote["piquete_id"]:
                continue

            novo_piquete.options.append(
                ft.DropdownOption(
                    key=str(piquete["id"]),
                    text=(
                        f"{codigo_piquete(piquete['id'])}"
                        f" — {piquete['nome']}"
                    )
                )
            )

        campo_data_movimentacao = ft.TextField(
            label="Data da movimentação",
            hint_text="DD/MM/AAAA",
            width=450,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=aplicar_mascara_data
        )

        mensagem_movimentacao = ft.Text()

        def confirmar_movimentacao(e):

            if novo_piquete.value is None:

                mensagem_movimentacao.value = (
                    "Selecione o novo piquete."
                )

                mensagem_movimentacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            data_movimentacao = (
                data_interface_para_banco(
                    campo_data_movimentacao.value
                )
            )

            if data_movimentacao is None:

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
                    data_movimentacao=(
                        data_movimentacao
                    )
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

        if not novo_piquete.options:

            conteudo = ft.Column(
                controls=[
                    ft.Text(
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}"
                    ),

                    ft.Text(
                        f"Piquete atual: "
                        f"{lote['piquete_nome']}"
                    ),

                    ft.Text(
                        "Não existem outros piquetes "
                        "ativos disponíveis nesta fazenda."
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
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}"
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
            )

            acoes = [
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),

                ft.Button(
                    content="Confirmar movimentação",
                    icon=ft.Icons.SWAP_HORIZ,
                    on_click=confirmar_movimentacao
                )
            ]

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Movimentar lote"
            ),

            content=conteudo,

            actions=acoes,

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

    # ======================================================
    # HISTÓRICO DE PIQUETES
    # ======================================================

    def abrir_historico_piquetes(lote):

        if lote["fazenda_id"] != fazenda_atual_id():
            return

        historico = (
            listar_historico_piquetes_lote(
                lote["id"]
            )
        )

        itens = []

        if not historico:

            itens.append(
                ft.Text(
                    "Nenhum histórico de localização "
                    "foi encontrado para este lote."
                )
            )

        else:

            # A consulta vem do mais recente
            # para o mais antigo.
            # Para leitura, mostramos cronologicamente.
            for registro in reversed(
                historico
            ):

                inicio = (
                    data_banco_para_interface(
                        registro["data_inicio"]
                    )
                )

                if registro["data_fim"]:

                    fim = (
                        data_banco_para_interface(
                            registro["data_fim"]
                        )
                    )

                else:

                    fim = "Atual"

                identificacao = (
                    registro[
                        "piquete_identificacao"
                    ]
                    or "Sem identificação adicional"
                )

                itens.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    (
                                        f"{codigo_piquete(registro['piquete_id'])}"
                                        f" — {registro['piquete_nome']}"
                                    ),
                                    weight=(
                                        ft.FontWeight.BOLD
                                    )
                                ),

                                ft.Text(
                                    f"Identificação: "
                                    f"{identificacao}"
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
                f"Histórico de localização — "
                f"{codigo_lote(lote['id'])}"
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
    # ENCERRAR LOTE
    # ======================================================

    def abrir_encerramento(lote):

        if lote["fazenda_id"] != fazenda_atual_id():
            return

        campo_data_saida = ft.TextField(
            label="Data de saída",
            hint_text="DD/MM/AAAA",
            width=420,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=aplicar_mascara_data
        )

        mensagem_saida = ft.Text()

        def confirmar_encerramento(e):

            if not pode_acessar_fazenda():
                return

            data_saida = (
                data_interface_para_banco(
                    campo_data_saida.value
                )
            )

            if data_saida is None:

                mensagem_saida.value = (
                    "Informe uma data de saída válida "
                    "no formato DD/MM/AAAA."
                )

                mensagem_saida.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if lote["data_entrada"]:

                if data_saida < lote["data_entrada"]:

                    mensagem_saida.value = (
                        "A data de saída não pode ser "
                        "anterior à data de entrada."
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
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}"
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
                    on_click=confirmar_encerramento
                )
            ],

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)

        # ======================================================
    # REATIVAR LOTE
    # ======================================================

    def confirmar_reativacao(lote):

        if lote["fazenda_id"] != fazenda_atual_id():
            return

        if not pode_acessar_fazenda():
            return

        piquetes = listar_piquetes_fazenda(
            fazenda_atual_id()
        )

        campo_piquete_retorno = ft.Dropdown(
            label="Piquete de retorno",
            width=450
        )

        for piquete in piquetes:

            campo_piquete_retorno.options.append(
                ft.DropdownOption(
                    key=str(
                        piquete["id"]
                    ),
                    text=(
                        f"{codigo_piquete(piquete['id'])}"
                        f" — {piquete['nome']}"
                    )
                )
            )

        campo_data_retorno = ft.TextField(
            label="Data de retorno",
            hint_text="DD/MM/AAAA",
            width=450,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=aplicar_mascara_data
        )

        mensagem_reativacao = ft.Text()

        def executar(e):

            if not pode_acessar_fazenda():

                mensagem_reativacao.value = (
                    "Acesso não autorizado."
                )

                mensagem_reativacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            if campo_piquete_retorno.value is None:

                mensagem_reativacao.value = (
                    "Selecione o piquete de retorno."
                )

                mensagem_reativacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            data_retorno = (
                data_interface_para_banco(
                    campo_data_retorno.value
                )
            )

            if data_retorno is None:

                mensagem_reativacao.value = (
                    "Informe uma data válida "
                    "no formato DD/MM/AAAA."
                )

                mensagem_reativacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            try:

                reativar_lote(
                    lote_id=lote["id"],
                    fazenda_id=fazenda_atual_id(),
                    piquete_id=int(
                        campo_piquete_retorno.value
                    ),
                    data_retorno=data_retorno
                )

            except ValueError as erro:

                mensagem_reativacao.value = (
                    str(erro)
                )

                mensagem_reativacao.color = (
                    ft.Colors.RED
                )

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"{codigo_lote(lote['id'])} "
                "reativado com sucesso."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_lotes()

        if not campo_piquete_retorno.options:

            conteudo = ft.Column(
                controls=[
                    ft.Text(
                        "Não existem piquetes ativos "
                        "disponíveis nesta fazenda."
                    )
                ],
                tight=True
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
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}"
                    ),

                    ft.Text(
                        f"Última saída: "
                        f"{data_banco_para_interface(lote['data_saida'])}"
                    ),

                    ft.Text(
                        "Informe onde e quando este lote "
                        "voltará à atividade."
                    ),

                    campo_piquete_retorno,

                    campo_data_retorno,

                    mensagem_reativacao
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
                    content="Reativar lote",
                    icon=ft.Icons.REFRESH,
                    on_click=executar
                )
            ]

        dialogo = ft.AlertDialog(
            modal=True,

            title=ft.Text(
                "Reativar lote"
            ),

            content=conteudo,

            actions=acoes,

            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)
        # ======================================================
    # DEFINIR DIETA E CONSUMO DO LOTE
    # ======================================================

    def abrir_definicao_consumo(lote):

        if not pode_acessar_fazenda():
            return

        if lote["fazenda_id"] != fazenda_atual_id():
            return

        dietas = listar_dietas_fazenda(
            fazenda_id=fazenda_atual_id(),
            incluir_arquivadas=False
        )

        campo_dieta = ft.Dropdown(
            label="Dieta",
            width=450
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

        campo_consumo = ft.TextField(
            label="Consumo de MS (kg/animal/dia)",
            hint_text="Ex.: 8,5",
            width=450,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        campo_data = ft.TextField(
            label="Início da vigência",
            hint_text="DD/MM/AAAA",
            width=450,
            max_length=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=aplicar_mascara_data
        )

        texto_calculo = ft.Text(
            "Necessidade do lote: —"
        )

        mensagem_consumo = ft.Text()

        # --------------------------------------------------
        # Mostra cálculo imediatamente
        # --------------------------------------------------

        def atualizar_previa(e=None):

            consumo = converter_decimal(
                campo_consumo.value
            )

            if (
                consumo is None
                or consumo <= 0
            ):

                texto_calculo.value = (
                    "Necessidade do lote: —"
                )

            else:

                consumo_lote = (
                    consumo
                    * lote["numero_animais"]
                )

                texto_calculo.value = (
                    f"Necessidade do lote: "
                    f"{consumo_lote:.2f} kg MS/dia"
                )

            page.update()

        campo_consumo.on_change = atualizar_previa

        # --------------------------------------------------
        # Salvar
        # --------------------------------------------------

        def confirmar(e):

            if campo_dieta.value is None:

                mensagem_consumo.value = (
                    "Selecione uma dieta."
                )
                mensagem_consumo.color = ft.Colors.RED

                page.update()
                return

            consumo = converter_decimal(
                campo_consumo.value
            )

            if (
                consumo is None
                or consumo <= 0
            ):

                mensagem_consumo.value = (
                    "Informe um consumo válido "
                    "em kg MS/animal/dia."
                )

                mensagem_consumo.color = ft.Colors.RED

                page.update()
                return

            data_inicio = (
                data_interface_para_banco(
                    campo_data.value
                )
            )

            if data_inicio is None:

                mensagem_consumo.value = (
                    "Informe uma data válida "
                    "no formato DD/MM/AAAA."
                )

                mensagem_consumo.color = ft.Colors.RED

                page.update()
                return

            try:

                definir_consumo_lote(
                    fazenda_id=fazenda_atual_id(),
                    lote_id=lote["id"],
                    dieta_id=int(
                        campo_dieta.value
                    ),
                    consumo_ms_animal_dia=consumo,
                    data_inicio=data_inicio
                )

            except ValueError as erro:

                mensagem_consumo.value = str(erro)
                mensagem_consumo.color = ft.Colors.RED

                page.update()
                return

            page.pop_dialog()

            mensagem.value = (
                f"Consumo de {codigo_lote(lote['id'])} "
                "atualizado com sucesso."
            )

            mensagem.color = ft.Colors.GREEN

            carregar_lotes()

        # --------------------------------------------------
        # Caso não exista dieta
        # --------------------------------------------------

        if not dietas:

            conteudo = ft.Column(
                controls=[
                    ft.Text(
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}"
                    ),

                    ft.Text(
                        "Nenhuma dieta ativa foi "
                        "cadastrada nesta fazenda."
                    ),

                    ft.Text(
                        "Cadastre uma dieta antes de "
                        "definir o consumo do lote."
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
                        f"{codigo_lote(lote['id'])}"
                        f" — {lote['nome']}",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),

                    ft.Text(
                        f"Animais atuais: "
                        f"{lote['numero_animais']}"
                    ),

                    campo_dieta,

                    campo_consumo,

                    texto_calculo,

                    campo_data,

                    ft.Text(
                        "Digite somente os números da data. "
                        "Ex.: 07092026 → 07/09/2026",
                        size=12
                    ),

                    mensagem_consumo
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
                    content="Salvar configuração",
                    icon=ft.Icons.SAVE,
                    on_click=confirmar
                )
            ]

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Dieta e consumo do lote"
            ),
            content=conteudo,
            actions=acoes,
            actions_alignment=(
                ft.MainAxisAlignment.END
            )
        )

        page.show_dialog(dialogo)
        # ======================================================
    # HISTÓRICO DE CONSUMO DO LOTE
    # ======================================================

    def abrir_historico_consumo(lote):

        if lote["fazenda_id"] != fazenda_atual_id():
            return

        historico = (
            listar_historico_consumo_lote(
                lote_id=lote["id"],
                fazenda_id=fazenda_atual_id()
            )
        )

        itens = []

        if not historico:

            itens.append(
                ft.Text(
                    "Nenhuma configuração de consumo "
                    "foi registrada para este lote."
                )
            )

        else:

            for registro in reversed(historico):

                inicio = data_banco_para_interface(
                    registro["data_inicio"]
                )

                if registro["data_fim"]:

                    fim = data_banco_para_interface(
                        registro["data_fim"]
                    )

                else:

                    fim = "Atual"

                consumo_lote = (
                    registro["consumo_ms_animal_dia"]
                    * lote["numero_animais"]
                )

                itens.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    (
                                        f"{registro['dieta_nome']} "
                                        f"— V{registro['dieta_versao']}"
                                    ),
                                    weight=ft.FontWeight.BOLD
                                ),

                                ft.Text(
                                    f"Vigência: {inicio} → {fim}"
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
                                        "Necessidade calculada "
                                        f"com o número atual de animais: "
                                        f"{consumo_lote:.2f} kg MS/dia"
                                    ),
                                    size=12
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
                f"Histórico de consumo — "
                f"{codigo_lote(lote['id'])}"
            ),

            content=ft.Column(
                controls=itens,
                spacing=10,
                width=540,
                height=420,
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

    def carregar_lotes(e=None):

        lista_lotes.controls.clear()

        fazenda_id = fazenda_atual_id()

        if fazenda_id is None:

            lista_lotes.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Selecione uma fazenda "
                        "para visualizar os lotes."
                    ),
                    padding=20
                )
            )

            page.update()
            return

        if not pode_acessar_fazenda():

            lista_lotes.controls.append(
                ft.Text(
                    "Você não possui acesso operacional "
                    "a esta fazenda.",
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
            consumo_atual = (
                buscar_consumo_atual_lote(
                    lote_id=lote["id"],
                    fazenda_id=fazenda_id
                )
            )
            if consumo_atual:

                dieta_texto = (
                    f"{consumo_atual['dieta_nome']} "
                    f"— V{consumo_atual['dieta_versao']}"
                )

                consumo_animal_texto = (
                    f"{consumo_atual['consumo_ms_animal_dia']:.2f} "
                    "kg MS/animal/dia"
                )

                consumo_lote_texto = (
                    f"{consumo_atual['consumo_ms_lote_dia']:.2f} "
                    "kg MS/dia"
                )

            else:

                dieta_texto = "Não definida"
                consumo_animal_texto = "Não definido"
                consumo_lote_texto = "Não calculado"
            piquete_nome = (
                lote["piquete_nome"]
                or "Não informado"
            )

            peso_medio = (
                (
                    f"{lote['peso_medio_entrada']:.2f} kg"
                )
                if lote["peso_medio_entrada"]
                is not None
                else "Não informado"
            )

            data_entrada = (
                data_banco_para_interface(
                    lote["data_entrada"]
                )
                if lote["data_entrada"]
                else "Não informada"
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
                    (
                        "Localização atual: "
                        f"{codigo_piquete(lote['piquete_id'])}"
                        f" — {piquete_nome}"
                    )
                ),

                ft.Text(
                    f"Número de animais: "
                    f"{lote['numero_animais']}"
                ),

                ft.Text(
                    f"Peso médio de entrada: "
                    f"{peso_medio}"
                ),

                ft.Text(
                    f"Data de entrada: "
                    f"{data_entrada}"
                ),
                                ft.Divider(),

                ft.Text(
                    f"Dieta atual: {dieta_texto}",
                    weight=ft.FontWeight.BOLD
                ),

                ft.Text(
                    f"Consumo: {consumo_animal_texto}"
                ),

                ft.Text(
                    f"Necessidade do lote: "
                    f"{consumo_lote_texto}"
                ),

                    
            ]

            if not ativo:

                data_saida = (
                    data_banco_para_interface(
                        lote["data_saida"]
                    )
                    if lote["data_saida"]
                    else "Não informada"
                )

                controles.append(
                    ft.Text(
                        f"Data de saída: "
                        f"{data_saida}"
                    )
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
                    ),
                        ft.Button(
                        content="Dieta / Consumo",
                        icon=ft.Icons.RESTAURANT,
                        on_click=lambda e,
                        l=lote:
                        abrir_definicao_consumo(l)
                    ),

                    ft.Button(
                        content="Histórico de consumo",
                        icon=ft.Icons.QUERY_STATS,
                        on_click=lambda e,
                        l=lote:
                        abrir_historico_consumo(l)
                    ),

                ])

            else:

                # Mesmo encerrado, o histórico
                # continua disponível.
                botoes.extend([
                    ft.Button(
                        content="Histórico",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda e,
                        l=lote:
                        abrir_historico_piquetes(l)
                    ),

                    ft.Button(
                        content="Reativar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e,
                        l=lote:
                        confirmar_reativacao(l)
                    )
                ])

            controles.append(
                ft.Row(
                    controls=botoes,
                    spacing=10,
                    wrap=True
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

    # ======================================================
    # INICIALIZAÇÃO
    # ======================================================

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
                "Cadastre os grupos de animais, "
                "acompanhe sua localização atual e "
                "preserve o histórico de movimentações."
            ),

            ft.Divider(),

            # ==============================================
            # NOVO LOTE
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

            ft.Text(
                "Digite apenas os números da data. "
                "Ex.: 06092026 → 06/09/2026",
                size=12
            ),

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