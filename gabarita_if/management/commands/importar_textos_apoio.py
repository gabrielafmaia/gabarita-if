import html
import re
import unicodedata
from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.table import Table
from docx.text.paragraph import Paragraph
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import strip_tags

from gabarita_if.models import Assunto, Disciplina, Questao, TextoApoio


NOTICE_RE = re.compile(
    r"(?:para responder|texto para responder|considere.{0,100}trecho|"
    r"leia os textos).{0,180}quest(?:ão|ões)",
    re.IGNORECASE,
)
QUESTION_NUMBERS_RE = re.compile(r"quest(?:ão|ões)\s+([^.;:]+)", re.IGNORECASE)
NUMBERED_PARAGRAPH_RE = re.compile(r"^\s*(\d{1,3})\s*[.)-]\s*(.+?)\s*$")


def iter_paragraphs(parent):
    """Yield document paragraphs in order, including paragraphs in tables."""
    if isinstance(parent, DocumentObject):
        blocks = parent.iter_inner_content()
    else:
        blocks = parent.iter_inner_content()

    for block in blocks:
        if isinstance(block, Paragraph):
            yield block
        elif isinstance(block, Table):
            for row in block.rows:
                for cell in row.cells:
                    yield from iter_paragraphs(cell)


def normalize(value):
    value = html.unescape(strip_tags(value or ""))
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-zA-Z0-9]+", " ", value.lower()).split())


def question_numbers(notice):
    match = QUESTION_NUMBERS_RE.search(notice)
    if not match:
        return []

    numbers = [int(number) for number in re.findall(r"\d+", match.group(1))]
    if len(numbers) == 2 and re.search(r"\b(?:a|à|ate)\b", match.group(1), re.I):
        first, last = numbers
        if first <= last and last - first <= 30:
            return list(range(first, last + 1))
    return list(dict.fromkeys(numbers))


def question_heading(text):
    match = NUMBERED_PARAGRAPH_RE.match(text)
    if not match:
        return None
    return int(match.group(1)), match.group(2).strip()


def passage_html(paragraphs):
    parts = []
    for paragraph in paragraphs:
        text = paragraph.strip()
        if text:
            escaped = html.escape(text).replace("\n", "<br>")
            parts.append(f"<p>{escaped}</p>")
    return "\n".join(parts)


class Command(BaseCommand):
    help = "Importa textos de apoio de questões a partir de um arquivo DOCX."

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=Path, help="Caminho para o arquivo .docx")
        parser.add_argument(
            "--assunto",
            required=True,
            help="Nome da disciplina ou do assunto usado para limitar a busca",
        )

    def handle(self, *args, **options):
        file_path = options["arquivo"]
        assunto_nome = options["assunto"].strip()

        if file_path.suffix.lower() != ".docx":
            raise CommandError("O arquivo informado precisa ter extensão .docx.")
        if not file_path.is_file():
            raise CommandError(f"Arquivo não encontrado: {file_path}")

        try:
            document = Document(file_path)
        except Exception as exc:
            raise CommandError(f"Não foi possível ler o DOCX: {exc}") from exc

        discipline_exists = Disciplina.objects.filter(nome__iexact=assunto_nome).exists()
        subject_exists = Assunto.objects.filter(nome__iexact=assunto_nome).exists()
        if discipline_exists:
            questions = list(
                Questao.objects.filter(disciplina__nome__iexact=assunto_nome)
            )
            scope_name = f"disciplina {assunto_nome}"
        elif subject_exists:
            questions = list(Questao.objects.filter(assunto__nome__iexact=assunto_nome))
            scope_name = f"assunto {assunto_nome}"
        else:
            raise CommandError(
                f"Não existe disciplina nem assunto com o nome '{assunto_nome}'."
            )

        paragraphs = [paragraph.text.strip() for paragraph in iter_paragraphs(document)]
        notices = [
            (index, paragraph, question_numbers(paragraph))
            for index, paragraph in enumerate(paragraphs)
            if NOTICE_RE.search(paragraph)
        ]

        if not notices:
            self.stdout.write(self.style.WARNING("Nenhum aviso de texto-base reconhecido."))
            return

        updated = 0
        skipped_existing = 0
        not_found = []
        ambiguous = []
        processed_ids = set()

        for notice_index, notice, numbers in notices:
            if not numbers:
                not_found.append(f"Aviso sem número de questão: {notice}")
                continue

            next_notice_index = next(
                (index for index, _, _ in notices if index > notice_index),
                len(paragraphs),
            )
            passage_end = next_notice_index
            heading_at_end = None
            for index in range(notice_index + 1, next_notice_index):
                heading = question_heading(paragraphs[index])
                if heading:
                    passage_end = index
                    heading_at_end = heading
                    break

            passage = passage_html(paragraphs[notice_index + 1 : passage_end])
            if not passage:
                not_found.append(f"Aviso sem texto-base extraível: {notice}")
                continue

            candidate_headings = []
            if heading_at_end and heading_at_end[0] in numbers:
                candidate_headings.append(heading_at_end)
            else:
                for index in range(notice_index - 1, -1, -1):
                    heading = question_heading(paragraphs[index])
                    if heading and heading[0] in numbers:
                        candidate_headings.append(heading)
                        break

            for number in numbers:
                matching_headers = [
                    heading_text
                    for heading_number, heading_text in candidate_headings
                    if heading_number == number
                ]
                if len(matching_headers) != 1:
                    not_found.append(
                        f"Questão {number}: cabeçalho identificador não encontrado no DOCX ({notice})"
                    )
                    continue

                header_key = normalize(matching_headers[0])
                if len(header_key) < 12:
                    not_found.append(
                        f"Questão {number}: cabeçalho curto demais para busca segura ({matching_headers[0]})"
                    )
                    continue

                matches = []
                for question in questions:
                    enunciado_key = normalize(question.enunciado)
                    if header_key in enunciado_key or enunciado_key in header_key:
                        matches.append(question)

                if len(matches) == 0:
                    not_found.append(matching_headers[0])
                    continue
                if len(matches) > 1:
                    ambiguous.append(
                        f"{matching_headers[0]} (IDs: {', '.join(str(q.id) for q in matches)})"
                    )
                    continue

                question = matches[0]
                if question.pk in processed_ids:
                    continue
                processed_ids.add(question.pk)

                if question.textoapoio_set.exists():
                    skipped_existing += 1
                    continue

                with transaction.atomic():
                    support = TextoApoio.objects.create(
                        titulo="Texto para responder à questão",
                        texto=passage,
                    )
                    support.questoes.add(question)
                updated += 1

        self.stdout.write(f"Escopo: {scope_name}")
        self.stdout.write(f"Avisos de texto-base identificados: {len(notices)}")
        self.stdout.write(self.style.SUCCESS(f"Questões atualizadas: {updated}"))
        self.stdout.write(f"Questões que já tinham texto de apoio: {skipped_existing}")
        self.stdout.write(f"Cabeçalhos não encontrados: {len(not_found)}")
        for item in not_found:
            self.stdout.write(f"  - {item}")
        self.stdout.write(f"Correspondências ambíguas (ignoradas): {len(ambiguous)}")
        for item in ambiguous:
            self.stdout.write(f"  - {item}")
