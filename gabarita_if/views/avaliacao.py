from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Avaliacao, RespostaQuestao, RespostaAvaliacao

@login_required
def avaliacoes(request):
    ordenar = request.GET.get("ordenar")
    tipo = request.GET.get("tipo", "Prova")
    if ordenar:
        avaliacoes = Avaliacao.objects.filter(tipo=tipo).order_by(ordenar)
    else:
        avaliacoes = Avaliacao.objects.filter(tipo=tipo).order_by("-ano")

    for avaliacao in avaliacoes:
        avaliacao.finalizada = RespostaAvaliacao.objects.filter(usuario=request.user, avaliacao=avaliacao, finalizada=True).exists()

    paginator = Paginator(avaliacoes, 9)
    numero_da_pagina = request.GET.get("p")
    avaliacoes_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Avaliações",
        "subtitulo_pagina": "Aqui você pode responder todos os Exames de Seleção do IFRN.",
        "nome": "avaliação",
        "url_responder": "gabarita_if:responder-avaliacao",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": avaliacoes_paginadas,
        "tipo_avaliacao": "avaliacao",
        "avaliacoes": True,
        "tipo_selecionado": tipo,
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    questoes = avaliacao.questoes.all().order_by("id")
    if request.method == "POST":
        tentativa = RespostaAvaliacao.objects.create(usuario=request.user, avaliacao=avaliacao, finalizada=False)
        for questao in questoes:
            alternativa_escolhida = request.POST.get(f"questao_{questao.id}")
            if alternativa_escolhida:
                RespostaQuestao.objects.create(
                    usuario=request.user,
                    questao=questao,
                    tentativa=tentativa,
                    alternativa_escolhida=alternativa_escolhida,
                    acertou=alternativa_escolhida == questao.alternativa_correta,
                )

        tentativa.finalizada = True
        tentativa.save()

        return redirect("gabarita_if:ver-feedback-avaliacao", id=tentativa.id)

    context = {
        "object": avaliacao,
        "objects": questoes,
        "url_voltar": "gabarita_if:avaliacoes",
        "url_responder": "gabarita_if:responder-avaliacao",
        "mostrar_feedback": False,
        "tipo_avaliacao": "avaliacao"
    }

    return render(request, "gabarita_if/responder.html", context)

@login_required
def ver_feedback_avaliacao(request, id):
    tentativa = get_object_or_404(RespostaAvaliacao, id=id, usuario=request.user,finalizada=True)
    avaliacao = tentativa.avaliacao
    questoes = avaliacao.questoes.all().order_by("id")
    respostas = RespostaQuestao.objects.filter(usuario=request.user, tentativa=tentativa)

    respostas_por_questao = {
        resposta.questao_id: resposta for resposta in respostas
    }

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    total_respondidas = respostas.count()
    total_acertos = respostas.filter(acertou=True).count()
    total_erros = total_respondidas - total_acertos

    context = {
        "object": avaliacao,
        "objects": questoes,
        "tentativa": tentativa,
        "url_voltar": "gabarita_if:avaliacoes",
        "url_responder": "gabarita_if:responder-avaliacao",
        "mostrar_feedback": True,
        "total_respondidas": total_respondidas,
        "total_acertos": total_acertos,
        "total_erros": total_erros,
    }

    return render(request, "gabarita_if/responder.html", context)
