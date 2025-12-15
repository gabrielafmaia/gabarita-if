from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, F, ExpressionWrapper, FloatField
from gabarita_if.models import RespostaUsuario

@login_required
def meu_desempenho(request):
    usuario = request.user
    total_respostas = RespostaUsuario.objects.filter(usuario=usuario).count()
    total_acertos = RespostaUsuario.objects.filter(usuario=usuario, acertou=True).count()
    total_erros = total_respostas - total_acertos
    percentual_acertos = round((total_acertos / total_respostas * 100), 1) if total_respostas > 0 else 0
    percentual_erros = round((total_erros / total_respostas * 100), 1) if total_respostas > 0 else 0
    desempenho_por_assunto = RespostaUsuario.objects.filter(
        usuario=usuario).values("questao__assunto__nome").annotate(
        total=Count("id"),
        acertos=Count("id", filter=Q(acertou=True))).annotate(
        percentual=ExpressionWrapper(F("acertos") * 100.0 / F("total"), output_field=FloatField())
    ).order_by("-percentual")
    respostas = RespostaUsuario.objects.filter(usuario=request.user)
    total_respondidas = respostas.count()

    context = {
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