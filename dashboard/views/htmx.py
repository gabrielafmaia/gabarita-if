from django.shortcuts import render


def render_crud_response(request, context):
    response = render(request, "dashboard/partials/_crud_response.html", context)
    response["HX-Trigger"] = "crudSaved"
    return response


def render_form_response(request, context):
    return render(request, "dashboard/partials/_form_response.html", context)