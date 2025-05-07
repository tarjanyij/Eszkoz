from django.db import models
import datetime

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
    megnevezes = models.CharField(max_length=255, verbose_name="Eszköz elnevezése",help_text="Az esköz pontos típuselnevezése")
    gyariszam = models.CharField(max_length=60,verbose_name="Gyári szám",help_text="Az esköz gyártási száma")
    tartozek = models.BooleanField(verbose_name="Tartozék",help_text="Ez az eszköz valamely másik eszköz tartozéka - beépítésre került")
    tartozek_eszkoz = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Mely eszköz tartozéka",help_text="Melyik eszköznek a tartozéka")
    beszerzesiIdo = models.DateField(auto_now_add=True, verbose_name="Beszerzés ideje",help_text="Beszerzés időpontja ( asz eszköz felvétel időpontja)")
    selejtezesiIdo = models.DateField(auto_now=False, auto_now_add=False, default=datetime.date.today, verbose_name="Selejtezési idő",help_text="Mikor került selejtezésre az esköz")
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