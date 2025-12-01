from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Simulado, RespostaUsuario

@login_required
def simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("id")

    paginator = Paginator(simulados, 9)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    simulados_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica

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
    questoes = simulado.questoes.all().order_by("id")

    if request.method == "POST":

        # 🔁 REFazer simulado (apaga todas as respostas)
        if request.POST.get("refazer"):
            RespostaUsuario.objects.filter(
                usuario=request.user,
                simulado=simulado,
            ).delete()

            return redirect("gabarita_if:responder-simulado", id=simulado.id)

        # ✅ RESPONDER simulado (uma única vez, sobrescrevendo)
        else:
            for questao in questoes:
                alternativa_escolhida = request.POST.get(f"questao_{questao.id}")

                if alternativa_escolhida:
                    RespostaUsuario.objects.update_or_create(
                        usuario=request.user,
                        questao=questao,
                        simulado=simulado,
                        defaults={
                            "alternativa_escolhida": alternativa_escolhida,
                            "acertou": alternativa_escolhida == questao.alternativa_correta,
                        },
                    )

    # respostas do usuário dessa simulado
    respostas = RespostaUsuario.objects.filter(
        usuario=request.user,
        simulado=simulado,
    )

    respostas_por_questao = {
        resposta.questao_id: resposta for resposta in respostas
    }

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    # ✅ verifica se a simulado já foi respondida
    simulado.respondida = respostas.exists()

    context = {
        "simulado": simulado,
        "logo": "assets/img/ifrn-branco.png",
        "objects": questoes,
    }

    return render(request, "gabarita_if/responder.html", context)