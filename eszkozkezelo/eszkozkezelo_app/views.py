from django.contrib.auth.decorators import user_passes_test, login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from .models import Eszkoz, Beszallito, Szemely, Tipus,  TipusParameter, EszkozParameter ,Kepek
from .forms import EszkozForm, BeszallitoForm, SzemelyForm, TipusForm, MozgasForm, EszkozParameterForm, TipusParameterForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
import datetime
import os
from django.core.files.base import ContentFile

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
    mozgastortenet = eszkoz.mozgastortenet.order_by('-mozgasIdo')  # legfrissebb mozgás elöl
    eszkoz_parameterek = eszkoz.parameterek.select_related('parameter').all()
    return render(request, 'eszkozkezelo_app/eszkoz_brief.html', {
        'eszkoz': eszkoz,
        'mozgastortenet': mozgastortenet,
        'eszkoz_parameterek': eszkoz_parameterek,
        })

# Létrehozás
@user_passes_test(is_operator_or_admin, login_url='login')
def eszkoz_create(request):
    if request.method == 'POST':
        form = EszkozForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('eszkoz_list')
        else:
            print("FORM ERRORS:", form.errors)  # Hibák naplózása fejlesztéshez
    else:
        form = EszkozForm()
    return render(request, 'eszkozkezelo_app/eszkoz_form.html', {'form': form})

def get_tipus_parameterek(request):
    tipus_id = request.GET.get('tipus_id')
    adatok = []

    if tipus_id:
        kapcsolatok = TipusParameter.objects.filter(tipus_id=tipus_id).select_related('parameter')
        for kapcsolat in kapcsolatok:
            param = kapcsolat.parameter
            adatok.append({
                'id': param.id,
                'nev': param.nev,
                'tipus': param.tipus,
            })

    return JsonResponse({'parameterek': adatok})

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
        eszkoz.delete()  # <-- példány törlése!
        return redirect('eszkoz_list')
    return render(request, 'eszkozkezelo_app/eszkoz_confirm_delete.html', {'eszkoz': eszkoz})

# Képfeltöltés
# A feltöltéshez AJAX kérés szükséges, ezért a nézet JSON választ ad
@user_passes_test(is_operator_or_admin, login_url='login')
def eszkoz_image_upload(request, eszkoz_id):
    if request.method == 'POST' and request.FILES.getlist('images'):
        eszkoz = get_object_or_404(Eszkoz, pk=eszkoz_id)
        today = datetime.date.today()
        existing_count = Kepek.objects.filter(eszkoz_id=eszkoz.pk).count()
        for idx, img in enumerate(request.FILES.getlist('images'), start=1):
            ext = os.path.splitext(img.name)[1] or '.jpg'
            sorszam = existing_count + idx
            filename = f"{eszkoz.leltari_szam}_{sorszam}{ext}"
            kep_instance = Kepek(
                eszkoz_id=eszkoz,  # <-- Itt Eszkoz példányt kell átadni!
                keszitesIdeje=today
            )
            kep_instance.kep.save(filename, img, save=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

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
   

#### Mozgás ####
###############################################################################################################
def mozgas_letrehozas(request):
    if request.method == 'POST':
        form = MozgasForm(request.POST)
        if form.is_valid():
            # Először mentsük el a mozgást és tároljuk el a változóban
            mozgas = form.save()
            # Eszköz tulajdonosának frissítése a 'hova' mező alapján
            eszkoz = mozgas.eszkoz
            eszkoz.holvanId = mozgas.hova
            eszkoz.save()

            return redirect('eszkoz_list')  # vagy vissza az eszköz részletező oldalára
    else:
        form = MozgasForm()
    
    return render(request, 'eszkozkezelo_app/mozgas_form.html', {'form': form})

def mozgas_letrehozas_eszkozhoz(request, eszkoz_id):
    eszkoz = get_object_or_404(Eszkoz, id=eszkoz_id)
    honnan = eszkoz.holvanId

    if request.method == 'POST':
        form = MozgasForm(request.POST, eszkoz=eszkoz, honnan=honnan)
        if form.is_valid():
            mozgas = form.save()
            eszkoz.holvanId = form.cleaned_data['hova']
            eszkoz.save()
            return redirect('eszkoz_list')
    else:
        form = MozgasForm(eszkoz=eszkoz, honnan=honnan)

    return render(request, 'eszkozkezelo_app/mozgas_form.html', {
        'form': form,
        'eszkoz': eszkoz,
        'honnan': honnan,
    })

### Eszköz Paraméter ###
####################################################################################################################
@user_passes_test(is_operator_or_admin, login_url='login')
def eszkozparameter_list(request):
    parameterek = EszkozParameter.objects.all()
    user = request.user
    is_admin = user.is_superuser
    is_operator = user.groups.filter(name='Operator').exists()
    return render(request, 'eszkozkezelo_app/eszkozparameter_list.html', {
        'parameterek': parameterek,
        'is_admin': is_admin,
        'is_operator': is_operator,
    })

@user_passes_test(is_operator_or_admin, login_url='login')
def eszkozparameter_create(request):
    if request.method == 'POST':
        form = EszkozParameterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('eszkozparameter_list')
    else:
        form = EszkozParameterForm()
    return render(request, 'eszkozkezelo_app/eszkozparameter_form.html', {'form': form})

@user_passes_test(is_operator_or_admin, login_url='login')
def eszkozparameter_edit(request, pk):
    param = get_object_or_404(EszkozParameter, pk=pk)
    if request.method == 'POST':
        form = EszkozParameterForm(request.POST, instance=param)
        if form.is_valid():
            form.save()
            return redirect('eszkozparameter_list')
    else:
        form = EszkozParameterForm(instance=param)
    return render(request, 'eszkozkezelo_app/eszkozparameter_form.html', {'form': form})

@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def eszkozparameter_delete(request, pk):
    param = get_object_or_404(EszkozParameter, pk=pk)
    if request.method == 'POST':
        param.delete()
        return redirect('eszkozparameter_list')
    return render(request, 'eszkozkezelo_app/eszkozparameter_confirm_delete.html', {'param': param})

@user_passes_test(is_operator_or_admin, login_url='login')
def tipusparameter_list(request):
    kapcsolatok = TipusParameter.objects.select_related('tipus', 'parameter').all()
    user = request.user
    is_admin = user.is_superuser
    is_operator = user.groups.filter(name='Operator').exists()
    return render(request, 'eszkozkezelo_app/tipusparameter_list.html', {
        'kapcsolatok': kapcsolatok,
        'is_admin': is_admin,
        'is_operator': is_operator,
    })

@user_passes_test(is_operator_or_admin, login_url='login')
def tipusparameter_create(request):
    if request.method == 'POST':
        form = TipusParameterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tipusparameter_list')
    else:
        form = TipusParameterForm()
    return render(request, 'eszkozkezelo_app/tipusparameter_form.html', {'form': form})

@user_passes_test(is_operator_or_admin, login_url='login')
def tipusparameter_edit(request, pk):
    kapcsolat = get_object_or_404(TipusParameter, pk=pk)
    if request.method == 'POST':
        form = TipusParameterForm(request.POST, instance=kapcsolat)
        if form.is_valid():
            form.save()
            return redirect('tipusparameter_list')
    else:
        form = TipusParameterForm(instance=kapcsolat)
    return render(request, 'eszkozkezelo_app/tipusparameter_form.html', {'form': form})

@user_passes_test(is_operator_or_admin, login_url='login')
@user_passes_test(lambda u: u.is_superuser)
def tipusparameter_delete(request, pk):
    kapcsolat = get_object_or_404(TipusParameter, pk=pk)
    if request.method == 'POST':
        kapcsolat.delete()
        return redirect('tipusparameter_list')
    return render(request, 'eszkozkezelo_app/tipusparameter_confirm_delete.html', {'kapcsolat': kapcsolat})