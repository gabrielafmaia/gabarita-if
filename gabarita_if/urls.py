from django.urls import path
from . import views

app_name = "gabarita_if"

urlpatterns = [
    path("", views.index, name="index"),
    path("questoes/", views.questoes, name="questoes"),
    path("questao/<int:id_questao>/", views.questao_detalhar, name="questao-detalhar"),
    path("provas/", views.provas, name="provas"),
    path("simulados/", views.simulados, name="simulados"),
    path("listas-personalizadas/", views.listas_personalizadas, name="listas-personalizadas"),
    path("meu-desempenho/", views.meu_desempenho, name="meu-desempenho"),
]