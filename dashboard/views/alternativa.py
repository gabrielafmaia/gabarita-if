from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *

@login_required
@permission_required("gabarita_if.add_alternativa", raise_exception=True)
def alternativas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        alternativas = Alternativa.objects.all().order_by(ordenar)
    else:
        alternativas = Alternativa.objects.all().order_by("id")

    paginator = Paginator(alternativas, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    alternativas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Alternativas",
        "subtitulo_pagina": "Aqui você pode cadastrar separadamente as alternativas das questões.",
        "url_criar": "dashboard:criar-alternativa",
        "partial_lista": "dashboard/partials/_lista_alternativas.html",
        "mostrar_botao": True,
        "nome": "alternativa",
        "alternativas": alternativas_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_alternativa", raise_exception=True)
def criar_alternativa(request):
    if request.method == "POST":
        form = AlternativaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Alternativa criada com sucesso!")
            return redirect("dashboard:alternativas")
        else:
            messages.error(request, "Falha ao criar Alternativa!")
    else:
        form = AlternativaForm()
    
    context = {
        "titulo_pagina": "Criar Alternativa",
        "url_voltar": "dashboard:alternativas",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_alternativa", raise_exception=True)
def detalhar_alternativa(request, id):
    alternativa = get_object_or_404(Alternativa, id=id)

    context = {
        "titulo_pagina": "Detalhar Alternativa",
        "partial_detalhe": "dashboard/partials/_detalhe_alternativa.html",
        "alternativa": alternativa
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_alternativa", raise_exception=True)
def editar_alternativa(request, id):
    alternativa = get_object_or_404(Alternativa, id=id)
    if request.method == "POST":
        form = AlternativaForm(request.POST, request.FILES, instance=alternativa)
        if form.is_valid():
            form.save()
            messages.success(request, "Alternativa atualizada com sucesso!")
            return redirect("dashboard:alternativas")
        else:
            messages.error(request, "Falha ao criar Alternativa!")
    else:
        form = AlternativaForm(instance=alternativa)

    context = {
        "titulo_pagina": "Editar Alternativa",
        "url_voltar": "dashboard:alternativas",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_alternativa(request, id):
    alternativa = get_object_or_404(Alternativa, id=id)

    if request.method == "POST":
        alternativa.delete()
        messages.success(request, "Alternativa removida com sucesso!")
        return redirect("dashboard:alternativas")
    else:
        context = {
            "object": alternativa,
            "url_remover": "dashboard:remover-alternativa"
        }

        return render(request, "remover.html", context)
