from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse 
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
@permission_required("gabarita_if.add_filtro", raise_exception=True)
def filtros(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        filtros = Filtro.objects.filter(usuario=request.user).order_by(ordenar)
    else:
        filtros = Filtro.objects.filter(usuario=request.user).order_by("id")

    paginator = Paginator(filtros, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    filtros_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "filtros",
        "subtitulo_pagina": "Aqui você pode cadastrar filtros personalizadas.",
        "url_criar": "gabarita_if:criar-filtro",
        "partial_listar": "gabarita_if/partials/_listar_filtros.html",
        "mostrar_botao": True,
        "filtros": filtros_paginados
    }
    
    return render(request, "gabarita_if/listar.html", context)

@login_required
@permission_required("gabarita_if.add_filtro", raise_exception=True)
def criar_filtro(request):
    if request.method == "POST":
        form = FiltroForm(request.POST, request.FILES)
        if form.is_valid():
            filtro = form.save(commit=False)
            filtro.usuario = request.user
            filtro.save()
            messages.success(request, "filtro criada com sucesso!")
            return redirect("gabarita_if:filtros")
        else:
            messages.error(request, "Falha ao criar filtro!")
    else:
        form = FiltroForm()
    
    context = {
        "titulo_pagina": "Criar filtro",
        "url_cancelar": "gabarita_if:filtros",
        "form": form
    }

    return render(request, "gabarita_if/criar.html", context)

@login_required
@permission_required("gabarita_if.view_filtro", raise_exception=True)
def detalhar_filtro(request, id):
    filtro = get_object_or_404(Filtro, id=id)

    context = {
        "titulo_pagina": "Detalhar filtro",
        "partial_detalhar": "gabarita_if/partials/_detalhar_filtro.html",
        "filtro": filtro
    }

    return render(request, "gabarita_if/detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_filtro", raise_exception=True)
def editar_filtro(request, id):
    filtro = get_object_or_404(Filtro, id=id)
    if request.method == "POST":
        form = FiltroForm(request.POST, request.FILES, instance=filtro)
        if form.is_valid():
            form.save()
            messages.success(request, "filtro atualizada com sucesso!")
            return redirect("gabarita_if:filtros")
        else:
            messages.error(request, "Falha ao criar filtro!")
    else:
        form = FiltroForm(instance=filtro)

    context = {
        "titulo_pagina": "Editar filtro",
        "url_cancelar": "gabarita_if:filtros",
        "form": form
    }

    return render(request, "gabarita_if/editar.html", context)

@login_required
def remover_filtro(request, id):
    filtro = get_object_or_404(Filtro, id=id)

    if request.method == "POST":
        filtro.delete()
        messages.success(request, "filtro removida com sucesso!")
        return redirect("gabarita_if:filtros")
    else:
        context = {
            "object": filtro,
            "url_remover": "gabarita_if:remover-filtro"
        }

        return render(request, "gabarita_if/remover.html", context)
