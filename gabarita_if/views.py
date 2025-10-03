from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from .models import *
from .forms import *

def index(request):
    return render(request, "gabarita_if/index.html")

def question(request, pk_question):
    question = get_object_or_404(Question, pk=pk_question)
    context = {"question": question}
    return render(request, "gabarita_if/question.html", context)