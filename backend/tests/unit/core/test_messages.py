from app.core.messages import DEFAULT_LOCALE, MESSAGES, get_message


def test_default_locale_is_pt_br() -> None:
    assert DEFAULT_LOCALE == "pt-BR"
    assert get_message("user.not_found") == "Usuário não encontrado."


def test_unknown_locale_falls_back_to_default_locale() -> None:
    assert get_message("user.not_found", locale="xx-XX") == get_message(
        "user.not_found"
    )


def test_unknown_code_falls_back_to_code() -> None:
    assert get_message("does.not_exist") == "does.not_exist"


def test_uses_requested_locale_when_available(monkeypatch) -> None:
    monkeypatch.setitem(MESSAGES, "en", {"user.not_found": "User not found."})

    assert get_message("user.not_found", locale="en") == "User not found."
