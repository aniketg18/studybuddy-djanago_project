from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "location", "skills_known", "skills_wanted"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "class": "w-full px-3 py-2 border rounded"}),
            "location": forms.TextInput(attrs={"class": "w-full px-3 py-2 border rounded"}),
            "skills_known": forms.CheckboxSelectMultiple(),
            "skills_wanted": forms.CheckboxSelectMultiple(),
        }
