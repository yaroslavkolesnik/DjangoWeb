from django import forms
from .models import BotMenuElem

# Исправленный forms.py
# Наследуемся от стандартного forms.ModelForm

class BotMenuElemForm(forms.ModelForm):
    class Meta:
        model = BotMenuElem
        fields = ['command', "is_visable", "callbacks_db", "message", "buttons_db"]