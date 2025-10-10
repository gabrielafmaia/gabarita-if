from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import Questao
from .forms import QuestaoForm
from usuarios.forms import UsuarioChangeForm, UsuarioCreationForm


def index(request):
    context = {
        "num_questoes": Questao.objects.count(),
    }
    return render(request, "dashboard/index.html", context)


def listar_questoes(request):
    questoes = Questao.objects.all()
    return render(request, "dashboard/questoes.html", {"questoes":questoes})

# @login_required
# @permission_required("gabarita_if.add_questao", raise_exception=True)
def criar_questao(request):
    if request.method == "POST":
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão criada com sucesso!")
            return redirect("dashboard:questoes")
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = QuestaoForm()
    return render(request, "dashboard/criar_questao.html", {"form": form})

# @login_required
# @permission_required("gabarita_if.view_questao", raise_exception=True)
def ler_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    return render(request, "dashboard/detalhar_questao.html", {"questao": questao})

# @login_required
# @permission_required("gabarita_if.change_questao", raise_exception=True)
def editar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        form = QuestaoForm(request.POST, request.FILES, instance=questao)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão atualizada com sucesso!")
            return redirect("dashboard:questoes")
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = QuestaoForm(instance=questao)
    return render(request, "dashboard/editar_questao.html", {"form": form})

def remover_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        questao.delete()
        messages.success(request, "Questão removida com sucesso!")
        return redirect("dashboard:questaos")
    else:
        return render(request, "dashboard/remover_questao.html")
