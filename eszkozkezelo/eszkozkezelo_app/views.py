from django.contrib.auth.decorators import user_passes_test, login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from .models import Eszkoz, Beszallito, Szemely, Tipus
from .forms import EszkozForm, BeszallitoForm, SzemelyForm, TipusForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

def is_operator_or_admin(user):
    return user.is_superuser or user.groups.filter(name='Operator').exists()

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
##################################################################################################################
@user_passes_test(is_operator_or_admin, login_url='login')
def eszkoz_list(request):
    query = request.GET.get('q', '')
    tipus_id = request.GET.get('tipus')
    szemely_id = request.GET.get('szemely')
    beszallito_id = request.GET.get('beszallito')
    aktiv = request.GET.get('aktiv')

    eszkozok = Eszkoz.objects.all()

    if query:
        eszkozok = eszkozok.filter(
            Q(megnevezes__icontains=query) | Q(gyariszam__icontains=query)
        )
    
    if tipus_id:
        eszkozok = eszkozok.filter(tipus_id=tipus_id)
    
    if szemely_id:
        eszkozok = eszkozok.filter(holvanId_id=szemely_id)
    
    if beszallito_id:
        eszkozok = eszkozok.filter(beszallito_id=beszallito_id)
    
    if aktiv in ['true', 'false']:
        eszkozok = eszkozok.filter(aktiv=(aktiv == 'true'))
    # Lapozás (10 elem/lap)
    paginator = Paginator(eszkozok, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

 # AJAX kérés esetén csak a táblázatot adjuk vissza
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'eszkozkezelo_app/partials/eszkoz_table.html', {
            'page_obj': page_obj,
            'query': query,
        })
    
    user = request.user
    is_admin = user.is_superuser
    is_operator = user.groups.filter(name='Operator').exists()

    szemelyek = Szemely.objects.all()
    szemelyek = szemelyek.order_by('nev')  # <--- ABC sorrend

    return render(request, 'eszkozkezelo_app/eszkoz_list.html', {
        'eszkozok': eszkozok,
        'query': query,
        'tipusok': Tipus.objects.all(),
        'szemely': szemelyek,
        'beszallitok': Beszallito.objects.all(),
        'tipus_id': tipus_id,
        'beszallito_id': beszallito_id,
        'aktiv': aktiv,
        'page_obj': page_obj,
        'is_admin': is_admin,
        'is_operator': is_operator,
    })
@user_passes_test(is_operator_or_admin, login_url='login')
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def eszkoz_delete(request, pk):
    eszkoz = get_object_or_404(Eszkoz, pk=pk)
    if request.method == 'POST':
        Eszkoz.delete()
        return redirect('eszkoz_list')
    return render(request, 'eszkozkezelo_app/eszkoz_confirm_delete.html', {'eszkoz': eszkoz})

### Beszállító ###
############################################################################################################################
@user_passes_test(is_operator_or_admin, login_url='login')
def beszallito_list(request):
    query = request.GET.get('q', '')
    beszallitok = Beszallito.objects.all()
    
    if query:
        beszallitok = beszallitok.filter(
            Q(beszallitoNev__icontains=query) | Q(beszallitoKontatkt__icontains=query)
        )
    
    # Lapozás (10 elem/lap)
    paginator = Paginator(beszallitok, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user = request.user
    is_admin = user.is_superuser
    is_operator = user.groups.filter(name='Operator').exists()
    
    return render(request, 'eszkozkezelo_app/beszallito_list.html', {
        'beszallitok': beszallitok,
        'query': query,
        'page_obj': page_obj,
        'is_admin': is_admin,
        'is_operator': is_operator,
    })

@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def beszallito_delete(request, pk):
    beszallito = get_object_or_404(Beszallito, pk=pk)
    if request.method == 'POST':
        beszallito.delete()
        return redirect('beszallito_list')
    return render(request, 'eszkozkezelo_app/beszallito_confirm_delete.html', {'beszallito': beszallito})


### Személy ###
####################################################################################################################
@user_passes_test(is_operator_or_admin, login_url='login')
def szemely_list(request):
    query = request.GET.get('q', '')

    szemelyek = Szemely.objects.all()

    if query:
        szemelyek = szemelyek.filter(
            Q(nev__icontains=query) | Q(email__icontains=query)
        )

    szemelyek = szemelyek.order_by('nev')  # <--- ABC sorrend

    # Lapozás (10 elem/lap)
    paginator = Paginator(szemelyek, 14)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # AJAX kérés esetén csak a táblázatot adjuk vissza
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'eszkozkezelo_app/partials/szemely_table.html', {
            'page_obj': page_obj,
            'query': query,
        })

    user = request.user
    is_admin = user.is_superuser
    is_operator = user.groups.filter(name='Operator').exists()

    return render(request, 'eszkozkezelo_app/szemely_list.html', {
        'szemelyek': szemelyek,
        'query': query,
        'page_obj': page_obj,
        'is_admin': is_admin,
        'is_operator': is_operator,
        })
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def szemely_delete(request, pk):
    szemely = get_object_or_404(Szemely, pk=pk)
    if request.method == 'POST':
        szemely.delete()
        return redirect('szemely_list')
    return render(request, 'eszkozkezelo_app/szemely_confirm_delete.html', {'szemely': szemely})


### Típus ###
################################################################################################################################
@user_passes_test(is_operator_or_admin, login_url='login')
def tipus_list(request):
    tipusok = Tipus.objects.all()
    return render(request, 'eszkozkezelo_app/tipus_list.html', {'tipusok': tipusok})

@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(is_operator_or_admin)
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
@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def tipus_delete(request, pk):
    tipus = get_object_or_404(Tipus, pk=pk)
    if request.method == 'POST':
        tipus.delete()
        return redirect('tipus_list')
    return render(request, 'eszkozkezelo_app/stipus_confirm_delete.html', {'tipus': tipus})
   