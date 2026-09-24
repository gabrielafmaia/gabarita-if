from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import AvaliacaoTabela
from django_tables2 import RequestConfig
from gabarita_if.models import Avaliacao
from gabarita_if.models import Questao, Disciplina, Assunto
import random
import re
from dashboard.forms import AvaliacaoForm
from .htmx import render_crud_response, render_form_response
from django.views.decorators.http import require_GET


def _salvar_blocos_avaliacao(post_data, avaliacao):
    indices = sorted({int(m.group(1)) for key in post_data if (m := re.match(r"blocos\[(\d+)\]\[disciplina\]$", key))})
    if not indices:
        return
    blocos = []
    questoes = []
    for index in indices:
        disciplina = post_data.get(f"blocos[{index}][disciplina]")
        assunto = post_data.get(f"blocos[{index}][assunto]")
        if not disciplina and not assunto:
            continue
        ano = post_data.get(f"blocos[{index}][ano]") or ""
        try:
            quantidade = max(1, min(int(post_data.get(f"blocos[{index}][quantidade]", 10) or 10), 100))
        except (TypeError, ValueError):
            quantidade = 10
        bloco = {"indice": index, "disciplina": disciplina, "assunto": assunto, "ano": ano, "quantidade": quantidade}
        blocos.append(bloco)
        qs = Questao.objects.filter(disciplina_id=disciplina)
        if assunto:
            qs = qs.filter(assunto_id=assunto)
        if ano:
            qs = qs.filter(ano=ano)
        disponiveis = list(qs)
        random.shuffle(disponiveis)
        questoes.extend(disponiveis[:quantidade])
    if not blocos:
        return
    avaliacao.blocos = blocos
    avaliacao.save(update_fields=["blocos"])
    avaliacao.questoes.set(dict.fromkeys(q.pk for q in questoes))


def _contexto_form_avaliacao(form, titulo_modal):
    instance = form.instance
    blocos = getattr(instance, "blocos", []) if instance and instance.pk else []
    return {
        "partial_form": "dashboard/partials/_form_avaliacao.html",
        "form": form,
        "titulo_modal": titulo_modal,
        "disciplinas": Disciplina.objects.all(),
        "assuntos": Assunto.objects.select_related("disciplina").all(),
        "blocos": blocos,
    }


@login_required
@require_GET
def ajax_adicionar_bloco_avaliacao(request):
    try:
        index = max(0, int(request.GET.get("index", 0)))
    except (TypeError, ValueError):
        index = 0
    return render(request, "dashboard/partials/_bloco_avaliacao.html", {
        "numero": index + 1,
        "disciplinas": Disciplina.objects.all(),
        "assuntos": Assunto.objects.select_related("disciplina").all(),
    })


def _context_avaliacoes(request):
    avaliacoes = Avaliacao.objects.all()
    tabela = AvaliacaoTabela(avaliacoes)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)
    return {
        "titulo_pagina": "Avaliações",
        "subtitulo_pagina": "Aqui você pode cadastrar os Exames de Seleção do IFRN e os Simuladões do Meta IFRN.",
        "nome": "avaliação",
        "url_criar": "dashboard:ajax-criar-avaliacao",
        "url_detalhar": "dashboard:ajax-detalhar-avaliacao",
        "url_editar": "dashboard:ajax-editar-avaliacao",
        "url_remover": "dashboard:ajax-remover-avaliacao",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": avaliacoes,
    }

@login_required
@permission_required("gabarita_if.add_avaliacao", raise_exception=True)
def avaliacoes(request):
    return render(request, "listar.html", _context_avaliacoes(request))

@login_required
@permission_required("gabarita_if.add_avaliacao", raise_exception=True)
def ajax_criar_avaliacao(request):
    if request.method == "POST":
        form = AvaliacaoForm(request.POST, request.FILES)
        if form.is_valid():
            avaliacao = form.save()
            _salvar_blocos_avaliacao(request.POST, avaliacao)
            messages.success(request, "Avaliação criada com sucesso!")
            return render_crud_response(request, _context_avaliacoes(request))
        else:
            messages.error(request, "Falha ao criar avaliação!")
    else:
        form = AvaliacaoForm()
    
    context = _contexto_form_avaliacao(form, "Criar")
    if request.method == "POST":
        return render_form_response(request, context)
    return render(request, "editar.html", context)

@login_required
@permission_required("gabarita_if.view_avaliacao", raise_exception=True)
def ajax_detalhar_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    fields = "__all__"
    safe_fields = []

    def get_fields():
        selected_fields = []
        no_check = not isinstance(fields, (list, tuple))
        for field in avaliacao._meta.fields:
            if no_check or field.name in fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(avaliacao, field.name),
                        "safe": True if field.name in safe_fields else False,
                    }
                )
        
        for field in avaliacao._meta.many_to_many:
            if no_check or field.name in fields:
                selected_fields.append({
                    "label": field.verbose_name,
                    "value": getattr(avaliacao, field.name).all(),
                    "safe": False,
                    "many": True,
                })

        return selected_fields
    
    context = {
        "nome": "avaliação",
        "object": avaliacao,
        "fields": get_fields(),
        "titulo_modal": "Detalhar",
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_avaliacao", raise_exception=True)
def ajax_editar_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    if request.method == "POST":
        form = AvaliacaoForm(request.POST, request.FILES, instance=avaliacao)
        if form.is_valid():
            avaliacao = form.save()
            _salvar_blocos_avaliacao(request.POST, avaliacao)
            messages.success(request, "Avaliação atualizada com sucesso!")
            return render_crud_response(request, _context_avaliacoes(request))
        else:
            messages.error(request, "Falha ao atualizar avaliação!")
    else:
        form = AvaliacaoForm(instance=avaliacao)

    context = _contexto_form_avaliacao(form, "Editar")

    if request.method == "POST":
        return render_form_response(request, context)
    return render(request, "editar.html", context)

@login_required
@permission_required("gabarita_if.delete_avaliacao", raise_exception=True)
def ajax_remover_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    if request.method == "POST":
        avaliacao.delete()
        messages.success(request, "Avaliação removida com sucesso!")
        return render_crud_response(request, _context_avaliacoes(request))
    else:
        context = {
            "object": avaliacao,
            "url_remover": "dashboard:remover-avaliacao",
            "titulo_modal": "Remover",
        }

        return render(request, "remover.html", context)
