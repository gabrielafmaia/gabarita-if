from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    # path("questoes/", views.listar_questoes, name="questoes"),
    path("questoes/criar/", views.criar_questao, name="criar-questao"),
    path("questoes/<int:id_questao>/", views.ler_questao, name="ler-questao"),
    path("questoes/<int:id_questao>/editar/", views.editar_questao, name="editar-questao"),
    path("questoes/<int:id_questao>/remover/", views.remover_questao, name="remover-questao"),
    # path("usuarios/", views.listar_usuarios, name="usuarios"),
    # path("usuarios/criar/", views.criar_usuario, name="criar-usuario"),
    # path("usuarios/<int:id>/", views.ler_usuario, name="ler-usuario"),
    # path("usuarios/<int:id>/editar/", views.editar_usuario, name="editar-usuario"),
    # path("usuarios/<int:id>/remover/", views.remover_usuario, name="remover-usuario"),
]