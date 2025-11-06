from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import *
from dashboard.forms import *

@login_required
@permission_required("gabarita_if.add_simulado", raise_exception=True)
def simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("id")

    paginator = Paginator(simulados, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    simulados_paginadas = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Simulados",
        "subtitulo_pagina": "Aqui você pode cadastrar os simulados do Meta IFRN.",
        "url_criar": "dashboard:criar-simulado",
        "partial_tabela": "dashboard/partials/_tabela_simulados.html",
        "simulados": simulados_paginadas
    }
    
    return render(request, "dashboard/listar.html", context)

@login_required
@permission_required("gabarita_if.add_simulado", raise_exception=True)
def criar_simulado(request):
    if request.method == "POST":
        form = SimuladoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Simulado criada com sucesso!")
            return redirect("dashboard:simulados")
        else:
            messages.error(request, "Falha ao criar Simulado!")
    else:
        form = SimuladoForm()
    
    context = {
        "titulo_pagina": "Criar Simulado",
        "url_cancelar": "dashboard:simulados",
        "form": form
    }

    return render(request, "dashboard/criar.html", context)

@login_required
@permission_required("gabarita_if.view_simulado", raise_exception=True)
def detalhar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)

    context = {
        "titulo_pagina": "Detalhar Simulado",
        "partial_detalhar": "dashboard/partials/_detalhar_simulado.html",
        "simulado": simulado
    }

    return render(request, "dashboard/detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_simulado", raise_exception=True)
def editar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    if request.method == "POST":
        form = SimuladoForm(request.POST, request.FILES, instance=simulado)
        if form.is_valid():
            form.save()
            messages.success(request, "Simulado atualizada com sucesso!")
            return redirect("dashboard:simulados")
        else:
            messages.error(request, "Falha ao criar Simulado!")
    else:
        form = SimuladoForm(instance=simulado)

    context = {
        "titulo_pagina": "Editar Simulado",
        "url_cancelar": "dashboard:simulados",
        "form": form
    }

    return render(request, "dashboard/editar.html", context)

@login_required
def remover_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)

    if request.method == "POST":
        simulado.delete()
        messages.success(request, "Simulado removida com sucesso!")
        return redirect("dashboard:simulados")
    else:
        context = {
            "object": simulado,
            "url_remover": "dashboard:remover-simulado"
        }

        return render(request, "dashboard/remover.html", context)
