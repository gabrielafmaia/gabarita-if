from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import UsuarioTabela
from django_tables2 import RequestConfig
from usuarios.models import Usuario
from usuarios.forms import *
from django.http import JsonResponse

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
        "url_criar": "dashboard:ajax-criar-usuario",
        "url_detalhar": "dashboard:ajax-detalhar-usuario",
        "url_editar": "dashboard:ajax-editar-usuario",
        "url_remover": "dashboard:ajax-remover-usuario",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": usuarios
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_usuario", raise_exception=True)
def ajax_criar_usuario(request):
    if request.method == "POST":
        form = UsuarioCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário criado com sucesso!")
            return JsonResponse({"mensagem": "Usuário criado com sucesso!"}, status=201)
        else:
            messages.error(request, "Falha ao criar usuário!")
    else:
        form = UsuarioCreationForm()

    return render(request, "criar.html", {"form": form})

@login_required
@permission_required("gabarita_if.view_usuario", raise_exception=True)
def ajax_detalhar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    fields = ["username", "first_name", "last_name", "email"]
    safe_fields = []

    def get_fields():
        selected_fields = []
        no_check = not isinstance(fields, (list, tuple))
        for field in usuario._meta.fields:
            if no_check or field.name in fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(usuario, field.name),
                        "safe": True if field.name in safe_fields else False,
                    }
                )
                
        return selected_fields

    context = {
        "nome": "usuário",
        "perfil": True,
        "object": usuario,
        "fields": get_fields()
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_usuario", raise_exception=True)
def ajax_editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            return JsonResponse({"mensagem": "Usuário atualizado com sucesso!"}, status=200)
        else:
            messages.error(request, "Falha ao atualizar usuário!")
    else:
        form = UsuarioChangeForm(instance=usuario)

    return render(request, "editar.html", {"form": form})

@login_required
@permission_required("gabarita_if.delete_usuario", raise_exception=True)
def ajax_remover_usuario(request, id):
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
