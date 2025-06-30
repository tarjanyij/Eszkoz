from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='eszkozkezelo_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('eszkozkezelo_app/', views.eszkozkezelo_app, name='eszkozkezelo_app'),
    path('', views.eszkoz_list, name='eszkoz_list'),
    path('uj/', views.eszkoz_create, name='eszkoz_create'),
    path('ajax/get-tipus-parameterek/', views.get_tipus_parameterek, name='get_tipus_parameterek'),
    path('eszkoz/<int:pk>/brief/', views.eszkoz_brief_view, name='eszkoz_brief'),
    path('eszkoz/<int:pk>/szerkesztes/', views.eszkoz_edit, name='eszkoz_edit'),
    path('eszkoz/<int:pk>/torles/', views.eszkoz_delete, name='eszkoz_delete'),

    path('beszallitok/', views.beszallito_list, name='beszallito_list'),
    path('beszallitok/uj/', views.beszallito_create, name='beszallito_create'),
    path('beszallitok/<int:pk>/szerkesztes/', views.beszallito_edit, name='beszallito_edit'),
    path('beszallitok/<int:pk>/torles/', views.beszallito_delete, name='beszallito_delete'),

    path('szemelyek/', views.szemely_list, name='szemely_list'),
    path('szemelyek/uj/', views.szemely_create, name='szemely_create'),
    path('szemelyek/<int:pk>/szerkesztes/', views.szemely_edit, name='szemely_edit'),
    path('szemelyek/<int:pk>/torles/', views.szemely_delete, name='szemely_delete'),

    path('tipusok/', views.tipus_list, name='tipus_list'),
    path('tipusok/uj/', views.tipus_create, name='tipus_create'),
    path('tipusok/<int:pk>/szerkesztes/', views.tipus_edit, name='tipus_edit'),
    path('tipusok/<int:pk>/torles/', views.tipus_delete, name='tipus_delete'),

    path('mozgas/uj/', views.mozgas_letrehozas, name='mozgas_letrehozas'),
    path('mozgas/uj/<int:eszkoz_id>/', views.mozgas_letrehozas_eszkozhoz, name='mozgas_letrehozas_eszkozhez'),

    path('eszkozparameterek/', views.eszkozparameter_list, name='eszkozparameter_list'),
    path('eszkozparameterek/uj/', views.eszkozparameter_create, name='eszkozparameter_create'),
    path('eszkozparameterek/<int:pk>/szerkesztes/', views.eszkozparameter_edit, name='eszkozparameter_edit'),
    path('eszkozparameterek/<int:pk>/torles/', views.eszkozparameter_delete, name='eszkozparameter_delete'),

    path('tipusparameterek/', views.tipusparameter_list, name='tipusparameter_list'),
    path('tipusparameterek/uj/', views.tipusparameter_create, name='tipusparameter_create'),
    path('tipusparameterek/<int:pk>/szerkesztes/', views.tipusparameter_edit, name='tipusparameter_edit'),
    path('tipusparameterek/<int:pk>/torles/', views.tipusparameter_delete, name='tipusparameter_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)