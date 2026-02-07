from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import QuestaoTabela
from django_tables2 import RequestConfig
from gabarita_if.models import Questao
from dashboard.forms import QuestaoForm
from django.http import JsonResponse
import time

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def questoes(request):
    questoes = Questao.objects.all()
    tabela = QuestaoTabela(questoes)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode cadastrar as questões das provas e simulados.",
        "nome": "questão",
        "url_criar": "dashboard:criar-questao",
        "url_detalhar": "dashboard:ajax-detalhar-questao",
        "url_editar": "dashboard:editar-questao",
        "url_remover": "dashboard:remover-questao",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": questoes
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def criar_questao(request):
    if request.method == "POST":
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão criada com sucesso!")
            return redirect("dashboard:questoes")
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = QuestaoForm()
    
    context = {
        "titulo_pagina": "Criar questão",
        "url_voltar": "dashboard:questoes",
        "partial_form": "dashboard/partials/_form_questao.html",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_questao", raise_exception=True)
def ajax_detalhar_questao(request, id):
    time.sleep(1)
    questao = get_object_or_404(Questao, id=id)
    fields = "__all__"
    safe_fields = ["enunciado", "alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d", "gabarito_comentado"]

    def get_fields():
        selected_fields = []
        no_check = not isinstance(fields, (list, tuple))
        for field in questao._meta.fields:
            if no_check or field.name in fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(questao, field.name),
                        "safe": True if field.name in safe_fields else False,
                        "many": False,
                    }
                )

        return selected_fields

    context = {
        "titulo_pagina": "Detalhar questão",
        "nome": "questão",
        "url_voltar": "dashboard:questoes",
        "url_editar": "dashboard:editar-questao",
        "url_remover": "dashboard:remover-questao",
        "object": questao,
        "fields": get_fields()
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_questao", raise_exception=True)
def editar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        form = QuestaoForm(request.POST, request.FILES, instance=questao)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão atualizada com sucesso!")
            return redirect("dashboard:questoes")
        else:
            messages.error(request, "Falha ao atualizar questão!")
    else:
        form = QuestaoForm(instance=questao)
        
    context = {
        "titulo_pagina": "Editar questão",
        "url_voltar": "dashboard:questoes",
        "partial_form": "dashboard/partials/_form_questao.html",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
@permission_required("gabarita_if.delete_questao", raise_exception=True)
def remover_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        questao.delete()
        messages.success(request, "Questão removida com sucesso!")
        return redirect("dashboard:questoes")
    else:
        context = {
            "object": questao,
            "url_remover": "dashboard:remover-questao"
        }

        return render(request, "remover.html", context)
    