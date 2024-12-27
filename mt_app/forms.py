from django.contrib.auth.forms import UserCreationForm

from mt_app.models import CustomUser


class AdminSignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_active = False
        if commit:
            user.save()
        return user
