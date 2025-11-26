from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import TextoApoioTabela
from django_tables2 import RequestConfig
from gabarita_if.models import *
from dashboard.forms import *

@login_required
@permission_required("gabarita_if.add_texto", raise_exception=True)
def textos(request):
    textos = TextoApoio.objects.all()

    tabela = TextoApoioTabela(textos)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)

    context = {
        "titulo_pagina": "Textos de Apoio",
        "subtitulo_pagina": "Aqui você pode cadastrar os textos de apoio das questões.",
        "nome": "texto",
        "url_criar": "dashboard:criar-texto",
        "url_detalhar": "dashboard:detalhar-texto",
        "url_editar": "dashboard:editar-texto",
        "url_remover": "dashboard:remover-texto",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": textos
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_texto", raise_exception=True)
def criar_texto(request):
    if request.method == "POST":
        form = TextoApoioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Texto de apoio criado com sucesso!")
            return redirect("dashboard:textos")
        else:
            messages.error(request, "Falha ao criar texto de apoio!")
    else:
        form = TextoApoioForm()
    
    context = {
        "titulo_pagina": "Criar texto",
        "url_voltar": "dashboard:textos",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_texto", raise_exception=True)
def detalhar_texto(request, id):
    texto = get_object_or_404(TextoApoio, id=id)
    fields = "__all__"
    safe_fields = ["texto"]

    def get_fields():
        selected_fields = []
        no_check = not isinstance(fields, (list, tuple))
        for field in texto._meta.fields:
            if no_check or field.name in fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(texto, field.name),
                        "safe": True if field.name in safe_fields else False,
                        "many": False,
                    }
                )
        
        for field in texto._meta.many_to_many:
            if no_check or field.name in fields:
                selected_fields.append({
                    "label": field.verbose_name,
                    "value": getattr(texto, field.name).all(),
                    "safe": False,
                    "many": True,
                })

        return selected_fields

    context = {
        "titulo_pagina": "Detalhar texto",
        "nome": "texto",
        "url_voltar": "dashboard:textos",
        "url_editar": "dashboard:editar-texto",
        "url_remover": "dashboard:remover-texto",
        "object": texto,
        "fields": get_fields()
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_texto", raise_exception=True)
def editar_texto(request, id):
    texto = get_object_or_404(TextoApoio, id=id)
    if request.method == "POST":
        form = TextoApoioForm(request.POST, request.FILES, instance=texto)
        if form.is_valid():
            form.save()
            messages.success(request, "Texto de apoio atualizado com sucesso!")
            return redirect("dashboard:textos")
        else:
            messages.error(request, "Falha ao criar texto de apoio!")
    else:
        form = TextoApoioForm(instance=texto)

    context = {
        "titulo_pagina": "Editar texto",
        "url_voltar": "dashboard:textos",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_texto(request, id):
    texto = get_object_or_404(TextoApoio, id=id)

    if request.method == "POST":
        texto.delete()
        messages.success(request, "Texto de apoio removido com sucesso!")
        return redirect("dashboard:textos")
    else:
        context = {
            "object": texto,
            "url_remover": "dashboard:remover-texto"
        }

        return render(request, "remover.html", context)
