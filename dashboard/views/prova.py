from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *

@login_required
@permission_required("gabarita_if.add_prova", raise_exception=True)
def provas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        provas = Prova.objects.all().order_by(ordenar)
    else:
        provas = Prova.objects.all().order_by("id")

    paginator = Paginator(provas, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    provas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Provas",
        "subtitulo_pagina": "Aqui você pode cadastrar as provas do IFRN.",
        "url_criar": "dashboard:criar-prova",
        "partial_lista": "dashboard/partials/_lista_provas.html",
        "nome": "prova",
        "objects": provas_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_prova", raise_exception=True)
def criar_prova(request):
    if request.method == "POST":
        form = ProvaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Prova criada com sucesso!")
            return redirect("dashboard:provas")
        else:
            messages.error(request, "Falha ao criar Prova!")
    else:
        form = ProvaForm()
    
    context = {
        "titulo_pagina": "Criar prova",
        "url_voltar": "dashboard:provas",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_prova", raise_exception=True)
def detalhar_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    fields = "__all__"
    
    selected_fields = []
    no_check = not isinstance(fields, (list, tuple))
    
    for field in prova._meta.fields:
        if no_check or field.name in fields:
            selected_fields.append(
                {
                "label": field.verbose_name,
                "value": getattr(prova, field.name),
                }
            )
    
    context = {
        "titulo_pagina": "Detalhar prova",
        "url_voltar": "dashboard:provas",
        "url_editar": "dashboard:editar-prova", 
        "url_remover": "dashboard:remover-prova",
        "object": prova,
        "fields": selected_fields
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_prova", raise_exception=True)
def editar_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    if request.method == "POST":
        form = ProvaForm(request.POST, request.FILES, instance=prova)
        if form.is_valid():
            form.save()
            messages.success(request, "Prova atualizada com sucesso!")
            return redirect("dashboard:provas")
        else:
            messages.error(request, "Falha ao criar prova!")
    else:
        form = ProvaForm(instance=prova)

    context = {
        "titulo_pagina": "Editar prova",
        "url_voltar": "dashboard:provas",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_prova(request, id):
    prova = get_object_or_404(Prova, id=id)

    if request.method == "POST":
        prova.delete()
        messages.success(request, "Prova removida com sucesso!")
        return redirect("dashboard:provas")
    else:
        context = {
            "object": prova,
            "url_remover": "dashboard:remover-prova"
        }

        return render(request, "remover.html", context)
