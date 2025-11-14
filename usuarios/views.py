from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *
from .models import Usuario
from .forms import *

def cadastro(request):
    if request.method == "POST":
        form = CadastroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cadastro realizado com sucesso! Faça login para acessar o sistema.")
            return redirect("login")
    else:
        form = CadastroForm()
    return render(request, "registration/cadastro.html", {"form": form})

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
        "url_criar": "usuarios:criar-usuario",
        "partial_lista": "dashboard/partials/_lista_usuarios.html",
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
            return redirect("usuarios:usuarios")
        else:
            messages.error(request, "Falha ao criar usuário!")
    else:
        form = UsuarioCreationForm()
    
    context = {
        "titulo_pagina": "Criar usuário",
        "url_voltar": "usuarios:usuarios",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_usuario", raise_exception=True)
def detalhar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    fields = ["username", "first_name", "last_name", "email", "curso"]
    
    selected_fields = []
    no_check = not isinstance(fields, (list, tuple))
    
    for field in usuario._meta.fields:
        if no_check or field.name in fields:
            selected_fields.append(
                {
                "label": field.verbose_name,
                "value": getattr(usuario, field.name),
                }
            )

    context = {
        "titulo_pagina": "Detalhar usuário",
        "url_voltar": "usuarios:usuarios",
        "url_editar": "usuarios:editar-usuario",
        "object": usuario,
        "usuario": usuario,
        "fields": selected_fields
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
            return redirect("usuarios:usuarios")
        else:
            messages.error(request, "Falha ao criar usuário!")
    else:
        form = UsuarioChangeForm(instance=usuario)

    context = {
        "titulo_pagina": "Editar usuário",
        "url_voltar": "usuarios:usuarios",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
@permission_required("gabarita_if.delete_usuario", raise_exception=True)
def remover_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == "POST":
        if usuario.id == request.user.id:
            messages.error(request, "Não é possível remover o usuário logado!")
        else:
            usuario.delete()
            messages.success(request, "Usuário removido com sucesso!")
        return redirect("usuarios:usuarios")
    else:
        context = {
            "object": usuario,
            "url_remover": "usuarios:remover-usuario"
        }
        
        return render(request, "remover.html", context)
