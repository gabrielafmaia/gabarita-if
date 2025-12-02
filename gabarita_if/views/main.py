from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from gabarita_if.models import *
from gabarita_if.forms import *

@login_required
def redirecionar(request):
    if request.user.is_superuser:
        return redirect("dashboard:index")
    else:
        return render(request, "gabarita_if/index.html")

@login_required
def index(request):
    total_questoes = Questao.objects.count()
    respostas = RespostaUsuario.objects.filter(usuario=request.user)
    total_respondidas = respostas.count()

    context = {
        "num_questoes": total_questoes,
        "respondidas": total_respondidas,
        "acertos": respostas.filter(acertou=True).count(),
        "erros": respostas.filter(acertou=False).count(),
        "percentual": int((total_respondidas / total_questoes) * 100)
    }

    return render(request, "gabarita_if/index.html", context)
