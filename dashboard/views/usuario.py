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
        "subtitulo_pagina": "Aqui você pode cadastrar as Usuários das provas e simulados.",
        "url_criar": "dashboard:criar-usuario",
        "partial_tabela": "dashboard/partials/_tabela_usuarios.html",
        "usuarios": usuarios_paginadas
    }
    
    return render(request, "dashboard/listar.html", context)

@login_required
@permission_required("gabarita_if.add_usuario", raise_exception=True)
def criar_usuario(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário criada com sucesso!")
            return redirect("dashboard:usuarios")
        else:
            messages.error(request, "Falha ao criar Usuário!")
    else:
        form = UsuarioCreationForm()
    
    context = {
        "titulo_pagina": "Criar Usuário",
        "url_cancelar": "dashboard:usuarios",
        "form": form
    }

    return render(request, "dashboard/criar.html", context)

@login_required
@permission_required("gabarita_if.view_usuario", raise_exception=True)
def detalhar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    context = {
        "titulo_pagina": "Detalhar Usuário",
        "partial_detalhar": "dashboard/partials/_detalhar_usuario.html",
        "usuario": usuario
    }

    return render(request, "dashboard/detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_usuario", raise_exception=True)
def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizada com sucesso!")
            return redirect("dashboard:usuarios")
        else:
            messages.error(request, "Falha ao criar Usuário!")
    else:
        form = UsuarioChangeForm(instance=usuario)

    context = {
        "titulo_pagina": "Editar Usuário",
        "url_cancelar": "dashboard:usuarios",
        "form": form
    }

    return render(request, "dashboard/editar.html", context)

@login_required
def remover_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)

    if request.method == "POST":
        if usuario.id == request.user.id:
            messages.error(request, "Não é possível remover o usuário logado!")
        else:
            usuario.delete()
            messages.success(request, "Usuário removida com sucesso!")
            return redirect("dashboard:usuarios")
    else:
        context = {
            "object": usuario,
            "url_remover": "dashboard:remover-usuario"
        }

        return render(request, "dashboard/remover.html", context)





# # Crud Usuários
# @login_required
# def usuarios(request):
#     ordenar = request.GET.get("ordenar")
#     if ordenar:
#         usuarios = Usuario.objects.all().order_by(ordenar)
#     else:
#         usuarios = Usuario.objects.all().order_by("id")
#     paginator = Paginator(usuarios, 10)
#     numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
#     usuarios_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica
#     return render(request, "dashboard/usuarios.html", {"usuarios": usuarios_paginados})

# @login_required
# def criar_usuario(request):
#     if request.method == "POST":
#         form = UsuarioCreationForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Usuário criado com sucesso!")
#             return redirect("dashboard:usuarios")
#         else:
#             messages.error(request, "Falha ao criar usuário!")
#     else:
#         form = UsuarioCreationForm()
#     return render(request, "dashboard/criar_usuario.html", {"form": form})

# @login_required
# def detalhar_usuario(request, id):
#     usuario = get_object_or_404(Usuario, id=id)
#     return render(request, "dashboard/detalhar_usuario.html", {"usuario": usuario})

# @login_required
# def editar_usuario(request, id):
#     usuario = get_object_or_404(Usuario, id=id)
#     if request.method == "POST":
#         form = UsuarioChangeForm(request.POST, request.FILES, instance=usuario)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Usuário atualizado!")
#             return redirect("dashboard:usuarios")
#         else:
#             messages.error(request, "Falha ao criar usuário!")
#     else:
#         form = UsuarioChangeForm(instance=usuario)
#     return render(request, "dashboard/editar_usuario.html", {"form": form, "usuario": usuario})

# @login_required
# def remover_usuario(request, id):
#     usuario = get_object_or_404(Usuario, id=id)
#     if request.method == "POST":
#         if usuario.id == request.user.id:
#             messages.error(request, "Não é possível remover o usuário logado!")
#         else:
#             usuario.delete()
#             messages.success(request, "Usuário removido com sucesso!")
#         return redirect("dashboard:usuarios")
#     else:
#         return render(request, "dashboard/remover_usuario.html")