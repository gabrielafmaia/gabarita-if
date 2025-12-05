from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Simulado, RespostaUsuario, TentativaAvaliacao

@login_required
def simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("-ano")

    for simulado in simulados:
        simulado.finalizada = TentativaAvaliacao.objects.filter(usuario=request.user, simulado=simulado, finalizada=True).exists()

    paginator = Paginator(simulados, 9)
    numero_da_pagina = request.GET.get("p")
    simulados_paginados = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Simulados",
        "subtitulo_pagina": "Aqui você pode responder todos os Exames de Seleção do IFRN.",
        "nome": "simulado",
        "url_responder": "gabarita_if:responder-simulado",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": simulados_paginados,
        "tipo_avaliacao": "simulado",
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    questoes = simulado.questoes.all().order_by("id")

    if request.method == "POST":
        tentativa = TentativaAvaliacao.objects.create(usuario=request.user, simulado=simulado, finalizada=False)

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

        return redirect("gabarita_if:ver-feedback-simulado", id=tentativa.id)

    context = {
        "object": simulado,
        "objects": questoes,
        "url_voltar": "gabarita_if:simulados",
        "mostrar_feedback": False,
        "tipo_avaliacao": "simulado",
    }

    return render(request, "gabarita_if/responder.html", context)

@login_required
def ver_feedback_simulado(request, id):
    tentativa = get_object_or_404(TentativaAvaliacao, id=id, usuario=request.user,finalizada=True)
    
    if tentativa.simulado:
        avaliacao = tentativa.simulado
        tipo_avaliacao = "simulado"

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
        "url_voltar": "gabarita_if:simulados",
        "mostrar_feedback": True,
        "tipo_avaliacao": tipo_avaliacao
    }

    return render(request, "gabarita_if/responder.html", context)