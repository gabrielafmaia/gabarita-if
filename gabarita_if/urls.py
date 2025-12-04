from django.urls import path
from .views import *

app_name = "gabarita_if"

urlpatterns = [
    path("redirecionar/", redirecionar, name="redirecionar"),
    path("", index, name="index"),
    path("questoes/", questoes, name="questoes"),

    path("provas/", provas, name="provas"),
    path("provas/<int:id>/responder/", responder_prova, name="responder-prova"),
    path("provas/<int:tentativa_id>/detalhar", detalhar_prova, name="detalhar-prova"),

    path("simulados/", simulados, name="simulados"),
    path("simulados/<int:id>/responder/", responder_simulado, name="responder-simulado"),
    path("simulados/<int:tentativa_id>/detalhar", detalhar_simulado, name="detalhar-simulado"),

    path("cadernos/", cadernos, name="cadernos"),
    path("cadernos/criar/", criar_caderno, name="criar-caderno"),
    path("cadernos/<int:id>/detalhar/", detalhar_caderno, name="detalhar-caderno"),
    path("cadernos/<int:id>/editar/", editar_caderno, name="editar-caderno"),
    path("cadernos/<int:id>/remover/", remover_caderno, name="remover-caderno"),

    path("meu-desempenho/", meu_desempenho, name="meu-desempenho")
]