from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("question/<int:pk_question>/", views.question, name="question")
]