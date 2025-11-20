from django.urls import path
from .views import *

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    # Questões
    path("questoes/", questoes, name="questoes"),
    path("questoes/criar/", criar_questao, name="criar-questao"),
    path("questoes/<int:id>/detalhar/", detalhar_questao, name="detalhar-questao"),
    path("questoes/<int:id>/editar/", editar_questao, name="editar-questao"),
    path("questoes/<int:id>/remover/", remover_questao, name="remover-questao"),
    # Provas
    path("provas/", provas, name="provas"),
    path("provas/criar/", criar_prova, name="criar-prova"),
    path("provas/<int:id>/detalhar/", detalhar_prova, name="detalhar-prova"),
    path("provas/<int:id>/editar/", editar_prova, name="editar-prova"),
    path("provas/<int:id>/remover/", remover_prova, name="remover-prova"),
    # Simulados
    path("simulados/", simulados, name="simulados"),
    path("simulados/criar/", criar_simulado, name="criar-simulado"),
    path("simulados/<int:id>/detalhar/", detalhar_simulado, name="detalhar-simulado"),
    path("simulados/<int:id>/editar/", editar_simulado, name="editar-simulado"),
    path("simulados/<int:id>/remover/", remover_simulado, name="remover-simulado"),
    # Textos de Apoio
    path("textos-de-apoio/", textos, name="textos"),
    path("textos-de-apoio/criar/", criar_texto, name="criar-texto"),
    path("textos-de-apoio/<int:id>/detalhar/", detalhar_texto, name="detalhar-texto"),
    path("textos-de-apoio/<int:id>/editar/", editar_texto, name="editar-texto"),
    path("textos-de-apoio/<int:id>/remover/", remover_texto, name="remover-texto"),
    # Usuários
    path("usuarios/", usuarios, name="usuarios"),
    path("usuarios/criar/", criar_usuario, name="criar-usuario"),
    path("usuarios/<int:id>/detalhar/", detalhar_usuario, name="detalhar-usuario"),
    path("usuarios/<int:id>/editar/", editar_usuario, name="editar-usuario"),
    path("usuarios/<int:id>/remover/", remover_usuario, name="remover-usuario"),
]