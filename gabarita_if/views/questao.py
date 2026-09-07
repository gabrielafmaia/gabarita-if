import io
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from xhtml2pdf import pisa
from gabarita_if.filters import QuestaoFiltro
from gabarita_if.models import *
from random import shuffle


@login_required
def questoes(request):
    if request.method == "POST":
        questao_id = request.POST.get("questao_id")
        comentario_texto = request.POST.get("comentario_texto")

        # Comentário enviado
        if comentario_texto and questao_id:
            Comentario.objects.create(
                usuario=request.user,
                questao_id=questao_id,
                texto=comentario_texto,
            )

        # Refazer questão
        if request.POST.get("refazer"):
            RespostaQuestao.objects.filter(
                usuario=request.user,
                questao_id=questao_id,
                tentativa=None,
            ).delete()

        else:
            alternativa_escolhida = request.POST.get("alternativa")

            if questao_id and alternativa_escolhida:
                try:
                    questao = Questao.objects.get(id=questao_id)

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

                except Questao.DoesNotExist:
                    messages.error(
                        request,
                        "⚠️ Esta questão não está mais disponível.",
                    )

    filtro = QuestaoFiltro(
        request.GET,
        queryset=Questao.objects.all(),
        request=request,
    )

    questoes = filtro.qs.order_by("id")

    # 1 questão por página
    paginator = Paginator(questoes, 1)

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
    }

    return render(request, "listar.html", context)


@login_required
def gerar_pdf_questoes(request):
    """Gera PDF com todas as questões filtradas."""

    assunto_id = request.GET.get("assunto")

    if not assunto_id or assunto_id == "":
        messages.error(
            request,
            "⚠️ Selecione um ASSUNTO nos filtros para exportar o PDF!",
        )
        return redirect("gabarita_if:questoes")

    if not request.GET:
        messages.warning(
            request,
            "Por favor, aplique filtros antes de exportar o PDF.",
        )
        return redirect("gabarita_if:questoes")

    filtro = QuestaoFiltro(
        request.GET,
        queryset=Questao.objects.all(),
        request=request,
    )

    questoes = filtro.qs.order_by("id")

    if not questoes.exists():
        messages.warning(
            request,
            "Nenhuma questão encontrada com os filtros selecionados.",
        )
        return redirect("gabarita_if:questoes")

    # Busca respostas do usuário
    for questao in questoes:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user,
            questao=questao,
            tentativa=None,
        ).first()

    # Filtros aplicados
    filtros_aplicados = {}

    disciplina_id = request.GET.get("disciplina")

    if disciplina_id:
        try:
            disciplina = Questao.objects.get(
                disciplina_id=disciplina_id
            ).disciplina

            filtros_aplicados["Disciplina"] = disciplina.nome

        except Exception:
            filtros_aplicados["Disciplina"] = f"ID {disciplina_id}"

    assunto_id_value = request.GET.get("assunto")

    if assunto_id_value:
        try:
            assunto = Questao.objects.get(
                assunto_id=assunto_id_value
            ).assunto

            filtros_aplicados["Assunto"] = assunto.nome

        except Exception:
            filtros_aplicados["Assunto"] = (
                f"ID {assunto_id_value}"
            )

    fonte_id = request.GET.get("fonte")

    if fonte_id:
        try:
            fonte = Questao.objects.get(
                fonte_id=fonte_id
            ).fonte

            filtros_aplicados["Fonte"] = fonte.nome

        except Exception:
            filtros_aplicados["Fonte"] = f"ID {fonte_id}"

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

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes,
            "usuario": request.user,
            "filtros_aplicados": filtros_aplicados,
            "total_questoes": questoes.count(),
            "data_geracao": datetime.now(),
        },
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    filename = (
        f"questoes_assunto_"
        f"{assunto_id}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html_string.encode("UTF-8")),
        dest=response,
    )

    if pisa_status.err:
        return HttpResponse(
            f"Erro ao gerar PDF: {pisa_status.err}",
            status=500,
        )

    return response


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

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{avaliacao.titulo}.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response,
    )

    return response


@login_required
def baixar_pdf_questao(request, questao_codigo):
    questao = get_object_or_404(
        Questao,
        codigo=questao_codigo,
    )

    template_path = "pdf/questao_unica_pdf.html"

    context = {
        "questao": questao,
    }

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="questao_{questao.codigo}.pdf"'
    )

    html = render_to_string(
        template_path,
        context,
    )

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
    )

    if pisa_status.err:
        return HttpResponse(
            "Erro ao gerar o PDF",
            status=500,
        )

    return response


@login_required
def baixar_caderno(request, pk):
    caderno = get_object_or_404(
        Caderno,
        pk=pk,
    )

    questoes = caderno.questoes.all()

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes,
            "usuario": request.user,
            "total_questoes": questoes.count(),
            "data_geracao": timezone.now(),
            "filtros_aplicados": {
                "Caderno": caderno.nome,
            },
        },
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    filename = (
        f"caderno_{pk}_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html_string.encode("UTF-8")),
        dest=response,
    )

    if pisa_status.err:
        return HttpResponse(
            f"Erro ao gerar PDF: {pisa_status.err}",
            status=500,
        )

    return response


@login_required
def baixar_avaliacao(request, pk):
    avaliacao = get_object_or_404(
        Avaliacao,
        pk=pk,
    )

    questoes = avaliacao.questoes.all()

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": questoes,
            "usuario": request.user,
            "total_questoes": questoes.count(),
            "data_geracao": timezone.now(),
            "filtros_aplicados": {
                "Avaliação": avaliacao.titulo,
            },
        },
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    filename = (
        f"avaliacao_{pk}_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html_string.encode("UTF-8")),
        dest=response,
    )

    if pisa_status.err:
        return HttpResponse(
            f"Erro ao gerar PDF: {pisa_status.err}",
            status=500,
        )

    return response


@login_required
def baixar_questao(request, pk):
    questao = get_object_or_404(
        Questao,
        pk=pk,
    )

    html_string = render_to_string(
        "pdf/questoes_pdf.html",
        {
            "questoes": [questao],
            "usuario": request.user,
            "total_questoes": 1,
            "data_geracao": timezone.now(),
            "filtros_aplicados": {
                "ID da Questão": questao.id,
            },
        },
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    filename = (
        f"questao_{pk}_"
        f"{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{filename}"'
    )

    pisa_status = pisa.CreatePDF(
        io.BytesIO(html_string.encode("UTF-8")),
        dest=response,
    )

    if pisa_status.err:
        return HttpResponse(
            f"Erro ao gerar PDF: {pisa_status.err}",
            status=500,
        )

    return response


@login_required
def criar_caderno(request):

    # Importa o formulário
    from gabarita_if.forms import CadernoForm

    if request.method == "POST":

        form = CadernoForm(request.POST)

        if form.is_valid():

            # Cria o caderno sem salvar ainda
            caderno = form.save(commit=False)

            # Define o usuário logado
            caderno.usuario = request.user

            # Salva o caderno
            caderno.save()

            # Pega os dados do formulário
            disciplina = form.cleaned_data["disciplina"]
            assunto = form.cleaned_data["assunto"]
            quantidade = form.cleaned_data["quantidade"]
            dificuldades = form.cleaned_data["dificuldades"]

           
            questoes = Questao.objects.filter(
                disciplina=disciplina,
            )

            # Se escolheu um assunto
            if assunto:
                questoes = questoes.filter(
                    assunto=assunto,
                )

            # Se escolheu dificuldade(s)
            if dificuldades:
                questoes = questoes.filter(
                    dificuldade__in=dificuldades,
                )

            
            total_disponivel = questoes.count()

            if total_disponivel < quantidade:

                # Remove o caderno que foi criado
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

            questoes_selecionadas = list(questoes)

            # Embaralha para selecionar questões aleatórias
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
