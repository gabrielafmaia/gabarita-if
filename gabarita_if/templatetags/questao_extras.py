import re

from django import template


register = template.Library()


@register.filter
def limpar_letra_alternativa(value, letra):
    """Remove a letra da alternativa após tags HTML iniciais, se houver."""
    if value is None:
        return ""

    letra = str(letra).strip()
    if letra.upper() not in {"A", "B", "C", "D"}:
        return value

    prefixo = re.compile(
        r"^(\s*(?:<(?!/)[^>]*>\s*)*)" + re.escape(letra) + r"\)\s*",
        re.IGNORECASE,
    )
    texto = prefixo.sub(r"\1", str(value), count=1)
    texto = re.sub(r"</p>\s*<p\b[^>]*>", "<br>", texto, flags=re.IGNORECASE)
    return re.sub(r"</?p\b[^>]*>", "", texto, flags=re.IGNORECASE).strip()
