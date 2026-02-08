from django.urls import path
from .views import *

app_name = "dashboard"

urlpatterns = [
    path("", index, name="index"),
    path("ajax-messages/", ajax_mensagens, name="ajax-mensagens"),
    path("questoes/", questoes, name="questoes"),
    path("ajax/questoes/", ajax_questoes, name="ajax-questoes"),
    path("avaliacoes/", avaliacoes, name="avaliacoes"),
    path("textos-de-apoio/", textos, name="textos"),
    path("usuarios/", usuarios, name="usuarios"),

    path("ajax/questao/remover/<int:id>/", ajax_remover_questao, name="ajax-remover-questao"),
    path("ajax/avaliacoes/<int:id>/remover/", ajax_remover_avaliacao, name="ajax-remover-avaliacao"),
    path("ajax/textos-de-apoio/<int:id>/remover/", ajax_remover_texto, name="ajax-remover-texto"),
    path("ajax/usuarios/<int:id>/remover/", ajax_remover_usuario, name="ajax-remover-usuario"),

    path("ajax/questoes/<int:id>/detalhar/", ajax_detalhar_questao, name="ajax-detalhar-questao"),
    path("ajax/avaliacoes/<int:id>/detalhar/", ajax_detalhar_avaliacao, name="ajax-detalhar-avaliacao"),
    path("ajax/textos/<int:id>/detalhar/", ajax_detalhar_texto, name="ajax-detalhar-texto"),
    path("ajax/usuarios/<int:id>/detalhar/", ajax_detalhar_usuario, name="ajax-detalhar-usuario"),
    
    path("ajax/questoes/<int:id>/editar/", ajax_editar_questao, name="ajax-editar-questao"),
    path("ajax/avaliacoes/<int:id>/editar/", ajax_editar_avaliacao, name="ajax-editar-avaliacao"),
    path("ajax/textos-de-apoio/<int:id>/editar/", ajax_editar_texto, name="ajax-editar-texto"),
    path("ajax/usuarios/<int:id>/editar/", ajax_editar_usuario, name="ajax-editar-usuario"),

    path("ajax/questoes/criar/", ajax_criar_questao, name="ajax-criar-questao"),
    path("ajax/avaliacoes/criar/", ajax_criar_avaliacao, name="ajax-criar-avaliacao"),
    path("ajax/textos-de-apoio/criar/", ajax_criar_texto, name="ajax-criar-texto"),
    path("ajax/usuarios/criar/", ajax_criar_usuario, name="ajax-criar-usuario"),
]