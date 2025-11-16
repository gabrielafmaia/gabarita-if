from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
def simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("id")

    paginator = Paginator(simulados, 12)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    simulados_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica
    for simulado in simulados_paginadas:
        simulado.num_questoes = simulado.questao_set.count()

    context = {
        "titulo_pagina": "Simulados",
        "subtitulo_pagina": "Aqui você pode realizar todos os simuladões do Meta IFRN.",
        "partial_lista": "gabarita_if/partials/_lista_simulados.html",
        "simulados": simulados_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
def detalhar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)

    context = {
        "titulo_pagina": "Detalhar simulado",
        "url_voltar": "gabarita_if:simulados",
        "partial_detalhar": "gabarita_if/partials/_detalhar_simulado.html",
        "object": simulado
    }

    return render(request, "detalhar.html", context)