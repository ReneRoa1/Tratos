import math

from database.models import (
    buscar_consumo_lote_na_data,
    listar_itens_dieta,
    buscar_ms_alimento_na_data,
    buscar_calibracao_misturador_dieta_na_data,
    buscar_ultima_leitura_cocho,
)
# ==========================================================
# MOTOR DE CÁLCULO DO TRATO
# ==========================================================

def calcular_trato_planejado(
    fazenda_id,
    lote_id,
    misturador_id,
    data_referencia
):
    """
    Calcula o trato planejado para um lote.

    Retorna:
    - dieta vigente
    - consumo de MS
    - necessidade total de MS
    - matéria seca por ingrediente
    - matéria natural por ingrediente
    - matéria natural total
    - capacidade do misturador
    - número de cargas
    """

    # ======================================================
    # 1. CONSUMO / DIETA VIGENTE DO LOTE
    # ======================================================

    consumo = buscar_consumo_lote_na_data(
        lote_id=lote_id,
        fazenda_id=fazenda_id,
        data_referencia=data_referencia
    )

    if consumo is None:

        raise ValueError(
            "O lote não possui uma configuração "
            "de dieta e consumo vigente nesta data."
        )

    dieta_id = consumo["dieta_id"]

    numero_animais = int(
        consumo["numero_animais"]
    )

    consumo_ms_animal = float(
        consumo["consumo_ms_animal_dia"]
    )

    if numero_animais <= 0:

        raise ValueError(
            "O lote não possui animais para "
            "realizar o cálculo."
        )

    # ======================================================
    # 2. NECESSIDADE TOTAL DE MATÉRIA SECA
    # ======================================================

    necessidade_ms_lote = (
        numero_animais
        * consumo_ms_animal
    )
        # ======================================================
    # AJUSTE DE COCHO
    # ======================================================

    necessidade_ms_padrao = (
        necessidade_ms_lote
    )

    leitura_cocho = (
        buscar_ultima_leitura_cocho(
            lote_id=lote_id,
            fazenda_id=fazenda_id,
            data_referencia=data_referencia
        )
    )

    nota_cocho = None
    ajuste_cocho_percentual = 0.0

    if leitura_cocho is not None:

        nota_cocho = leitura_cocho["nota"]

        ajuste_cocho_percentual = float(
            leitura_cocho[
                "ajuste_percentual"
            ]
        )

        fator_ajuste = (
            1.0
            + ajuste_cocho_percentual
            / 100.0
        )

        necessidade_ms_lote = (
            necessidade_ms_padrao
            * fator_ajuste
        )
    # ======================================================
    # 3. ITENS DA DIETA
    # ======================================================

    itens_dieta = listar_itens_dieta(
        dieta_id=dieta_id,
        fazenda_id=fazenda_id
    )

    if not itens_dieta:

        raise ValueError(
            "A dieta vigente não possui ingredientes."
        )

    resultado_ingredientes = []

    total_materia_natural = 0.0
    soma_inclusoes = 0.0

    # ======================================================
    # 4. CALCULA CADA INGREDIENTE
    # ======================================================

    for item in itens_dieta:

        alimento_id = item["alimento_id"]

        inclusao_ms_percentual = float(
            item["inclusao_ms"]
        )

        soma_inclusoes += (
            inclusao_ms_percentual
        )

        # --------------------------------------------------
        # Busca a MS vigente do ingrediente
        # --------------------------------------------------

        registro_ms = (
            buscar_ms_alimento_na_data(
                alimento_id=alimento_id,
                fazenda_id=fazenda_id,
                data_referencia=data_referencia
            )
        )

        if registro_ms is None:

            raise ValueError(
                (
                    f"O alimento "
                    f"'{item['alimento_nome']}' "
                    "não possui matéria seca cadastrada "
                    f"para a data {data_referencia}."
                )
            )

        materia_seca_percentual = float(
            registro_ms["materia_seca"]
        )

        if (
            materia_seca_percentual <= 0
            or materia_seca_percentual > 100
        ):

            raise ValueError(
                (
                    f"A matéria seca do alimento "
                    f"'{item['alimento_nome']}' "
                    "é inválida."
                )
            )

        # --------------------------------------------------
        # Quantidade de MS do ingrediente
        # --------------------------------------------------

        quantidade_ms = (
            necessidade_ms_lote
            * inclusao_ms_percentual
            / 100.0
        )

        # --------------------------------------------------
        # Converte MS para matéria natural
        #
        # MN = MS / (MS% / 100)
        # --------------------------------------------------

        quantidade_mn = (
            quantidade_ms
            / (
                materia_seca_percentual
                / 100.0
            )
        )

        total_materia_natural += (
            quantidade_mn
        )

        resultado_ingredientes.append({
            "alimento_id": alimento_id,

            "alimento_nome":
                item["alimento_nome"],

            "ordem_carregamento":
                item["ordem_carregamento"],

            "inclusao_ms_percentual":
                inclusao_ms_percentual,

            "materia_seca_percentual":
                materia_seca_percentual,

            "data_ms":
                registro_ms["data_vigencia"],

            "quantidade_ms_kg":
                quantidade_ms,

            "quantidade_mn_kg":
                quantidade_mn,
        })

    # ======================================================
    # 5. VALIDA A DIETA
    # ======================================================

    if abs(soma_inclusoes - 100.0) > 0.01:

        raise ValueError(
            (
                "A composição da dieta está inválida. "
                f"A soma das inclusões é "
                f"{soma_inclusoes:.2f}%."
            )
        )

    # ======================================================
    # 6. BUSCA CALIBRAÇÃO DO MISTURADOR
    # ======================================================

    calibracao = (
        buscar_calibracao_misturador_dieta_na_data(
            misturador_id=misturador_id,
            dieta_id=dieta_id,
            fazenda_id=fazenda_id,
            data_referencia=data_referencia
        )
    )

    if calibracao is None:

        raise ValueError(
            (
                "Não existe calibração do misturador "
                "para esta dieta na data selecionada."
            )
        )

    capacidade_kg = float(
        calibracao[
            "capacidade_operacional_kg"
        ]
    )

    if capacidade_kg <= 0:

        raise ValueError(
            "A capacidade operacional do "
            "misturador é inválida."
        )

    # ======================================================
    # 7. NÚMERO DE CARGAS
    # ======================================================

    numero_cargas = math.ceil(
        total_materia_natural
        / capacidade_kg
    )

    if numero_cargas < 1:
        numero_cargas = 1

    # ======================================================
    # 8. QUANTIDADE MÉDIA POR CARGA
    # ======================================================

    quantidade_media_por_carga = (
        total_materia_natural
        / numero_cargas
    )

    for ingrediente in resultado_ingredientes:

        ingrediente[
            "quantidade_mn_por_carga_kg"
        ] = (
            ingrediente["quantidade_mn_kg"]
            / numero_cargas
        )

        ingrediente[
            "quantidade_ms_por_carga_kg"
        ] = (
            ingrediente["quantidade_ms_kg"]
            / numero_cargas
        )

    # ======================================================
    # 9. RESULTADO
    # ======================================================

    return {

        "fazenda_id": fazenda_id,

        "lote_id": lote_id,

        "dieta_id": dieta_id,

        "dieta_nome":
            consumo["dieta_nome"],

        "dieta_versao":
            consumo["dieta_versao"],

        "misturador_id":
            misturador_id,

        "data_referencia":
            data_referencia,

        "numero_animais":
            numero_animais,

        "consumo_ms_animal_dia":
            consumo_ms_animal,

        "necessidade_ms_padrao_kg":
            necessidade_ms_padrao,

        "necessidade_ms_lote_kg":
            necessidade_ms_lote,

        "nota_cocho":
            nota_cocho,

        "ajuste_cocho_percentual":
            ajuste_cocho_percentual,

        "leitura_cocho_id":
            (
                leitura_cocho["id"]
                if leitura_cocho is not None
                else None
            ),

        "total_materia_natural_kg":
            total_materia_natural,

        "densidade_kg_m3":
            calibracao["densidade_kg_m3"],

        "volume_util_m3":
            calibracao["volume_util_m3"],

        "capacidade_misturador_kg":
            capacidade_kg,

        "numero_cargas":
            numero_cargas,

        "quantidade_media_por_carga_kg":
            quantidade_media_por_carga,

        "ingredientes":
            resultado_ingredientes
    }

# ==========================================================
# AJUSTE DE COCHO
# ==========================================================

def calcular_ajuste_cocho(
    quantidade_padrao_mn_kg,
    nota
):
    """
    Escala:
    -2 = +20%
    -1 = +10%
     0 =   0%
    +1 = -10%
    +2 = -20%
    """

    ajustes = {
        -2: 20.0,
        -1: 10.0,
        0: 0.0,
        1: -10.0,
        2: -20.0,
    }

    try:
        nota = int(nota)
    except (TypeError, ValueError):
        raise ValueError(
            "Informe uma nota de cocho válida."
        )

    if nota not in ajustes:
        raise ValueError(
            "A nota de cocho deve estar "
            "entre -2 e +2."
        )

    try:
        quantidade_padrao = float(
            quantidade_padrao_mn_kg
        )
    except (TypeError, ValueError):
        raise ValueError(
            "Quantidade padrão inválida."
        )

    if quantidade_padrao <= 0:
        raise ValueError(
            "A quantidade padrão deve ser "
            "maior que zero."
        )

    ajuste_percentual = ajustes[nota]

    fator = (
        1.0
        + ajuste_percentual / 100.0
    )

    quantidade_recomendada = (
        quantidade_padrao
        * fator
    )

    return {
        "nota": nota,
        "ajuste_percentual":
            ajuste_percentual,

        "quantidade_padrao_mn_kg":
            quantidade_padrao,

        "quantidade_recomendada_mn_kg":
            quantidade_recomendada
    }
# ==========================================================
# QUANTIDADE PADRÃO DO LOTE
# ==========================================================

def calcular_quantidade_padrao_lote(
    fazenda_id,
    lote_id,
    data_referencia
):
    """
    Calcula a quantidade padrão diária do lote
    em matéria seca e matéria natural,
    sem considerar leitura de cocho
    e sem depender do misturador.
    """

    consumo = buscar_consumo_lote_na_data(
        lote_id=lote_id,
        fazenda_id=fazenda_id,
        data_referencia=data_referencia
    )

    if consumo is None:
        raise ValueError(
            "O lote não possui dieta e consumo "
            "vigentes nesta data."
        )

    numero_animais = int(
        consumo["numero_animais"]
    )

    consumo_ms_animal = float(
        consumo["consumo_ms_animal_dia"]
    )

    if numero_animais <= 0:
        raise ValueError(
            "O lote não possui animais."
        )

    necessidade_ms_lote = (
        numero_animais
        * consumo_ms_animal
    )

    itens_dieta = listar_itens_dieta(
        dieta_id=consumo["dieta_id"],
        fazenda_id=fazenda_id
    )

    if not itens_dieta:
        raise ValueError(
            "A dieta vigente não possui ingredientes."
        )

    ingredientes = []

    total_mn = 0.0
    soma_inclusoes = 0.0

    for item in itens_dieta:

        inclusao = float(
            item["inclusao_ms"]
        )

        soma_inclusoes += inclusao

        registro_ms = (
            buscar_ms_alimento_na_data(
                alimento_id=item["alimento_id"],
                fazenda_id=fazenda_id,
                data_referencia=data_referencia
            )
        )

        if registro_ms is None:

            raise ValueError(
                (
                    f"O alimento "
                    f"'{item['alimento_nome']}' "
                    "não possui matéria seca vigente "
                    "nesta data."
                )
            )

        ms_percentual = float(
            registro_ms["materia_seca"]
        )

        if (
            ms_percentual <= 0
            or ms_percentual > 100
        ):
            raise ValueError(
                (
                    f"A matéria seca de "
                    f"'{item['alimento_nome']}' "
                    "é inválida."
                )
            )

        quantidade_ms = (
            necessidade_ms_lote
            * inclusao
            / 100.0
        )

        quantidade_mn = (
            quantidade_ms
            / (ms_percentual / 100.0)
        )

        total_mn += quantidade_mn

        ingredientes.append({
            "alimento_id":
                item["alimento_id"],

            "alimento_nome":
                item["alimento_nome"],

            "inclusao_ms_percentual":
                inclusao,

            "materia_seca_percentual":
                ms_percentual,

            "quantidade_ms_kg":
                quantidade_ms,

            "quantidade_mn_kg":
                quantidade_mn,
        })

    if abs(soma_inclusoes - 100.0) > 0.01:

        raise ValueError(
            (
                "A composição da dieta está inválida. "
                f"Total: {soma_inclusoes:.2f}%."
            )
        )

    return {
        "fazenda_id":
            fazenda_id,

        "lote_id":
            lote_id,

        "dieta_id":
            consumo["dieta_id"],

        "dieta_nome":
            consumo["dieta_nome"],

        "dieta_versao":
            consumo["dieta_versao"],

        "numero_animais":
            numero_animais,

        "consumo_ms_animal_dia":
            consumo_ms_animal,

        "necessidade_ms_lote_kg":
            necessidade_ms_lote,

        "quantidade_padrao_mn_kg":
            total_mn,

        "ingredientes":
            ingredientes
    }