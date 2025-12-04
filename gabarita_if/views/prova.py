from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from gabarita_if.models import Prova, RespostaUsuario, TentativaAvaliacao
from django.utils import timezone

@login_required
def provas(request):
    ordenar = request.GET.get("ordenar")
    if ordenar:
        provas = Prova.objects.all().order_by(ordenar)
    else:
        provas = Prova.objects.all().order_by("-ano")
    
    for prova in provas:
        prova.finalizada = TentativaAvaliacao.objects.filter(usuario=request.user, prova=prova, finalizada=True).exists()
        tentativas = TentativaAvaliacao.objects.filter(usuario=request.user, prova=prova).order_by('-finalizada_em', '-iniciada_em')[:3]
        
        # Calcula acertos para cada tentativa
        for tentativa in tentativas:
            respostas = RespostaUsuario.objects.filter(usuario=request.user,tentativa=tentativa)
            tentativa.acertos = respostas.filter(acertou=True).count()
            tentativa.total_questoes = prova.questoes.count()
        prova.tentativas = tentativas

    paginator = Paginator(provas, 9)
    numero_da_pagina = request.GET.get("p")
    provas_paginadas = paginator.get_page(numero_da_pagina)

    context = {
        "titulo_pagina": "Provas",
        "subtitulo_pagina": "Aqui você pode responder todos os Exames de Seleção do IFRN.",
        "nome": "prova",
        "url_responder": "gabarita_if:responder-prova",
        "partial": "gabarita_if/partials/_card_avaliacao.html",
        "objects": provas_paginadas,
        "tipo_avaliacao": "prova",
    }
    
    return render(request, "listar.html", context)

@login_required
def responder_prova(request, id, tentativa_id=None):
    prova = get_object_or_404(Prova, id=id)
    questoes = prova.questoes.all().order_by("id")
    
    if tentativa_id:
        tentativa = get_object_or_404(TentativaAvaliacao, id=tentativa_id, usuario=request.user, prova=prova)
    else:
        tentativa_em_andamento = TentativaAvaliacao.objects.filter(usuario=request.user, prova=prova, finalizada=False).first()
        
        if tentativa_em_andamento:
            tentativa = tentativa_em_andamento
        else:
            tentativa = TentativaAvaliacao.objects.create(usuario=request.user, prova=prova, finalizada=False)

    if request.method == "POST":
        if request.POST.get("refazer"):
            tentativa.finalizada = True
            tentativa.finalizada_em = timezone.now()
            tentativa.save()
            nova_tentativa = TentativaAvaliacao.objects.create(usuario=request.user, prova=prova, finalizada=False)
            
            return redirect("gabarita_if:responder-prova", id=prova.id, tentativa_id=nova_tentativa.id)
        
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
            
            return redirect("gabarita_if:detalhar-prova", tentativa_id=tentativa.id)

    respostas = RespostaUsuario.objects.filter(usuario=request.user, tentativa=tentativa, questao__in=questoes)

    respostas_por_questao = {
        resposta.questao_id: resposta for resposta in respostas
    }

    for questao in questoes:
        questao.resposta = respostas_por_questao.get(questao.id)

    context = {
        "object": prova,
        "logo": "assets/img/ifrn-branco.png",
        "objects": questoes,
        "tentativa": tentativa,
        "url_voltar": "gabarita_if:provas",
        "mostrar_feedback": tentativa.finalizada,
        "tipo_avaliacao": "prova",
    }

    return render(request, "gabarita_if/responder.html", context)

@login_required
def detalhar_prova(request, tentativa_id):
    tentativa = get_object_or_404(TentativaAvaliacao, id=tentativa_id, usuario=request.user)
    
    # Verifique se é uma prova ou simulado
    if tentativa.prova:
        avaliacao = tentativa.prova
        tipo_avaliacao = "prova"
        url_voltar = "gabarita_if:provas"
    else:
        avaliacao = tentativa.simulado
        tipo_avaliacao = "simulado"
        url_voltar = "gabarita_if:simulados"
    
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