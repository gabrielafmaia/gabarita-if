from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from gabarita_if.models import RespostaQuestao
from gabarita_if.forms import *

@login_required
def redirecionar(request):
    if request.user.is_superuser:
        return redirect("dashboard:index")
    else:
        return render(request, "gabarita_if/index.html")

@login_required
def index(request):
    respostas = RespostaQuestao.objects.filter(usuario=request.user)
    total_respondidas = respostas.count()

    context = {
        "respondidas": total_respondidas,
        "acertos": respostas.filter(acertou=True).count(),
        "erros": respostas.filter(acertou=False).count(),
    }

    return render(request, "gabarita_if/index.html", context)
