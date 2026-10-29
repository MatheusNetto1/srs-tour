from app.indicators.slug import slugify


def test_slugify_derives_lowercase_hyphenated_slug() -> None:
    assert slugify("Meios de hospedagem") == "meios-de-hospedagem"


def test_slugify_strips_accents() -> None:
    assert slugify("Serviços turísticos") == "servicos-turisticos"


def test_slugify_collapses_punctuation_and_trims() -> None:
    assert (
        slugify("  Fluxo - estimado!! de visitantes  ")
        == "fluxo-estimado-de-visitantes"
    )


def test_slugify_truncates_to_the_slug_column_limit() -> None:
    slug = slugify("x" * 255)

    assert len(slug) <= 100
    assert slug == "x" * 100
