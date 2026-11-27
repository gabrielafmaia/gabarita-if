from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery
from django.utils import timezone
from gabarita_if.models import Avaliacao, RespostaQuestao, RespostaAvaliacao

@login_required
def avaliacoes(request):
    ordenar = request.GET.get("ordenar")
    tipo = request.GET.get("tipo", "Prova")
    if ordenar:
        avaliacoes = Avaliacao.objects.filter(tipo=tipo).order_by(ordenar)
    else:
        avaliacoes = Avaliacao.objects.filter(tipo=tipo).order_by("-ano")

    respostas_da_tentativa = RespostaQuestao.objects.filter(
        tentativa_id=OuterRef("pk"), usuario=request.user
    ).order_by("-respondida_em")
    tentativas_do_usuario = RespostaAvaliacao.objects.filter(
        usuario=request.user, avaliacao_id=OuterRef("pk"), finalizada=True
    ).annotate(
        ultima_resposta_em=Subquery(respostas_da_tentativa.values("respondida_em")[:1])
    ).order_by("-ultima_resposta_em", "-pk")
    avaliacoes = avaliacoes.annotate(
        finalizada=Exists(tentativas_do_usuario),
        ultima_tentativa_id=Subquery(tentativas_do_usuario.values("pk")[:1]),
    )

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
        "avaliacoes_area_estudante": True,
    }

    if request.htmx and not request.htmx.boosted:
        return render(request, "gabarita_if/partials/_avaliacoes_htmx_response.html", context)

    return render(request, "listar.html", context)


@login_required
def iniciar_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    formato = request.GET.get("formato")

    if formato == "online":
        return redirect("gabarita_if:responder-avaliacao", id=avaliacao.id)
    if formato == "impressa":
        return redirect("gabarita_if:baixar-avaliacao", pk=avaliacao.id)

    return HttpResponseBadRequest("Formato de avaliação inválido.")


@login_required
def responder_avaliacao(request, id):
    avaliacao = get_object_or_404(Avaliacao, id=id)
    questoes = avaliacao.questoes.all().order_by("id")

    if request.method == "POST":
        tentativa_id = request.POST.get("tentativa_id")
        with transaction.atomic():
            if tentativa_id:
                tentativa = get_object_or_404(
                    RespostaAvaliacao.objects.select_for_update(),
                    id=tentativa_id,
                    usuario=request.user,
                    avaliacao=avaliacao,
                )
            else:
                tentativa, _ = RespostaAvaliacao.objects.get_or_create(
                    usuario=request.user,
                    avaliacao=avaliacao,
                    finalizada=False,
                    defaults={"iniciada_em": timezone.now()},
                )

            if tentativa.finalizada:
                return redirect("gabarita_if:ver-feedback-avaliacao", id=tentativa.id)

            agora = timezone.now()
            if tentativa.expirou(agora):
                tentativa.encerrar(agora)
                return redirect("gabarita_if:ver-feedback-avaliacao", id=tentativa.id)

            for questao in questoes:
                alternativa_escolhida = request.POST.get(f"questao_{questao.id}")
                if alternativa_escolhida:
                    RespostaQuestao.objects.update_or_create(
                        usuario=request.user,
                        questao=questao,
                        tentativa=tentativa,
                        defaults={
                            "alternativa_escolhida": alternativa_escolhida,
                            "acertou": alternativa_escolhida == questao.alternativa_correta,
                        },
                    )

            tentativa.encerrar(agora)
        return redirect("gabarita_if:ver-feedback-avaliacao", id=tentativa.id)

    with transaction.atomic():
        tentativa, _ = RespostaAvaliacao.objects.get_or_create(
            usuario=request.user,
            avaliacao=avaliacao,
            finalizada=False,
            defaults={"iniciada_em": timezone.now()},
        )
        tentativa = RespostaAvaliacao.objects.select_for_update().get(id=tentativa.id)
        if tentativa.iniciada_em is None:
            tentativa.iniciada_em = timezone.now()
            tentativa.save(update_fields=["iniciada_em"])
        agora = timezone.now()
        if tentativa.expirou(agora):
            tentativa.encerrar(agora)
            return redirect("gabarita_if:ver-feedback-avaliacao", id=tentativa.id)

        tempo_restante = max(
            0,
            tentativa.TEMPO_MAXIMO_SEGUNDOS
            - int((agora - tentativa.iniciada_em).total_seconds()),
        )
        horas, restante = divmod(tempo_restante, 60 * 60)
        minutos, segundos = divmod(restante, 60)

    context = {
        "object": avaliacao,
        "objects": questoes,
        "tentativa": tentativa,
        "tempo_restante_segundos": tempo_restante,
        "tempo_restante_formatado": f"{horas:02d}:{minutos:02d}:{segundos:02d}",
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
        "tempo_gasto_formatado": tentativa.tempo_gasto_formatado,
    }

    return render(request, "gabarita_if/responder.html", context)
