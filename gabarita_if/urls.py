from django.urls import path
from . import views

app_name = "gabarita_if"

urlpatterns = [
    path("", views.index, name="index"),
    # Questões
    path("questoes/", views.questoes, name="questoes"),
    path("questao/<int:id_questao>/detalhar", views.detalhar_questao, name="detalhar-questao"),
    # Provas
    path("provas/", views.provas, name="provas"),
    path("provas/<int:id>/detalhar", views.detalhar_avaliacao, name="detalhar-prova"),
    # Simulados
    path("simulados/", views.simulados, name="simulados"),
    path("simulados/<int:id>/detalhar", views.detalhar_avaliacao, name="detalhar-simulado"),
    # Meu Desempenho
    path("meu-desempenho/", views.meu_desempenho, name="meu-desempenho"),
    # Listas Personalizadas
    path("listas-personalizadas/", views.listar_listas, name="listas"),
    path("listas-personalizadas/criar/", views.criar_lista, name="criar-lista"),
    path("listas-personalizadas/<int:id>/detalhar", views.detalhar_lista, name="detalhar-lista"),
    path("listas-personalizadas/<int:id>/editar/", views.editar_lista, name="editar-lista"),
    path("listas-personalizadas/<int:id>/remover/", views.remover_lista, name="remover-lista"),
    # Filtros
    path("filtros/", views.listar_filtros, name="filtros"),
    path("filtros/criar/", views.criar_filtro, name="criar-filtro"),
    path("filtros/<int:id>/detalhar", views.detalhar_filtro, name="detalhar-filtro"),
    path("filtros/<int:id>/editar/", views.editar_filtro, name="editar-filtro"),
    path("filtros/<int:id>/remover/", views.remover_filtro, name="remover-filtro"),
]