from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Questao, RespostaUsuario
from gabarita_if.filters import QuestaoFiltro

@login_required
def questoes(request):
    if request.method == "POST":
        questao_id = request.POST.get("questao_id")
        alternativa_escolhida = request.POST.get("alternativa")

        if questao_id and alternativa_escolhida:
            questao = Questao.objects.get(id=questao_id)

            RespostaUsuario.objects.update_or_create(
                usuario=request.user,
                questao=questao,
                simulado=None,
                prova=None,
                defaults={"alternativa_escolhida": alternativa_escolhida,
                          "acertou": alternativa_escolhida == questao.alternativa_correta}
            )

    filtro = QuestaoFiltro(request.GET, queryset=Questao.objects.all())
    questoes = filtro.qs

    ordenar = request.GET.get("ordenar")
    if ordenar:
        questoes = questoes.order_by(ordenar)
    else:
        questoes = questoes.order_by("id")

    paginator = Paginator(questoes, 1)
    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    for questao in questoes_paginadas:
        questao.resposta = RespostaUsuario.objects.filter(usuario=request.user, questao=questao, simulado=None, prova=None).first()

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode resolver todas as questões disponíveis no Gabarita.",
        "partial": "gabarita_if/partials/_card_questao.html",
        "filtro": filtro,
        "objects": questoes_paginadas,
    }

    return render(request, "listar.html", context)
    