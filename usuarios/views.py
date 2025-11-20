from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from dashboard.tables import UsuarioTabela
from django_tables2 import RequestConfig
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
    usuarios = Usuario.objects.all()
    
    tabela = UsuarioTabela(usuarios)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)

    context = {
        "titulo_pagina": "Usuários",
        "subtitulo_pagina": "Aqui você pode cadastrar os usuários.",
        "nome": "usuário",
        "url_criar": "usuarios:criar-usuario",
        "url_detalhar": "usuarios:detalhar-usuario",
        "url_editar": "usuarios:editar-usuario",
        "url_remover": "usuarios:remover-usuario",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": usuarios
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
        "titulo_pagina": "Perfil",
        "url_voltar": "usuarios:usuarios",
        "url_editar": "usuarios:editar-usuario",
        "object": usuario,
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
