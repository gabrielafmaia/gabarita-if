from django.shortcuts import render

def index(request):
    return render(request, 'gabarita_if/index.html')