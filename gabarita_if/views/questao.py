from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator  
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import io
from xhtml2pdf import pisa

# Todos os modelos importados em uma única linha limpa
from gabarita_if.models import Questao, RespostaQuestao, Comentario, Caderno, Avaliacao
from gabarita_if.filters import QuestaoFiltro

@login_required
def questoes(request):
    if request.method == "POST":
        questao_id = request.POST.get("questao_id")
        # comentário enviado
        comentario_texto = request.POST.get("comentario_texto")
        if comentario_texto and questao_id:
            Comentario.objects.create(usuario=request.user, questao_id=questao_id, texto=comentario_texto)
        if request.POST.get("refazer"):
            RespostaQuestao.objects.filter(usuario=request.user, questao_id=questao_id, tentativa=None).delete()
        else:
            alternativa_escolhida = request.POST.get("alternativa")
            if questao_id and alternativa_escolhida:
                questao = Questao.objects.get(id=questao_id)
                RespostaQuestao.objects.create(
                    usuario=request.user,
                    questao=questao,
                    tentativa=None,
                    alternativa_escolhida=alternativa_escolhida,
                    acertou=alternativa_escolhida == questao.alternativa_correta,
                )

    filtro = QuestaoFiltro(request.GET, queryset=Questao.objects.all(), request=request)
    questoes = filtro.qs.order_by("id")
    
    # Paginator - 1 questão por página
    paginator = Paginator(questoes, 1)  
    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)

    for questao in questoes_paginadas:
        questao.resposta = RespostaQuestao.objects.filter(usuario=request.user, questao=questao, tentativa=None).first()

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode resolver todas as questões disponíveis no Gabarita.",
        "partial": "gabarita_if/partials/_card_questao.html",
        "filtro": filtro,
        "objects": questoes_paginadas
    }

    return render(request, "listar.html", context)


@login_required
def gerar_pdf_questoes(request):
    """Gera PDF com todas as questões filtradas"""
    
    # Verifica se tem assunto
    assunto_id = request.GET.get('assunto')
    if not assunto_id or assunto_id == '':
        messages.error(request, '⚠️ Selecione um ASSUNTO nos filtros para exportar o PDF!')
        return redirect('gabarita_if:questoes')
    
    # Verificar se há filtros aplicados
    if not request.GET:
        messages.warning(request, 'Por favor, aplique filtros antes de exportar o PDF.')
        return redirect('gabarita_if:questoes')
    
    # Aplica os filtros
    filtro = QuestaoFiltro(request.GET, queryset=Questao.objects.all(), request=request)
    questoes = filtro.qs.order_by("id")
    
    # Se não há questões, mostrar mensagem
    if not questoes.exists():
        messages.warning(request, 'Nenhuma questão encontrada com os filtros selecionados.')
        return redirect('gabarita_if:questoes')
    
    # Busca respostas do usuário (apenas para referência)
    for questao in questoes:
        questao.resposta = RespostaQuestao.objects.filter(
            usuario=request.user, 
            questao=questao, 
            tentativa=None
        ).first()
    
    # Coleta filtros aplicados para mostrar no PDF
    filtros_aplicados = {}
    
    disciplina_id = request.GET.get('disciplina')
    if disciplina_id:
        try:
            from gabarita_if.models import Disciplina
            disciplina = Disciplina.objects.get(id=disciplina_id)
            filtros_aplicados['Disciplina'] = disciplina.nome
        except:
            filtros_aplicados['Disciplina'] = f"ID {disciplina_id}"
    
    assunto_id_value = request.GET.get('assunto')
    if assunto_id_value:
        try:
            from gabarita_if.models import Assunto
            assunto = Assunto.objects.get(id=assunto_id_value)
            filtros_aplicados['Assunto'] = assunto.nome
        except:
            filtros_aplicados['Assunto'] = f"ID {assunto_id_value}"
    
    fonte_id = request.GET.get('fonte')
    if fonte_id:
        try:
            from gabarita_if.models import Fonte
            fonte = Fonte.objects.get(id=fonte_id)
            filtros_aplicados['Fonte'] = fonte.nome
        except:
            filtros_aplicados['Fonte'] = f"ID {fonte_id}"
    
    dificuldade = request.GET.get('dificuldade')
    if dificuldade:
        filtros_aplicados['Dificuldade'] = dificuldade
    
    status = request.GET.get('status')
    if status:
        status_map = {
            'respondidas': 'Respondidas',
            'nao_respondidas': 'Não Respondidas',
            'corretas': 'Corretas',
            'incorretas': 'Incorretas'
        }
        filtros_aplicados['Status'] = status_map.get(status, status)
    
    codigo = request.GET.get('codigo')
    if codigo:
        filtros_aplicados['Código'] = codigo
    
    # Renderiza o template HTML do PDF
    html_string = render_to_string('pdf/questoes_pdf.html', {
        'questoes': questoes,
        'usuario': request.user,
        'filtros_aplicados': filtros_aplicados,
        'total_questoes': questoes.count(),
        'data_geracao': datetime.now(),
    })
    
    # Cria a resposta HTTP com o PDF
    response = HttpResponse(content_type='application/pdf')
    filename = f"questoes_assunto_{assunto_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Converte HTML para PDF usando xhtml2pdf
    pisa_status = pisa.CreatePDF(io.BytesIO(html_string.encode('UTF-8')), dest=response)
    
    # Verifica se houve erro na geração do PDF
    if pisa_status.err:
        return HttpResponse(f'Erro ao gerar PDF: {pisa_status.err}', status=500)
    
    return response

@login_required
def baixar_caderno(request, pk):
    caderno = get_object_or_404(Caderno, pk=pk)
    if hasattr(caderno, 'questoes'):
        questoes = caderno.questoes.all()
    else:
        questoes = caderno.questao_set.all()
    
    # Monta os dados estruturados para o template
    html_string = render_to_string('pdf/questoes_pdf.html', {
        'questoes': questoes,
        'usuario': request.user,
        'total_questoes': questoes.count(),
        'data_geracao': timezone.now(),
        'filtros_aplicados': {'Caderno': caderno.nome}  # Mostra o nome do caderno nos filtros do PDF
    })
    
    # Transforma em download de PDF em vez de abrir página HTML
    response = HttpResponse(content_type='application/pdf')
    filename = f"caderno_{pk}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(io.BytesIO(html_string.encode('UTF-8')), dest=response)
    if pisa_status.err:
        return HttpResponse(f'Erro ao gerar PDF: {pisa_status.err}', status=500)
    return response


@login_required
def baixar_avaliacao(request, pk):
    avaliacao = get_object_or_404(Avaliacao, pk=pk)
    questoes = avaliacao.questoes.all() 
    
    # Monta os dados estruturados para o template
    html_string = render_to_string('pdf/questoes_pdf.html', {
        'questoes': questoes,
        'usuario': request.user,
        'total_questoes': questoes.count(),
        'data_geracao': timezone.now(),
        'filtros_aplicados': {'Avaliação': avaliacao.titulo}  # Mostra o nome da avaliação nos filtros do PDF
    })
    
    # Transforma em download de PDF em vez de abrir página HTML
    response = HttpResponse(content_type='application/pdf')
    filename = f"avaliacao_{pk}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(io.BytesIO(html_string.encode('UTF-8')), dest=response)
    if pisa_status.err:
        return HttpResponse(f'Erro ao gerar PDF: {pisa_status.err}', status=500)
    return response


@login_required
def baixar_questao(request, pk):
    questao = get_object_or_404(Questao, pk=pk)
    
    # Monta os dados estruturados para o template
    html_string = render_to_string('pdf/questoes_pdf.html', {
        'questoes': [questao],
        'usuario': request.user,
        'total_questoes': 1,
        'data_geracao': timezone.now(),
        'filtros_aplicados': {'ID da Questão': questao.id}
    })
    
    # Transforma em download de PDF em vez de abrir página HTML
    response = HttpResponse(content_type='application/pdf')
    filename = f"questao_{pk}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    pisa_status = pisa.CreatePDF(io.BytesIO(html_string.encode('UTF-8')), dest=response)
    if pisa_status.err:
        return HttpResponse(f'Erro ao gerar PDF: {pisa_status.err}', status=500)
    return response