from django.urls import path
from .views import *

app_name = "gabarita_if"

urlpatterns = [
    path("", index, name="index"),
    # Questões
    path("questoes/", questoes, name="questoes"),
    # path("questao/<int:id_questao>/detalhar/", detalhar_questao, name="detalhar-questao"),
    # Provas
    path("provas/", provas, name="provas"),
    path("provas/<int:id>/detalhar/", detalhar_prova, name="detalhar-prova"),
    # Simulados
    path("simulados/", simulados, name="simulados"),
    path("simulados/<int:id>/detalhar/", detalhar_simulado, name="detalhar-simulado"),
    # Meu Desempenho
    path("meu-desempenho/", meu_desempenho, name="meu-desempenho"),
    # Listas Personalizadas
    path("listas-personalizadas/", listas, name="listas"),
    path("listas-personalizadas/criar/", criar_lista, name="criar-lista"),
    path("listas-personalizadas/<int:id>/detalhar/", detalhar_lista, name="detalhar-lista"),
    path("listas-personalizadas/<int:id>/editar/", editar_lista, name="editar-lista"),
    path("listas-personalizadas/<int:id>/remover/", remover_lista, name="remover-lista"),
    # Filtros
    path("filtros/", filtros, name="filtros"),
    path("filtros/criar/", criar_filtro, name="criar-filtro"),
    path("filtros/<int:id>/detalhar/", detalhar_filtro, name="detalhar-filtro"),
    path("filtros/<int:id>/editar/", editar_filtro, name="editar-filtro"),
    path("filtros/<int:id>/remover/", remover_filtro, name="remover-filtro"),
    # Comentários
    path("comentarios/", comentarios, name="comentarios"),
    path("comentarios/criar/", criar_comentario, name="criar-comentario"),
    path("comentarios/<int:id>/detalhar/", detalhar_comentario, name="detalhar-comentario"),
    path("comentarios/<int:id>/editar/", editar_comentario, name="editar-comentario"),
    path("comentarios/<int:id>/remover/", remover_comentario, name="remover-comentario"),
    # Listas PDF
    path("baixar-pdf/", baixar_pdf, name="baixar_pdf"),
]