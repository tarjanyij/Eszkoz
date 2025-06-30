from django import forms
from .models import Eszkoz, Beszallito, Szemely, Tipus, Mozgas, EszkozParameter, EszkozParameterErtek, TipusParameter, Parametertipus, Kepek

#class EszkozForm(forms.ModelForm):
#   class Meta:
#        model = Eszkoz
#        fields = '__all__'

class EszkozForm(forms.ModelForm):
    class Meta:
        model = Eszkoz
        fields = ['megnevezes', 'gyariszam', 'tartozek', 'tartozek_eszkoz', 'beszerzesiIdo',
                  'selejtezesiIdo', 'aktiv', 'garanciaIdo', 'beszallito', 'tipus', 'holvanId']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'tipus' in self.data:
            try:
                tipus_id = int(self.data.get('tipus'))
                self.add_param_fields(tipus_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.add_param_fields(self.instance.tipus_id)
        
        

    def add_param_fields(self, tipus_id):
        kapcsolatok = TipusParameter.objects.filter(tipus_id=tipus_id).select_related('parameter')
        for kapcsolat in kapcsolatok:
            param = kapcsolat.parameter
            field_name = f'param_{param.id}'

            if param.tipus == Parametertipus.SZOVEG:
                self.fields[field_name] = forms.CharField(label=param.nev, required=False)
            elif param.tipus == Parametertipus.EGESZ:
                self.fields[field_name] = forms.IntegerField(label=param.nev, required=False)
            elif param.tipus == Parametertipus.SZAM:
                self.fields[field_name] = forms.FloatField(label=param.nev, required=False)
            elif param.tipus == Parametertipus.LOGIKAI:
                self.fields[field_name] = forms.BooleanField(label=param.nev, required=False)
            elif param.tipus == Parametertipus.DATUM:
                self.fields[field_name] = forms.DateField(label=param.nev, required=False, widget=forms.DateInput(attrs={'type': 'date'}))

            self.fields[field_name].param_obj = param  # hozzárendeljük a paraméter objektumot
    
    def save(self, commit=True):
        instance = super().save(commit=commit)

        for name, field in self.fields.items():
            if name.startswith("param_") and hasattr(field, "param_obj"):
                value = self.cleaned_data.get(name)

                param = field.param_obj
                ertek = EszkozParameterErtek(eszkoz=instance, parameter=param)

                if param.tipus == Parametertipus.SZOVEG:
                    ertek.ertek_szoveg = value
                elif param.tipus in [Parametertipus.EGESZ, Parametertipus.SZAM]:
                    ertek.ertek_szam = value
                elif param.tipus == Parametertipus.LOGIKAI:
                    ertek.ertek_logikai = value
                elif param.tipus == Parametertipus.DATUM:
                    ertek.ertek_datum = value

                ertek.save()
        return instance

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

class EszkozParameterForm(forms.ModelForm):
    class Meta:
        model = EszkozParameter
        fields = ['nev', 'tipus', 'mertekegyseg', 'leiras']

class TipusParameterForm(forms.ModelForm):
    class Meta:
        model = TipusParameter
        fields = ['tipus', 'parameter']
