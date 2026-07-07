from django.urls import path
from gabarita_if.views.questao import questoes, gerar_pdf_questoes
from .views import *
from gabarita_if.models import Questao, Avaliacao

app_name = "gabarita_if"

urlpatterns = [
    path("redirecionar/", redirecionar, name="redirecionar"),
    path("", index, name="index"),
    path("questoes/", questoes, name="questoes"),
    path("baixar-pdf/", gerar_pdf_questoes, name="gerar_pdf_questoes"),
    path("avaliacoes/", avaliacoes, name="avaliacoes"),
    path("avaliacoes/<int:id>/responder/", responder_avaliacao, name="responder-avaliacao"),
    path("avaliacoes/<int:id>/feedback/", ver_feedback_avaliacao, name="ver-feedback-avaliacao"),
    path("cadernos/", cadernos, name="cadernos"),
    path("ajax/cadernos/criar/", ajax_criar_caderno, name="ajax-criar-caderno"),
    path("cadernos/<int:id>/detalhar/", detalhar_caderno, name="detalhar-caderno"),
    path("ajax/cadernos/<int:id>/editar/", ajax_editar_caderno, name="ajax-editar-caderno"),
    path("ajax/cadernos/<int:id>/remover/", ajax_remover_caderno, name="ajax-remover-caderno"),
    path("meu-desempenho/", meu_desempenho, name="meu-desempenho"),
    path("avaliacao/<int:pk>/pdf/", gerar_pdf_avaliacao, name="avaliacao_pdf"),
    path('questao/<str:questao_codigo>/pdf/', questao.baixar_pdf_questao, name='baixar_pdf_questao'),
]