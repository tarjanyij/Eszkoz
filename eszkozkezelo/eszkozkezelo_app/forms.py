from django import forms
from .models import Eszkoz, Beszallito, Szemely, Tipus, Mozgas

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

class MozgasForm(forms.ModelForm):
    class Meta:
        model = Mozgas
        fields = ['eszkoz', 'honnan', 'hova', 'mozgasIdo', 'mozgastipus']

    def __init__(self, *args, **kwargs):
        eszkoz = kwargs.pop('eszkoz', None)
        honnan = kwargs.pop('honnan', None)
        super().__init__(*args, **kwargs)

        # Rejtett mezők – elküldődnek a POST-tal
        if eszkoz:
            self.fields['eszkoz'].initial = eszkoz
            self.fields['eszkoz'].widget = forms.HiddenInput()

        if honnan:
            self.fields['honnan'].initial = honnan
            self.fields['honnan'].widget = forms.HiddenInput()

        # Bootstrap osztályokat hozzáadjuk manuálisan
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.HiddenInput):
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_classes} form-control'

    def clean(self):
        cleaned_data = super().clean()
        honnan = cleaned_data.get("honnan")
        hova = cleaned_data.get("hova")
        eszkoz = cleaned_data.get("eszkoz")

        if honnan and hova and honnan == hova:
            raise forms.ValidationError("Nem lehet az eszközt ugyanattól ugyanannak mozgatni.")

        return cleaned_data