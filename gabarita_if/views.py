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
def questao_detalhar(request, id):
    questao = get_object_or_404(Questao, id=id)
    return render(request, "gabarita_if/questao_detalhar.html", {"questao": questao})

@login_required
def provas(request):
    return render(request, "gabarita_if/provas.html")

@login_required
def simulados(request):
    return render(request, "gabarita_if/simulados.html")

@login_required
def listas_personalizadas(request):
    return render(request, "gabarita_if/listas_personalizadas.html")

@login_required
def meu_desempenho(request):
    return render(request, "gabarita_if/meu_desempenho.html")