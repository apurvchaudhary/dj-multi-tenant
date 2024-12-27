from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from mt_app.forms import AdminSignupForm
from mt_app.models import Organization


def admin_signup(request):
    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Account created successfully!, Kindly ask admin to give you login access"
            )
            return redirect("/admin/")
    else:
        form = AdminSignupForm()
    return render(request, "signup.html", {"form": form})


def org_list(request):
    return render(request, "org_list.html", {"organizations": Organization.objects.all()})


def org_detail(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    return render(
        request,
        "org_detail.html",
        {
            "organization": org,
        },
    )
