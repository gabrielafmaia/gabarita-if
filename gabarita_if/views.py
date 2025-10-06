from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from .models import *
from .forms import *

def index(request):
    return render(request, "gabarita_if/index.html")

# direciona pra página de filtrar questoes
def questions(request):
    questions = Question.objects.all().order_by()
    return render(request, "gabarita_if/questions/", {"questions": questions})

def question_detail(request, pk_question):
    question = get_object_or_404(Question, pk=pk_question)
    return render(request, "gabarita_if/question_detail.html", {"question": question})