from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from dashboard.tables import QuestaoTabela
from django_tables2 import RequestConfig
from gabarita_if.models import Questao
from dashboard.forms import QuestaoForm
from django.http import JsonResponse

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def questoes(request):
    questoes = Questao.objects.all()
    tabela = QuestaoTabela(questoes)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode cadastrar as questões das provas e simulados.",
        "nome": "questão",
        "url_criar": "dashboard:ajax-criar-questao",
        "url_detalhar": "dashboard:ajax-detalhar-questao",
        "url_editar": "dashboard:ajax-editar-questao",
        "url_remover": "dashboard:ajax-remover-questao",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": questoes
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def ajax_questoes(request):
    questoes = Questao.objects.all()
    tabela = QuestaoTabela(questoes)
    RequestConfig(request, paginate={"per_page": 10}).configure(tabela)

    context = {
        "titulo_pagina": "Questões",
        "subtitulo_pagina": "Aqui você pode cadastrar as questões das provas e simulados.",
        "nome": "questão",
        "url_criar": "dashboard:ajax-criar-questao",
        "url_detalhar": "dashboard:ajax-detalhar-questao",
        "url_editar": "dashboard:ajax-editar-questao",
        "url_remover": "dashboard:ajax-remover-questao",
        "tabela": tabela,
        "partial": "dashboard/partials/_tabela.html",
        "objects": questoes
    }
    
    return render(request, "listar.html", context)

@login_required
@permission_required("gabarita_if.add_questao", raise_exception=True)
def ajax_criar_questao(request):
    if request.method == "POST":
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão criada com sucesso!")
            return JsonResponse({"mensagem": "Questão criada com sucesso!"}, status=201)
        else:
            messages.error(request, "Falha ao criar questão!")
    else:
        form = QuestaoForm()
    
    context = {
        "partial_form": "dashboard/partials/_form_questao.html",
        "form": form
    }

    return render(request, "criar.html", context)

@login_required
@permission_required("gabarita_if.view_questao", raise_exception=True)
def ajax_detalhar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    fields = "__all__"
    safe_fields = ["enunciado", "alternativa_a", "alternativa_b", "alternativa_c", "alternativa_d", "gabarito_comentado"]

    def get_fields():
        selected_fields = []
        no_check = not isinstance(fields, (list, tuple))
        for field in questao._meta.fields:
            if no_check or field.name in fields:
                selected_fields.append(
                    {
                        "label": field.verbose_name,
                        "value": getattr(questao, field.name),
                        "safe": True if field.name in safe_fields else False,
                        "many": False,
                    }
                )

        return selected_fields

    context = {
        "nome": "questão",
        "object": questao,
        "fields": get_fields()
    }

    return render(request, "detalhar.html", context)

@login_required
@permission_required("gabarita_if.change_questao", raise_exception=True)
def ajax_editar_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        form = QuestaoForm(request.POST, request.FILES, instance=questao)
        if form.is_valid():
            form.save()
            messages.success(request, "Questão atualizada com sucesso!")
            return JsonResponse({"mensagem": "Questão atualizada com sucesso!"}, status=200)
        else:
            messages.error(request, "Falha ao atualizar questão!")
    else:
        form = QuestaoForm(instance=questao)
        
    context = {
        "partial_form": "dashboard/partials/_form_questao.html",
        "form": form
    }

    return render(request, "editar.html", context)

@login_required
@permission_required("gabarita_if.delete_questao", raise_exception=True)
def ajax_remover_questao(request, id):
    questao = get_object_or_404(Questao, id=id)
    if request.method == "POST":
        questao.delete()
        messages.success(request, "Questão removida com sucesso!")
        return redirect("dashboard:questoes")
    else:
        context = {
            "object": questao,
            "url_remover": "dashboard:remover-questao"
        }

        return render(request, "remover.html", context)
    
@login_required
@permission_required("gabarita_if.view_questao", raise_exception=True)
def baixar_pdf_questoes(request):

    assunto = request.GET.get("assunto", "").strip()

    if assunto:
        questoes = Questao.objects.filter(assunto_id=assunto)
    else:
        questoes = Questao.objects.all()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="questoes.pdf"'

    p = canvas.Canvas(response)

    y = 800

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "Lista de Questões")

    y -= 40

    p.setFont("Helvetica", 12)

    for questao in questoes:

        texto = f"{questao.enunciado}"

        p.drawString(50, y, texto[:100])

        y -= 30

        if y < 50:
            p.showPage()
            y = 800

    p.save()

    return response
@login_required
def baixar_pdf_avaliacao(request, avaliacao_id):
    avaliacao = get_object_or_404(Avaliacao, id=avaliacao_id)
    questoes = avaliacao.questoes.all() 
    
    context = {
        'avaliacao': avaliacao,
        'questoes': questoes,
    }
    

    html_string = render_to_string('pdf/avaliacao_pdf.html', context)
    
    response = HttpResponse(content_type='application/pdf')'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Erro ao gerar o PDF', status=500)
        
    return response