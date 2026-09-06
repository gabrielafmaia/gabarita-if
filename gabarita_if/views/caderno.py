from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
import random
import re
import logging

from gabarita_if.models import (
    Caderno,
    RespostaQuestao,
    Questao,
    Disciplina,
    Assunto,
    Fonte,
)
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
def ajax_criar_caderno(request):
    if request.method == "POST":
        logger.info(f"Dados POST recebidos: {request.POST}")
        
        # Criar o formulário com os dados recebidos
        form = CadernoForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Salvar o caderno
                caderno = form.save(commit=False)
                caderno.usuario = request.user
                caderno.save()
                
                # Processar os blocos
                blocos_processados = processar_blocos(request.POST, caderno)
                
                if blocos_processados > 0:
                    messages.success(request, f"Caderno criado com {blocos_processados} bloco(s)!")
                    return render_crud_response(request, _context_cadernos(request))
                else:
                    messages.warning(request, "Caderno criado, mas nenhum bloco foi adicionado.")
                    return render_crud_response(request, _context_cadernos(request))
                    
            except Exception as e:
                logger.error(f"Erro ao criar caderno: {str(e)}")
                messages.error(request, f"Erro ao criar caderno: {str(e)}")
                return render(request, "criar.html", {
                    "form": form,
                    "disciplinas": Disciplina.objects.all(),
                    "assuntos": Assunto.objects.select_related("disciplina").all(),
                    "fontes": Fonte.objects.all(),
                })

        # Se o formulário não for válido
        logger.error(f"Erros no formulário: {form.errors}")
        messages.error(request, "Falha ao criar caderno! Verifique os dados.")
        
        return render(request, "criar.html", {
            "form": form,
            "disciplinas": Disciplina.objects.all(),
            "assuntos": Assunto.objects.select_related("disciplina").all(),
            "fontes": Fonte.objects.all(),
        })

    # GET - Carregar dados para o formulário
    form = CadernoForm()
    return render(request, "criar.html", {
        "form": form,
        "disciplinas": Disciplina.objects.all(),
        "assuntos": Assunto.objects.select_related("disciplina").all(),
        "fontes": Fonte.objects.all(),
    })


def processar_blocos(post_data, caderno):
    """
    Processa os blocos de questões enviados via POST
    Retorna o número de blocos processados
    """
    blocos_criados = 0
    
    # Procurar todos os campos relacionados a blocos
    for key, value in post_data.items():
        # Encontrar campos de disciplina (ex: blocos[0][disciplina])
        if 'disciplina' in key and 'blocos' in key:
            try:
                # Extrair o índice do bloco
                match = re.search(r'blocos\[(\d+)\]', key)
                if not match:
                    continue
                    
                indice = int(match.group(1))
                
                # Pular se não tiver disciplina selecionada
                if not value:
                    continue
                
                # Buscar a quantidade para este bloco
                quantidade_key = f'blocos[{indice}][quantidade]'
                quantidade = post_data.get(quantidade_key, 10)
                
                # Buscar os tópicos para este bloco
                topicos_key = f'blocos[{indice}][topicos]'
                topicos_ids = post_data.getlist(topicos_key)
                
                # Buscar as dificuldades para este bloco
                dificuldades_key = f'blocos[{indice}][dificuldades]'
                dificuldades = post_data.getlist(dificuldades_key)
                
                # Buscar o status
                status = post_data.get('status', 'todas')
                
                logger.info(f"Processando bloco {indice}:")
                logger.info(f"  Disciplina: {value}")
                logger.info(f"  Quantidade: {quantidade}")
                logger.info(f"  Tópicos: {topicos_ids}")
                logger.info(f"  Dificuldades: {dificuldades}")
                logger.info(f"  Status: {status}")
                
                # Buscar questões com base nos filtros
                questoes = buscar_questoes(
                    disciplina_id=value,
                    topicos_ids=topicos_ids,
                    dificuldades=dificuldades,
                    status=status,
                    usuario=caderno.usuario
                )
                
                # Limitar a quantidade
                questoes = questoes[:int(quantidade)]
                
                # Adicionar questões ao caderno
                caderno.questoes.add(*questoes)
                
                blocos_criados += 1
                
                logger.info(f"Bloco {indice} criado com {len(questoes)} questões")
                
            except Exception as e:
                logger.error(f"Erro ao processar bloco {key}: {str(e)}")
                continue
    
    return blocos_criados


def buscar_questoes(disciplina_id, topicos_ids=None, dificuldades=None, status='todas', usuario=None):
    """
    Busca questões com base nos filtros
    """
    # Começar com todas as questões da disciplina
    questoes = Questao.objects.filter(disciplina_id=disciplina_id)
    
    # Filtrar por tópicos (assuntos)
    if topicos_ids:
        questoes = questoes.filter(assunto_id__in=topicos_ids)
    
    # Filtrar por dificuldades
    if dificuldades:
        questoes = questoes.filter(dificuldade__in=dificuldades)
    
    # Filtrar por status (respondidas/não respondidas)
    if usuario and status != 'todas':
        from django.db.models import Exists, OuterRef
        
        respostas = RespostaQuestao.objects.filter(
            usuario=usuario,
            questao=OuterRef('id'),
            tentativa=None
        )
        
        if status == 'nao_respondidas':
            questoes = questoes.filter(~Exists(respostas))
        elif status == 'respondidas':
            questoes = questoes.filter(Exists(respostas))
        elif status == 'corretas':
            questoes = questoes.filter(Exists(respostas.filter(acertou=True)))
        elif status == 'incorretas':
            questoes = questoes.filter(Exists(respostas.filter(acertou=False)))
    
    return questoes


@login_required
def detalhar_caderno(request, id):
    caderno = get_object_or_404(
        Caderno,
        id=id
    )

    if request.method == "POST":
        questao_id = request.POST.get("questao_id")

        if request.POST.get("refazer"):
            RespostaQuestao.objects.filter(
                usuario=request.user,
                questao_id=questao_id,
                tentativa=None
            ).delete()

        else:
            alternativa_escolhida = request.POST.get(
                "alternativa"
            )

            if questao_id and alternativa_escolhida:
                questao = Questao.objects.get(
                    id=questao_id
                )

                RespostaQuestao.objects.create(
                    usuario=request.user,
                    questao=questao,
                    tentativa=None,
                    alternativa_escolhida=alternativa_escolhida,
                    acertou=(
                        alternativa_escolhida
                        == questao.alternativa_correta
                    ),
                )

    filtro = QuestaoFiltro(
        request.GET,
        queryset=caderno.questoes.all(),
        request=request
    )

    questoes_filtradas = filtro.qs.order_by("id")

    paginator = Paginator(
        questoes_filtradas,
        1
    )

    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(
        numero_da_pagina
    )

    for questao in questoes_paginadas:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user,
            questao=questao,
            tentativa=None
        ).first()

    context = {
        "titulo": caderno.nome,
        "object": caderno,
        "objects": questoes_paginadas,
        "filtro": filtro,
    }

    return render(
        request,
        "gabarita_if/detalhar_caderno.html",
        context
    )


@login_required
def ajax_editar_caderno(request, id):
    caderno = get_object_or_404(
        Caderno,
        id=id
    )

    if request.method == "POST":
        form = CadernoForm(
            request.POST,
            request.FILES,
            instance=caderno
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Caderno atualizado com sucesso!"
            )

            return render_crud_response(request, _context_cadernos(request))

        messages.error(
            request,
            "Falha ao atualizar caderno!"
        )

    else:
        form = CadernoForm(
            instance=caderno
        )

    context = {"form": form}
    if request.method == "POST":
        return render_form_response(request, context)
    return render(request, "editar.html", context)


@login_required
def ajax_remover_caderno(request, id):
    caderno = get_object_or_404(
        Caderno,
        id=id
    )

    if request.method == "POST":
        caderno.delete()

        messages.success(
            request,
            "Caderno removido com sucesso!"
        )

        return render_crud_response(request, _context_cadernos(request))

    context = {
        "object": caderno,
        "url_remover": "gabarita_if:ajax-remover-caderno",
    }

    return render(
        request,
        "remover.html",
        context
    )