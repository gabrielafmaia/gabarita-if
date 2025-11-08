from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse 
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
def provas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        provas = Prova.objects.all().order_by(ordenar)
    else:
        provas = Prova.objects.all().order_by("id")

    paginator = Paginator(provas, 12)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    provas_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    for prova in provas_paginadas:
        prova.num_questoes = prova.questao_set.count()

    context = {
        "titulo_pagina": "Provas",
        "subtitulo_pagina": "Aqui você pode cadastrar provas.",
        "url_criar": "gabarita_if:criar-prova",
        "partial_lista": "gabarita_if/partials/_lista_provas.html",
        "mostrar_botao": False,
        "provas": provas_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
def detalhar_prova(request, id):
    prova = get_object_or_404(Prova, id=id)

    context = {
        "titulo_pagina": "Detalhar prova",
        "partial_detalhar": "gabarita_if/partials/_detalhar_prova.html",
        "prova": prova
    }

    return render(request, "detalhar.html", context)