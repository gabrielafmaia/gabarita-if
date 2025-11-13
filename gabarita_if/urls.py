from django.urls import path
from .views import *

app_name = "gabarita_if"

urlpatterns = [
    path("redirecionar/", redirecionar, name="redirecionar"),
    path("", index, name="index"),
    path("meu-desempenho/", meu_desempenho, name="meu-desempenho"),

    path("questoes/", questoes, name="questoes"),
    path("responder-questao/", responder_questao, name="responder-questao"),

    path("provas/", provas, name="provas"),
    path("provas/<int:id>/detalhar/", detalhar_prova, name="detalhar-prova"),

    path("simulados/", simulados, name="simulados"),
    path("simulados/<int:id>/detalhar/", detalhar_simulado, name="detalhar-simulado"),

    path("listas-personalizadas/", listas, name="listas"),
    path("listas-personalizadas/criar/", criar_lista, name="criar-lista"),
    path("listas-personalizadas/<int:id>/detalhar/", detalhar_lista, name="detalhar-lista"),
    path("listas-personalizadas/<int:id>/editar/", editar_lista, name="editar-lista"),
    path("listas-personalizadas/<int:id>/remover/", remover_lista, name="remover-lista"),

    path("comentarios/", comentarios, name="comentarios"),
    path("comentarios/criar/", criar_comentario, name="criar-comentario"),
    path("comentarios/<int:id>/detalhar/", detalhar_comentario, name="detalhar-comentario"),
    path("comentarios/<int:id>/editar/", editar_comentario, name="editar-comentario"),
    path("comentarios/<int:id>/remover/", remover_comentario, name="remover-comentario"),
]