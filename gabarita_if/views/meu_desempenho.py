from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from gabarita_if.models import RespostaUsuario, Questao

@login_required
def meu_desempenho(request):
    usuario = request.user
    
    # Dados para gráfico de desempenho ao longo do tempo (últimos 30 dias)
    data_limite = datetime.now() - timedelta(days=30)
    respostas_por_dia = RespostaUsuario.objects.filter(usuario=usuario,respondida_em__gte=data_limite
    ).annotate(
        dia=TruncDate("respondida_em")
    ).values("dia").annotate(
        total=Count("id"),
        acertos=Count("id", filter=Q(acertou=True)),
        erros=Count("id", filter=Q(acertou=False))
    ).order_by("dia")
    
    # Preparar dados para o gráfico de linha/coluna
    dias = []
    totais = []
    percentuais = []
    
    for item in respostas_por_dia:
        dias.append(item["dia"].strftime("%d/%m"))
        totais.append(item["total"])
        if item["total"] > 0:
            percentual = round((item["acertos"] / item["total"]) * 100, 1)
        else:
            percentual = 0
        percentuais.append(percentual)
    
    # Dados para gráfico de donnut (acertos vs erros)
    total_respostas = RespostaUsuario.objects.filter(usuario=usuario).count()
    total_acertos = RespostaUsuario.objects.filter(usuario=usuario, acertou=True).count()
    total_erros = total_respostas - total_acertos
    
    percentual_acertos = round((total_acertos / total_respostas * 100), 1) if total_respostas > 0 else 0
    percentual_erros = round((total_erros / total_respostas * 100), 1) if total_respostas > 0 else 0
    
    # Dados para tabela de percentual por assunto
    desempenho_por_assunto = RespostaUsuario.objects.filter(
        usuario=usuario).values("questao__assunto__nome").annotate(
        total=Count("id"),
        acertos=Count("id", filter=Q(acertou=True))).annotate(
        percentual=ExpressionWrapper(F("acertos") * 100.0 / F("total"), output_field=FloatField())
    ).order_by("-percentual")
    
    respostas = RespostaUsuario.objects.filter(usuario=request.user)
    total_respondidas = respostas.count()

    context = {
        "dias": dias,
        "totais": totais,
        "percentuais": percentuais,
        "total_respostas": total_respostas,
        "total_acertos": total_acertos,
        "total_erros": total_erros,
        "percentual_acertos": percentual_acertos,
        "percentual_erros": percentual_erros,
        "desempenho_por_assunto": desempenho_por_assunto,
        "respondidas": total_respondidas,
        "acertos": respostas.filter(acertou=True).count(),
        "erros": respostas.filter(acertou=False).count(),
    }
    
    return render(request, "gabarita_if/meu_desempenho.html", context)