from django.shortcuts import render
from .models import *

def index(request):
    context = {
        "about": About.objects.first(),
        "members": Member.objects.all(),
        "cards": Card.objects.all()
    }
    return render(request, 'website/index.html', context)