from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from gabarita_if.forms import ComentarioForm
from gabarita_if.models import Comentario, Questao


@login_required
@require_POST
def criar_comentario(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    form = ComentarioForm(request.POST)
    valido = form.is_valid()

    if valido:
        Comentario.objects.create(
            usuario=request.user,
            questao=questao,
            texto=form.cleaned_data["texto"],
        )
        messages.success(request, "Comentário publicado com sucesso.")
    else:
        messages.error(request, "Informe um comentário válido.")

    return render(
        request,
        "gabarita_if/partials/_comentarios_questao.html",
        {
            "questao": questao,
            "form": form if not valido else None,
            "show_messages": True,
        },
    )


@login_required
@require_GET
def exibir_comentario(request, comentario_id):
    comentario = get_object_or_404(
        Comentario.objects.select_related("usuario"), pk=comentario_id
    )
    return render(
        request,
        "gabarita_if/partials/_comentario_item.html",
        {"comentario": comentario},
    )


@login_required
@require_http_methods(["GET", "POST"])
def editar_comentario(request, comentario_id):
    comentario = get_object_or_404(
        Comentario.objects.select_related("usuario"),
        pk=comentario_id,
        usuario=request.user,
    )

    if request.method == "GET":
        form = ComentarioForm(initial={"texto": comentario.texto})
        return render(
            request,
            "gabarita_if/partials/_comentario_form.html",
            {"comentario": comentario, "form": form},
        )

    form = ComentarioForm(request.POST)
    if form.is_valid():
        comentario.texto = form.cleaned_data["texto"]
        comentario.save()
        messages.success(request, "Comentário atualizado com sucesso.")
        return render(
            request,
            "gabarita_if/partials/_comentario_item.html",
            {"comentario": comentario, "comentario_show_messages": True},
        )

    messages.error(request, "Informe um comentário válido.")
    return render(
        request,
        "gabarita_if/partials/_comentario_form.html",
        {"comentario": comentario, "form": form, "show_messages": True},
    )


@login_required
@require_POST
def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(
        Comentario, pk=comentario_id, usuario=request.user
    )
    comentario.delete()
    messages.success(request, "Comentário excluído com sucesso.")
    return render(request, "gabarita_if/partials/_comentario_messages.html")
