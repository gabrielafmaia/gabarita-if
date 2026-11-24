import glob
import hashlib
import os
import re
import zipfile
import pymupdf
from django.conf import settings
from gabarita_if.models import Assunto, Avaliacao, Disciplina, Fonte, Questao, TextoApoio


def extrair_gabarito_pdf(doc):
    """Extrai um dicionário {1: 'A', ..., 40: 'D'} (ou 'ANULADA') de qualquer formato de gabarito do IFRN."""
    linhas = []
    for page in doc:
        for line in page.get_text("text").splitlines():
            s = line.strip()
            if s:
                linhas.append(s)

    idx_def = None
    for i, l in enumerate(linhas):
        if "gabarito definitivo" in l.lower():
            idx_def = i
    if idx_def is not None:
        linhas = linhas[idx_def:]

    tokens_brutos = []
    for l in linhas:
        # Ignora linhas explicativas de rodapé ("X = ANULADA", "A questão 22 da prova...")
        if re.match(r"^(X\s*=|.*foi anulada)", l.strip(), re.IGNORECASE):
            continue
        for tok in l.split():
            t = tok.strip("().- ")
            if t:
                tokens_brutos.append(t)

    gabarito = {}

    # Padrão 1 (prioritário): blocos de números (ex: 1..20) seguidos por bloco de 20 letras (2013-2019, 2023-2025)
    tokens = []
    for t in tokens_brutos:
        u = t.upper()
        if re.fullmatch(r"0?\d{1,2}", u) and 1 <= int(u) <= 40:
            tokens.append(int(u))
        elif u in ("A", "B", "C", "D", "X", "X*", "*", "ANULADA", "NULA"):
            tokens.append("ANULADA" if u in ("X", "X*", "*", "ANULADA", "NULA") else u)

    idx = 0
    while idx < len(tokens):
        nums_bloco = []
        while idx < len(tokens) and isinstance(tokens[idx], int):
            nums_bloco.append(tokens[idx])
            idx += 1
        letras_bloco = []
        while idx < len(tokens) and isinstance(tokens[idx], str):
            letras_bloco.append(tokens[idx])
            idx += 1
        if len(nums_bloco) >= 10 and len(nums_bloco) == len(letras_bloco):
            for n, let in zip(nums_bloco, letras_bloco):
                gabarito[n] = let

    # Padrão 2 (fallback): pares sequenciais ("1" seguido de "B", "36" seguido de "ANULADA") - 2011, 2012, 2020, 2022
    if len(gabarito) < 40:
        i = 0
        while i < len(tokens_brutos) - 1:
            m_num = re.fullmatch(r"0?(\d{1,2})", tokens_brutos[i])
            val_prox = tokens_brutos[i + 1].upper()
            if m_num and val_prox in ("A", "B", "C", "D", "X", "X*", "*", "ANULADA", "NULA"):
                num = int(m_num.group(1))
                if 1 <= num <= 40:
                    gabarito[num] = "ANULADA" if val_prox in ("X", "X*", "*", "ANULADA", "NULA") else val_prox
                    i += 2
                    continue
            i += 1

    return gabarito


def salvar_imagem_pdf(doc, xref, pasta_destino):
    try:
        base_img = doc.extract_image(xref)
    except Exception:
        return None
    if not base_img or "image" not in base_img:
        return None

    largura = base_img.get("width", 0)
    altura = base_img.get("height", 0)
    if largura < 60 or altura < 45:
        return None

    img_bytes = base_img["image"]
    ext = "." + base_img.get("ext", "png").lower()
    nome_hash = hashlib.md5(img_bytes).hexdigest() + ext
    caminho_fisico = os.path.join(pasta_destino, nome_hash)

    if not os.path.exists(caminho_fisico):
        with open(caminho_fisico, "wb") as f:
            f.write(img_bytes)

    media_url = getattr(settings, "MEDIA_URL", "/media/")
    if not media_url.endswith("/"):
        media_url += "/"
    return f"{media_url}questoes_importadas/{nome_hash}"


def eh_cabecalho_ou_rodape(texto, y_top, page_height):
    t = texto.strip()
    if not t:
        return True
    if re.fullmatch(r"\d{1,2}", t) and (y_top < 95 or y_top > page_height - 70):
        return True
    padroes_ignorar = [
        r"^IFRN\s*[–\-]\s*PROCESSO SELETIVO",
        r"^IFRN\s*[–\-]\s*Exame de Sele",
        r"^EDITAL\s*N[º°\.]",
        r"^Edital\s+\d+/",
        r"^EXAME DE SELEÇÃO",
        r"^Processo Seletivo\s*[–\-]\s*Cursos Técnicos",
        r"^Caderno de Provas?$",
    ]
    if y_top < 115 or y_top > page_height - 60:
        for pad in padroes_ignorar:
            if re.search(pad, t, re.IGNORECASE):
                return True
    return False


def extrair_itens_ordenados_pdf(doc, pasta_destino):
    """Extrai blocos de texto e imagens das páginas de prova (pula capa e redação)."""
    itens = []
    prova_iniciada = False

    for page_idx, page in enumerate(doc):
        if page_idx == 0:
            continue

        page_height = page.rect.height
        page_dict = page.get_text("dict")
        blocos_pagina = []

        for b in page_dict.get("blocks", []):
            if b.get("type") == 0:
                y0 = b["bbox"][1]
                linhas_bloco = []
                for line in b.get("lines", []):
                    txt_line = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
                    if txt_line:
                        linhas_bloco.append(txt_line)
                texto_bloco = "\n".join(linhas_bloco).strip()
                if not texto_bloco:
                    continue
                if eh_cabecalho_ou_rodape(texto_bloco, y0, page_height):
                    continue
                blocos_pagina.append((y0, "texto", texto_bloco))

        for img_info in page.get_image_info(xrefs=True):
            xref = img_info.get("xref")
            bbox = img_info.get("bbox", (0, 0, 0, 0))
            y0 = bbox[1]
            if y0 < 75:
                continue
            if xref:
                url_img = salvar_imagem_pdf(doc, xref, pasta_destino)
                if url_img:
                    blocos_pagina.append((y0, "imagem", url_img))

        blocos_pagina.sort(key=lambda x: x[0])

        for _, tipo, conteudo in blocos_pagina:
            if tipo == "texto":
                if re.search(
                    r"^(PROPOSTA DE )?PRODUÇÃO TEXTUAL|FOLHA DE RASCUNHO\s*[–\-]\s*REDAÇÃO|REDAÇÃO$",
                    conteudo.strip(),
                    re.IGNORECASE,
                ):
                    return itens

                if not prova_iniciada:
                    if re.search(
                        r"LÍNGUA PORTUGUESA|TEXTO\s+[0-9IVX]+|QUESTÕES DE MÚLTIPLA ESCOLHA|^0?1[\.\)]\s*",
                        conteudo,
                        re.IGNORECASE,
                    ):
                        prova_iniciada = True
                    else:
                        continue

                for linha in conteudo.splitlines():
                    linha_limpa = linha.strip()
                    if not linha_limpa:
                        continue
                    partes_alt = re.split(r"(?<=\S)\s+(?=[a-dA-D]\)\s)", linha_limpa)
                    for sub in partes_alt:
                        sub_s = sub.strip()
                        if sub_s:
                            itens.append(("texto", sub_s))
            elif tipo == "imagem" and prova_iniciada:
                itens.append(("imagem", conteudo))

    return itens


def extrair_numeros_questoes(texto_instrucao):
    m = re.search(
        r"quest[õo](?:es|ao|ão)(?:\s+de\s+n[úu]mero)?\s+([\d,\s eE\-aA]+)",
        texto_instrucao,
        re.IGNORECASE,
    )
    if not m:
        return []
    trecho = m.group(1)
    numeros = set()
    for intervalo in re.finditer(r"0?(\d+)\s*(?:a|-)\s*0?(\d+)", trecho):
        ini, fim = int(intervalo.group(1)), int(intervalo.group(2))
        if fim >= ini and (fim - ini) <= 40:
            numeros.update(range(ini, fim + 1))
    for num in re.findall(r"\d+", trecho):
        numeros.add(int(num))
    return sorted(numeros)


def parsear_prova_pdf(doc, pasta_destino, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao):
    itens = extrair_itens_ordenados_pdf(doc, pasta_destino)

    disciplina_atual = disc_port
    assunto_atual = assunto_port

    textos_apoio = []
    ta_atual = None
    questoes = []
    q_atual = None
    contexto_pre_questao = []
    em_texto_apoio = False
    numeros_ja_vistos = set()

    def fechar_ta():
        nonlocal ta_atual, em_texto_apoio
        if ta_atual and ta_atual["html_partes"]:
            textos_apoio.append(ta_atual)
        ta_atual = None
        em_texto_apoio = False

    def fechar_q():
        nonlocal q_atual
        if q_atual:
            questoes.append(q_atual)
            q_atual = None

    for tipo, conteudo in itens:
        if tipo == "imagem":
            img_html = (
                f'<p><img src="{conteudo}" alt="Imagem da prova IFRN" style="max-width: 100%; height: auto;"></p>'
            )
            if em_texto_apoio and ta_atual is not None:
                ta_atual["html_partes"].append(img_html)
            elif q_atual is not None:
                q_atual["enunciado_partes"].append(img_html)
            elif contexto_pre_questao:
                contexto_pre_questao.append(img_html)
            continue

        txt = conteudo
        txt_upper = txt.upper().strip()

        if re.fullmatch(r"(QUESTÕES DE MÚLTIPLA ESCOLHA\s*[–\-]\s*)?(LÍNGUA PORTUGUESA|PORTUGUÊS)", txt_upper):
            fechar_q()
            fechar_ta()
            disciplina_atual = disc_port
            assunto_atual = assunto_port
            continue

        if re.fullmatch(r"(QUESTÕES DE MÚLTIPLA ESCOLHA\s*[–\-]\s*)?MATEMÁTICA", txt_upper):
            fechar_q()
            fechar_ta()
            disciplina_atual = disc_mat
            assunto_atual = assunto_mat
            continue

        m_ta = re.fullmatch(r"TEXTO\s+([0-9IVX]+)\.?", txt_upper)
        if m_ta:
            fechar_q()
            fechar_ta()
            rotulo = m_ta.group(1)
            ta_atual = {
                "rotulo": rotulo,
                "titulo": f"Texto {rotulo} - {titulo_avaliacao}"[:50],
                "html_partes": [],
            }
            em_texto_apoio = True
            continue

        if re.match(r"^(Para responder|Considere|Leve em considera|Leia)\b", txt, re.IGNORECASE) and re.search(
            r"quest[õo](?:es|ao|ão)(?:\s+de\s+n[úu]mero)?\s+0?\d+", txt, re.IGNORECASE
        ):
            fechar_q()
            fechar_ta()
            contexto_pre_questao = [f"<p>{txt}</p>"]
            continue

        # Ignora números de milhar/decimal (ex: "18.599") para não confundir com "18."
        eh_milhar = bool(re.match(r"^\d{1,2}\.\d{3}\b", txt))
        m_q = None if eh_milhar else re.match(r"^0?(\d{1,2})[\.\)]\s*(.*)", txt)
        if m_q:
            num_q = int(m_q.group(1))
            pode_ser_nova_q = (
                1 <= num_q <= 40
                and num_q not in numeros_ja_vistos
                and (
                    q_atual is None
                    or len(q_atual["alternativas"]) >= 2
                    or num_q == q_atual["numero"] + 1
                )
            )
            if pode_ser_nova_q:
                fechar_q()
                fechar_ta()
                numeros_ja_vistos.add(num_q)
                if num_q >= 21:
                    disciplina_atual = disc_mat
                    assunto_atual = assunto_mat

                resto_enunc = m_q.group(2).strip()
                enunc_init = list(contexto_pre_questao)
                if resto_enunc:
                    enunc_init.append(f"<p>{resto_enunc}</p>")

                if contexto_pre_questao:
                    nums_ctx = extrair_numeros_questoes(re.sub(r"<[^>]+>", "", contexto_pre_questao[0]))
                    if (num_q + 1) not in nums_ctx:
                        contexto_pre_questao = []

                q_atual = {
                    "numero": num_q,
                    "disciplina": disciplina_atual,
                    "assunto": assunto_atual,
                    "enunciado_partes": enunc_init,
                    "alternativas": {},
                }
                continue

        if em_texto_apoio and ta_atual is not None:
            ta_atual["html_partes"].append(f"<p>{txt}</p>")
            continue

        if q_atual is None and contexto_pre_questao:
            contexto_pre_questao.append(f"<p>{txt}</p>")
            continue

        if q_atual is None:
            continue

        m_alt = re.match(r"^([a-dA-D])\)\s*(.*)", txt)
        if m_alt:
            letra = m_alt.group(1).upper()
            if letra not in q_atual["alternativas"]:
                q_atual["alternativas"][letra] = m_alt.group(2).strip()[:500]
                continue

        if not q_atual["alternativas"]:
            q_atual["enunciado_partes"].append(f"<p>{txt}</p>")
        else:
            ultima = list(q_atual["alternativas"].keys())[-1]
            q_atual["alternativas"][ultima] = (q_atual["alternativas"][ultima] + " " + txt).strip()[:500]

    fechar_q()
    fechar_ta()
    questoes.sort(key=lambda item: item["numero"])
    return questoes, textos_apoio


def run():
    zips = [z for z in glob.glob("doc/*.zip") if "Exames" in os.path.basename(z)]
    if not zips:
        print("Nenhum arquivo .zip de Exames de Seleção encontrado na pasta doc/.")
        return

    media_root = getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(), "media"))
    pasta_imagens = os.path.join(media_root, "questoes_importadas")
    os.makedirs(pasta_imagens, exist_ok=True)

    zip_path = zips[0]
    print(f"Lendo arquivo de provas oficiais: {zip_path}\n")

    fonte_ifrn, _ = Fonte.objects.get_or_create(nome="IFRN")
    disc_port, _ = Disciplina.objects.get_or_create(nome="Português")
    disc_mat, _ = Disciplina.objects.get_or_create(nome="Matemática")

    assunto_port, _ = Assunto.objects.get_or_create(nome="Prova Oficial - Português", disciplina=disc_port)
    assunto_mat, _ = Assunto.objects.get_or_create(nome="Prova Oficial - Matemática", disciplina=disc_mat)

    por_ano = {}
    with zipfile.ZipFile(zip_path, "r") as z:
        for caminho in z.namelist():
            if not caminho.lower().endswith(".pdf"):
                continue
            partes = caminho.split("/")
            ano = None
            for p in partes:
                if re.fullmatch(r"20\d{2}", p.strip()):
                    ano = int(p.strip())
                    break
            if not ano:
                continue
            por_ano.setdefault(ano, {"prova": None, "gabarito": None})
            nome_base = os.path.basename(caminho).lower()
            if "gabarito" in nome_base:
                por_ano[ano]["gabarito"] = caminho
            else:
                por_ano[ano]["prova"] = caminho

        total_provas = 0
        total_questoes = 0
        total_textos = 0

        for ano in sorted(por_ano.keys()):
            arq_prova = por_ano[ano]["prova"]
            arq_gab = por_ano[ano]["gabarito"]
            if not arq_prova or not arq_gab:
                print(f"[AVISO] Ano {ano} incompleto (prova={arq_prova}, gabarito={arq_gab})")
                continue

            titulo_avaliacao = f"Exame de Seleção IFRN {ano}"[:50]
            subtitulo_avaliacao = f"Prova Oficial - Cursos Técnicos Integrados ({ano})"[:50]

            if Avaliacao.objects.filter(titulo=titulo_avaliacao, ano=ano, tipo="Prova").exists():
                print(f"[PULADO] Já existe: {titulo_avaliacao}")
                continue

            doc_gab = pymupdf.open(stream=z.read(arq_gab), filetype="pdf")
            gabarito_dict = extrair_gabarito_pdf(doc_gab)

            doc_prova = pymupdf.open(stream=z.read(arq_prova), filetype="pdf")
            questoes_extraidas, textos_apoio_lista = parsear_prova_pdf(
                doc_prova, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao
            )

            questoes_criadas = []
            for q in questoes_extraidas:
                num = q["numero"]
                alts = q["alternativas"]
                for letra_obr in ("A", "B", "C", "D"):
                    alts.setdefault(letra_obr, "-")

                resp_gab = gabarito_dict.get(num, "A")
                if resp_gab == "ANULADA":
                    letra_correta = "A"
                    gab_comentado = "<p><strong>Questão ANULADA</strong> no gabarito oficial do IFRN.</p>"
                else:
                    letra_correta = resp_gab
                    gab_comentado = f"<p>Gabarito Oficial IFRN: <strong>{letra_correta}</strong></p>"

                q_obj = Questao.objects.create(
                    ano=ano,
                    disciplina=q["disciplina"],
                    assunto=q["assunto"],
                    fonte=fonte_ifrn,
                    dificuldade="Média",
                    enunciado="".join(q["enunciado_partes"]),
                    gabarito_comentado=gab_comentado,
                    alternativa_a=alts["A"],
                    alternativa_b=alts["B"],
                    alternativa_c=alts["C"],
                    alternativa_d=alts["D"],
                    alternativa_correta=letra_correta,
                )
                questoes_criadas.append(q_obj)

            textos_criados_ano = 0
            for ta in textos_apoio_lista:
                conteudo_ta = "".join(ta["html_partes"]).strip()
                if not conteudo_ta:
                    continue

                rotulo = ta["rotulo"]
                qs_vinculadas = [
                    q_obj
                    for q_obj in questoes_criadas
                    if re.search(rf"\bTexto\s+{re.escape(rotulo)}\b", q_obj.enunciado, re.IGNORECASE)
                ]
                if not qs_vinculadas:
                    qs_vinculadas = [q_obj for q_obj in questoes_criadas if q_obj.disciplina == disc_port]

                if qs_vinculadas:
                    ta_obj = TextoApoio.objects.create(
                        titulo=ta["titulo"],
                        texto=conteudo_ta,
                    )
                    ta_obj.questoes.set(qs_vinculadas)
                    textos_criados_ano += 1
                    total_textos += 1

            avaliacao = Avaliacao.objects.create(
                titulo=titulo_avaliacao,
                subtitulo=subtitulo_avaliacao,
                fonte=fonte_ifrn,
                ano=ano,
                tipo="Prova",
                blocos=[{"tipo": "questao", "id": q_obj.id} for q_obj in questoes_criadas],
            )
            avaliacao.questoes.set(questoes_criadas)

            total_provas += 1
            total_questoes += len(questoes_criadas)
            print(
                f"{titulo_avaliacao}: {len(questoes_criadas)} questões (gabarito: {len(gabarito_dict)} itens) | {textos_criados_ano} textos de apoio."
            )

    print(
        f"\nConcluído! Provas: {total_provas} | Questões: {total_questoes} | Textos de Apoio: {total_textos}"
    )