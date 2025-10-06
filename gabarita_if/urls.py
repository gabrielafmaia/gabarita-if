from django.urls import path
from . import views

app_name = "gabarita_if"

urlpatterns = [
    path("", views.index, name="index"),
    path("questoes/", views.questions, name="questions"),
    path("questao/<int:pk_question>/", views.question_detail, name="question_detail"),
]