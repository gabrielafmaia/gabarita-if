from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from gabarita_if.models import Simulado, Questao
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
        "objects": simulados_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
def realizar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    questoes = Questao.objects.filter(simulado=simulado)
    
    if request.method == 'POST':
        acertos = 0
        respostas_detalhadas = []
        
        for questao in questoes:
            resposta_usuario = request.POST.get(f'questao_{questao.id}')
            acertou = resposta_usuario == questao.alternativa_correta
            if acertou:
                acertos += 1
            
            respostas_detalhadas.append({
                'questao_id': questao.id,
                'resposta_usuario': resposta_usuario,
                'resposta_correta': questao.alternativa_correta,
                'acertou': acertou
            })
        
        return JsonResponse({
            'acertos': acertos,
            'total': questoes.count(),
            'respostas': respostas_detalhadas
        })
    
    context = {
        "simulado": simulado,
        "questoes": questoes,
    }
    return render(request, "gabarita_if/realizar_simulado.html", context)