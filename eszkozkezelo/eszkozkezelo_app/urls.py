from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='eszkozkezelo_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('eszkozkezelo_app/', views.eszkozkezelo_app, name='eszkozkezelo_app'),
    path('', views.eszkoz_list, name='eszkoz_list'),
    path('uj/', views.eszkoz_create, name='eszkoz_create'),
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
]