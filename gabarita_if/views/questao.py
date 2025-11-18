from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
def questoes(request):
    form = FiltroForm(request.GET)
    questoes = Questao.objects.all()
    
    if form.is_valid():
        disciplina = form.cleaned_data.get('disciplina')
        assunto = form.cleaned_data.get('assunto')
        ano = form.cleaned_data.get('ano')
        id_questao = form.cleaned_data.get('id_questao')
        tipo_avaliacao = form.cleaned_data.get('tipo_avaliacao')
        
        if disciplina:
            questoes = questoes.filter(disciplina=disciplina)
        if assunto:
            questoes = questoes.filter(assunto=assunto)
        if ano:
            questoes = questoes.filter(Q(prova__ano=ano) | Q(simulado__ano=ano))
        if id_questao:
            questoes = questoes.filter(id=id_questao)
        if tipo_avaliacao:
            if tipo_avaliacao == 'prova':
                questoes = questoes.filter(prova__isnull=False)
            elif tipo_avaliacao == 'simulado':
                questoes = questoes.filter(simulado__isnull=False)

    ordenar = request.GET.get("ordenar", "id")
    questoes = questoes.order_by(ordenar)

    paginator = Paginator(questoes, 1)
    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "form": form,
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode resolver todas as questões disponíveis no Gabarita.",
        "partial_lista": "gabarita_if/partials/_lista_questoes.html",
        "objects": questoes_paginadas,
    }

    return render(request, "listar.html", context)

def responder_questao(request):
    questao_id = request.POST.get('questao_id')
    alternativa_letra = request.POST.get('alternativa_letra')
    questao = Questao.objects.get(id=questao_id)
    acertou = (alternativa_letra == questao.alternativa_correta)
    
    return JsonResponse({
        'acertou': acertou,
        'alternativa_correta': questao.alternativa_correta
    })
    