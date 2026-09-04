import logging
import random
import re
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from gabarita_if.filters import QuestaoFiltro
from gabarita_if.forms import CadernoForm
from gabarita_if.models import (
    Assunto,
    Caderno,
    Disciplina,
    Fonte,
    Questao,
    RespostaQuestao,
)

logger = logging.getLogger(__name__)


@login_required
def cadernos(request):
    cadernos = Caderno.objects.filter(usuario=request.user).order_by("-id")

    paginator = Paginator(cadernos, 10)
    numero_da_pagina = request.GET.get("p")
    cadernos_paginados = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Cadernos",
        "subtitulo_pagina": "Aqui você pode cadastrar seus cadernos.",
        "nome": "caderno",
        "url_criar": "gabarita_if:ajax-criar-caderno",
        "partial": "gabarita_if/partials/_card_caderno.html",
        "objects": cadernos_paginados,
    }

    return render(request, "listar.html", context)


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
            },
        )

    # POST - Processar criação
    if request.method == "POST":
        logger.info(f"📝 Dados POST recebidos: {dict(request.POST)}")
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        post_data = request.POST.copy()
        
        # Garante que se a disciplina não veio diretamente, mas veio nos blocos, nós atribuímos
        if not post_data.get('disciplina'):
            primeira_disciplina = post_data.get('blocos[0][disciplina]')
            if primeira_disciplina:
                post_data['disciplina'] = primeira_disciplina
            else:
                # Fallback seguro caso não venha nenhuma (pega a primeira do banco para não dar erro)
                primeira_cadastrada = Disciplina.objects.first()
                if primeira_cadastrada:
                    post_data['disciplina'] = primeira_cadastrada.id

        # Remove 'cor' se não for necessário ou se estiver vazio
        if 'cor' in post_data and not post_data.get('cor'):
            post_data.pop('cor', None)
        
        # Remove 'quantidade' do nível principal (já está nos blocos)
        if 'quantidade' in post_data:
            post_data.pop('quantidade', None)
        
        # Cria o formulário com os dados limpos
        form = CadernoForm(post_data, request.FILES)

        if form.is_valid():
            try:
                caderno = form.save(commit=False)
                caderno.usuario = request.user
                caderno.save()
                form.save_m2m()

                # Processar os blocos de questões (caso a função exista no projeto)
                blocos_processados = 0
                if 'processar_blocos' in globals():
                    blocos_processados = processar_blocos(request.POST, caderno)

                logger.info(f"✅ Caderno '{caderno.nome}' criado com sucesso")
                
                messages.success(request, f"Caderno '{caderno.nome}' criado com sucesso!")
                
                if is_ajax:
                    return JsonResponse({
                        "success": True,
                        "status": "ok",
                        "mensagem": f"Caderno '{caderno.nome}' criado com sucesso!",
                        "caderno_id": caderno.id,
                    }, status=201)

                return redirect('gabarita_if:cadernos')

            except Exception as e:
                logger.error(f"❌ Erro ao criar caderno: {str(e)}")
                messages.error(request, f"Erro ao criar caderno: {str(e)}")
                
                if is_ajax:
                    return JsonResponse({
                        "success": False,
                        "errors": str(e)
                    }, status=400)
                
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
                    },
                )

        # Se o formulário não for válido
        logger.error(f"❌ Erros no formulário: {form.errors}")
        messages.error(request, "Falha ao criar caderno! Verifique os dados fornecidos.")
        
        if is_ajax:
            return JsonResponse({
                "success": False,
                "errors": form.errors
            }, status=400)
        
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
            },
        )


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
                    acertou=(
                        alternativa_escolhida == questao.alternativa_correta
                    ),
                )

    filtro = QuestaoFiltro(
        request.GET, queryset=caderno.questoes.all(), request=request
    )

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

            return JsonResponse(
                {"mensagem": "Caderno atualizado com sucesso!", "success": True}, 
                status=200
            )

        messages.error(request, "Falha ao atualizar caderno!")

    else:
        form = CadernoForm(instance=caderno)

    return render(request, "editar.html", {"form": form})


@login_required
def ajax_remover_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        caderno.delete()

        messages.success(request, "Caderno removido com sucesso!")

        return redirect("gabarita_if:cadernos")

    context = {
        "object": caderno,
        "url_remover": "gabarita_if:ajax-remover-caderno",
    }

    return render(request, "remover.html", context)