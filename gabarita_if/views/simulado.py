from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from gabarita_if.models import Simulado

@login_required
def simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("id")

    paginator = Paginator(simulados, 12)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    simulados_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica
    for simulado in simulados_paginados:
        simulado.num_questoes = simulado.questao_set.count()

    context = {
        "titulo_pagina": "Simulados",
        "subtitulo_pagina": "Aqui você pode responder todos os simuladões do Meta IFRN.",
        "nome": "simulado",
        "url_responder": "gabarita_if:responder-simulado",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": simulados_paginados
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)

    return render(request, "gabarita_if/avaliacao.html", {"object": simulado})

@login_required
def ajax_responder_simulado(request, id):
    pass