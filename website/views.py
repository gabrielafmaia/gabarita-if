from django.shortcuts import render
from .models import *

def index(request):
    context = {
        "sobre": Sobre.objects.first(),
        "membros": Membro.objects.all(),
        "cards": Card.objects.all()
    }
    return render(request, 'website/index.html', context)