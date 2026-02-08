from django.urls import path
from .views import *

app_name = "gabarita_if"

urlpatterns = [
    path("redirecionar/", redirecionar, name="redirecionar"),
    path("", index, name="index"),
    path("questoes/", questoes, name="questoes"),
    path("avaliacoes/", avaliacoes, name="avaliacoes"),
    path("avaliacoes/<int:id>/responder/", responder_avaliacao, name="responder-avaliacao"),
    path("avaliacoes/<int:id>/feedback/", ver_feedback_avaliacao, name="ver-feedback-avaliacao"),
    path("cadernos/", cadernos, name="cadernos"),
    path("ajax/cadernos/criar/", ajax_criar_caderno, name="ajax-criar-caderno"),
    path("cadernos/<int:id>/detalhar/", detalhar_caderno, name="detalhar-caderno"),
    path("ajax/cadernos/<int:id>/editar/", ajax_editar_caderno, name="ajax-editar-caderno"),
    path("ajax/cadernos/<int:id>/remover/", ajax_remover_caderno, name="ajax-remover-caderno"),
    path("meu-desempenho/", meu_desempenho, name="meu-desempenho")
]