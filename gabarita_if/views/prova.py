from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from gabarita_if.models import Prova, Questao, RespostaQuestao, RespostaAvaliacao

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
        "subtitulo_pagina": "Aqui você pode responder todos os Exames de Seleção do IFRN.",
        "nome": "prova",
        "url_responder": "gabarita_if:responder-prova",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": provas_paginadas
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_prova(request, id):
    prova = get_object_or_404(Prova, id=id)
    questoes = Questao.objects.filter(prova=prova).order_by("id")

    if request.method == "POST":
        for questao in questoes:
            alternativa_escolhida = request.POST.get(f"questao_{questao.id}")
            if alternativa_escolhida:
                RespostaQuestao.objects.update_or_create(
                    usuario=request.user,
                    questao=questao,
                    prova=prova,
                    defaults={"alternativa_escolhida": alternativa_escolhida, 
                              "acertou": alternativa_escolhida == questao.alternativa_correta}
                )
        RespostaAvaliacao.objects.update_or_create(usuario=request.user, prova=prova, defaults={"finalizada": True})

    respostas = RespostaQuestao.objects.filter(usuario=request.user, prova=prova)
    
    respostas_por_questao = {}
    for resposta in respostas:
        respostas_por_questao[resposta.questao_id] = resposta

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    avaliacao = RespostaAvaliacao.objects.filter(usuario=request.user, prova=prova).first()

    context = {
        "prova": prova,
        "logo": "assets/img/ifrn-branco.png",
        "objects": questoes,
        "finalizado": avaliacao.finalizada if avaliacao else False,
    }

    return render(request, "gabarita_if/responder.html", context)