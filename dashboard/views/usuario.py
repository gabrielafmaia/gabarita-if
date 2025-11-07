from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *
from usuarios.models import Usuario
from usuarios.forms import UsuarioChangeForm, UsuarioCreationForm

@login_required
@permission_required("gabarita_if.add_usuario", raise_exception=True)
def usuarios(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        usuarios = Usuario.objects.all().order_by(ordenar)
    else:
        usuarios = Usuario.objects.all().order_by("id")

    paginator = Paginator(usuarios, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    usuarios_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Usuários",
        "subtitulo_pagina": "Aqui você pode cadastrar os usuários.",
        "url_criar": "dashboard:criar-usuario",
        "partial_listar": "dashboard/partials/_listar_usuarios.html",
        "mostrar_botao": True,
        "nome": "usuário",
        "usuarios": usuarios_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_usuario", raise_exception=True)
def criar_usuario(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário criado com sucesso!")
            return redirect("dashboard:usuarios")
        else:
            messages.error(request, "Falha ao criar usuário!")
    else:
        form = UsuarioCreationForm()
    
    context = {
        "titulo_pagina": "Criar usuário",
        "url_cancelar": "dashboard:usuarios",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_usuario", raise_exception=True)
def detalhar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    context = {
        "titulo_pagina": "Detalhar usuário",
        "partial_detalhar": "dashboard/partials/_detalhar_usuario.html",
        "usuario": usuario
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_usuario", raise_exception=True)
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect("dashboard:usuarios")
        else:
            messages.error(request, "Falha ao criar usuário!")
    else:
        form = UsuarioChangeForm(instance=usuario)

    context = {
        "titulo_pagina": "Editar usuário",
        "url_cancelar": "dashboard:usuarios",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == "POST":
        if usuario.id == request.user.id:
            messages.error(request, "Não é possível remover o usuário logado!")
        else:
            usuario.delete()
            messages.success(request, "Usuário removido com sucesso!")
        return redirect("dashboard:usuarios")
    else:
        context = {
            "object": usuario,
            "url_remover": "dashboard:remover-usuario"
        }
        
        return render(request, "remover.html", context)
