from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def questoes(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        questoes = Questao.objects.all().order_by(ordenar)
    else:
        questoes = Questao.objects.all().order_by("id")

    paginator = Paginator(questoes, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    questoes_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode cadastrar as questões das provas e simulados.",
        "url_criar": "dashboard:criar-questao",
        "partial_tabela": "dashboard/partials/_tabela_questoes.html",
        "questoes": questoes_paginadas
    }
    
    return render(request, "dashboard/listar.html", context)

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
        "titulo_pagina": "Criar Questão",
        "url_cancelar": "dashboard:questoes",
        "form": form
    }

    return render(request, "dashboard/criar.html", context)

@login_required
@permission_required("gabarita_if.view_questao", raise_exception=True)
def detalhar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)

    context = {
        "titulo_pagina": "Detalhar Questão",
        "partial_detalhar": "dashboard/partials/_detalhar_questao.html",
        "questao": questao
    }

    return render(request, "dashboard/detalhar.html", context)

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
            messages.error(request, "Falha ao criar questão!")
    else:
        form = QuestaoForm(instance=questao)

    context = {
        "titulo_pagina": "Editar Questão",
        "url_cancelar": "dashboard:questoes",
        "form": form
    }

    return render(request, "dashboard/editar.html", context)

@login_required
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

        return render(request, "dashboard/remover.html", context)
