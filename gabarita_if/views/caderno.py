from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
import random
import re
import logging
from gabarita_if.models import *
from gabarita_if.forms import CadernoForm
from gabarita_if.filters import QuestaoFiltro
from dashboard.views.htmx import render_crud_response, render_form_response

logger = logging.getLogger(__name__)


def processar_blocos(post_data, caderno):
    """Seleciona as questões dos blocos usando os filtros do caderno."""
    indices = sorted({
        int(match.group(1))
        for key in post_data
        if (match := re.match(r"blocos\[(\d+)\]\[quantidade\]$", key))
    })

    questoes_selecionadas = []
    for indice in indices:
        quantidade = int(post_data.get(f"blocos[{indice}][quantidade]", 0) or 0)
        if quantidade <= 0:
            continue

        questoes = Questao.objects.all()
        disciplina = post_data.get(f"blocos[{indice}][disciplina]")
        assunto = post_data.get(f"blocos[{indice}][assunto]")

        if disciplina:
            questoes = questoes.filter(disciplina_id=disciplina)
        if assunto:
            questoes = questoes.filter(assunto_id=assunto)
        if caderno.dificuldade:
            questoes = questoes.filter(dificuldade__in=caderno.dificuldade)

        if caderno.instituicao_id:
            questoes = questoes.filter(fonte_id=caderno.instituicao_id)

        # O status é relativo às respostas avulsas do usuário. Respostas de
        # avaliações não devem alterar o filtro do Caderno.
        respostas_usuario = {
            "respostas__usuario": caderno.usuario,
            "respostas__tentativa": None,
        }
        status = caderno.status_questao
        if status == "nao_respondi":
            questoes = questoes.exclude(**respostas_usuario)
        elif status == "ja_respondi":
            questoes = questoes.filter(**respostas_usuario)
        elif status == "acertei":
            questoes = questoes.filter(**respostas_usuario, respostas__acertou=True)
        elif status == "errei":
            questoes = questoes.filter(**respostas_usuario, respostas__acertou=False)

        disponiveis = list(questoes.distinct())
        random.shuffle(disponiveis)
        questoes_selecionadas.extend(disponiveis[:quantidade])

    caderno.questoes.set(questoes_selecionadas)
    return len(indices)


def extrair_blocos(post_data):
    """Conserva os filtros usados para que o formulário possa ser reaberto."""
    indices = sorted({
        int(match.group(1))
        for key in post_data
        if (match := re.match(r"blocos\[(\d+)\]\[quantidade\]$", key))
    })

    return [
        {
            "indice": indice,
            "disciplina": post_data.get(f"blocos[{indice}][disciplina]", ""),
            "assunto": post_data.get(f"blocos[{indice}][assunto]", ""),
            "quantidade": int(post_data.get(f"blocos[{indice}][quantidade]", 10) or 10),
        }
        for indice in indices
    ]


def salvar_blocos(post_data, caderno):
    caderno.blocos = extrair_blocos(post_data)
    caderno.save(update_fields=["blocos"])


def preparar_dados_caderno(post_data, disciplina_padrao=None):
    """Adiciona ao formulário os campos de modelo enviados pelos blocos."""
    dados = post_data.copy()

    if not dados.get("disciplina"):
        primeira_disciplina = dados.get("blocos[0][disciplina]")
        if primeira_disciplina:
            dados["disciplina"] = primeira_disciplina
        elif disciplina_padrao:
            dados["disciplina"] = disciplina_padrao
        else:
            primeira_cadastrada = Disciplina.objects.first()
            if primeira_cadastrada:
                dados["disciplina"] = primeira_cadastrada.id

    if "cor" in dados and not dados.get("cor"):
        dados.pop("cor", None)

    dados.pop("quantidade", None)
    return dados


def _opcoes_formulario_caderno():
    return {
        "disciplinas": Disciplina.objects.all().order_by("nome"),
        "assuntos": Assunto.objects.select_related("disciplina").all().order_by("nome"),
        "fontes": Fonte.objects.all().order_by("nome"),
    }


def _contexto_formulario_caderno(form, titulo_modal, is_edicao, **kwargs):
    contexto = {
        "form": form,
        "titulo_modal": titulo_modal,
        "is_edicao": is_edicao,
        **_opcoes_formulario_caderno(),
        **kwargs,
    }
    if "blocos" not in contexto:
        instancia = form.instance if form.instance and form.instance.pk else None
        blocos = getattr(instancia, "blocos", None) if instancia else None
        if blocos:
            contexto["blocos"] = blocos
        else:
            contexto["blocos"] = [{
                "indice": 0,
                "disciplina": instancia.disciplina_id if instancia else "",
                "assunto": instancia.assunto_id if instancia and instancia.assunto_id else "",
                "quantidade": instancia.questoes.count() if instancia and instancia.questoes.exists() else 10,
            }]
    return contexto


@login_required
def cadernos(request):
    return render(request, "listar.html", _context_cadernos(request))


def _context_cadernos(request):
    cadernos = Caderno.objects.filter(usuario=request.user).order_by("id")
    paginator = Paginator(cadernos, 10)
    cadernos_paginados = paginator.get_page(request.GET.get("p"))
    return {
        "titulo_pagina": "Cadernos",
        "cadernos_area_estudante": True,
        "subtitulo_pagina": "Aqui você pode cadastrar seus cadernos.",
        "nome": "caderno",
        "url_criar": "gabarita_if:ajax-criar-caderno",
        "partial": "gabarita_if/partials/_card_caderno.html",
        "objects": cadernos_paginados,
    }


def _criar_caderno(request, post_data):
    """Cria um caderno com a mesma preparação usada pelo CRUD normal."""
    form = CadernoForm(post_data, request.FILES)
    if not form.is_valid():
        return None, form

    caderno = form.save(commit=False)
    caderno.usuario = request.user
    caderno.save()
    form.save_m2m()
    salvar_blocos(post_data, caderno)
    processar_blocos(post_data, caderno)
    return caderno, form


@login_required
@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def ajax_criar_caderno(request):
    """Cria um novo caderno via AJAX com suporte a blocos de questões"""

    # GET - Carregar dados para o modal de criação
    if request.method == "GET":
        form = CadernoForm()
        return render(
            request,
            "gabarita_if/partials/_form_caderno.html",
            _contexto_formulario_caderno(
                form,
                titulo_modal="Criar",
                is_edicao=False,
                url_criar="gabarita_if:ajax-criar-caderno",
            ),
        )
    
    # POST - Processar criação
    if request.method == "POST":
        logger.info(f"📝 Dados POST recebidos: {dict(request.POST)}")

        # Detecta requisições AJAX tradicionais e HTMX
        is_ajax = (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.headers.get("HX-Request") == "true"
            or request.META.get("HTTP_HX_REQUEST") == "true"
            or hasattr(request, "htmx") and bool(getattr(request, "htmx"))
        )

        post_data = preparar_dados_caderno(request.POST)

        form = CadernoForm(post_data, request.FILES)

        if form.is_valid():
            try:
                caderno, form = _criar_caderno(request, post_data)

                logger.info(f"✅ Caderno '{caderno.nome}' criado com sucesso")

                messages.success(request, f"Caderno '{caderno.nome}' criado com sucesso!")

                return render_crud_response(request, _context_cadernos(request))

            except Exception as e:
                logger.error(f"❌ Erro ao criar caderno: {str(e)}")
                messages.error(request, f"Erro ao criar caderno: {str(e)}")

                if is_ajax:
                    return JsonResponse({"success": False, "errors": str(e)}, status=400)

                return render(
                    request,
                    "gabarita_if/partials/_form_caderno.html",
                    _contexto_formulario_caderno(
                        form,
                        titulo_modal="Criar",
                        is_edicao=False,
                        url_criar="gabarita_if:ajax-criar-caderno",
                    ),
                )

        logger.error(f"❌ Erros no formulário: {form.errors}")
        messages.error(request, "Falha ao criar caderno! Verifique os dados fornecidos.")

        if is_ajax:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        return render(
            request,
            "gabarita_if/partials/_form_caderno.html",
            _contexto_formulario_caderno(
                form,
                titulo_modal="Criar",
                is_edicao=False,
                url_criar="gabarita_if:ajax-criar-caderno",
            ),
        )


@login_required
@require_http_methods(["GET", "POST"])
def ajax_adicionar_questao_caderno(request, questao_id):
    questao = get_object_or_404(Questao, id=questao_id)
    cadernos = Caderno.objects.filter(usuario=request.user).order_by("nome")
    cadernos_com_questao = set(
        cadernos.filter(questoes=questao).values_list("id", flat=True)
    )
    contexto = {
        "questao": questao,
        "cadernos": cadernos,
        "cadernos_com_questao": cadernos_com_questao,
    }

    if request.method == "POST":
        cadernos_selecionados = set()
        for caderno_id in request.POST.getlist("caderno_ids"):
            try:
                cadernos_selecionados.add(int(caderno_id))
            except (TypeError, ValueError):
                continue

        ids_permitidos = set(cadernos.values_list("id", flat=True))
        cadernos_selecionados &= ids_permitidos

        if request.POST.getlist("caderno_ids") and not cadernos_selecionados:
            messages.error(request, "Selecione um caderno válido.")
            return render(
                request,
                "gabarita_if/partials/_selecionar_caderno.html",
                contexto,
            )

        for caderno in cadernos:
            if caderno.id in cadernos_selecionados:
                caderno.questoes.add(questao)
            elif caderno.id in cadernos_com_questao:
                caderno.questoes.remove(questao)

        messages.success(request, "Caderno atualizado com sucesso!")
        response = render(request, "gabarita_if/partials/_questao_caderno_response.html")
        response["HX-Trigger"] = "crudSaved"
        return response

    return render(
        request,
        "gabarita_if/partials/_selecionar_caderno.html",
        contexto,
    )


@login_required
@require_http_methods(["GET", "POST"])
def ajax_criar_caderno_para_questao(request, questao_id):
    questao = get_object_or_404(Questao, id=questao_id)
    post_data = preparar_dados_caderno(request.POST)

    if request.method == "POST":
        form = CadernoForm(post_data, request.FILES)
        if form.is_valid():
            try:
                caderno, form = _criar_caderno(request, post_data)
                caderno.questoes.add(questao)
                messages.success(
                    request,
                    f"Caderno '{caderno.nome}' criado e questão adicionada!",
                )
                response = render(
                    request,
                    "gabarita_if/partials/_questao_caderno_response.html",
                )
                response["HX-Trigger"] = "crudSaved"
                return response
            except Exception as error:
                logger.error("Erro ao criar caderno para questão: %s", error)
                messages.error(request, "Erro ao criar o caderno. Tente novamente.")
        else:
            messages.error(request, "Falha ao criar caderno! Verifique os dados fornecidos.")
    else:
        form = CadernoForm()

    return render(
        request,
        "gabarita_if/partials/_form_caderno.html",
        _contexto_formulario_caderno(
            form,
            titulo_modal="Criar caderno",
            is_edicao=False,
            fluxo_questao_id=questao.id,
        ),
    )

@login_required
@require_http_methods(["GET"])
def ajax_adicionar_bloco(request):
    """Retorna um bloco de questões parcial para inserção via HTMX.

    Recebe o parâmetro `index` (0-based) via querystring ou `GET` e
    retorna o HTML do bloco pronto para ser inserido em `#containerBlocos`.
    """
    try:
        index = int(request.GET.get("index", 0))
    except (ValueError, TypeError):
        index = 0

    numero = index + 1

    context = {
        "numero": numero,
        **_opcoes_formulario_caderno(),
    }

    return render(request, "gabarita_if/partials/_bloco_questao.html", context)
    


@login_required
def detalhar_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        questao_id = request.POST.get("questao_id")

        if request.POST.get("refazer"):
            RespostaQuestao.objects.filter(
                usuario=request.user, questao_id=questao_id, tentativa=None
            ).delete()
        else:
            alternativa_escolhida = request.POST.get("alternativa")

            if questao_id and alternativa_escolhida:
                questao = Questao.objects.get(id=questao_id)

                RespostaQuestao.objects.create(
                    usuario=request.user,
                    questao=questao,
                    tentativa=None,
                    alternativa_escolhida=alternativa_escolhida,
                    acertou=(alternativa_escolhida == questao.alternativa_correta),
                )

    filtro = QuestaoFiltro(request.GET, queryset=caderno.questoes.all(), request=request)

    questoes_filtradas = filtro.qs.order_by("id")

    paginator = Paginator(questoes_filtradas, 1)

    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    for questao in questoes_paginadas:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user, questao=questao, tentativa=None
        ).first()

    context = {
        "titulo": caderno.nome,
        "object": caderno,
        "objects": questoes_paginadas,
        "filtro": filtro,
        "titulo_modal": "Detalhar",  # 👈 ADICIONADO
    }

    if request.htmx:
        return render(request, "gabarita_if/partials/_card_questao.html", context)

    return render(request, "gabarita_if/detalhar_caderno.html", context)


@login_required
def ajax_editar_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        post_data = preparar_dados_caderno(
            request.POST,
            disciplina_padrao=caderno.disciplina_id,
        )
        form = CadernoForm(post_data, request.FILES, instance=caderno)

        if form.is_valid():
            caderno = form.save()
            if any(re.match(r"blocos\[\d+\]\[quantidade\]$", key) for key in post_data):
                salvar_blocos(post_data, caderno)
                processar_blocos(post_data, caderno)

            messages.success(request, "Caderno atualizado com sucesso!")

            return render_crud_response(request, _context_cadernos(request))

        logger.error(f"❌ Erros no formulário de edição: {form.errors}")
        messages.error(request, "Falha ao atualizar caderno!")

    else:
        form = CadernoForm(instance=caderno)

    context = _contexto_formulario_caderno(
        form,
        titulo_modal="Editar",
        is_edicao=True,
        partial_form="gabarita_if/partials/_form_caderno.html",
        url_criar="gabarita_if:ajax-editar-caderno",
    )

    if request.method == "POST":
        return render_form_response(request, context)
    return render(request, "editar.html", context)


@login_required
def ajax_remover_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        caderno.delete()

        messages.success(request, "Caderno removido com sucesso!")

        return render_crud_response(request, _context_cadernos(request))

    context = {
        "object": caderno,
        "url_remover": "gabarita_if:ajax-remover-caderno",
        "titulo_modal": "Remover",  
    }

    return render(request, "remover.html", context)
