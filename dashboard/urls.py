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
    # Avaliações
    path("avaliacoes/", avaliacoes, name="avaliacoes"),
    path("avaliacoes/criar/", criar_avaliacao, name="criar-avaliacao"),
    path("avaliacoes/<int:id>/detalhar/", detalhar_avaliacao, name="detalhar-avaliacao"),
    path("avaliacoes/<int:id>/editar/", editar_avaliacao, name="editar-avaliacao"),
    path("avaliacoes/<int:id>/remover/", remover_avaliacao, name="remover-avaliacao"),
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