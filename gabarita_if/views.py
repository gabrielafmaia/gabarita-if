from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from .models import *
from .forms import *

def index(request):
    return render(request, "gabarita_if/index.html")

def questoes(request):
    questoes = Questao.objects.all()
    return render(request, "gabarita_if/questoes.html", {"questoes": questoes})

def questao_detalhar(request, id_question):
    questao = get_object_or_404(Questao, id=id_question)
    return render(request, "gabarita_if/questao_detalhar.html", {"questao": questao})

def provas(request):
    return render(request, "gabarita_if/provas.html")

def simulados(request):
    return render(request, "gabarita_if/simulados.html")

def listas_personalizadas(request):
    return render(request, "gabarita_if/listas_personalizadas.html")

def meu_desempenho(request):
    return render(request, "gabarita_if/meu_desempenho.html")