from django.urls import path
from . import views

app_name = "gabarita_if"

urlpatterns = [
    path("redirecionar/", views.redirecionar, name="redirecionar"),
    path("", views.index, name="index"),
    # Questões
    path("questoes/", views.listar_questoes, name="questoes"),
    path("questao/<int:id_questao>/detalhar/", views.detalhar_questao, name="detalhar-questao"),
    # Provas
    path("provas/", views.listar_provas, name="provas"),
    path("provas/<int:id>/detalhar/", views.detalhar_prova, name="detalhar-prova"),
    # Simulados
    path("simulados/", views.listar_simulados, name="simulados"),
    path("simulados/<int:id>/detalhar/", views.detalhar_simulado, name="detalhar-simulado"),
    # Meu Desempenho
    path("meu-desempenho/", views.meu_desempenho, name="meu-desempenho"),
    # Listas Personalizadas
    path("listas-personalizadas/", views.listar_listas, name="listas"),
    path("listas-personalizadas/criar/", views.criar_lista, name="criar-lista"),
    path("listas-personalizadas/<int:id>/detalhar/", views.detalhar_lista, name="detalhar-lista"),
    path("listas-personalizadas/<int:id>/editar/", views.editar_lista, name="editar-lista"),
    path("listas-personalizadas/<int:id>/remover/", views.remover_lista, name="remover-lista"),
    # Filtros
    path("filtros/", views.listar_filtros, name="filtros"),
    path("filtros/criar/", views.criar_filtro, name="criar-filtro"),
    path("filtros/<int:id>/detalhar/", views.detalhar_filtro, name="detalhar-filtro"),
    path("filtros/<int:id>/editar/", views.editar_filtro, name="editar-filtro"),
    path("filtros/<int:id>/remover/", views.remover_filtro, name="remover-filtro"),
    # Comentários
    path("comentarios/", views.listar_comentarios, name="comentarios"),
    path("comentarios/criar/", views.criar_comentario, name="criar-comentario"),
    path("comentarios/<int:id>/detalhar/", views.detalhar_comentario, name="detalhar-comentario"),
    path("comentarios/<int:id>/editar/", views.editar_comentario, name="editar-comentario"),
    path("comentarios/<int:id>/remover/", views.remover_comentario, name="remover-comentario"),
]