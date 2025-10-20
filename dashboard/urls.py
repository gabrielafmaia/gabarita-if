from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Usuários
    path("", views.index, name="index"),
    path("usuarios/", views.listar_usuarios, name="usuarios"),
    path("usuarios/criar/", views.criar_usuario, name="criar-usuario"),
    path("usuarios/<int:id>/detalhar", views.detalhar_usuario, name="detalhar-usuario"),
    path("usuarios/<int:id>/editar/", views.editar_usuario, name="editar-usuario"),
    path("usuarios/<int:id>/remover/", views.remover_usuario, name="remover-usuario"),
    # Questões
    path("questoes/", views.listar_questoes, name="questoes"),
    path("questoes/criar/", views.criar_questao, name="criar-questao"),
    path("questoes/<int:id>/detalhar", views.detalhar_questao, name="detalhar-questao"),
    path("questoes/<int:id>/editar/", views.editar_questao, name="editar-questao"),
    path("questoes/<int:id>/remover/", views.remover_questao, name="remover-questao"),
    # Provas
    path("provas/", views.listar_provas, name="provas"),
    path("provas/criar/", views.criar_prova, name="criar-prova"),
    path("provas/<int:id>/detalhar/", views.detalhar_prova, name="detalhar-prova"),
    path("provas/<int:id>/editar/", views.editar_prova, name="editar-prova"),
    path("provas/<int:id>/remover/", views.remover_prova, name="remover-prova"),
    # Simulados
    path("simulados/", views.listar_simulados, name="simulados"),
    path("simulados/criar/", views.criar_simulado, name="criar-simulado"),
    path("simulados/<int:id>/detalhar/", views.detalhar_simulado, name="detalhar-simulado"),
    path("simulados/<int:id>/editar/", views.editar_simulado, name="editar-simulado"),
    path("simulados/<int:id>/remover/", views.remover_simulado, name="remover-simulado"),
    # Textos de Apoio
    path("textos-de-apoio/", views.listar_textos, name="textos"),
    path("textos-de-apoio/criar/", views.criar_texto, name="criar-texto"),
    path("textos-de-apoio/<int:id>/detalhar", views.detalhar_texto, name="detalhar-texto"),
    path("textos-de-apoio/<int:id>/editar/", views.editar_texto, name="editar-texto"),
    path("textos-de-apoio/<int:id>/remover/", views.remover_texto, name="remover-texto"),
    # Alternativas
    path("alternativas/", views.listar_alternativas, name="alternativas"),
    path("alternativas/criar/", views.criar_alternativa, name="criar-alternativa"),
    path("alternativas/<int:id>/detalhar", views.detalhar_alternativa, name="detalhar-alternativa"),
    path("alternativas/<int:id>/editar/", views.editar_alternativa, name="editar-alternativa"),
    path("alternativas/<int:id>/remover/", views.remover_alternativa, name="remover-alternativa"),
]