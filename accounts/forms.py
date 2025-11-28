from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=['profile_picture','dob','bio']

        widgets={
            'dob':forms.DateInput(attrs={'type':'date'})
        }
