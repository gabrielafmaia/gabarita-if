from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from .forms import *
from usuarios.models import Usuario
from usuarios.forms import UsuarioChangeForm, UsuarioCreationForm

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def index(request):
    context = {
        "num_questoes": Questao.objects.count(),
        "num_usuarios": Usuario.objects.count(),
        "num_provas": Prova.objects.count(),
        "num_simulados": Simulado.objects.count(),
    }
    return render(request, "dashboard/index.html", context)

# Crud Usuários
@login_required
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

@login_required
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

@login_required
def detalhar_usuario(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    return render(request, "dashboard/detalhar_usuario.html", {"usuario": usuario})

@login_required
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

@login_required
def remover_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        questao.delete()
        messages.success(request, "Questão removida com sucesso!")
        return redirect("dashboard:questoes")
    else:
        return render(request, "dashboard/remover_questao.html")

# Crud Provas
@login_required
def listar_provas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        provas = Prova.objects.all().order_by(ordenar)
    else:
        provas = Prova.objects.all().order_by("id")

    paginator = Paginator(provas, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    provas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "dashboard/provas.html", {"provas": provas_paginadas})

@login_required
def criar_prova(request):
    if request.method == "POST":
        form = ProvaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Prova criada com sucesso!")
            return redirect("dashboard:provas")
        else:
            messages.error(request, "Falha ao criar prova!")
    else:
        form = ProvaForm()
    return render(request, "dashboard/criar_prova.html", {"form": form})

@login_required
def detalhar_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    return render(request, "dashboard/detalhar_prova.html", {"prova": prova})

@login_required
def editar_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    if request.method == "POST":
        form = ProvaForm(request.POST, request.FILES, instance=prova)
        if form.is_valid():
            form.save()
            messages.success(request, "Prova atualizado com sucesso!")
            return redirect("dashboard:provas")
        else:
            messages.error(request, "Falha ao criar prova!")
    else:
        form = ProvaForm(instance=prova)
    return render(request, "dashboard/editar_prova.html", {"form": form})

@login_required
def remover_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    if request.method == "POST":
        prova.delete()
        messages.success(request, "Prova removida com sucesso!")
        return redirect("dashboard:provas")
    else:
        return render(request, "dashboard/remover_prova.html")

# Crud Simulados
@login_required
def listar_simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("id")

    paginator = Paginator(simulados, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    simulados_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "dashboard/simulados.html", {"simulados": simulados_paginados})

@login_required
def criar_simulado(request):
    if request.method == "POST":
        form = SimuladoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Simulado criado com sucesso!")
            return redirect("dashboard:simulados")
        else:
            messages.error(request, "Falha ao criar simulado!")
    else:
        form = SimuladoForm()
    return render(request, "dashboard/criar_simulado.html", {"form": form})

@login_required
def detalhar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    return render(request, "dashboard/detalhar_simulado.html", {"simulado": simulado})

@login_required
def editar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    if request.method == "POST":
        form = SimuladoForm(request.POST, request.FILES, instance=simulado)
        if form.is_valid():
            form.save()
            messages.success(request, "Simulado atualizado com sucesso!")
            return redirect("dashboard:simulados")
        else:
            messages.error(request, "Falha ao criar simulado!")
    else:
        form = SimuladoForm(instance=simulado)
    return render(request, "dashboard/editar_simulado.html", {"form": form})

@login_required
def remover_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    if request.method == "POST":
        simulado.delete()
        messages.success(request, "Simulado removido com sucesso!")
        return redirect("dashboard:simulados")
    else:
        return render(request, "dashboard/remover_simulado.html")

# Crud Textos de Apoio
@login_required
def listar_textos(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        textos = TextoDeApoio.objects.all().order_by(ordenar)
    else:
        textos = TextoDeApoio.objects.all().order_by("id")

    paginator = Paginator(textos, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    textos_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "dashboard/textos.html", {"textos": textos_paginados})

@login_required
def criar_texto(request):
    if request.method == "POST":
        form = TextoDeApoioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Texto de Apoio criado com sucesso!")
            return redirect("dashboard:textos")
        else:
            messages.error(request, "Falha ao criar texto de apoio!")
    else:
        form = TextoDeApoioForm()
    return render(request, "dashboard/criar_texto.html", {"form": form})

@login_required
def detalhar_texto(request, id):
    texto = get_object_or_404(TextoDeApoio, id=id)
    return render(request, "dashboard/detalhar_texto.html", {"texto": texto})

@login_required
def editar_texto(request, id):
    texto = get_object_or_404(TextoDeApoio, id=id)
    if request.method == "POST":
        form = TextoDeApoioForm(request.POST, request.FILES, instance=texto)
        if form.is_valid():
            form.save()
            messages.success(request, "Texto de Apoio atualizado com sucesso!")
            return redirect("dashboard:textos")
        else:
            messages.error(request, "Falha ao criar texto de apoio!")
    else:
        form = TextoDeApoioForm(instance=texto)
    return render(request, "dashboard/editar_texto.html", {"form": form})

@login_required
def remover_texto(request, id):
    texto = get_object_or_404(TextoDeApoio, id=id)
    if request.method == "POST":
        texto.delete()
        messages.success(request, "Texto de Apoio removido com sucesso!")
        return redirect("dashboard:textos")
    else:
        return render(request, "dashboard/remover_texto.html")

# Crud Alternativas
@login_required
def listar_alternativas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        alternativas = Alternativa.objects.all().order_by(ordenar)
    else:
        alternativas = Alternativa.objects.all().order_by("id")

    paginator = Paginator(alternativas, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    alternativas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "dashboard/alternativas.html", {"alternativas": alternativas_paginadas})

@login_required
def criar_alternativa(request):
    if request.method == "POST":
        form = AlternativaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Alternativa criada com sucesso!")
            return redirect("dashboard:alternativas")
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = AlternativaForm()
    return render(request, "dashboard/criar_alternativa.html", {"form": form})

@login_required
def detalhar_alternativa(request, id):
    alternativa = get_object_or_404(Alternativa, id=id)
    return render(request, "dashboard/detalhar_alternativa.html", {"alternativa": alternativa})

@login_required
def editar_alternativa(request, id):
    alternativa = get_object_or_404(Alternativa, id=id)
    if request.method == "POST":
        form = AlternativaForm(request.POST, request.FILES, instance=alternativa)
        if form.is_valid():
            form.save()
            messages.success(request, "Alternativa atualizada com sucesso!")
            return redirect("dashboard:alternativas")
        else:
            messages.error(request, "Falha ao criar alternativa!")
    else:
        form = AlternativaForm(instance=alternativa)
    return render(request, "dashboard/editar_alternativa.html", {"form": form})

@login_required
def remover_alternativa(request, id):
    alternativa = get_object_or_404(Alternativa, id=id)
    if request.method == "POST":
        alternativa.delete()
        messages.success(request, "Alternativa removida com sucesso!")
        return redirect("dashboard:alternativas")
    else:
        return render(request, "dashboard/remover_alternativa.html")