from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import Questao
from .forms import QuestaoForm
from usuarios.models import Usuario
from usuarios.forms import UsuarioChangeForm, UsuarioCreationForm

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def index(request):
    context = {
        "num_questoes": Questao.objects.count(),
        "num_usuarios": Usuario.objects.count(),
    }
    return render(request, "dashboard/index.html", context)

# Crud Usuários
def listar_usuarios(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        usuarios = Usuario.objects.all().order_by(ordenar)
    else:
        usuarios = Usuario.objects.all().order_by("id")
    paginator = Paginator(usuarios, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    usuarios_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "dashboard/usuarios.html", {"usuarios": usuarios_paginados})

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
    return render(request, "dashboard/criar_usuario.html", {"form": form})

def detalhar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    return render(request, "dashboard/detalhar_usuario.html", {"usuario": usuario})

def editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == "POST":
        form = UsuarioChangeForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado!")
            return redirect("dashboard:usuarios")
        else:
            messages.error(request, "Falha ao criar usuário!")
    else:
        form = UsuarioChangeForm(instance=usuario)
    return render(request, "dashboard/editar_usuario.html", {"form": form})

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
        return render(request, "dashboard/remover_usuario.html")
    
# Crud Questões
@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def listar_questoes(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        questoes = Questao.objects.all().order_by(ordenar)
    else:
        questoes = Questao.objects.all().order_by("id")

    paginator = Paginator(questoes, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    questoes_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "dashboard/questoes.html", {"questoes": questoes_paginadas})

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
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

@login_required
@permission_required("gabarita_if.view_questao", raise_exception=True)
def detalhar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    return render(request, "dashboard/detalhar_questao.html", {"questao": questao})

@login_required
@permission_required("gabarita_if.change_questao", raise_exception=True)
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
    
# Crud Provas
def listar_provas(resquest):
    pass
def criar_prova(resquest):
    pass
def detalhar_prova(resquest, id):
    pass
def editar_prova(resquest, id):
    pass
def remover_prova(resquest, id):
    pass

# Crud Simulados
def listar_simulados(resquest):
    pass
def criar_simulado(resquest):
    pass
def detalhar_simulado(resquest, id):
    pass
def editar_simulado(resquest, id):
    pass
def remover_simulado(resquest, id):
    pass

# Crud Textos de Apoio
def listar_textos(resquest):
    pass
def criar_texto(resquest):
    pass
def detalhar_texto(resquest, id):
    pass
def editar_texto(resquest, id):
    pass
def remover_texto(resquest, id):
    pass

# Crud Alternativas
def listar_alternativas(resquest):
    pass
def criar_alternativa(resquest):
    pass
def detalhar_alternativa(resquest, id):
    pass
def editar_alternativa(resquest, id):
    pass
def remover_alternativa(resquest, id):
    pass
