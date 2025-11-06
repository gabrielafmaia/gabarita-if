from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

@login_required
def meu_desempenho(request):
    return render(request, "gabarita_if/meu_desempenho.html")