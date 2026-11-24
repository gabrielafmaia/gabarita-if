import glob
import hashlib
import io
import os
import re
import zipfile
import docx
from django.conf import settings
from gabarita_if.models import Assunto, Disciplina, Fonte, Questao, TextoApoio

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}


def salvar_imagem_relacionamento(part, r_id, pasta_destino):
    """Salva uma imagem embutida do docx em media/questoes_importadas e retorna a URL pública."""
    if r_id not in part.rels:
        return None
    rel = part.rels[r_id]
    if "image" not in rel.reltype:
        return None

    img_bytes = rel.target_part.blob
    ext = os.path.splitext(rel.target_ref)[1].lower() or ".png"
    nome_hash = hashlib.md5(img_bytes).hexdigest() + ext
    caminho_fisico = os.path.join(pasta_destino, nome_hash)

    if not os.path.exists(caminho_fisico):
        with open(caminho_fisico, "wb") as f:
            f.write(img_bytes)

    media_url = getattr(settings, "MEDIA_URL", "/media/")
    if not media_url.endswith("/"):
        media_url += "/"
    return f"{media_url}questoes_importadas/{nome_hash}"


def paragrafo_para_html_e_texto(paragrafo, pasta_destino):
    """Converte um parágrafo do Word em texto limpo e HTML (incluindo imagens embutidas)."""
    texto = paragrafo.text.strip()
    imgs_html = []

    for blip in paragrafo._element.findall(".//a:blip", NS):
        r_id = blip.get(f"{{{NS['r']}}}embed")
        if r_id:
            url_img = salvar_imagem_relacionamento(paragrafo.part, r_id, pasta_destino)
            if url_img:
                imgs_html.append(
                    f'<p><img src="{url_img}" alt="Imagem da questão" style="max-width: 100%; height: auto;"></p>'
                )

    html = ""
    if texto:
        html += f"<p>{texto}</p>"
    html += "".join(imgs_html)
    return texto, html


def extrair_links_paragrafo(paragrafo):
    links = []
    for child in paragrafo._element:
        if child.tag.endswith("hyperlink"):
            r_id = child.get(f"{{{NS['r']}}}id")
            if r_id and r_id in paragrafo.part.rels:
                links.append(paragrafo.part.rels[r_id].target_ref)
    return links


def extrair_numeros_questoes(texto_instrucao):
    """Extrai os números das questões citadas em 'Leia o Texto 1 para responder às questões 1, 2, 3 e 4.'"""
    m = re.search(r"quest[õo](?:es|ao|ão)\s+([\d,\s eE\-aA]+)", texto_instrucao, re.IGNORECASE)
    if not m:
        return []
    trecho = m.group(1)
    # Trata intervalos como "1 a 4" ou "1-4"
    numeros = set()
    for intervalo in re.finditer(r"(\d+)\s*(?:a|-)\s*(\d+)", trecho):
        ini, fim = int(intervalo.group(1)), int(intervalo.group(2))
        if fim >= ini and (fim - ini) <= 30:
            numeros.update(range(ini, fim + 1))
    for num in re.findall(r"\d+", trecho):
        numeros.add(int(num))
    return sorted(numeros)


def run():
    zips = glob.glob("doc/*.zip")
    if not zips:
        print("Nenhum arquivo .zip encontrado na pasta doc/.")
        return

    media_root = getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(), "media"))
    pasta_imagens = os.path.join(media_root, "questoes_importadas")
    os.makedirs(pasta_imagens, exist_ok=True)

    zip_path = zips[0]
    print(f"Lendo arquivo: {zip_path}")
    print(f"Salvando imagens em: {pasta_imagens}\n")

    total_importadas = 0
    total_textos_apoio = 0
    total_ignoradas = 0

    with zipfile.ZipFile(zip_path, "r") as z:
        arquivos_docx = [
            n
            for n in z.namelist()
            if n.endswith(".docx") and not os.path.basename(n).startswith("~$")
        ]

        for caminho in sorted(arquivos_docx):
            partes = caminho.split("/")
            if len(partes) < 3:
                continue

            nome_disciplina = partes[-2].strip()[:20]
            nome_assunto = os.path.splitext(partes[-1])[0].strip()[:50]

            disciplina, _ = Disciplina.objects.get_or_create(nome=nome_disciplina)
            assunto, _ = Assunto.objects.get_or_create(
                nome=nome_assunto, disciplina=disciplina
            )

            doc = docx.Document(io.BytesIO(z.read(caminho)))

            idx_resolucoes = None
            for i, p in enumerate(doc.paragraphs):
                if p.text.strip().lower() in ("resoluções", "resolucoes", "gabarito"):
                    idx_resolucoes = i
                    break

            if idx_resolucoes is None:
                print(f"[AVISO] Seção 'Resoluções' não encontrada em: {caminho}")
                continue

            paragrafos_questoes = doc.paragraphs[:idx_resolucoes]
            paragrafos_resolucoes = doc.paragraphs[idx_resolucoes + 1 :]

            # 1. Mapear resoluções por número da questão (preservando imagens nas resoluções)
            resolucoes = {}
            num_atual = None
            letra_atual = None
            html_res = []

            for p in paragrafos_resolucoes:
                txt, html = paragrafo_para_html_e_texto(p, pasta_imagens)
                if not html:
                    continue

                m_res = re.match(
                    r"^Quest[ãa]o\s+(\d+)\s*:\s*\(?([a-dA-D])\)?", txt, re.IGNORECASE
                )
                m_res_discursiva = re.match(r"^Quest[ãa]o\s+(\d+)\s*:", txt, re.IGNORECASE)

                if m_res:
                    if num_atual and letra_atual:
                        resolucoes[num_atual] = (letra_atual, "".join(html_res))
                    num_atual = int(m_res.group(1))
                    letra_atual = m_res.group(2).upper()
                    html_res = [html]
                elif m_res_discursiva:
                    if num_atual and letra_atual:
                        resolucoes[num_atual] = (letra_atual, "".join(html_res))
                    num_atual = None
                    letra_atual = None
                    html_res = []
                elif txt.lower().startswith("voltar para quest"):
                    if num_atual and letra_atual:
                        resolucoes[num_atual] = (letra_atual, "".join(html_res))
                    num_atual = None
                    letra_atual = None
                    html_res = []
                elif num_atual and letra_atual:
                    html_res.append(html)

            if num_atual and letra_atual:
                resolucoes[num_atual] = (letra_atual, "".join(html_res))

            # 2. Ler Textos de Apoio, Enunciados e Alternativas
            questoes_extraidas = []
            textos_apoio_extraidos = []  # lista de dicts: {titulo, html_partes, questoes_nums}

            q_atual = None
            texto_apoio_atual = None
            questoes_alvo_pendentes = []

            for p in paragrafos_questoes:
                txt, html = paragrafo_para_html_e_texto(p, pasta_imagens)
                if not html:
                    continue

                # Verifica instrução "Leia o(s) Texto(s) ... para responder às questões ..."
                if re.match(r"^Leia\s+(?:o|os|a|as)\s+textos?", txt, re.IGNORECASE):
                    if q_atual:
                        questoes_extraidas.append(q_atual)
                        q_atual = None
                    if texto_apoio_atual:
                        textos_apoio_extraidos.append(texto_apoio_atual)
                        texto_apoio_atual = None
                    questoes_alvo_pendentes = extrair_numeros_questoes(txt)
                    continue

                # Verifica início de bloco "TEXTO 1", "TEXTO 2", "TEXTO I", etc.
                m_texto = re.match(r"^TEXTO\s+([0-9IVX]+)\b[:\-]?\s*(.*)", txt, re.IGNORECASE)
                if m_texto:
                    if q_atual:
                        questoes_extraidas.append(q_atual)
                        q_atual = None
                    if texto_apoio_atual:
                        textos_apoio_extraidos.append(texto_apoio_atual)

                    rotulo = m_texto.group(1).upper()
                    resto = m_texto.group(2).strip()
                    titulo_ta = f"Texto {rotulo} - {nome_assunto}"[:50]
                    partes_iniciais = [f"<p>{resto}</p>"] if resto else []
                    # Se o próprio parágrafo de título tinha imagem embutida:
                    imgs_no_titulo = re.findall(r"<p><img[^>]+></p>", html)
                    partes_iniciais.extend(imgs_no_titulo)

                    texto_apoio_atual = {
                        "titulo": titulo_ta,
                        "html_partes": partes_iniciais,
                        "questoes_nums": list(questoes_alvo_pendentes),
                    }
                    continue

                # Verifica início de nova questão ("1. ...", "2. ...")
                m_q = re.match(r"^(\d+)\.\s*(.+)", txt)
                if m_q:
                    if texto_apoio_atual:
                        textos_apoio_extraidos.append(texto_apoio_atual)
                        texto_apoio_atual = None
                        questoes_alvo_pendentes = []
                    if q_atual:
                        questoes_extraidas.append(q_atual)

                    imgs_no_inicio = "".join(re.findall(r"<p><img[^>]+></p>", html))
                    q_atual = {
                        "numero": int(m_q.group(1)),
                        "texto_inicial": m_q.group(2),
                        "enunciado_html": [imgs_no_inicio] if imgs_no_inicio else [],
                        "alternativas": {},
                        "video": None,
                    }
                    continue

                # Se estamos dentro de um Texto de Apoio, acumula parágrafos e imagens nele
                if texto_apoio_atual is not None:
                    texto_apoio_atual["html_partes"].append(html)
                    continue

                # Se estamos dentro de uma Questão
                if not q_atual:
                    continue

                if "ver resolução em vídeo" in txt.lower() or "ver resolucao em video" in txt.lower():
                    links = extrair_links_paragrafo(p)
                    if links:
                        q_atual["video"] = links[0]
                    continue

                if txt.lower().startswith("ver resposta"):
                    continue

                m_alt = re.match(r"^([a-fA-F])\)\s*(.*)", txt)
                if m_alt:
                    letra = m_alt.group(1).upper()
                    q_atual["alternativas"][letra] = m_alt.group(2).strip()
                else:
                    if not q_atual["alternativas"]:
                        q_atual["enunciado_html"].append(html)
                    else:
                        ultima_letra = list(q_atual["alternativas"].keys())[-1]
                        if txt:
                            q_atual["alternativas"][ultima_letra] += " " + txt

            if texto_apoio_atual:
                textos_apoio_extraidos.append(texto_apoio_atual)
            if q_atual:
                questoes_extraidas.append(q_atual)

            # 3. Salvar Questões no banco e mapear numero -> objeto Questao criado
            mapa_questoes_criadas = {}
            importadas_arq = 0

            for q in questoes_extraidas:
                num = q["numero"]
                alts = q["alternativas"]

                if set(alts.keys()) != {"A", "B", "C", "D"} or num not in resolucoes:
                    total_ignoradas += 1
                    continue

                letra_correta, gabarito_html = resolucoes[num]
                texto_inicial = q["texto_inicial"]

                nome_fonte = "IFRN"
                ano = 2024
                m_meta = re.match(
                    r"^\(([^-\)]+?)\s*-\s*(\d{4})\)\s*(.*)",
                    texto_inicial,
                    re.DOTALL,
                )
                if m_meta:
                    nome_fonte = m_meta.group(1).strip()[:100]
                    ano = int(m_meta.group(2))
                    texto_inicial = m_meta.group(3).strip()

                fonte, _ = Fonte.objects.get_or_create(nome=nome_fonte)

                enunciado_final_html = f"<p>{texto_inicial}</p>" + "".join(q["enunciado_html"])

                questao_obj = Questao.objects.create(
                    ano=ano,
                    disciplina=disciplina,
                    assunto=assunto,
                    fonte=fonte,
                    dificuldade="Média",
                    enunciado=enunciado_final_html,
                    gabarito_comentado=gabarito_html,
                    video_solucao=q["video"],
                    alternativa_a=alts["A"][:500],
                    alternativa_b=alts["B"][:500],
                    alternativa_c=alts["C"][:500],
                    alternativa_d=alts["D"][:500],
                    alternativa_correta=letra_correta,
                )
                mapa_questoes_criadas[num] = questao_obj
                importadas_arq += 1
                total_importadas += 1

            # 4. Salvar Textos de Apoio e vincular às questões correspondentes
            textos_arq = 0
            for ta in textos_apoio_extraidos:
                conteudo_ta = "".join(ta["html_partes"]).strip()
                if not conteudo_ta:
                    continue

                questoes_vinculadas = [
                    mapa_questoes_criadas[n]
                    for n in ta["questoes_nums"]
                    if n in mapa_questoes_criadas
                ]
                # Fallback: se o enunciado citar "Texto X", também vincula
                if not questoes_vinculadas:
                    rotulo_busca = ta["titulo"].split(" - ")[0].lower()
                    for num_q, q_obj in mapa_questoes_criadas.items():
                        if rotulo_busca in q_obj.enunciado.lower():
                            questoes_vinculadas.append(q_obj)

                if questoes_vinculadas:
                    ta_obj = TextoApoio.objects.create(
                        titulo=ta["titulo"],
                        texto=conteudo_ta,
                    )
                    ta_obj.questoes.set(questoes_vinculadas)
                    textos_arq += 1
                    total_textos_apoio += 1

            print(
                f"{nome_disciplina} > {nome_assunto}: {importadas_arq} questões | {textos_arq} textos de apoio."
            )

    print(
        f"\nConcluído! Questões: {total_importadas} | Textos de Apoio: {total_textos_apoio} | Ignoradas: {total_ignoradas}"
    )