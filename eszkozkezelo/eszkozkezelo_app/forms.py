from django import forms
from .models import Eszkoz,  Beszallito, Szemely, Tipus

class EszkozForm(forms.ModelForm):
    class Meta:
        model = Eszkoz
        fields = '__all__'

class BeszallitoForm(forms.ModelForm):
    class Meta:
        model = Beszallito
        fields = '__all__'

class SzemelyForm(forms.ModelForm):
    class Meta:
        model = Szemely
        fields = '__all__'

class TipusForm(forms.ModelForm):
    class Meta:
        model = Tipus
        fields = '__all__'