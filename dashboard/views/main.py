from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from gabarita_if.models import Questao, Avaliacao, TextoApoio
from usuarios.models import Usuario

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def index(request):
    context = {
        "num_questoes": Questao.objects.count(),
        "num_usuarios": Usuario.objects.count(),
        "num_avaliacoes": Avaliacao.objects.count(),
        "num_textos": TextoApoio.objects.count(),
    }
    
    return render(request, "dashboard/index.html", context)
