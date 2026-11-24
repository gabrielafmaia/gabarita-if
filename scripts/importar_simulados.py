import glob
import hashlib
import io
import os
import re
import zipfile
import docx
from django.conf import settings
from gabarita_if.models import Assunto, Avaliacao, Disciplina, Fonte, Questao, TextoApoio

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}


def salvar_imagem_relacionamento(part, r_id, pasta_destino):
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
    texto = paragrafo.text.strip()
    imgs_html = []

    for blip in paragrafo._element.findall(".//a:blip", NS):
        r_id = blip.get(f"{{{NS['r']}}}embed")
        if r_id:
            url_img = salvar_imagem_relacionamento(paragrafo.part, r_id, pasta_destino)
            if url_img:
                imgs_html.append(
                    f'<p><img src="{url_img}" alt="Imagem do simulado" style="max-width: 100%; height: auto;"></p>'
                )

    html = ""
    if texto:
        html += f"<p>{texto}</p>"
    html += "".join(imgs_html)
    return texto, html


def tem_lista_word(paragrafo):
    pPr = paragrafo._element.pPr
    return pPr is not None and pPr.numPr is not None


def extrair_gabarito_tabela(doc):
    letras = []
    for tabela in doc.tables:
        for row in tabela.rows:
            for cell in row.cells:
                val = cell.text.strip().upper()
                if val in ("A", "B", "C", "D"):
                    letras.append(val)
    return letras


def limpar_prefixo_alternativa(texto):
    return re.sub(r"^[a-dA-D][\)\.\-]\s*", "", texto).strip()


def extrair_numeros_questoes(texto_instrucao):
    m = re.search(r"quest[õo](?:es|ao|ão)\s+([\d,\s eE\-aA]+)", texto_instrucao, re.IGNORECASE)
    if not m:
        return []
    trecho = m.group(1)
    numeros = set()
    for intervalo in re.finditer(r"(\d+)\s*(?:a|-)\s*(\d+)", trecho):
        ini, fim = int(intervalo.group(1)), int(intervalo.group(2))
        if fim >= ini and (fim - ini) <= 40:
            numeros.update(range(ini, fim + 1))
    for num in re.findall(r"\d+", trecho):
        numeros.add(int(num))
    return sorted(numeros)


def processar_modelo_2022_2024(doc, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao):
    """Simulados 2022-2024: questões numeradas '1. ...' e seção 'Resoluções' no final."""
    idx_resolucoes = None
    for i, p in enumerate(doc.paragraphs):
        if p.text.strip().lower() in ("resoluções", "resolucoes"):
            idx_resolucoes = i
            break

    paragrafos_q = doc.paragraphs[:idx_resolucoes] if idx_resolucoes else doc.paragraphs
    paragrafos_res = doc.paragraphs[idx_resolucoes + 1 :] if idx_resolucoes else []

    resolucoes = {}
    num_atual = None
    letra_atual = None
    html_res = []

    for p in paragrafos_res:
        txt, html = paragrafo_para_html_e_texto(p, pasta_imagens)
        if not html:
            continue
        if txt.lower().startswith("voltar para quest") or txt.lower() == "gabarito":
            if num_atual and letra_atual:
                resolucoes[num_atual] = (letra_atual, "".join(html_res))
            num_atual = None
            letra_atual = None
            html_res = []
            continue

        m_res = re.match(r"^Quest[ãa]o\s+(\d+)\s*:\s*\(?([a-dA-D])\)?", txt, re.IGNORECASE)
        if m_res:
            if num_atual and letra_atual:
                resolucoes[num_atual] = (letra_atual, "".join(html_res))
            num_atual = int(m_res.group(1))
            letra_atual = m_res.group(2).upper()
            html_res = [html]
        elif num_atual and letra_atual:
            html_res.append(html)

    if num_atual and letra_atual:
        resolucoes[num_atual] = (letra_atual, "".join(html_res))

    disciplina_atual = disc_port
    assunto_atual = assunto_port
    fase_questoes_iniciada = False

    textos_apoio_lista = []
    texto_apoio_atual = None
    questoes_lista = []
    q_atual = None
    contexto_pre_questao = []

    for p in paragrafos_q:
        txt, html = paragrafo_para_html_e_texto(p, pasta_imagens)
        if not html:
            continue
        txt_upper = txt.upper().strip()

        if txt_upper in ("PORTUGUÊS", "PORTUGUES", "LÍNGUA PORTUGUESA"):
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
                texto_apoio_atual = None
            disciplina_atual = disc_port
            assunto_atual = assunto_port
            fase_questoes_iniciada = True
            continue

        if txt_upper in ("MATEMÁTICA", "MATEMATICA"):
            if q_atual:
                questoes_lista.append(q_atual)
                q_atual = None
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
                texto_apoio_atual = None
            disciplina_atual = disc_mat
            assunto_atual = assunto_mat
            fase_questoes_iniciada = True
            continue

        m_ta = re.match(r"^TEXTO\s+([0-9IVX]+)\b[:\-]?\s*(.*)", txt, re.IGNORECASE)
        if m_ta and not fase_questoes_iniciada:
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
            rotulo = m_ta.group(1).upper()
            resto = m_ta.group(2).strip()
            titulo_ta = f"Texto {rotulo} - {titulo_avaliacao}"[:50]
            partes_init = [f"<p>{resto}</p>"] if resto else []
            imgs_init = re.findall(r"<p><img[^>]+></p>", html)
            partes_init.extend(imgs_init)
            texto_apoio_atual = {"rotulo": rotulo, "titulo": titulo_ta, "html_partes": partes_init}
            continue

        if not fase_questoes_iniciada:
            if texto_apoio_atual is not None:
                texto_apoio_atual["html_partes"].append(html)
            continue

        if re.match(r"^(Considere|Leve em considera|Leia)\b", txt, re.IGNORECASE) and re.search(
            r"quest[õo](?:es|ao|ão)\s+\d+", txt, re.IGNORECASE
        ):
            if q_atual:
                questoes_lista.append(q_atual)
                q_atual = None
            contexto_pre_questao = [html]
            continue

        m_q = re.match(r"^(\d+)\.\s*(.+)", txt)
        if m_q:
            if q_atual:
                questoes_lista.append(q_atual)
            num_q = int(m_q.group(1))
            imgs_inicio = "".join(re.findall(r"<p><img[^>]+></p>", html))
            enunc_inicial = list(contexto_pre_questao) + [f"<p>{m_q.group(2).strip()}</p>"]
            if imgs_inicio:
                enunc_inicial.append(imgs_inicio)

            if contexto_pre_questao:
                nums_ctx = extrair_numeros_questoes(re.sub(r"<[^>]+>", "", contexto_pre_questao[0]))
                if (num_q + 1) not in nums_ctx:
                    contexto_pre_questao = []

            q_atual = {
                "numero": num_q,
                "disciplina": disciplina_atual,
                "assunto": assunto_atual,
                "enunciado_partes": enunc_inicial,
                "alternativas": {},
            }
            continue

        if txt.lower().startswith("ver resposta"):
            continue

        if q_atual is None and contexto_pre_questao:
            contexto_pre_questao.append(html)
            continue

        if q_atual is None:
            continue

        m_alt = re.match(r"^([a-dA-D])\)\s*(.*)", txt)
        if m_alt:
            letra = m_alt.group(1).upper()
            q_atual["alternativas"][letra] = m_alt.group(2).strip()[:500]
        else:
            if not q_atual["alternativas"]:
                q_atual["enunciado_partes"].append(html)
            elif txt:
                ultima = list(q_atual["alternativas"].keys())[-1]
                q_atual["alternativas"][ultima] = (q_atual["alternativas"][ultima] + " " + txt)[:500]

    if q_atual:
        questoes_lista.append(q_atual)

    gabarito_tabela = extrair_gabarito_tabela(doc)
    resultado_questoes = []
    for idx, q in enumerate(questoes_lista):
        num = q["numero"]
        alts = q["alternativas"]
        if set(alts.keys()) != {"A", "B", "C", "D"}:
            continue
        if num in resolucoes:
            letra_correta, res_html = resolucoes[num]
        else:
            letra_correta = gabarito_tabela[idx] if idx < len(gabarito_tabela) else "A"
            res_html = f"<p>Gabarito: {letra_correta}</p>"

        resultado_questoes.append(
            {
                "numero": num,
                "disciplina": q["disciplina"],
                "assunto": q["assunto"],
                "enunciado_html": "".join(q["enunciado_partes"]),
                "alternativas": alts,
                "letra_correta": letra_correta,
                "resposta_html": res_html,
            }
        )

    return resultado_questoes, textos_apoio_lista


def processar_modelo_2021(doc, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao):
    """Simulados 2021: questões numeradas '1. ...' a '40. ...' com 'RESPOSTA' logo abaixo de cada uma."""
    gabarito_tabela = extrair_gabarito_tabela(doc)
    disciplina_atual = disc_port
    assunto_atual = assunto_port
    fase_questoes_iniciada = False

    textos_apoio_lista = []
    texto_apoio_atual = None
    questoes_lista = []
    q_atual = None
    estado = "INICIO"  # INICIO | TEXTO_APOIO | QUESTAO | RESPOSTA
    contexto_pre_questao = []

    for p in doc.paragraphs:
        txt, html = paragrafo_para_html_e_texto(p, pasta_imagens)
        if not html:
            continue
        txt_upper = txt.upper().strip()

        if txt_upper in ("GABARITO", "RESOLUÇÕES", "RESOLUCOES"):
            if q_atual:
                questoes_lista.append(q_atual)
                q_atual = None
            break

        if txt_upper in ("PORTUGUÊS", "PORTUGUES", "LÍNGUA PORTUGUESA"):
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
                texto_apoio_atual = None
            disciplina_atual = disc_port
            assunto_atual = assunto_port
            fase_questoes_iniciada = True
            estado = "QUESTAO"
            continue

        if txt_upper in ("MATEMÁTICA", "MATEMATICA"):
            if q_atual:
                questoes_lista.append(q_atual)
                q_atual = None
            disciplina_atual = disc_mat
            assunto_atual = assunto_mat
            fase_questoes_iniciada = True
            estado = "QUESTAO"
            continue

        m_ta = re.match(r"^TEXTO\s+([0-9IVX]+)\b[:\-]?\s*(.*)", txt, re.IGNORECASE)
        if m_ta and not fase_questoes_iniciada:
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
            rotulo = m_ta.group(1).upper()
            resto = m_ta.group(2).strip()
            titulo_ta = f"Texto {rotulo} - {titulo_avaliacao}"[:50]
            partes_init = [f"<p>{resto}</p>"] if resto else []
            imgs_init = re.findall(r"<p><img[^>]+></p>", html)
            partes_init.extend(imgs_init)
            texto_apoio_atual = {"rotulo": rotulo, "titulo": titulo_ta, "html_partes": partes_init}
            estado = "TEXTO_APOIO"
            continue

        if not fase_questoes_iniciada:
            if texto_apoio_atual is not None:
                texto_apoio_atual["html_partes"].append(html)
            continue

        if re.match(r"^(Considere|Leve em considera|Leia|Para responder)\b", txt, re.IGNORECASE) and re.search(
            r"quest[õo](?:es|ao|ão)\s+\d+", txt, re.IGNORECASE
        ):
            if q_atual:
                questoes_lista.append(q_atual)
                q_atual = None
            contexto_pre_questao = [html]
            estado = "QUESTAO"
            continue

        m_q = re.match(r"^(\d{1,2})\.\s*(.+)", txt)
        if m_q:
            num_q = int(m_q.group(1))
            if 1 <= num_q <= 40:
                if q_atual:
                    questoes_lista.append(q_atual)
                imgs_inicio = "".join(re.findall(r"<p><img[^>]+></p>", html))
                enunc_inicial = list(contexto_pre_questao) + [f"<p>{m_q.group(2).strip()}</p>"]
                if imgs_inicio:
                    enunc_inicial.append(imgs_inicio)

                if contexto_pre_questao:
                    nums_ctx = extrair_numeros_questoes(re.sub(r"<[^>]+>", "", contexto_pre_questao[0]))
                    if (num_q + 1) not in nums_ctx:
                        contexto_pre_questao = []

                q_atual = {
                    "numero": num_q,
                    "disciplina": disciplina_atual,
                    "assunto": assunto_atual,
                    "enunciado_partes": enunc_inicial,
                    "alternativas": {},
                    "resposta_html": [],
                }
                estado = "QUESTAO"
                continue

        if re.match(r"^RESPOSTA\s*:?$", txt_upper):
            estado = "RESPOSTA"
            continue

        if estado == "RESPOSTA" and q_atual is not None:
            q_atual["resposta_html"].append(html)
            continue

        if estado == "QUESTAO":
            if q_atual is None and contexto_pre_questao:
                contexto_pre_questao.append(html)
                continue
            if q_atual is None:
                continue

            m_alt = re.match(r"^([a-dA-D])\)\s*(.*)", txt)
            if m_alt:
                letra = m_alt.group(1).upper()
                q_atual["alternativas"][letra] = m_alt.group(2).strip()[:500]
            else:
                if not q_atual["alternativas"]:
                    q_atual["enunciado_partes"].append(html)
                elif txt:
                    ultima = list(q_atual["alternativas"].keys())[-1]
                    q_atual["alternativas"][ultima] = (q_atual["alternativas"][ultima] + " " + txt)[:500]

    if q_atual:
        questoes_lista.append(q_atual)

    questoes_unicas = {}
    for q in questoes_lista:
        alts = q["alternativas"]
        if set(alts.keys()) != {"A", "B", "C", "D"}:
            continue
        num = q["numero"]
        if num not in questoes_unicas or q["resposta_html"]:
            questoes_unicas[num] = q

    resultado_questoes = []
    for idx, num in enumerate(sorted(questoes_unicas.keys())):
        q = questoes_unicas[num]
        alts = q["alternativas"]
        letra_correta = gabarito_tabela[idx] if idx < len(gabarito_tabela) else "A"
        resultado_questoes.append(
            {
                "numero": q["numero"],
                "disciplina": q["disciplina"],
                "assunto": q["assunto"],
                "enunciado_html": "".join(q["enunciado_partes"]),
                "alternativas": alts,
                "letra_correta": letra_correta,
                "resposta_html": "".join(q["resposta_html"]) or f"<p>Gabarito: {letra_correta}</p>",
            }
        )

    return resultado_questoes, textos_apoio_lista


def processar_modelo_2020(doc, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao):
    """Simulados 2020: questões e alternativas usam lista do Word (numPr), seguidas por 'RESPOSTA' sem lista."""
    gabarito_tabela = extrair_gabarito_tabela(doc)
    disciplina_atual = disc_port
    assunto_atual = assunto_port
    fase_disciplina_iniciada = False

    textos_apoio_lista = []
    texto_apoio_atual = None

    questoes_brutas = []
    estado = "INICIO"
    q_atual = None
    buffer_questao = []

    def finalizar_q():
        nonlocal q_atual, buffer_questao
        if not q_atual:
            return
        itens_texto = [it for it in buffer_questao if it[0]]
        if len(itens_texto) >= 5:
            alts_itens = itens_texto[-4:]
            idx_corte = buffer_questao.index(alts_itens[0])
            enunc_partes = [it[1] for it in buffer_questao[:idx_corte]]
            q_atual["enunciado_html"] = "".join(enunc_partes)
            q_atual["alternativas"] = {
                "A": limpar_prefixo_alternativa(alts_itens[0][0])[:500],
                "B": limpar_prefixo_alternativa(alts_itens[1][0])[:500],
                "C": limpar_prefixo_alternativa(alts_itens[2][0])[:500],
                "D": limpar_prefixo_alternativa(alts_itens[3][0])[:500],
            }
            questoes_brutas.append(q_atual)
        q_atual = None
        buffer_questao = []

    for p in doc.paragraphs:
        txt, html = paragrafo_para_html_e_texto(p, pasta_imagens)
        if not html:
            continue
        txt_upper = txt.upper().strip()
        eh_item_lista = tem_lista_word(p)

        if txt_upper.startswith("GABARITO"):
            finalizar_q()
            break

        if txt_upper in ("PORTUGUÊS", "PORTUGUES", "LÍNGUA PORTUGUESA"):
            finalizar_q()
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
                texto_apoio_atual = None
            disciplina_atual = disc_port
            assunto_atual = assunto_port
            fase_disciplina_iniciada = True
            estado = "QUESTAO"
            q_atual = {"disciplina": disciplina_atual, "assunto": assunto_atual, "resposta_html": []}
            buffer_questao = []
            continue

        if txt_upper in ("MATEMÁTICA", "MATEMATICA"):
            finalizar_q()
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
                texto_apoio_atual = None
            disciplina_atual = disc_mat
            assunto_atual = assunto_mat
            fase_disciplina_iniciada = True
            estado = "QUESTAO"
            q_atual = {"disciplina": disciplina_atual, "assunto": assunto_atual, "resposta_html": []}
            buffer_questao = []
            continue

        m_ta = re.match(r"^TEXTO\s+([0-9IVX]+)\b[:\-]?\s*(.*)", txt, re.IGNORECASE)
        if m_ta and not fase_disciplina_iniciada:
            if texto_apoio_atual:
                textos_apoio_lista.append(texto_apoio_atual)
            rotulo = m_ta.group(1).upper()
            resto = m_ta.group(2).strip()
            titulo_ta = f"Texto {rotulo} - {titulo_avaliacao}"[:50]
            partes_init = [f"<p>{resto}</p>"] if resto else []
            imgs_init = re.findall(r"<p><img[^>]+></p>", html)
            partes_init.extend(imgs_init)
            texto_apoio_atual = {"rotulo": rotulo, "titulo": titulo_ta, "html_partes": partes_init}
            estado = "TEXTO_APOIO"
            continue

        if estado == "TEXTO_APOIO" and texto_apoio_atual is not None:
            texto_apoio_atual["html_partes"].append(html)
            continue

        if re.match(r"^RESPOSTA\s*:?$", txt_upper):
            estado = "RESPOSTA"
            continue

        if estado == "RESPOSTA" and q_atual is not None:
            eh_instrucao_texto = bool(
                re.match(r"^(Leve em considera|Considere|Leia)\b", txt, re.IGNORECASE)
                and re.search(r"quest[õo](?:es|ao|ão)\s+\d+", txt, re.IGNORECASE)
            )
            if eh_item_lista or eh_instrucao_texto:
                finalizar_q()
                estado = "QUESTAO"
                q_atual = {"disciplina": disciplina_atual, "assunto": assunto_atual, "resposta_html": []}
                buffer_questao = [(txt, html)]
            else:
                q_atual["resposta_html"].append(html)
            continue

        if estado == "QUESTAO" and q_atual is not None:
            buffer_questao.append((txt, html))

    finalizar_q()

    resultado_questoes = []
    for idx, q in enumerate(questoes_brutas):
        letra_correta = gabarito_tabela[idx] if idx < len(gabarito_tabela) else "A"
        resultado_questoes.append(
            {
                "numero": idx + 1,
                "disciplina": q["disciplina"],
                "assunto": q["assunto"],
                "enunciado_html": q["enunciado_html"],
                "alternativas": q["alternativas"],
                "letra_correta": letra_correta,
                "resposta_html": "".join(q["resposta_html"]) or f"<p>Gabarito: {letra_correta}</p>",
            }
        )

    return resultado_questoes, textos_apoio_lista


def run():
    zips = [z for z in glob.glob("doc/*.zip") if "Simulado" in os.path.basename(z)]
    if not zips:
        print("Nenhum arquivo .zip de simulados encontrado na pasta doc/.")
        return

    media_root = getattr(settings, "MEDIA_ROOT", os.path.join(os.getcwd(), "media"))
    pasta_imagens = os.path.join(media_root, "questoes_importadas")
    os.makedirs(pasta_imagens, exist_ok=True)

    zip_path = zips[0]
    print(f"Lendo arquivo de simulados: {zip_path}\n")

    fonte_simulado, _ = Fonte.objects.get_or_create(nome="Meta IFRN")
    disc_port, _ = Disciplina.objects.get_or_create(nome="Português")
    disc_mat, _ = Disciplina.objects.get_or_create(nome="Matemática")

    assunto_port, _ = Assunto.objects.get_or_create(nome="Simulado - Português", disciplina=disc_port)
    assunto_mat, _ = Assunto.objects.get_or_create(nome="Simulado - Matemática", disciplina=disc_mat)

    total_simulados = 0
    total_questoes = 0
    total_textos = 0

    with zipfile.ZipFile(zip_path, "r") as z:
        arquivos_docx = [
            n
            for n in z.namelist()
            if n.endswith(".docx") and not os.path.basename(n).startswith("~$")
        ]

        for caminho in sorted(arquivos_docx):
            nome_arquivo = os.path.splitext(os.path.basename(caminho))[0].strip()
            partes_caminho = caminho.split("/")

            ano = 2024
            for parte in partes_caminho:
                if re.fullmatch(r"20\d{2}", parte.strip()):
                    ano = int(parte.strip())
                    break
            else:
                m_ano = re.search(r"(20\d{2})", nome_arquivo)
                if m_ano:
                    ano = int(m_ano.group(1))

            titulo_avaliacao = nome_arquivo[:50]
            subtitulo_avaliacao = f"Simulado Meta IFRN - {ano}"[:50]

            if Avaliacao.objects.filter(titulo=titulo_avaliacao, ano=ano, tipo="Simulado").exists():
                print(f"[PULADO] Já existe: {titulo_avaliacao} ({ano})")
                continue

            doc = docx.Document(io.BytesIO(z.read(caminho)))

            tem_secao_resolucoes = any(
                p.text.strip().lower() in ("resoluções", "resolucoes") for p in doc.paragraphs
            )
            tem_questoes_numeradas = any(
                re.match(r"^1\.\s+\S", p.text.strip()) for p in doc.paragraphs
            )

            if tem_secao_resolucoes:
                questoes_extraidas, textos_apoio_lista = processar_modelo_2022_2024(
                    doc, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao
                )
            elif tem_questoes_numeradas:
                questoes_extraidas, textos_apoio_lista = processar_modelo_2021(
                    doc, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao
                )
            else:
                questoes_extraidas, textos_apoio_lista = processar_modelo_2020(
                    doc, pasta_imagens, disc_port, disc_mat, assunto_port, assunto_mat, titulo_avaliacao
                )

            if not questoes_extraidas:
                print(f"[AVISO] Nenhuma questão extraída de: {caminho}")
                continue

            questoes_criadas = []
            for q in questoes_extraidas:
                q_obj = Questao.objects.create(
                    ano=ano,
                    disciplina=q["disciplina"],
                    assunto=q["assunto"],
                    fonte=fonte_simulado,
                    dificuldade="Média",
                    enunciado=q["enunciado_html"],
                    gabarito_comentado=q["resposta_html"],
                    alternativa_a=q["alternativas"]["A"],
                    alternativa_b=q["alternativas"]["B"],
                    alternativa_c=q["alternativas"]["C"],
                    alternativa_d=q["alternativas"]["D"],
                    alternativa_correta=q["letra_correta"],
                )
                questoes_criadas.append(q_obj)

            textos_criados_arq = 0
            for ta in textos_apoio_lista:
                conteudo_ta = "".join(ta["html_partes"]).strip()
                if not conteudo_ta:
                    continue

                rotulo_num = ta["rotulo"]
                qs_vinculadas = [
                    q_obj
                    for q_obj in questoes_criadas
                    if re.search(rf"\bTexto\s+{re.escape(rotulo_num)}\b", q_obj.enunciado, re.IGNORECASE)
                ]
                if not qs_vinculadas:
                    qs_vinculadas = [q_obj for q_obj in questoes_criadas if q_obj.disciplina == disc_port]

                if qs_vinculadas:
                    ta_obj = TextoApoio.objects.create(
                        titulo=ta["titulo"],
                        texto=conteudo_ta,
                    )
                    ta_obj.questoes.set(qs_vinculadas)
                    textos_criados_arq += 1
                    total_textos += 1

            avaliacao = Avaliacao.objects.create(
                titulo=titulo_avaliacao,
                subtitulo=subtitulo_avaliacao,
                fonte=fonte_simulado,
                ano=ano,
                tipo="Simulado",
                blocos=[{"tipo": "questao", "id": q_obj.id} for q_obj in questoes_criadas],
            )
            avaliacao.questoes.set(questoes_criadas)

            total_simulados += 1
            total_questoes += len(questoes_criadas)
            print(
                f"{titulo_avaliacao} ({ano}): {len(questoes_criadas)} questões | {textos_criados_arq} textos de apoio."
            )

    print(
        f"\nConcluído! Simulados: {total_simulados} | Questões: {total_questoes} | Textos de Apoio: {total_textos}"
    )