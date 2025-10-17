from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from .models import *
from .forms import *

@login_required
def index(request):
    return render(request, "gabarita_if/index.html")

@login_required
def questoes(request):
    questoes = Questao.objects.all()
    return render(request, "gabarita_if/questoes.html", {"questoes": questoes})

@login_required
def detalhar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    return render(request, "gabarita_if/detalhar_questao.html", {"questao": questao})

@login_required
def provas(request):
    return render(request, "gabarita_if/provas.html")

def detalhar_prova(request, id):
    pass

@login_required
def simulados(request):
    return render(request, "gabarita_if/simulados.html")

def detalhar_simulado(request, id):
    pass

@login_required
def meu_desempenho(request):
    return render(request, "gabarita_if/meu_desempenho.html")

# Crud Listas Personalizadas
def listar_listas(request):
    return render(request, "gabarita_if/listas.html")
def criar_lista(request):
    pass
def detalhar_lista(request, id):
    pass
def editar_lista(request, id):
    pass
def remover_lista(request, id):
    pass

# Crud Filtros
def listar_filtros(request):
    pass
def criar_filtro(request):
    pass
def detalhar_filtro(request, id):
    pass
def editar_filtro(request, id):
    pass
def remover_filtro(request, id):
    pass
