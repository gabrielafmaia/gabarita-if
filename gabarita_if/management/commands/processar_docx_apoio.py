import hashlib
import html
import re
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

from docx import Document
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.html import strip_tags

from gabarita_if.models import Assunto, Questao


HEADING_RE = re.compile(r"^\s*(\d{1,3})\s*[.)-]\s+(.+?)\s*$")


def normalize(value):
    value = html.unescape(strip_tags(value or ""))
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-zA-Z0-9]+", " ", value.lower()).split())


def safe_stem(value):
    value = normalize(value).replace(" ", "_")
    return value[:80] or "documento"


class Command(BaseCommand):
    help = "Extrai imagens dos DOCX e associa somente imagens com questão identificada sem ambiguidade."

    def add_arguments(self, parser):
        parser.add_argument(
            "--diretorio",
            type=Path,
            default=Path("arquivos_originais"),
        )

    def handle(self, *args, **options):
        directory = options["diretorio"].resolve()
        output_dir = Path(settings.MEDIA_ROOT) / "questoes"
        output_dir.mkdir(parents=True, exist_ok=True)

        embedded = 0
        extracted = 0
        associated = 0
        associated_questions = set()
        skipped_associations = 0
        processed_files = 0
        scanned_files = 0

        for source in sorted(directory.glob("*.docx")):
            scanned_files += 1
            embedded_in_file, newly_saved = self._extract_all_images(source, output_dir)
            embedded += embedded_in_file
            extracted += newly_saved
            subject = Assunto.objects.filter(nome__iexact=source.stem).first()
            if subject is not None:
                questions = list(Questao.objects.filter(assunto=subject))
            elif "simuladão" in source.stem.casefold():
                questions = list(
                    Questao.objects.filter(assunto__nome__iexact="Simulados Meta IFRN")
                )
            else:
                continue

            processed_files += 1
            if not questions:
                continue

            question_by_heading = {}
            for question in questions:
                key = normalize(question.enunciado)
                if key:
                    question_by_heading[key] = question

            document = Document(source)
            pending_images = []

            for paragraph in document.paragraphs:
                image_names = self._image_names(source, paragraph, output_dir)
                for image_name in image_names:
                    pending_images.append(image_name)

                heading = HEADING_RE.match(paragraph.text.strip())
                if not heading or not pending_images:
                    continue

                candidates = []
                heading_key = normalize(heading.group(2))
                for question in questions:
                    question_key = normalize(question.enunciado)
                    if (
                        len(heading_key) >= 12
                        and (heading_key in question_key or question_key in heading_key)
                    ):
                        candidates.append(question)

                if len(candidates) != 1:
                    skipped_associations += len(pending_images)
                    pending_images = []
                    continue

                question = candidates[0]
                supports = list(question.textoapoio_set.all())
                if len(supports) != 1:
                    skipped_associations += len(pending_images)
                    pending_images = []
                    continue

                support = supports[0]
                additions = []
                for image_name in pending_images:
                    if f"/media/questoes/{image_name}" not in (support.texto or ""):
                        additions.append(
                            f'<p><img src="/media/questoes/{image_name}" '
                            'alt="Imagem do texto de apoio" /></p>'
                        )

                if additions:
                    with transaction.atomic():
                        support.texto = "\n".join(additions) + "\n" + (support.texto or "")
                        support.save(update_fields=["texto"])
                    associated += len(additions)
                    associated_questions.add(question.pk)

                pending_images = []

        self.stdout.write(f"Arquivos DOCX escaneados: {scanned_files}")
        self.stdout.write(f"Arquivos temáticos processados: {processed_files}")
        self.stdout.write(f"Imagens embutidas nos DOCX processados: {embedded}")
        self.stdout.write(f"Novos arquivos de imagem salvos: {extracted}")
        self.stdout.write(f"Imagens associadas: {associated}")
        self.stdout.write(f"Questões que receberam imagens: {len(associated_questions)}")
        self.stdout.write(f"Imagens sem associação segura: {skipped_associations}")
        self.stdout.write(
            "IDs associados: "
            + ", ".join(str(identifier) for identifier in sorted(associated_questions))
        )

    @staticmethod
    def _extract_all_images(source, output_dir):
        embedded = 0
        saved = 0
        with zipfile.ZipFile(source) as archive:
            for member in archive.infolist():
                if not member.filename.startswith("word/media/") or member.is_dir():
                    continue
                embedded += 1
                data = archive.read(member)
                digest = hashlib.sha1(data).hexdigest()[:12]
                extension = PurePosixPath(member.filename).suffix.lower()
                if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension):
                    extension = ".bin"
                name = f"docx_{safe_stem(source.stem)}_{digest}{extension}"
                destination = output_dir / name
                if not destination.exists():
                    destination.write_bytes(data)
                    saved += 1
        return embedded, saved

    @staticmethod
    def _image_names(source, paragraph, output_dir):
        names = []
        blobs = paragraph._p.xpath('.//*[local-name()="blip"]/@*[local-name()="embed"]')
        if not blobs:
            return names

        with zipfile.ZipFile(source) as archive:
            relationships = archive.read("word/_rels/document.xml.rels").decode("utf-8")
            for relationship_id in blobs:
                match = re.search(
                    rf'Id="{re.escape(relationship_id)}"[^>]+Target="([^"]+)"',
                    relationships,
                )
                if not match:
                    continue
                member = "word/" + match.group(1).lstrip("/")
                if member not in archive.namelist():
                    continue
                data = archive.read(member)
                digest = hashlib.sha1(data).hexdigest()[:12]
                extension = PurePosixPath(member).suffix.lower()
                if not re.fullmatch(r"\.[a-z0-9]{1,10}", extension):
                    extension = ".bin"
                name = f"docx_{safe_stem(source.stem)}_{digest}{extension}"
                destination = output_dir / name
                if not destination.exists():
                    destination.write_bytes(data)
                names.append(name)
        return names
