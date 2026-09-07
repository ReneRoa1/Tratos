def codigo_usuario(usuario_id):
    return f"USR-{usuario_id:06d}"


def codigo_organizacao(organizacao_id):
    return f"ORG-{organizacao_id:06d}"


def codigo_fazenda(fazenda_id):
    return f"FAZ-{fazenda_id:06d}"


def codigo_piquete(piquete_id):
    return f"PIQ-{piquete_id:06d}"


def codigo_lote(lote_id):
    return f"LOT-{lote_id:06d}"


def codigo_alimento(alimento_id):
    return f"ALI-{alimento_id:06d}"


def codigo_dieta(dieta_id):
    return f"DIE-{dieta_id:06d}"


def codigo_misturador(misturador_id):
    return f"MIS-{misturador_id:06d}"


def codigo_trato(trato_id):
    return f"TRA-{trato_id:06d}"

def codigo_responsavel(responsavel_id):
    return f"RSP-{responsavel_id:06d}"

def codigo_trato_planejado(id_registro):
    return f"TRP-{int(id_registro):06d}"