from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Prova, RespostaUsuario, TentativaAvaliacao

@login_required
def provas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        provas = Prova.objects.all().order_by(ordenar)
    else:
        provas = Prova.objects.all().order_by("-ano")

    for prova in provas:
        prova.finalizada = TentativaAvaliacao.objects.filter(usuario=request.user, prova=prova, finalizada=True).exists()

    paginator = Paginator(provas, 9)
    numero_da_pagina = request.GET.get("p")
    provas_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Provas",
        "subtitulo_pagina": "Aqui você pode responder todos os Exames de Seleção do IFRN.",
        "nome": "prova",
        "url_responder": "gabarita_if:responder-prova",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": provas_paginadas,
        "tipo_avaliacao": "prova",
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    questoes = prova.questoes.all().order_by("id")
    if request.method == "POST":
        tentativa = TentativaAvaliacao.objects.create(usuario=request.user, prova=prova, finalizada=False)
        for questao in questoes:
            alternativa_escolhida = request.POST.get(f"questao_{questao.id}")
            if alternativa_escolhida:
                RespostaUsuario.objects.create(
                    usuario=request.user,
                    questao=questao,
                    tentativa=tentativa,
                    alternativa_escolhida=alternativa_escolhida,
                    acertou=alternativa_escolhida == questao.alternativa_correta,
                )

        tentativa.finalizada = True
        tentativa.save()

        return redirect("gabarita_if:ver-feedback-prova", id=tentativa.id)

    context = {
        "object": prova,
        "objects": questoes,
        "url_voltar": "gabarita_if:provas",
        "url_responder": "gabarita_if:responder-prova",
        "mostrar_feedback": False,
        "tipo_avaliacao": "prova"
    }

    return render(request, "gabarita_if/responder.html", context)

@login_required
def ver_feedback_prova(request, id):
    tentativa = get_object_or_404(TentativaAvaliacao, id=id, usuario=request.user,finalizada=True)
    
    if tentativa.prova:
        avaliacao = tentativa.prova
        tipo_avaliacao = "prova"

    questoes = avaliacao.questoes.all().order_by("id")
    respostas = RespostaUsuario.objects.filter(usuario=request.user, tentativa=tentativa)

    respostas_por_questao = {
        resposta.questao_id: resposta for resposta in respostas
    }

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    context = {
        "object": avaliacao,
        "objects": questoes,
        "tentativa": tentativa,
        "url_voltar": "gabarita_if:provas",
        "url_responder": "gabarita_if:responder-prova",
        "mostrar_feedback": True,
        "tipo_avaliacao": tipo_avaliacao
    }

    return render(request, "gabarita_if/responder.html", context)