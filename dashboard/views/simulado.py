from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import SimuladoTabela
from django_tables2 import RequestConfig
from gabarita_if.models import Simulado
from dashboard.forms import SimuladoForm

@login_required
@permission_required("gabarita_if.add_simulado", raise_exception=True)
def simulados(request):
    simulados = Simulado.objects.all()

    tabela = SimuladoTabela(simulados)
    RequestConfig(request, paginate={"per_page": 12}).configure(tabela)

    context = {
        "titulo_pagina": "Simulados",
        "subtitulo_pagina": "Aqui você pode cadastrar os simulados do Meta IFRN.",
        "nome": "simulado",
        "url_criar": "dashboard:criar-simulado",
        "url_detalhar": "dashboard:detalhar-simulado",
        "url_editar": "dashboard:editar-simulado",
        "url_remover": "dashboard:remover-simulado",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": simulados
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_simulado", raise_exception=True)
def criar_simulado(request):
    if request.method == "POST":
        form = SimuladoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Simulado criado com sucesso!")
            return redirect("dashboard:simulados")
        else:
            messages.error(request, "Falha ao criar simulado!")
    else:
        form = SimuladoForm()
    
    context = {
        "titulo_pagina": "Criar simulado",
        "url_voltar": "dashboard:simulados",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_simulado", raise_exception=True)
def detalhar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    fields = "__all__"
    safe_fields = []

    def get_fields():
        selected_fields = []
        no_check = not isinstance(fields, (list, tuple))
        for field in simulado._meta.fields:
            if no_check or field.name in fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(simulado, field.name),
                        "safe": True if field.name in safe_fields else False,
                    }
                )
        return selected_fields

    context = {
        "titulo_pagina": "Detalhar simulado",
        "nome": "simulado",
        "url_voltar": "dashboard:simulados",
        "url_editar": "dashboard:editar-simulado",
        "url_remover": "dashboard:remover-simulado",
        "object": simulado,
        "fields": get_fields()
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_simulado", raise_exception=True)
def editar_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)
    if request.method == "POST":
        form = SimuladoForm(request.POST, request.FILES, instance=simulado)
        if form.is_valid():
            form.save()
            messages.success(request, "Simulado atualizado com sucesso!")
            return redirect("dashboard:simulados")
        else:
            messages.error(request, "Falha ao criar simulado!")
    else:
        form = SimuladoForm(instance=simulado)

    context = {
        "titulo_pagina": "Editar simulado",
        "url_voltar": "dashboard:simulados",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_simulado(request, id):
    simulado = get_object_or_404(Simulado, id=id)

    if request.method == "POST":
        simulado.delete()
        messages.success(request, "Simulado removido com sucesso!")
        return redirect("dashboard:simulados")
    else:
        context = {
            "object": simulado,
            "url_remover": "dashboard:remover-simulado"
        }

        return render(request, "remover.html", context)
