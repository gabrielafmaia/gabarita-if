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
    path("cadernos/criar/", criar_caderno, name="criar-caderno"),
    path("cadernos/<int:id>/detalhar/", detalhar_caderno, name="detalhar-caderno"),
    path("cadernos/<int:id>/editar/", editar_caderno, name="editar-caderno"),
    path("cadernos/<int:id>/remover/", remover_caderno, name="remover-caderno"),
    path("meu-desempenho/", meu_desempenho, name="meu-desempenho")
]