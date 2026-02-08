from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import AvaliacaoTabela
from django_tables2 import RequestConfig
from gabarita_if.models import Avaliacao
from dashboard.forms import AvaliacaoForm
from django.http import JsonResponse

@login_required
@permission_required("gabarita_if.add_avaliacao", raise_exception=True)
def avaliacoes(request):
    avaliacoes = Avaliacao.objects.all()
    tabela = AvaliacaoTabela(avaliacoes)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)

    context = {
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
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_avaliacao", raise_exception=True)
def ajax_criar_avaliacao(request):
    if request.method == "POST":
        form = AvaliacaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Avaliação criada com sucesso!")
            return JsonResponse({"mensagem": "Avaliação criada com sucesso!"}, status=201)
        else:
            messages.error(request, "Falha ao criar avaliação!")
    else:
        form = AvaliacaoForm()
    
    return render(request, "criar.html", {"form": form})

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
        "fields": get_fields()
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_avaliacao", raise_exception=True)
def ajax_editar_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    if request.method == "POST":
        form = AvaliacaoForm(request.POST, request.FILES, instance=avaliacao)
        if form.is_valid():
            form.save()
            messages.success(request, "Avaliação atualizada com sucesso!")
            return JsonResponse({"mensagem": "Avaliação atualizada com sucesso!"}, status=200)
        else:
            messages.error(request, "Falha ao atualizar avaliação!")
    else:
        form = AvaliacaoForm(instance=avaliacao)

    context = {
        "url_voltar": "dashboard:avaliacoes",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
@permission_required("gabarita_if.delete_avaliacao", raise_exception=True)
def ajax_remover_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    if request.method == "POST":
        avaliacao.delete()
        messages.success(request, "Avaliação removida com sucesso!")
        return redirect("dashboard:avaliacoes")
    else:
        context = {
            "object": avaliacao,
            "url_remover": "dashboard:remover-avaliacao"
        }

        return render(request, "remover.html", context)
