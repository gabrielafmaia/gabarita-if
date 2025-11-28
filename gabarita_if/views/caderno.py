from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from gabarita_if.models import Caderno, RespostaUsuario, Questao
from gabarita_if.forms import CadernoForm
from gabarita_if.filters import QuestaoFiltro


@login_required
def cadernos(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        cadernos = Caderno.objects.filter(usuario=request.user).order_by(ordenar)
    else:
        cadernos = Caderno.objects.filter(usuario=request.user).order_by("id")

    paginator = Paginator(cadernos, 10)
    numero_da_pagina = request.GET.get("p")  # Pega o número da página da URL
    cadernos_paginados = paginator.get_page(numero_da_pagina)  # Pega a página específica

    context = {
        "titulo_pagina": "Cadernos",
        "subtitulo_pagina": "Aqui você pode cadastrar seus cadernos.",
        "nome": "caderno",
        "url_criar": "gabarita_if:criar-caderno",
        "partial": "gabarita_if/partials/_card_caderno.html",
        "objects": cadernos_paginados
    }
    
    return render(request, "listar.html", context)

@login_required
def criar_caderno(request):
    if request.method == "POST":
        form = CadernoForm(request.POST, request.FILES)
        if form.is_valid():
            caderno = form.save(commit=False)
            caderno.usuario = request.user
            caderno.save()
            form.save_m2m() # Importante para carregar as questões
            messages.success(request, "caderno criada com sucesso!")
            return redirect("gabarita_if:cadernos")
        else:
            messages.error(request, "Falha ao criar caderno!")
    else:
        form = CadernoForm()
    
    context = {
        "titulo_pagina": "Criar caderno",
        "url_voltar": "gabarita_if:cadernos",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
def detalhar_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        questao_id = request.POST.get("questao_id")
        alternativa_escolhida = request.POST.get("alternativa")

        if questao_id and alternativa_escolhida:
            questao = Questao.objects.get(id=questao_id)

            RespostaUsuario.objects.update_or_create(
                usuario=request.user,
                questao=questao,
                simulado=None,
                prova=None,
                defaults={"alternativa_escolhida": alternativa_escolhida,
                          "acertou": alternativa_escolhida == questao.alternativa_correta}
            )
    
    questoes = caderno.questoes.all()
    filtro = QuestaoFiltro(request.GET, queryset=questoes, request=request)
    questoes_filtradas = filtro.qs
    
    ordenar = request.GET.get("ordenar")
    if ordenar:
        questoes_filtradas = questoes_filtradas.order_by(ordenar)
    else:
        questoes_filtradas = questoes_filtradas.order_by("id")
    
    paginator = Paginator(questoes_filtradas, 1)
    numero_da_pagina = request.GET.get("p")
    questoes_paginadas = paginator.get_page(numero_da_pagina)
    
    for questao in questoes_paginadas:
        questao.resposta = RespostaUsuario.objects.filter(
            usuario=request.user, 
            questao=questao, 
            simulado=None, 
            prova=None
        ).first()

    context = {
        "titulo": caderno.nome,
        "object": caderno,
        "objects": questoes_paginadas,
        "filtro": filtro,
    }

    return render(request, "gabarita_if/detalhar_caderno.html", context)

@login_required
def editar_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)
    if request.method == "POST":
        form = CadernoForm(request.POST, request.FILES, instance=caderno)
        if form.is_valid():
            form.save()
            messages.success(request, "Caderno atualizado com sucesso!")
            return redirect("gabarita_if:cadernos")
        else:
            messages.error(request, "Falha ao criar caderno!")
    else:
        form = CadernoForm(instance=caderno)

    context = {
        "titulo_pagina": "Editar caderno",
        "url_voltar": "gabarita_if:cadernos",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
def remover_caderno(request, id):
    caderno = get_object_or_404(Caderno, id=id)

    if request.method == "POST":
        caderno.delete()
        messages.success(request, "Caderno removido com sucesso!")
        return redirect("gabarita_if:cadernos")
    else:
        context = {
            "object": caderno,
            "url_remover": "gabarita_if:remover-caderno"
        }

        return render(request, "remover.html", context)
