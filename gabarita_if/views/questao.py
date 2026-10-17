
import io
import os
from datetime import datetime
from random import shuffle
from urllib.parse import unquote, urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa

from gabarita_if.filters import QuestaoFiltro
from gabarita_if.models import *


def questoes_banco():
    return Questao.objects.exclude(
        avaliacao__tipo="Simulado"
    ).distinct()


def preparar_questoes_pdf(questoes):
    questoes_preparadas = []
    textos_exibidos = set()

    for questao in questoes:
        questao.textos_pdf = []

        for texto in questao.textoapoio_set.all():
            if texto.pk not in textos_exibidos:
                questao.textos_pdf.append(texto)
                textos_exibidos.add(texto.pk)

        questoes_preparadas.append(questao)

    return questoes_preparadas


def link_callback(uri, rel):
    caminho_url = unquote(urlparse(uri).path)

    media_url = urlparse(settings.MEDIA_URL).path
    static_url = urlparse(settings.STATIC_URL).path

    if media_url and caminho_url.startswith(media_url):
        caminho_relativo = caminho_url[len(media_url):].lstrip("/")
        caminho = os.path.abspath(
            os.path.join(
                str(settings.MEDIA_ROOT),
                caminho_relativo,
            )
        )

        raiz = os.path.abspath(str(settings.MEDIA_ROOT))

        if os.path.commonpath([raiz, caminho]) != raiz:
            return uri

    elif static_url and caminho_url.startswith(static_url):
        caminho_relativo = caminho_url[len(static_url):].lstrip("/")
        caminho = finders.find(caminho_relativo)

    else:
        caminho = uri

    if caminho and os.path.isfile(caminho):
        return os.path.abspath(caminho)

    return uri


def gerar_resposta_pdf(html, filename):
    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html.encode("UTF-8")),
        dest=response,
        link_callback=link_callback,
    )

    if pisa_status.err:
        return HttpResponse(
            f"Erro ao gerar PDF: {pisa_status.err}",
            status=500,
        )

    return response


@login_required
def questoes(request):
    questoes_disponiveis = questoes_banco()

    if request.method == "POST":
        questao_id = request.POST.get("questao_id")
        comentario_texto = request.POST.get("comentario_texto")

        questao = None

        if questao_id:
            questao = questoes_disponiveis.filter(
                id=questao_id
            ).first()

            if questao is None:
                messages.error(
                    request,
                    "Esta questão não está disponível nesta área.",
                )
                return redirect("gabarita_if:questoes")

        if comentario_texto and questao:
            Comentario.objects.create(
                usuario=request.user,
                questao=questao,
                texto=comentario_texto,
            )

        if request.POST.get("refazer"):
            if questao:
                RespostaQuestao.objects.filter(
                    usuario=request.user,
                    questao=questao,
                    tentativa=None,
                ).delete()

        else:
            alternativa_escolhida = request.POST.get(
                "alternativa"
            )

            if questao and alternativa_escolhida:
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

        if getattr(request, "htmx", False) and questao:
            questao.resposta = RespostaQuestao.objects.filter(
                usuario=request.user,
                questao=questao,
                tentativa=None,
            ).first()

            return render(
                request,
                "gabarita_if/partials/_questao_resposta.html",
                {"object": questao},
            )

    filtro = QuestaoFiltro(
        request.GET,
        queryset=questoes_disponiveis,
        request=request,
    )

    questoes_filtradas = filtro.qs.order_by("id")

    paginator = Paginator(questoes_filtradas, 1)

    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    for questao in questoes_paginadas:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user,
            questao=questao,
            tentativa=None,
        ).first()

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": (
            "Aqui você pode resolver todas as questões "
            "disponíveis no Gabarita."
        ),
        "partial": "gabarita_if/partials/_card_questao.html",
        "filtro": filtro,
        "objects": questoes_paginadas,
        "questoes_area_estudante": True,
    }

    if getattr(request, "htmx", False):
        return render(
            request,
            "gabarita_if/partials/questoes_lista.html",
            context,
        )

    return render(request, "listar.html", context)


@login_required
def gerar_pdf_questoes(request):
    assunto_id = request.GET.get("assunto")

    if not assunto_id:
        messages.error(
            request,
            "Selecione um ASSUNTO nos filtros para exportar o PDF!",
        )
        return redirect("gabarita_if:questoes")

    filtro = QuestaoFiltro(
        request.GET,
        queryset=questoes_banco(),
        request=request,
    )

    questoes_filtradas = filtro.qs.order_by("id")

    if not questoes_filtradas.exists():
        messages.warning(
            request,
            "Nenhuma questão encontrada com os filtros selecionados.",
        )
        return redirect("gabarita_if:questoes")

    for questao in questoes_filtradas:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user,
            questao=questao,
            tentativa=None,
        ).first()

    filtros_aplicados = {}

    disciplina_id = request.GET.get("disciplina")

    if disciplina_id:
        disciplina = Disciplina.objects.filter(
            id=disciplina_id
        ).first()

        filtros_aplicados["Disciplina"] = (
            disciplina.nome
            if disciplina
            else f"ID {disciplina_id}"
        )

    assunto_id_value = request.GET.get("assunto")

    if assunto_id_value:
        assunto = Assunto.objects.filter(
            id=assunto_id_value
        ).first()

        filtros_aplicados["Assunto"] = (
            assunto.nome
            if assunto
            else f"ID {assunto_id_value}"
        )

    fonte_id = request.GET.get("fonte")

    if fonte_id:
        fonte = Fonte.objects.filter(
            id=fonte_id
        ).first()

        filtros_aplicados["Fonte"] = (
            fonte.nome
            if fonte
            else f"ID {fonte_id}"
        )

    dificuldade = request.GET.get("dificuldade")

    if dificuldade:
        filtros_aplicados["Dificuldade"] = dificuldade

    status = request.GET.get("status")

    if status:
        status_map = {
            "respondidas": "Respondidas",
            "nao_respondidas": "Não Respondidas",
            "corretas": "Corretas",
            "incorretas": "Incorretas",
        }

        filtros_aplicados["Status"] = status_map.get(
            status,
            status,
        )

    codigo = request.GET.get("codigo")

    if codigo:
        filtros_aplicados["Código"] = codigo

    questoes_preparadas = preparar_questoes_pdf(
        questoes_filtradas.prefetch_related(
            "textoapoio_set"
        )
    )

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes_preparadas,
            "usuario": request.user,
            "filtros_aplicados": filtros_aplicados,
            "total_questoes": len(questoes_preparadas),
            "data_geracao": timezone.now(),
        },
    )

    filename = (
        f"questoes_assunto_"
        f"{assunto_id}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    return gerar_resposta_pdf(
        html_string,
        filename,
    )


@login_required
def gerar_pdf_avaliacao(request, pk):
    avaliacao = get_object_or_404(
        Avaliacao,
        pk=pk,
    )

    questoes = avaliacao.questoes.all()

    html = render_to_string(
        "pdf/avaliacao_pdf.html",
        {
            "avaliacao": avaliacao,
            "questoes": questoes,
        },
    )

    filename = f"avaliacao_{pk}.pdf"

    return gerar_resposta_pdf(
        html,
        filename,
    )


@login_required
def baixar_pdf_questao(request, questao_codigo):
    questao = get_object_or_404(
        Questao,
        codigo=questao_codigo,
    )

    html = render_to_string(
        "pdf/questao_unica_pdf.html",
        {
            "questao": questao,
        },
    )

    filename = f"questao_{questao.codigo}.pdf"

    return gerar_resposta_pdf(
        html,
        filename,
    )


@login_required
def baixar_caderno(request, pk):
    caderno = get_object_or_404(
        Caderno,
        pk=pk,
    )

    questoes = caderno.questoes.prefetch_related(
        "textoapoio_set"
    ).all()

    questoes_preparadas = preparar_questoes_pdf(questoes)

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes_preparadas,
            "usuario": request.user,
            "total_questoes": len(questoes_preparadas),
            "data_geracao": timezone.now(),
            "filtros_aplicados": {
                "Caderno": caderno.nome,
            },
        },
    )

    filename = (
        f"caderno_{pk}_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    return gerar_resposta_pdf(
        html_string,
        filename,
    )


@login_required
def baixar_avaliacao(request, pk):
    avaliacao = get_object_or_404(
        Avaliacao,
        pk=pk,
    )

    questoes = avaliacao.questoes.prefetch_related(
        "textoapoio_set"
    ).all()

    questoes_preparadas = preparar_questoes_pdf(questoes)

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes_preparadas,
            "usuario": request.user,
            "total_questoes": len(questoes_preparadas),
            "data_geracao": timezone.now(),
            "filtros_aplicados": {
                "Avaliação": avaliacao.titulo,
            },
        },
    )

    filename = (
        f"avaliacao_{pk}_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    return gerar_resposta_pdf(
        html_string,
        filename,
    )


@login_required
def baixar_questao(request, pk):
    questao = get_object_or_404(
        Questao.objects.prefetch_related(
            "textoapoio_set"
        ),
        pk=pk,
    )

    questoes_preparadas = preparar_questoes_pdf(
        [questao]
    )

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes_preparadas,
            "usuario": request.user,
            "total_questoes": 1,
            "data_geracao": timezone.now(),
            "filtros_aplicados": {
                "ID da Questão": questao.id,
            },
        },
    )

    filename = (
        f"questao_{pk}_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    return gerar_resposta_pdf(
        html_string,
        filename,
    )


@login_required
def criar_caderno(request):
    from gabarita_if.forms import CadernoForm

    if request.method == "POST":
        form = CadernoForm(request.POST)

        if form.is_valid():
            caderno = form.save(commit=False)
            caderno.usuario = request.user
            caderno.save()

            disciplina = form.cleaned_data["disciplina"]
            assunto = form.cleaned_data["assunto"]
            quantidade = form.cleaned_data["quantidade"]
            dificuldades = form.cleaned_data["dificuldade"]

            questoes_disponiveis = questoes_banco().filter(
                disciplina=disciplina,
            )

            if assunto:
                questoes_disponiveis = questoes_disponiveis.filter(
                    assunto=assunto,
                )

            if dificuldades:
                questoes_disponiveis = questoes_disponiveis.filter(
                    dificuldade__in=dificuldades,
                )

            total_disponivel = questoes_disponiveis.count()

            if total_disponivel < quantidade:
                caderno.delete()

                form.add_error(
                    None,
                    (
                        "Não existem questões suficientes para "
                        "os filtros selecionados. Foram encontradas "
                        f"{total_disponivel} questões, mas você "
                        f"pediu {quantidade}."
                    ),
                )

                return render(
                    request,
                    "gabarita_if/criar_caderno.html",
                    {
                        "form": form,
                    },
                )

            questoes_selecionadas = list(
                questoes_disponiveis
            )

            shuffle(questoes_selecionadas)

            questoes_selecionadas = (
                questoes_selecionadas[:quantidade]
            )

            caderno.questoes.set(
                questoes_selecionadas
            )

            messages.success(
                request,
                f"Caderno criado com {quantidade} questões!",
            )

            return redirect(
                "gabarita_if:baixar_caderno",
                pk=caderno.pk,
            )

    else:
        form = CadernoForm()

    return render(
        request,
        "gabarita_if/criar_caderno.html",
        {
            "form": form,
        },
    )
