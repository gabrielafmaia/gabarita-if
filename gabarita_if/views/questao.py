from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
def questoes(request):
    disciplina_filtro = request.GET.get("disciplina")
    assunto_filtro = request.GET.get("assunto")
    ano_filtro = request.GET.get("ano")
    id_filtro = request.GET.get("codigo")
    tipo_filtro = request.GET.get("tipo", "todos")

    questoes = Questao.objects.all().order_by("id")

    if disciplina_filtro:
        questoes = questoes.filter(disciplina_id=disciplina_filtro)
    if assunto_filtro:
        questoes = questoes.filter(assunto_id=assunto_filtro)
    if ano_filtro:
        questoes = questoes.filter(
            models.Q(prova__ano=ano_filtro) | models.Q(simulado__ano=ano_filtro)
        )
    if id_filtro:
        questoes = questoes.filter(id=id_filtro)

    if tipo_filtro == "prova":
        questoes = questoes.filter(prova__isnull=False)
    elif tipo_filtro == "simulado":
        questoes = questoes.filter(simulado__isnull=False)

    anos = list(Prova.objects.values_list("ano", flat=True)) + list(Simulado.objects.values_list("ano", flat=True))
    anos = sorted(set(anos))

    paginator = Paginator(questoes, 1)
    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "questoes": questoes_paginadas,
        "disciplinas": Disciplina.objects.all(),
        "assuntos": Assunto.objects.all(),
        "anos": anos,
        "tipo_atual": tipo_filtro,
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode cadastrar as questões das provas e simulados.",
        "partial_lista": "gabarita_if/partials/_lista_questoes.html",
        "mostrar_botao": False,
        "questoes": questoes_paginadas
    }

    return render(request, "listar.html", context)

@login_required
def responder_questao(request):
    if request.method == "POST":
        questao_id = request.POST.get('questao_id')
        alternativa_id = request.POST.get('alternativa_id')
        
        questao = Questao.objects.get(id=questao_id)
        alternativa_selecionada = Alternativa.objects.get(id=alternativa_id)
        alternativa_correta = questao.alternativa_set.get(correta=True)
        
        # Encontra o índice da alternativa correta
        alternativas = list(questao.alternativa_set.all().order_by('id'))
        alternativa_correta_index = None
        for i, alt in enumerate(alternativas):
            if alt.id == alternativa_correta.id:
                alternativa_correta_index = i
                break
        
        acertou = alternativa_selecionada.correta
        
        return JsonResponse({
            'acertou': acertou,
            'alternativa_correta_id': alternativa_correta.id,
            'alternativa_correta_index': alternativa_correta_index,
            'mensagem': 'Boa, futuro federal! Você acertou!' if acertou else 'Poxa, futuro federal! Não foi dessa vez!'
        })
