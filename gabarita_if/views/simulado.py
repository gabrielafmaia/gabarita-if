


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Simulado, RespostaUsuario, TentativaAvaliacao
from django.utils import timezone

@login_required
def simulados(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        simulados = Simulado.objects.all().order_by(ordenar)
    else:
        simulados = Simulado.objects.all().order_by("-ano")
    
    for simulado in simulados:
        simulado.finalizada = TentativaAvaliacao.objects.filter(usuario=request.user, simulado=simulado, finalizada=True).exists()
        tentativas = TentativaAvaliacao.objects.filter(usuario=request.user, simulado=simulado).order_by('-finalizada_em', '-iniciada_em')[:3]
        
        # Calcula acertos para cada tentativa
        for tentativa in tentativas:
            respostas = RespostaUsuario.objects.filter(usuario=request.user,tentativa=tentativa)
            tentativa.acertos = respostas.filter(acertou=True).count()
            tentativa.total_questoes = simulado.questoes.count()
        simulado.tentativas = tentativas

    paginator = Paginator(simulados, 9)
    numero_da_pagina = request.GET.get("p")
    simulados_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "simulados",
        "subtitulo_pagina": "Aqui você pode responder todos os Exames de Seleção do IFRN.",
        "nome": "simulado",
        "url_responder": "gabarita_if:responder-simulado",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": simulados_paginadas,
        "tipo_avaliacao": "simulado",
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_simulado(request, id, tentativa_id=None):
    simulado = get_object_or_404(Simulado, id=id)
    questoes = simulado.questoes.all().order_by("id")
    
    if tentativa_id:
        tentativa = get_object_or_404(TentativaAvaliacao, id=tentativa_id, usuario=request.user, simulado=simulado)
    else:
        tentativa_em_andamento = TentativaAvaliacao.objects.filter(usuario=request.user, simulado=simulado, finalizada=False).first()
        
        if tentativa_em_andamento:
            tentativa = tentativa_em_andamento
        else:
            tentativa = TentativaAvaliacao.objects.create(usuario=request.user, simulado=simulado, finalizada=False)

    if request.method == "POST":
        if request.POST.get("refazer"):
            tentativa.finalizada = True
            tentativa.finalizada_em = timezone.now()
            tentativa.save()
            nova_tentativa = TentativaAvaliacao.objects.create(usuario=request.user, simulado=simulado, finalizada=False)
            
            return redirect("gabarita_if:responder-simulado", id=simulado.id, tentativa_id=nova_tentativa.id)
        
        else:
            for questao in questoes:
                alternativa_escolhida = request.POST.get(f"questao_{questao.id}")

                if alternativa_escolhida:
                    RespostaUsuario.objects.update_or_create(
                        usuario=request.user,
                        questao=questao,
                        tentativa=tentativa,
                        defaults={
                            "alternativa_escolhida": alternativa_escolhida,
                            "acertou": alternativa_escolhida == questao.alternativa_correta,
                        }
                    )
            
            tentativa.finalizada = True
            tentativa.finalizada_em = timezone.now()
            tentativa.save()
            
            return redirect("gabarita_if:detalhar-simulado", tentativa_id=tentativa.id)

    respostas = RespostaUsuario.objects.filter(usuario=request.user, tentativa=tentativa, questao__in=questoes)

    respostas_por_questao = {
        resposta.questao_id: resposta for resposta in respostas
    }

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    context = {
        "object": simulado,
        "logo": "assets/img/ifrn-branco.png",
        "objects": questoes,
        "tentativa": tentativa,
        "url_voltar": "gabarita_if:simulados",
        "mostrar_feedback": tentativa.finalizada,
        "tipo_avaliacao": "simulado",
    }

    return render(request, "gabarita_if/responder.html", context)

@login_required
def detalhar_simulado(request, tentativa_id):
    tentativa = get_object_or_404(TentativaAvaliacao, id=tentativa_id, usuario=request.user)
    
    # Verifique se é uma prova ou simulado
    if tentativa.simulado:
        avaliacao = tentativa.simulado
        tipo_avaliacao = "simulado"
        url_voltar = "gabarita_if:simulados"
    else:
        avaliacao = tentativa.prova
        tipo_avaliacao = "prova"
        url_voltar = "gabarita_if:provas"
    
    questoes = avaliacao.questoes.all().order_by("id")
    respostas = RespostaUsuario.objects.filter(usuario=request.user, tentativa=tentativa)

    respostas_por_questao = {
        resposta.questao_id: resposta for resposta in respostas
    }

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    context = {
        "object": avaliacao,
        "objects": questoes,
        "tentativa": tentativa,
        "url_voltar": url_voltar,
        "mostrar_feedback": True,
        "tipo_avaliacao": tipo_avaliacao,  # Adicione isso
    }

    return render(request, "gabarita_if/responder.html", context)