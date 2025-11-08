from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *

@login_required
@permission_required("gabarita_if.add_texto", raise_exception=True)
def textos(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        textos = TextoDeApoio.objects.all().order_by(ordenar)
    else:
        textos = TextoDeApoio.objects.all().order_by("id")

    paginator = Paginator(textos, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    textos_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Textos de Apoio",
        "subtitulo_pagina": "Aqui você pode cadastrar os textos de apoio das questões.",
        "url_criar": "dashboard:criar-texto",
        "partial_lista": "dashboard/partials/_lista_textos.html",
        "mostrar_botao": True,
        "nome": "texto",
        "textos": textos_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_texto", raise_exception=True)
def criar_texto(request):
    if request.method == "POST":
        form = TextoDeApoioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Texto de apoio criado com sucesso!")
            return redirect("dashboard:textos")
        else:
            messages.error(request, "Falha ao criar texto de apoio!")
    else:
        form = TextoDeApoioForm()
    
    context = {
        "titulo_pagina": "Criar texto",
        "url_voltar": "dashboard:textos",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_texto", raise_exception=True)
def detalhar_texto(request, id):
    texto = get_object_or_404(TextoDeApoio, id=id)

    context = {
        "titulo_pagina": "Detalhar texto",
        "partial_detalhe": "dashboard/partials/_detalhe_texto.html",
        "url_voltar": "dashboard:textos",
        "url_editar": "dashboard:editar-texto",
        "url_remover": "dashboard:remover-texto",
        "object": texto,
        "texto": texto
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_texto", raise_exception=True)
def editar_texto(request, id):
    texto = get_object_or_404(TextoDeApoio, id=id)
    if request.method == "POST":
        form = TextoDeApoioForm(request.POST, request.FILES, instance=texto)
        if form.is_valid():
            form.save()
            messages.success(request, "Texto de apoio atualizado com sucesso!")
            return redirect("dashboard:textos")
        else:
            messages.error(request, "Falha ao criar texto de apoio!")
    else:
        form = TextoDeApoioForm(instance=texto)

    context = {
        "titulo_pagina": "Editar texto",
        "url_voltar": "dashboard:textos",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_texto(request, id):
    texto = get_object_or_404(TextoDeApoio, id=id)

    if request.method == "POST":
        texto.delete()
        messages.success(request, "Texto de apoio removido com sucesso!")
        return redirect("dashboard:textos")
    else:
        context = {
            "object": texto,
            "url_remover": "dashboard:remover-texto"
        }

        return render(request, "remover.html", context)
