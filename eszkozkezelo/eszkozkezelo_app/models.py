from django.db import models
import datetime
import os
from django.conf import settings
import environ

# Create your models here.
class Tipus(models.Model):
    megnevezes = models.CharField(
        max_length=60,
        verbose_name="Típus neve",
        help_text="A típus pontos megnevezése")

    def __str__(self):
        return self.megnevezes

class Szemely(models.Model):
    nev =models.CharField(
        max_length=60,
        verbose_name="Személy neve",
        help_text="A személy teljes neve")
    
    email = models.EmailField(
        verbose_name="Email cím",
        help_text="Kérjük, adja meg az érvényes e-mail címet")

    aktiv = models.BooleanField(
        default=True,
        verbose_name="Aktív",
        help_text="Az adott személyre kiadható-e eszköz")

    def __str__(self):
        return self.nev

class Kepek(models.Model):
    eszkoz_id = models.ForeignKey(
        "Eszkoz",
        verbose_name=("Eszkoz"),
        on_delete=models.CASCADE,
        related_name="kepek")

    kep = models.ImageField(
        upload_to='kepek/',
        height_field=None,
        width_field=None,
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Kép",
        help_text="Az eszközről készült fotó")

    keszitesIdeje = models.DateField(
        auto_now=False,
        auto_now_add=False,
        verbose_name="Kép készítés ideje",
        help_text="")

class Beszallito(models.Model):
    beszallitoNev = models.CharField(
        max_length=50,
        verbose_name="Beszállító neve",
        help_text="Beszállító elnevezése")

    beszallitoCim = models.CharField(
        max_length=50,
        verbose_name="Beszállító címe",
        help_text="Beszállító pontos címe")

    beszallitoKontatkt = models.CharField(
        max_length=50,
        verbose_name="Beszállító kontatkt",
        help_text="Beszállító kontatkt személy neve")

    beszallitoTel = models.CharField(
        max_length=50,
        verbose_name="Beszállító telefon",
        help_text="Beszállító kontatkt személy telefonszáma")

    def __str__(self):
        return self.beszallitoNev

class Eszkoz(models.Model):
    leltari_szam = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Leltári szám",
        help_text="Automatikusan generált leltári szám"
    )
    megnevezes = models.CharField(max_length=255, verbose_name="Eszköz elnevezése",help_text="Az esköz pontos típuselnevezése")
    gyariszam = models.CharField(max_length=60,verbose_name="Gyári szám",help_text="Az esköz gyártási száma")
    tartozek = models.BooleanField(verbose_name="Tartozék",help_text="Ez az eszköz valamely másik eszköz tartozéka - beépítésre került")
    tartozek_eszkoz = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mely eszköz tartozéka",help_text="Melyik eszköznek a tartozéka")
    beszerzesiIdo = models.DateField(default=datetime.date.today, verbose_name="Beszerzés ideje",help_text="Beszerzés időpontja ( asz eszköz felvétel időpontja)")
    selejtezesiIdo = models.DateField(auto_now=False, auto_now_add=False, verbose_name="Selejtezési idő",help_text="Mikor került selejtezésre az esköz")
    aktiv = models.BooleanField(default=True, verbose_name="Aktív",help_text="Kiadható még az eszköz")
    garanciaIdo = models.IntegerField(verbose_name="Garancia idő",help_text="Garancia időtartama hónapokban")

    beszallito = models.ForeignKey(
        Beszallito,
        on_delete=models.CASCADE,
        verbose_name="Beszallító"
    )

    tipus = models.ForeignKey(
        Tipus,
        on_delete=models.CASCADE,
        verbose_name="Típus"
    )

    holvanId = models.ForeignKey(
        Szemely,
        on_delete=models.CASCADE,
        verbose_name="Hol van"
    )

    def save(self, *args, **kwargs):
        if not self.leltari_szam:
            # Betöltjük az előtagot az .env-ből
            env = environ.Env()
            env.read_env(os.path.join(settings.BASE_DIR, '.env'))
            prefix = env('LELTARI_PREFIX', default='TDF')
            last = Eszkoz.objects.order_by('-id').first()
            next_num = 0
            if last and last.leltari_szam and last.leltari_szam.startswith(prefix):
                try:
                    last_num = int(last.leltari_szam[len(prefix):])
                    next_num = last_num + 1
                except ValueError:
                    next_num = 0
            self.leltari_szam = f"{prefix}{next_num:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.megnevezes  

class Mozgastipusok(models.Model):
    megnevezes = models.CharField(
        max_length = 50,
        verbose_name="Mozgástípusok",
        help_text="Az eszköz kiadásra vagy bevételezésre sbt került")
    
    def __str__(self):
        return self.megnevezes

class Mozgas(models.Model):
    mozgasIdo = models.DateField(
        auto_now=False,
        auto_now_add=False,
        default=datetime.date.today,
        verbose_name="Mozgás ideje",
        help_text="Az esköz mozgatásának pontos ideje"
    )
    
    honnan = models.ForeignKey(
        Szemely,
        on_delete=models.CASCADE,
        related_name='mozgasok_honnan'
    )

    hova = models.ForeignKey(
        Szemely,
        on_delete=models.CASCADE,
        related_name='mozgasok_hova'
    )

    mozgastipus = models.ForeignKey(
        Mozgastipusok,
        on_delete=models.CASCADE
    )
    
    eszkoz = models.ForeignKey(
    Eszkoz,
    on_delete=models.CASCADE,
    related_name='mozgastortenet',
    verbose_name="Eszköz"
    )

# Paraméter típusa - csak szövegként, választható típusokkal
class Parametertipus(models.TextChoices):
    SZOVEG = 'SZ', 'Szöveg'
    EGESZ = 'INT', 'Egész szám'
    SZAM = 'FLOAT', 'Tört szám'
    LOGIKAI = 'BOOL', 'Logikai (igen/nem)'
    DATUM = 'DATE', 'Dátum'

# Lehetséges paraméter definíciók
class EszkozParameter(models.Model):
    nev = models.CharField(max_length=100, verbose_name="Paraméter neve")
    tipus = models.CharField(max_length=10, choices=Parametertipus.choices, verbose_name="Paraméter típusa")
    mertekegyseg = models.CharField(max_length=20, null=True, blank=True, verbose_name="Mértékegység", help_text="Opcionális mértékegység a paraméterhez")
    leiras = models.TextField(null=True, blank=True, verbose_name="Leírás", help_text="Rövid leírás a paraméterről")
    def __str__(self):
        return self.nev

# Eszközökhöz rendelt paraméterértékek
class EszkozParameterErtek(models.Model):
    eszkoz = models.ForeignKey(Eszkoz, on_delete=models.CASCADE, related_name="parameterek")
    parameter = models.ForeignKey(EszkozParameter, on_delete=models.CASCADE)
    ertek_szoveg = models.TextField(null=True, blank=True)
    ertek_szam = models.FloatField(null=True, blank=True)
    ertek_logikai = models.BooleanField(null=True, blank=True)
    ertek_datum = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.eszkoz.megnevezes} - {self.parameter.nev}: {self.ertek_formazott()}"

    def ertek_formazott(self):
        if self.parameter.tipus == Parametertipus.SZOVEG:
            return self.ertek_szoveg
        elif self.parameter.tipus == Parametertipus.EGESZ or self.parameter.tipus == Parametertipus.SZAM:
            return str(self.ertek_szam)
        elif self.parameter.tipus == Parametertipus.LOGIKAI:
            return "Igen" if self.ertek_logikai else "Nem"
        elif self.parameter.tipus == Parametertipus.DATUM:
            return self.ertek_datum.strftime("%Y-%m-%d") if self.ertek_datum else ""
        return ""

class TipusParameter(models.Model):
    tipus = models.ForeignKey('Tipus', on_delete=models.CASCADE)
    parameter = models.ForeignKey(EszkozParameter, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipus} - {self.parameter}"
