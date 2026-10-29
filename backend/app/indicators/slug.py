import re
import unicodedata

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    """Derive a stable, URL-safe slug from an indicator name.

    Normalizes accents (ex: "Serviços" -> "servicos") and collapses any
    run of non-alphanumeric characters into a single hyphen.
    """
    ascii_only = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = _NON_ALNUM.sub("-", ascii_only.lower()).strip("-")

    # `slug` é String(100); `name` pode ter até 255 chars (ver models.py).
    return slug[:100].rstrip("-")
