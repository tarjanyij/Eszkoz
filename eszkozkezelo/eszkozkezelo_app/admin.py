from django.contrib import admin

# Register your models here.
from .models import Tipus, Szemely, Kepek, Beszallito, Eszkoz, Mozgas, Mozgastipusok

admin.site.register(Tipus)
admin.site.register(Szemely)
admin.site.register(Kepek)
admin.site.register(Beszallito)
admin.site.register(Eszkoz)
admin.site.register(Mozgastipusok)
admin.site.register(Mozgas)