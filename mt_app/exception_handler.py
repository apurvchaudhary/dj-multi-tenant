from django.shortcuts import render


def handler404(request, exception):
    return render(request, template_name="error404.html")


def handler403(request, exception):
    return render(request, template_name="error403.html")
