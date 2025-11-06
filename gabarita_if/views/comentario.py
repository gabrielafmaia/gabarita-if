from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse 
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
@permission_required("gabarita_if.add_comentario", raise_exception=True)
def comentarios(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        comentarios = Comentario.objects.all().order_by(ordenar)
    else:
        comentarios = Comentario.objects.all().order_by("id")

    paginator = Paginator(comentarios, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    comentarios_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode cadastrar as questões das provas e simulados.",
        "url_criar": "gabarita_if:criar-comentario",
        "partial_tabela": "gabarita_if/partials/_tabela_comentarios.html",
        # "mostrar_botao": True,
        "comentarios": comentarios_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_comentario", raise_exception=True)
def criar_comentario(request):
    if request.method == "POST":
        form = ComentarioForm(request.POST, request.FILES)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Questão criada com sucesso!")
            return redirect("gabarita_if:comentarios")
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = ComentarioForm()
    
    context = {
        "titulo_pagina": "Criar Questão",
        "url_cancelar": "gabarita_if:comentarios",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_comentario", raise_exception=True)
def detalhar_comentario(request, id):
    comentario = get_object_or_404(Comentario, id=id)

    context = {
        "titulo_pagina": "Detalhar Questão",
        "partial_detalhar": "gabarita_if/partials/_detalhar_comentario.html",
        "comentario": comentario
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_comentario", raise_exception=True)
def editar_comentario(request, id):
    comentario = get_object_or_404(Comentario, id=id)
    if request.method == "POST":
        form = ComentarioForm(request.POST, request.FILES, instance=comentario)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão atualizada com sucesso!")
            return redirect("gabarita_if:comentarios")
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = ComentarioForm(instance=comentario)

    context = {
        "titulo_pagina": "Editar Questão",
        "url_cancelar": "gabarita_if:comentarios",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_comentario(request, id):
    comentario = get_object_or_404(Comentario, id=id)

    if request.method == "POST":
        comentario.delete()
        messages.success(request, "Questão removida com sucesso!")
        return redirect("gabarita_if:comentarios")
    else:
        context = {
            "object": comentario,
            "url_remover": "gabarita_if:remover-comentario"
        }

        return render(request, "remover.html", context)
