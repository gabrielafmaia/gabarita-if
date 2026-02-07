from django.urls import path
from .views import *

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    # Questões
    path("questoes/", questoes, name="questoes"),
    path("questoes/criar/", criar_questao, name="criar-questao"),
    path("ajax/questoes/<int:id>/editar/", ajax_editar_questao, name="ajax-editar-questao"),
    path("questoes/<int:id>/remover/", remover_questao, name="remover-questao"),
    # Avaliações
    path("avaliacoes/", avaliacoes, name="avaliacoes"),
    path("avaliacoes/criar/", criar_avaliacao, name="criar-avaliacao"),
    path("ajax/avaliacoes/<int:id>/editar/", ajax_editar_avaliacao, name="ajax-editar-avaliacao"),
    path("avaliacoes/<int:id>/remover/", remover_avaliacao, name="remover-avaliacao"),
    # Textos de Apoio
    path("textos-de-apoio/", textos, name="textos"),
    path("textos-de-apoio/criar/", criar_texto, name="criar-texto"),
    path("ajax/textos-de-apoio/<int:id>/editar/", ajax_editar_texto, name="ajax-editar-texto"),
    path("textos-de-apoio/<int:id>/remover/", remover_texto, name="remover-texto"),
    # Usuários
    path("usuarios/", usuarios, name="usuarios"),
    path("usuarios/criar/", criar_usuario, name="criar-usuario"),
    path("ajax/usuarios/<int:id>/editar/", ajax_editar_usuario, name="ajax-editar-usuario"),
    path("usuarios/<int:id>/remover/", remover_usuario, name="remover-usuario"),
    # AJAX
    path("ajax/questoes/<int:id>/detalhar/", ajax_detalhar_questao, name="ajax-detalhar-questao"),
    path("ajax/avaliacoes/<int:id>/detalhar/", ajax_detalhar_avaliacao, name="ajax-detalhar-avaliacao"),
    path("ajax/textos/<int:id>/detalhar/", ajax_detalhar_texto, name="ajax-detalhar-texto"),
    path("ajax/usuarios/<int:id>/detalhar/", ajax_detalhar_usuario, name="ajax-detalhar-usuario"),
    # path("questao/criar/", ajax_criar_questao, name="ajax-criar-questao"),
    path("questao/<int:id>/editar/", ajax_editar_questao, name="ajax-editar-questao"),
    # path("questao/<int:id>/remover/", ajax_remover_questao, name="ajax-remover-questao"),
]