from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from gabarita_if.models import (
    Caderno,
    RespostaQuestao,
    Questao,
    Disciplina,
    Assunto,
    Fonte,
)
from gabarita_if.forms import CadernoForm
from gabarita_if.filters import QuestaoFiltro


@login_required
def cadernos(request):
    cadernos = Caderno.objects.filter(
        usuario=request.user
    ).order_by("id")

    paginator = Paginator(cadernos, 10)
    numero_da_pagina = request.GET.get("p")
    cadernos_paginados = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Cadernos",
        "subtitulo_pagina": "Aqui você pode cadastrar seus cadernos.",
        "nome": "caderno",
        "url_criar": "gabarita_if:ajax-criar-caderno",
        "partial": "gabarita_if/partials/_card_caderno.html",
        "objects": cadernos_paginados,
    }

    return render(request, "listar.html", context)


@login_required
def ajax_criar_caderno(request):
    if request.method == "POST":
        form = CadernoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            disciplina = form.cleaned_data["disciplina"]
            assunto = form.cleaned_data["assunto"]
            quantidade = form.cleaned_data["quantidade"]
            dificuldades = form.cleaned_data["dificuldades"]

            questoes = Questao.objects.filter(
                disciplina=disciplina
            )

            if assunto:
                questoes = questoes.filter(
                    assunto=assunto
                )

            if dificuldades:
                questoes = questoes.filter(
                    dificuldade__in=dificuldades
                )

            total_disponivel = questoes.count()

            if total_disponivel < quantidade:
                form.add_error(
                    None,
                    f"Foram encontradas apenas {total_disponivel} "
                    f"questões para os filtros selecionados, "
                    f"mas você pediu {quantidade}."
                )

                return render(
    request,
    "criar.html",
    {
        "form": form,
        "disciplinas": Disciplina.objects.all(),
        "assuntos": Assunto.objects.select_related("disciplina").all(),
        "fontes": Fonte.objects.all(),
    }
)

            caderno = form.save(commit=False)
            caderno.usuario = request.user
            caderno.save()

            import random

            questoes_selecionadas = random.sample(
                list(questoes),
                quantidade
            )

            caderno.questoes.set(
                questoes_selecionadas
            )

            messages.success(
                request,
                "Caderno criado com sucesso!"
            )

            return JsonResponse(
                {
                    "mensagem": "Caderno criado com sucesso!",
                    "caderno_id": caderno.id,
                },
                status=201
            )

        messages.error(
            request,
            "Falha ao criar caderno!"
        )

    else:
        form = CadernoForm()

    return render(
        request,
        "criar.html",
        {"form": form}
    )


@login_required
def detalhar_caderno(request, id):
    caderno = get_object_or_404(
        Caderno,
        id=id
    )

    if request.method == "POST":
        questao_id = request.POST.get("questao_id")

        if request.POST.get("refazer"):
            RespostaQuestao.objects.filter(
                usuario=request.user,
                questao_id=questao_id,
                tentativa=None
            ).delete()

        else:
            alternativa_escolhida = request.POST.get(
                "alternativa"
            )

            if questao_id and alternativa_escolhida:
                questao = Questao.objects.get(
                    id=questao_id
                )

                RespostaQuestao.objects.create(
                    usuario=request.user,
                    questao=questao,
                    tentativa=None,
                    alternativa_escolhida=alternativa_escolhida,
                    acertou=(
                        alternativa_escolhida
                        == questao.alternativa_correta
                    ),
                )

    filtro = QuestaoFiltro(
        request.GET,
        queryset=caderno.questoes.all(),
        request=request
    )

    questoes_filtradas = filtro.qs.order_by("id")

    paginator = Paginator(
        questoes_filtradas,
        1
    )

    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(
        numero_da_pagina
    )

    for questao in questoes_paginadas:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user,
            questao=questao,
            tentativa=None
        ).first()

    context = {
        "titulo": caderno.nome,
        "object": caderno,
        "objects": questoes_paginadas,
        "filtro": filtro,
    }

    return render(
        request,
        "gabarita_if/detalhar_caderno.html",
        context
    )


@login_required
def ajax_editar_caderno(request, id):
    caderno = get_object_or_404(
        Caderno,
        id=id
    )

    if request.method == "POST":
        form = CadernoForm(
            request.POST,
            request.FILES,
            instance=caderno
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Caderno atualizado com sucesso!"
            )

            return JsonResponse(
                {
                    "mensagem": "Caderno atualizado com sucesso!"
                },
                status=200
            )

        messages.error(
            request,
            "Falha ao atualizar caderno!"
        )

    else:
        form = CadernoForm(
            instance=caderno
        )

    return render(
        request,
        "editar.html",
        {"form": form}
    )


@login_required
def ajax_remover_caderno(request, id):
    caderno = get_object_or_404(
        Caderno,
        id=id
    )

    if request.method == "POST":
        caderno.delete()

        messages.success(
            request,
            "Caderno removido com sucesso!"
        )

        return redirect(
            "gabarita_if:cadernos"
        )

    context = {
        "object": caderno,
        "url_remover": "gabarita_if:ajax-remover-caderno",
    }

    return render(
        request,
        "remover.html",
        context
    )