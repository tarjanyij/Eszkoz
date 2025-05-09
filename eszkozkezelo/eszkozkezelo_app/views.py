from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Eszkoz, Beszallito, Szemely, Tipus
from .forms import EszkozForm, BeszallitoForm, SzemelyForm, TipusForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sikeres regisztráció. Most már bejelentkezhetsz.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'eszkozkezelo_app/register.html', {'form': form})

def eszkozkezelo_app(request):
    template = loader.get_template('myfirst.html')
    return HttpResponse(template.render())
# Create your views here.

### Eszköz ###
##############
def eszkoz_list(request):
    query = request.GET.get('q', '')
    tipus_id = request.GET.get('tipus')
    beszallito_id = request.GET.get('beszallito')
    aktiv = request.GET.get('aktiv')

    eszkozok = Eszkoz.objects.all()

    if query:
        eszkozok = eszkozok.filter(
            Q(megnevezes__icontains=query) | Q(gyariszam__icontains=query)
        )
    
    if tipus_id:
        eszkozok = eszkozok.filter(tipus_id=tipus_id)
    
    if beszallito_id:
        eszkozok = eszkozok.filter(beszallito_id=beszallito_id)
    
    if aktiv in ['true', 'false']:
        eszkozok = eszkozok.filter(aktiv=(aktiv == 'true'))

    return render(request, 'eszkozkezelo_app/eszkoz_list.html', {
        'eszkozok': eszkozok,
        'query': query,
        'tipusok': Tipus.objects.all(),
        'beszallitok': Beszallito.objects.all(),
        'tipus_id': tipus_id,
        'beszallito_id': beszallito_id,
        'aktiv': aktiv,
    })

def eszkoz_brief_view(request, pk):
    eszkoz = get_object_or_404(Eszkoz, pk=pk)
    return render(request, 'eszkozkezelo_app/eszkoz_brief.html', {'eszkoz': eszkoz})

def eszkoz_create(request):
    if request.method == 'POST':
        form = EszkozForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('eszkoz_list')
    else:
        form = EszkozForm()
    return render(request, 'eszkozkezelo_app/eszkoz_form.html', {'form': form})
# Szerkesztés
def eszkoz_edit(request, pk):
    eszkoz = get_object_or_404(Eszkoz, pk=pk)
    if request.method == 'POST':
        form = EszkozForm(request.POST, instance=eszkoz)
        if form.is_valid():
            form.save()
            return redirect('eszkoz_list')
    else:
        form = EszkozForm(instance=eszkoz)
    return render(request, 'eszkozkezelo_app/eszkoz_form.html', {'form': form, 'eszkoz': eszkoz})

# Törlés
def eszkoz_delete(request, pk):
    eszkoz = get_object_or_404(Eszkoz, pk=pk)
    if request.method == 'POST':
        Eszkoz.delete()
        return redirect('eszkoz_list')
    return render(request, 'eszkozkezelo_app/eszkoz_confirm_delete.html', {'eszkoz': eszkoz})

### Beszállító ###
##################
def beszallito_list(request):
    beszallitok = Beszallito.objects.all()
    return render(request, 'eszkozkezelo_app/beszallito_list.html', {'beszallitok': beszallitok})

def beszallito_create(request):
    if request.method == 'POST':
        form = BeszallitoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('beszallito_list')
    else:
        form = BeszallitoForm()
    return render(request, 'eszkozkezelo_app/beszallito_form.html', {'form': form})

# Szerkesztés
def beszallito_edit(request, pk):
    beszallito = get_object_or_404(Beszallito, pk=pk)
    if request.method == 'POST':
        form = BeszallitoForm(request.POST, instance=beszallito)
        if form.is_valid():
            form.save()
            return redirect('beszallito_list')
    else:
        form = BeszallitoForm(instance=beszallito)
    return render(request, 'eszkozkezelo_app/beszallito_form.html', {'form': form})

# Törlés
def beszallito_delete(request, pk):
    beszallito = get_object_or_404(Beszallito, pk=pk)
    if request.method == 'POST':
        beszallito.delete()
        return redirect('beszallito_list')
    return render(request, 'eszkozkezelo_app/beszallito_confirm_delete.html', {'beszallito': beszallito})


### Személy ###
###############
def szemely_list(request):
    szemelyek = Szemely.objects.all()
    return render(request, 'eszkozkezelo_app/szemely_list.html', {'szemelyek': szemelyek})

def szemely_create(request):
    if request.method == 'POST':
        form = SzemelyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('szemely_list')
    else:
        form = SzemelyForm()
    return render(request, 'eszkozkezelo_app/szemely_form.html', {'form': form})

# Szerkesztés
def szemely_edit(request, pk):
    szemely = get_object_or_404(Szemely, pk=pk)
    if request.method == 'POST':
        form = SzemelyForm(request.POST, instance=szemely)
        if form.is_valid():
            form.save()
            return redirect('szemely_list')
    else:
        form = SzemelyForm(instance=szemely)
    return render(request, 'eszkozkezelo_app/szemely_form.html', {'form': form})

# Törlés
def szemely_delete(request, pk):
    szemely = get_object_or_404(Szemely, pk=pk)
    if request.method == 'POST':
        szemely.delete()
        return redirect('szemely_list')
    return render(request, 'eszkozkezelo_app/szemely_confirm_delete.html', {'szemely': szemely})


### Típus ###
#############
def tipus_list(request):
    tipusok = Tipus.objects.all()
    return render(request, 'eszkozkezelo_app/tipus_list.html', {'tipusok': tipusok})

def tipus_create(request):
    if request.method == 'POST':
        form = TipusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tipus_list')
    else:
        form = TipusForm()
    return render(request, 'eszkozkezelo_app/tipus_form.html', {'form': form})

 # Szerkesztés
def tipus_edit(request, pk):
    tipus = get_object_or_404(Tipus, pk=pk)
    if request.method == 'POST':
        form = TipusForm(request.POST, instance=tipus)
        if form.is_valid():
            form.save()
            return redirect('tipus_list')
    else:
        form = TipusForm(instance=tipus)
    return render(request, 'eszkozkezelo_app/tipus_form.html', {'form': form})

# Törlés
def tipus_delete(request, pk):
    tipus = get_object_or_404(Tipus, pk=pk)
    if request.method == 'POST':
        tipus.delete()
        return redirect('tipus_list')
    return render(request, 'eszkozkezelo_app/stipus_confirm_delete.html', {'tipus': tipus})
   