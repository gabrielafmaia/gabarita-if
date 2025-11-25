from django.urls import path
from .views import *

app_name = "gabarita_if"

urlpatterns = [
    path("redirecionar/", redirecionar, name="redirecionar"),
    path("", index, name="index"),
    path("meu-desempenho/", meu_desempenho, name="meu-desempenho"),

    path("questoes/", questoes, name="questoes"),
    path("provas/", provas, name="provas"),
    path("simulados/", simulados, name="simulados"),
    path('simulado/<int:id>/responder/', responder_simulado, name='responder-simulado'),

    path("listas-personalizadas/", listas, name="listas"),
    path("listas-personalizadas/criar/", criar_lista, name="criar-lista"),
    path("listas-personalizadas/<int:id>/detalhar/", detalhar_lista, name="detalhar-lista"),
    path("listas-personalizadas/<int:id>/editar/", editar_lista, name="editar-lista"),
    path("listas-personalizadas/<int:id>/remover/", remover_lista, name="remover-lista"),
]