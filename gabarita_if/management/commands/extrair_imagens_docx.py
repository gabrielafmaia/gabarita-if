from pathlib import Path, PurePosixPath
import re
import zipfile

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Extrai imagens de um arquivo DOCX para media/simulados_meta/"

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=Path, help="Caminho para o arquivo .docx")

    def handle(self, *args, **options):
        arquivo = options["arquivo"]
        if arquivo.suffix.lower() != ".docx":
            raise CommandError("O arquivo informado precisa ter extensão .docx.")
        if not arquivo.is_file():
            raise CommandError(f"Arquivo não encontrado: {arquivo}")

        try:
            docx = zipfile.ZipFile(arquivo)
        except (OSError, zipfile.BadZipFile) as exc:
            raise CommandError(f"Não foi possível abrir o DOCX: {exc}") from exc

        with docx:
            imagens = [
                membro
                for membro in docx.infolist()
                if membro.filename.startswith("word/media/") and not membro.is_dir()
            ]

            if not imagens:
                self.stdout.write(self.style.WARNING("Nenhuma imagem encontrada no DOCX."))
                return

            pasta_saida = Path(settings.MEDIA_ROOT) / "simulados_meta"
            pasta_saida.mkdir(parents=True, exist_ok=True)

            numero = 1
            for membro in imagens:
                extensao = PurePosixPath(membro.filename).suffix.lower()
                if not re.fullmatch(r"\.[a-z0-9]{1,10}", extensao):
                    extensao = ".bin"

                while any(pasta_saida.glob(f"imagem_{numero}.*")):
                    numero += 1

                destino = pasta_saida / f"imagem_{numero}{extensao}"
                with destino.open("xb") as arquivo_saida:
                    arquivo_saida.write(docx.read(membro))

                self.stdout.write(f"{membro.filename} -> {destino}")
                numero += 1

            self.stdout.write(
                self.style.SUCCESS(f"Imagens extraídas: {len(imagens)} em {pasta_saida}")
            )
