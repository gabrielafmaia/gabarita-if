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


@login_required
def cadernos(request):
    return render(request, "listar.html", _context_cadernos(request))


def _context_cadernos(request):
    cadernos = Caderno.objects.filter(usuario=request.user).order_by("id")
    paginator = Paginator(cadernos, 10)
    cadernos_paginados = paginator.get_page(request.GET.get("p"))
    return {
        "titulo_pagina": "Cadernos",
        "subtitulo_pagina": "Aqui você pode cadastrar seus cadernos.",
        "nome": "caderno",
        "url_criar": "gabarita_if:ajax-criar-caderno",
        "partial": "gabarita_if/partials/_card_caderno.html",
        "objects": cadernos_paginados,
    }


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
            {
                "form": form,
                "url_criar": "gabarita_if:ajax-criar-caderno",
                "disciplinas": Disciplina.objects.all().order_by("nome"),
                "assuntos": Assunto.objects.select_related("disciplina").all().order_by("nome"),
                "fontes": Fonte.objects.all().order_by("nome"),
                "is_edicao": False,
                "titulo_modal": "Criar",  # 👈 ADICIONADO
            },
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

        post_data = request.POST.copy()

        if not post_data.get("disciplina"):
            primeira_disciplina = post_data.get("blocos[0][disciplina]")
            if primeira_disciplina:
                post_data["disciplina"] = primeira_disciplina
            else:
                primeira_cadastrada = Disciplina.objects.first()
                if primeira_cadastrada:
                    post_data["disciplina"] = primeira_cadastrada.id

        if "cor" in post_data and not post_data.get("cor"):
            post_data.pop("cor", None)

        if "quantidade" in post_data:
            post_data.pop("quantidade", None)

        form = CadernoForm(post_data, request.FILES)

        if form.is_valid():
            try:
                caderno = form.save(commit=False)
                caderno.usuario = request.user
                caderno.save()
                form.save_m2m()

                blocos_processados = 0
                if "processar_blocos" in globals():
                    blocos_processados = processar_blocos(request.POST, caderno)

                logger.info(f"✅ Caderno '{caderno.nome}' criado com sucesso")

                messages.success(request, f"Caderno '{caderno.nome}' criado com sucesso!")

                if blocos_processados > 0:
                    messages.success(request, f"Caderno criado com {blocos_processados} bloco(s)!")
                else:
                    messages.warning(request, "Caderno criado, mas nenhum bloco foi adicionado.")

                return render_crud_response(request, _context_cadernos(request))

            except Exception as e:
                logger.error(f"❌ Erro ao criar caderno: {str(e)}")
                messages.error(request, f"Erro ao criar caderno: {str(e)}")

                if is_ajax:
                    return JsonResponse({"success": False, "errors": str(e)}, status=400)

                return render(
                    request,
                    "gabarita_if/partials/_form_caderno.html",
                    {
                        "form": form,
                        "url_criar": "gabarita_if:ajax-criar-caderno",
                        "disciplinas": Disciplina.objects.all().order_by("nome"),
                        "assuntos": Assunto.objects.select_related("disciplina").all().order_by("nome"),
                        "fontes": Fonte.objects.all().order_by("nome"),
                        "is_edicao": False,
                        "titulo_modal": "Criar",
                    },
                )

        logger.error(f"❌ Erros no formulário: {form.errors}")
        messages.error(request, "Falha ao criar caderno! Verifique os dados fornecidos.")

        if is_ajax:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

        return render(
            request,
            "gabarita_if/partials/_form_caderno.html",
            {
                "form": form,
                "url_criar": "gabarita_if:ajax-criar-caderno",
                "disciplinas": Disciplina.objects.all().order_by("nome"),
                "assuntos": Assunto.objects.select_related("disciplina").all().order_by("nome"),
                "fontes": Fonte.objects.all().order_by("nome"),
                "is_edicao": False,
                "titulo_modal": "Criar",
            },
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
        "disciplinas": Disciplina.objects.all().order_by("nome"),
        "assuntos": Assunto.objects.select_related("disciplina").all().order_by("nome"),
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

    return render(request, "gabarita_if/detalhar_caderno.html", context)


@login_required
def ajax_editar_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        form = CadernoForm(request.POST, request.FILES, instance=caderno)

        if form.is_valid():
            form.save()

            messages.success(request, "Caderno atualizado com sucesso!")

            return render_crud_response(request, _context_cadernos(request))

        messages.error(request, "Falha ao atualizar caderno!")

    else:
        form = CadernoForm(instance=caderno)

    context = {
        "form": form,
        "partial_form": "gabarita_if/partials/_form_caderno.html",  # 👈 ADICIONADO
        "titulo_modal": "Editar",  # 👈 ADICIONADO
        "url_criar": "gabarita_if:ajax-editar-caderno",  # 👈 útil para o action do form
        "disciplinas": Disciplina.objects.all().order_by("nome"),  # 👈 FALTAVA
        "assuntos": Assunto.objects.select_related("disciplina").all().order_by("nome"),  # 👈 FALTAVA
        "fontes": Fonte.objects.all().order_by("nome"),  # 👈 FALTAVA
        "is_edicao": True,  # 👈 Útil para o template diferenciar
    }

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