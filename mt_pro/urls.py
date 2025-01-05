from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("mt_app.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.png")),
]
handler403 = "mt_app.exception_handler.handler403"
handler404 = "mt_app.exception_handler.handler404"
