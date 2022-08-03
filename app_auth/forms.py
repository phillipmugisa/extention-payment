from dataclasses import field
from django.forms import ModelForm
from django.contrib.auth.models import User


class UserFormManager(ModelForm):
    class Meta:
        model = User
        fields = "__all__"
