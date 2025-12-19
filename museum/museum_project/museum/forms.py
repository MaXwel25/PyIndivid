from django import forms
from .models import Exhibition, Session

class ExhibitionForm(forms.ModelForm):
    class Meta:
        model = Exhibition
        fields = ['title', 'description', 'date_start', 'date_end', 'price']
        widgets = {
            'date_start': forms.DateInput(attrs={'type': 'date'}),
            'date_end': forms.DateInput(attrs={'type': 'date'}),
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['exhibition', 'hall', 'datetime', 'seats_available']
        widgets = {
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }