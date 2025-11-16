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
    context = {
        "num_questoes": Questao.objects.count(),
        "num_provas": Prova.objects.count(),
        "num_simulados": Simulado.objects.count(),
    }
    return render(request, "gabarita_if/index.html", context)