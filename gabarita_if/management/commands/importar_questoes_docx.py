
import hashlib
import html
import re
import unicodedata
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.html import strip_tags
from docx import Document
from docx.oxml.ns import qn

from gabarita_if.models import Assunto, Disciplina, Fonte, Questao


INICIO = re.compile(
    r"^\s*(?:quest[aã]o\s*)?(\d{1,3})\s*[\).:\-–]\s*(.+)",
    re.I,
)

ALTERNATIVA = re.compile(
    r"^\s*(?:\(([a-e])\)|([a-e])\s*[\).:\-])\s*(.*)$",
    re.I,
)

RESOLUCAO = re.compile(
    r"^\s*quest[aã]o\s*(\d{1,3})\s*[:.\-–]\s*(.*)$",
    re.I,
)

LETRA = re.compile(
    r"^\s*[\(\[]?\s*([a-e])\s*[\)\].:\-]\s*(.*)$",
    re.I,
)

GABARITO = re.compile(
    r"(?i)\b(?:gabarito|resposta|alternativa\s+correta)\s*[:\-]\s*[\(\[]?\s*([a-e])\b"
)


def normalizar(valor):
    valor = unicodedata.normalize(
        "NFKD",
        strip_tags(valor or ""),
    )

    valor = "".join(
        c for c in valor
        if not unicodedata.combining(c)
    )

    return re.sub(r"\s+", " ", valor).strip().casefold()


def texto_paragrafo(p):
    return (p.text or "").strip()


def conteudo_paragrafo(p):
    partes = []

    for run in p.runs:
        texto = run.text

        if texto:
            partes.append(
                html.escape(texto).replace("\n", "<br>")
            )

        for elemento in run._element.iter():
            if elemento.tag == qn("a:blip"):
                rid = elemento.get(qn("r:embed"))

                if rid:
                    partes.append("{{IMG:" + rid + "}}")

    return "".join(partes).strip()


def extrair(documento):
    perguntas = []
    respostas = {}

    modo_resolucoes = False
    atual = None
    resposta_atual = None

    for p in documento.paragraphs:
        texto = texto_paragrafo(p)

        if not texto:
            if modo_resolucoes and resposta_atual is not None:
                respostas[resposta_atual]["html"].append("")
            continue

        if normalizar(texto) in (
            "resolucoes",
            "gabaritos",
            "gabarito",
            "respostas",
        ):
            modo_resolucoes = True
            atual = None
            resposta_atual = None
            continue

        if modo_resolucoes:
            m = RESOLUCAO.match(texto)

            if m:
                numero = int(m.group(1))
                trecho = m.group(2).strip()
                letra = LETRA.match(trecho)

                respostas[numero] = {
                    "letra": letra.group(1).upper() if letra else None,
                    "html": [
                        html.escape(trecho)
                    ] if trecho else [],
                }

                resposta_atual = numero
                continue

            if resposta_atual is not None:
                if normalizar(texto).startswith(
                    (
                        "voltar para questao",
                        "resolucoes em video",
                    )
                ):
                    continue

                respostas[resposta_atual]["html"].append(
                    conteudo_paragrafo(p)
                )

            continue

        m = INICIO.match(texto)

        if m and (
            m.group(2).strip().startswith("(")
            or len(m.group(2).strip()) >= 18
        ):
            atual = {
                "numero": int(m.group(1)),
                "enunciado": [conteudo_paragrafo(p)],
                "alternativas": {},
                "erro": None,
                "gabarito": None,
                "ano": None,
            }

            ano = re.search(
                r"\b(?:19|20)\d{2}\b",
                texto,
            )

            if ano:
                atual["ano"] = int(ano.group())

            perguntas.append(atual)
            continue

        if atual is None:
            continue

        if normalizar(texto).startswith(
            (
                "ver resposta",
                "ver resolucao em video",
                "voltar para questao",
            )
        ):
            continue

        gab = GABARITO.search(texto)

        if gab:
            atual["gabarito"] = gab.group(1).upper()
            continue

        alt = ALTERNATIVA.match(texto)

        if alt:
            letra = (
                alt.group(1) or alt.group(2)
            ).upper()

            valor = html.escape(
                alt.group(3)
            ).strip()

            if letra in atual["alternativas"]:
                atual["erro"] = (
                    "Alternativa " + letra + " repetida"
                )
            else:
                atual["alternativas"][letra] = valor

        elif atual["alternativas"]:
            ultima = list(
                atual["alternativas"]
            )[-1]

            atual["alternativas"][ultima] += (
                "<br>" + conteudo_paragrafo(p)
            )

        else:
            atual["enunciado"].append(
                conteudo_paragrafo(p)
            )

    for pergunta in perguntas:
        resposta = respostas.get(
            pergunta["numero"]
        )

        if resposta:
            pergunta["gabarito"] = (
                pergunta["gabarito"]
                or resposta["letra"]
            )

            pergunta["comentario"] = "<br>".join(
                x for x in resposta["html"] if x
            )

        else:
            pergunta["comentario"] = ""

    return perguntas


def imagem_em_html(conteudo, documento, salvar=False):
    if "{{IMG:" not in conteudo:
        return conteudo

    def substituir(m):
        rid = m.group(1)

        try:
            parte = documento.part.related_parts[rid]
            dados = parte.blob

            extensao = (
                Path(str(parte.partname)).suffix.lower()
                or ".png"
            )

            if extensao not in (
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".webp",
            ):
                return ""

            if not salvar:
                return "[imagem]"

            from django.core.files.base import ContentFile
            from django.core.files.storage import default_storage

            nome = (
                "questoes_docx/"
                + hashlib.sha256(dados).hexdigest()
                + extensao
            )

            if not default_storage.exists(nome):
                nome = default_storage.save(
                    nome,
                    ContentFile(dados),
                )

            return (
                '<img src="'
                + html.escape(
                    default_storage.url(nome),
                    quote=True,
                )
                + '" alt="Imagem da questão">'
            )

        except Exception:
            return "[imagem não recuperada]"

    return re.sub(
        r"\{\{IMG:([^}]+)\}\}",
        substituir,
        conteudo,
    )


def dificuldade(enunciado, alternativas):
    tamanho = len(strip_tags(enunciado))

    if tamanho > 950 or (
        len(alternativas) == 5
        and tamanho > 550
    ):
        return "Difícil"

    if tamanho > 350:
        return "Média"

    return "Fácil"


def validar(q):
    motivos = []

    if q["erro"]:
        motivos.append(q["erro"])

    alternativas = q["alternativas"]

    if not all(
        letra in alternativas
        and strip_tags(
            alternativas[letra]
        ).strip()
        for letra in "ABCD"
    ):
        motivos.append(
            "Alternativas incompletas"
        )

    if (
        "E" in alternativas
        and not strip_tags(
            alternativas["E"]
        ).strip()
    ):
        motivos.append(
            "Alternativa E vazia"
        )

    if (
        not q["gabarito"]
        or q["gabarito"] not in alternativas
    ):
        motivos.append(
            "Gabarito não identificado"
        )

    if not strip_tags(
        " ".join(q["enunciado"])
    ).strip():
        motivos.append(
            "Enunciado vazio"
        )

    return motivos


class Command(BaseCommand):
    help = (
        "Importa questões DOCX sem alterar ou excluir "
        "registros existentes. Use --commit para salvar."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "pasta",
            nargs="?",
            default="documentos_questoes",
        )

        parser.add_argument(
            "--commit",
            action="store_true",
        )

        parser.add_argument(
            "--fonte",
            default="IFRN",
        )

        parser.add_argument(
            "--detalhes",
            action="store_true",
        )

    def handle(self, *args, **opcoes):
        pasta = Path(opcoes["pasta"])

        if not pasta.is_dir():
            raise CommandError(
                "Pasta não encontrada: " + str(pasta)
            )

        arquivos = sorted(
            pasta.rglob("*.docx")
        )

        arquivos = [
            x for x in arquivos
            if not x.name.startswith("~$")
        ]

        if not arquivos:
            raise CommandError(
                "Nenhum DOCX encontrado."
            )

        totais = Counter()
        dificuldades = Counter()

        existentes = {
            normalizar(q.enunciado)
            for q in Questao.objects.only(
                "enunciado"
            ).iterator()
        }

        vistos = set(existentes)

        for arquivo in arquivos:
            relativo = arquivo.relative_to(pasta)

            disciplina_nome = (
                relativo.parts[0]
                if len(relativo.parts) > 1
                else "Geral"
            )

            assunto_nome = arquivo.stem[:50]

            self.stdout.write(
                "\n"
                + disciplina_nome
                + " / "
                + assunto_nome
            )

            try:
                documento = Document(
                    str(arquivo)
                )

                perguntas = extrair(
                    documento
                )

            except Exception as erro:
                totais["erros"] += 1

                self.stderr.write(
                    str(arquivo)
                    + ": "
                    + str(erro)
                )

                continue

            for q in perguntas:
                totais["encontradas"] += 1

                motivos = validar(q)

                enunciado = (
                    "<p>"
                    + "</p><p>".join(
                        x for x in q["enunciado"] if x
                    )
                    + "</p>"
                )

                chave = normalizar(
                    enunciado
                )

                if chave in vistos:
                    totais["duplicadas"] += 1

                    self.stdout.write(
                        "Questão "
                        + str(q["numero"])
                        + ": DUPLICADA"
                    )

                    continue

                if motivos:
                    totais["descartadas"] += 1

                    self.stdout.write(
                        "Questão "
                        + str(q["numero"])
                        + ": DESCARTADA — "
                        + "; ".join(motivos)
                    )

                    continue

                vistos.add(chave)

                nivel = dificuldade(
                    enunciado,
                    q["alternativas"],
                )

                dificuldades[nivel] += 1
                totais["prontas"] += 1

                self.stdout.write(
                    "Questão "
                    + str(q["numero"])
                    + ": PRONTA | "
                    + nivel
                )

                if not opcoes["commit"]:
                    continue

                try:
                    with transaction.atomic():
                        disciplina, _ = (
                            Disciplina.objects.get_or_create(
                                nome=disciplina_nome[:20]
                            )
                        )

                        assunto, _ = (
                            Assunto.objects.get_or_create(
                                nome=assunto_nome,
                                disciplina=disciplina,
                            )
                        )

                        fonte, _ = (
                            Fonte.objects.get_or_create(
                                nome=opcoes["fonte"][:100]
                            )
                        )

                        campos = {
                            "disciplina": disciplina,
                            "assunto": assunto,
                            "fonte": fonte,
                            "dificuldade": nivel,
                            "enunciado": imagem_em_html(
                                enunciado,
                                documento,
                                True,
                            ),
                            "gabarito_comentado": imagem_em_html(
                                q["comentario"],
                                documento,
                                True,
                            ),
                            "alternativa_correta": q["gabarito"],
                            "ano": q["ano"],
                        }

                        for letra in "ABCDE":
                            campos[
                                "alternativa_" + letra.lower()
                            ] = imagem_em_html(
                                q["alternativas"].get(
                                    letra,
                                    "",
                                ),
                                documento,
                                True,
                            )

                        Questao.objects.create(
                            **campos
                        )

                    totais["salvas"] += 1

                except Exception as erro:
                    totais["erros"] += 1

                    vistos.discard(
                        chave
                    )

                    self.stderr.write(
                        "Falha na questão "
                        + str(q["numero"])
                        + ": "
                        + str(erro)
                    )

        self.stdout.write(
            "\n========== RESUMO =========="
        )

        for nome, chave in (
            ("Encontradas", "encontradas"),
            ("Salvas", "salvas"),
            ("Prontas", "prontas"),
            ("Duplicadas", "duplicadas"),
            ("Descartadas", "descartadas"),
            ("Erros", "erros"),
        ):
            self.stdout.write(
                nome
                + ": "
                + str(totais[chave])
            )

        for nome in (
            "Fácil",
            "Média",
            "Difícil",
        ):
            self.stdout.write(
                nome
                + "s: "
                + str(dificuldades[nome])
            )

        if not opcoes["commit"]:
            self.stdout.write(
                "\nSimulação finalizada. "
                "Banco não alterado."
            )

        else:
            self.stdout.write(
                "\nImportação finalizada. "
                "Registros anteriores não foram excluídos."
            )
