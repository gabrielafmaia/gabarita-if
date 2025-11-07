from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse 
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
def listas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        listas = ListaPersonalizada.objects.filter(usuario=request.user).order_by(ordenar)
    else:
        listas = ListaPersonalizada.objects.filter(usuario=request.user).order_by("id")

    paginator = Paginator(listas, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    listas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Listas Personalizadas",
        "subtitulo_pagina": "Aqui você pode cadastrar listas personalizadas.",
        "url_criar": "gabarita_if:criar-lista",
        "partial_listar": "gabarita_if/partials/_listar_listas.html",
        "mostrar_botao": True,
        "nome": "lista",
        "listas": listas_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
def criar_lista(request):
    if request.method == "POST":
        form = ListaPersonalizadaForm(request.POST, request.FILES)
        if form.is_valid():
            lista = form.save(commit=False)
            lista.usuario = request.user
            lista.save()
            messages.success(request, "Lista criada com sucesso!")
            return redirect("gabarita_if:listas")
        else:
            messages.error(request, "Falha ao criar lista!")
    else:
        form = ListaPersonalizadaForm()
    
    context = {
        "titulo_pagina": "Criar lista",
        "url_cancelar": "gabarita_if:listas",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
def detalhar_lista(request, id):
    lista = get_object_or_404(ListaPersonalizada, id=id)

    context = {
        "titulo_pagina": "Detalhar lista",
        "partial_detalhar": "gabarita_if/partials/_detalhar_lista.html",
        "lista": lista
    }

    return render(request, "detalhar.html", context)

@login_required
def editar_lista(request, id):
    lista = get_object_or_404(ListaPersonalizada, id=id)
    if request.method == "POST":
        form = ListaPersonalizadaForm(request.POST, request.FILES, instance=lista)
        if form.is_valid():
            form.save()
            messages.success(request, "Lista atualizada com sucesso!")
            return redirect("gabarita_if:listas")
        else:
            messages.error(request, "Falha ao criar lista!")
    else:
        form = ListaPersonalizadaForm(instance=lista)

    context = {
        "titulo_pagina": "Editar lista",
        "url_cancelar": "gabarita_if:listas",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_lista(request, id):
    lista = get_object_or_404(ListaPersonalizada, id=id)

    if request.method == "POST":
        lista.delete()
        messages.success(request, "Lista removida com sucesso!")
        return redirect("gabarita_if:listas")
    else:
        context = {
            "object": lista,
            "url_remover": "gabarita_if:remover-lista"
        }

        return render(request, "remover.html", context)
