DEFAULT_LOCALE = "pt-BR"

MESSAGES: dict[str, dict[str, str]] = {
    "pt-BR": {
        "error": "Não foi possível processar a requisição.",
        "not_found": "Recurso não encontrado.",
        "conflict": "Conflito ao processar a requisição.",
        "unauthorized": "Não autorizado.",
        "validation.failed": "Dados inválidos.",
        "validation.invalid_value": "Valor inválido.",
        "http.not_found": "Recurso não encontrado.",
        "http.method_not_allowed": "Método não permitido.",
        "http.error": "Erro na requisição.",
        "internal_error": "Erro interno do servidor.",
        "auth.invalid_credentials": "E-mail ou senha inválidos.",
        "auth.invalid_token": "Não foi possível validar as credenciais.",
        "indicator.not_found": "Indicador não encontrado.",
        "user.not_found": "Usuário não encontrado.",
        "user.email_already_exists": "Já existe um usuário com este e-mail.",
    },
}


def get_message(code: str, locale: str = DEFAULT_LOCALE) -> str:
    """Return the message for an error code.

    Falls back to the default locale and, as a last resort, to the code itself,
    so a missing translation never breaks an error response.
    """
    for candidate in (locale, DEFAULT_LOCALE):
        message = MESSAGES.get(candidate, {}).get(code)

        if message is not None:
            return message

    return code
