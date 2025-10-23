from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .forms import *

@login_required
def index(request):
    return render(request, "gabarita_if/index.html")

@login_required
def listar_questoes(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        questoes = Questao.objects.all().order_by(ordenar)
    else:
        questoes = Questao.objects.all().order_by("id")

    paginator = Paginator(questoes, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    questoes_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "gabarita_if/questoes.html", {"questoes": questoes_paginadas})

@login_required
def detalhar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    return render(request, "gabarita_if/detalhar_questao.html", {"questao": questao})

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
    for prova in provas_paginadas:
        prova.num_questoes = prova.questao_set.count()
    return render(request, "gabarita_if/provas.html", {"provas": provas_paginadas})

@login_required
def detalhar_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    return render(request, "gabarita_if/detalhar_prova.html", {"prova": prova})

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
    for simulado in simulados_paginados:
        simulado.num_questoes = simulado.questao_set.count()
    return render(request, "gabarita_if/simulados.html", {"simulados": simulados_paginados})

@login_required
def detalhar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    return render(request, "gabarita_if/detalhar_simulado.html", {"simulado": simulado})

@login_required
def meu_desempenho(request):
    return render(request, "gabarita_if/meu_desempenho.html")

# Crud Listas Personalizadas
@login_required
def listar_listas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        listas = ListaPersonalizada.objects.all().order_by(ordenar)
    else:
        listas = ListaPersonalizada.objects.all().order_by("id")

    paginator = Paginator(listas, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    listas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "gabarita_if/listas.html", {"listas": listas_paginadas})

@login_required
def criar_lista(request):
    if request.method == "POST":
        form = ListaPersonalizadaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Lista criada com sucesso!")
            return redirect("gabarita_if:listas")
        else:
            messages.error(request, "Falha ao criar lista!")
    else:
        form = ListaPersonalizadaForm()
    return render(request, "gabarita_if/criar_lista.html", {"form": form})

@login_required
def detalhar_lista(request, id):
    lista = get_object_or_404(ListaPersonalizada, id=id)
    return render(request, "gabarita_if/detalhar_lista.html", {"lista": lista})

@login_required
def editar_lista(request, id):
    lista = get_object_or_404(ListaPersonalizada, id=id)
    if request.method == "POST":
        form = ListaPersonalizadaForm(request.POST, request.FILES, instance=lista)
        if form.is_valid():
            form.save()
            messages.success(request, "Lista atualizada com sucesso!")
            return redirect("gabarita_if:listas")
        else:
            messages.error(request, "Falha ao criar lista!")
    else:
        form = ListaPersonalizadaForm(instance=lista)
    return render(request, "gabarita_if/editar_lista.html", {"form": form})

@login_required
def remover_lista(request, id):
    lista = get_object_or_404(ListaPersonalizada, id=id)
    if request.method == "POST":
        lista.delete()
        messages.success(request, "Lista removida com sucesso!")
        return redirect("gabarita_if:listas")
    else:
        return render(request, "gabarita_if/remover_lista.html")

# Crud Filtros
@login_required
def listar_filtros(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        filtros = Filtro.objects.all().order_by(ordenar)
    else:
        filtros = Filtro.objects.all().order_by("id")

    paginator = Paginator(filtros, 10)
    numero_da_pagina = request.GET.get('p')  # Pega o número da página da URL
    filtros_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica
    return render(request, "gabarita_if/filtros.html", {"filtros": filtros_paginados})

@login_required
def criar_filtro(request):
    if request.method == "POST":
        form = FiltroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Filtro criado com sucesso!")
            return redirect("gabarita_if:filtros")
        else:
            messages.error(request, "Falha ao criar filtro!")
    else:
        form = FiltroForm()
    return render(request, "gabarita_if/criar_filtro.html", {"form": form})

@login_required
def detalhar_filtro(request, id):
    filtro = get_object_or_404(Filtro, id=id)
    return render(request, "gabarita_if/detalhar_filtro.html", {"filtro": filtro})

@login_required
def editar_filtro(request, id):
    filtro = get_object_or_404(Filtro, id=id)
    if request.method == "POST":
        form = FiltroForm(request.POST, request.FILES, instance=filtro)
        if form.is_valid():
            form.save()
            messages.success(request, "Filtro atualizado com sucesso!")
            return redirect("gabarita_if:filtro")
        else:
            messages.error(request, "Falha ao criar filtro!")
    else:
        form = FiltroForm(instance=filtro)
    return render(request, "gabarita_if/editar_filtro.html", {"form": form})

@login_required
def remover_filtro(request, id):
    filtro = get_object_or_404(Filtro, id=id)
    if request.method == "POST":
        filtro.delete()
        messages.success(request, "Filtro removido com sucesso!")
        return redirect("gabarita_if:filtros")
    else:
        return render(request, "gabarita_if/remover_filtro.html")
