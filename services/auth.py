import hashlib
import secrets


def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro para a senha.
    A senha original não é armazenada no banco.
    """

    salt = secrets.token_hex(16)

    senha_hash = hashlib.pbkdf2_hmac(
        "sha256",
        senha.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    ).hex()

    return f"{salt}${senha_hash}"


def verificar_senha(
    senha: str,
    senha_armazenada: str
) -> bool:

    try:

        salt, hash_salvo = senha_armazenada.split("$")

        hash_digitado = hashlib.pbkdf2_hmac(
            "sha256",
            senha.encode("utf-8"),
            salt.encode("utf-8"),
            100_000
        ).hex()

        return secrets.compare_digest(
            hash_digitado,
            hash_salvo
        )

    except Exception:

        return False