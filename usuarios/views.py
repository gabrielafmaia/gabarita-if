from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
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
def perfil(request):
    context = {
        "titulo_pagina": "Perfil",
        "url_editar": "usuarios:editar-perfil",
    }
    return render(request, "registration/perfil.html", context)

@login_required
def editar_perfil(request):
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado!")
            return redirect("usuarios:perfil")
        else:
            messages.success(request, "Falha ao atualizar o perfil!")
    else:
        form = UsuarioChangeForm(instance=request.user)

    context = {
        "titulo_pagina": "Editar perfil",
        "url_voltar": "usuarios:perfil",
        "form": form
    }

    return render(request, "registration/editar_perfil.html", context)
