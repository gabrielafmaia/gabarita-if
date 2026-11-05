from html import escape

from lxml import etree, html

from django.core.management.base import BaseCommand
from django.db import transaction

from gabarita_if.models import Questao, TextoApoio


EMPTY_TAGS = {"p", "div", "span"}


def _remove_empty_elements(element):
    for child in list(element):
        _remove_empty_elements(child)

        has_text = bool("".join(child.itertext()).strip())
        has_elements = len(child) > 0
        if child.tag in EMPTY_TAGS and not has_text and not has_elements:
            tail = child.tail or ""
            previous = child.getprevious()
            element.remove(child)
            if previous is not None:
                previous.tail = (previous.tail or "") + tail
            else:
                element.text = (element.text or "") + tail


def clean_html(value):
    if not value:
        return value

    parser = html.HTMLParser(recover=True)
    container = html.fragment_fromstring(value, create_parent="div", parser=parser)
    _remove_empty_elements(container)

    parts = []
    if container.text:
        parts.append(escape(container.text, quote=False))
    for child in container:
        parts.append(etree.tostring(child, encoding="unicode", method="xml"))
    return "".join(parts)


class Command(BaseCommand):
    help = "Corrige e salva o HTML de enunciados e textos de apoio."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Mostra as alterações sem gravá-las no banco.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        questoes_corrigidas = 0
        textos_corrigidos = 0
        exemplo = None

        with transaction.atomic():
            for questao in Questao.objects.only("pk", "enunciado").iterator():
                antes = questao.enunciado or ""
                depois = clean_html(antes)
                if depois != antes:
                    questao.enunciado = depois
                    questao.save(update_fields=["enunciado"])
                    questoes_corrigidas += 1
                    if exemplo is None:
                        exemplo = ("Questao.enunciado", antes, depois)

            for texto in TextoApoio.objects.only("pk", "texto").iterator():
                antes = texto.texto or ""
                depois = clean_html(antes)
                if depois != antes:
                    texto.texto = depois
                    texto.save(update_fields=["texto"])
                    textos_corrigidos += 1
                    if exemplo is None:
                        exemplo = ("TextoApoio.texto", antes, depois)

            if dry_run:
                transaction.set_rollback(True)

        modo = " (simulação; nada foi gravado)" if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"Questões corrigidas: {questoes_corrigidas}; "
                f"textos de apoio corrigidos: {textos_corrigidos}{modo}"
            )
        )
        if exemplo:
            campo, antes, depois = exemplo
            self.stdout.write(f"\nExemplo ({campo}) - antes:\n{antes}")
            self.stdout.write(f"\nExemplo ({campo}) - depois:\n{depois}")
