from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from gabarita_if.models import Questao
from gabarita_if.filters import QuestaoFiltersSet

@login_required
def questoes(request):
    filtros = QuestaoFiltersSet(request.GET, queryset=Questao.objects.all())
    
    ordenar = request.GET.get("ordenar", "id")
    questoes_filtradas = filtros.qs.order_by(ordenar)
    
    paginator = Paginator(questoes_filtradas, 1)
    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode resolver todas as questões disponíveis no Gabarita.",
        "partial": "gabarita_if/partials/_card_questao.html",
        "filtros": filtros,
        "objects": questoes_paginadas,
    }

    return render(request, "listar.html", context)

def responder_questao(request):
    questao_id = request.POST.get('questao_id')
    alternativa_letra = request.POST.get('alternativa_letra')
    
    try:
        questao = Questao.objects.get(id=questao_id)
        acertou = (alternativa_letra == questao.alternativa_correta)
        
        return JsonResponse({
            'acertou': acertou,
            'alternativa_correta': questao.alternativa_correta
        })
    except Questao.DoesNotExist:
        return JsonResponse({'error': 'Questão não encontrada'}, status=404)