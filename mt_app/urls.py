from django.urls import path

from mt_app import views

urlpatterns = [
    path("", views.org_list, name="org_list"),
    path("signup/", views.admin_signup, name="signup"),
    path("organization/<int:pk>/", views.org_detail, name="org_detail"),
]
