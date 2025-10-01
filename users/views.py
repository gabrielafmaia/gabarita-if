from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from .forms import CadastroForm, UsuarioChangeForm

def register(request):
    if request.method == "POST":
        form = CadastroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Usuário {username} criado com sucesso! Faça login para acessar o sistema.")
            return redirect("login")
    else:
        form = CadastroForm()
    return render(request, "registration/register.html", {"form": form})

@login_required
def profile(request):
    return render(request, "registration/profile.html")

@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado!")
            return redirect("profile")
        else:
            messages.error(request, "Falha ao atualizar o perfil!")
    else:
        form = UsuarioChangeForm(instance=request.user)

    return render(request, "registration/edit_profile.html", {"form": form})