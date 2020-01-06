from django.db import models
# from simple_history.models import HistoricalRecords
from datetime import datetime
from dateutil import parser
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
import requests, json
from requests.auth import HTTPBasicAuth

from dateutil import tz
runZone = tz.gettz('Indian/Reunion')

# import ipdb; ipdb.set_trace()


class StatusMembres(models.Model):
    name = models.CharField(db_index=True, max_length=50, unique=True)

    def __str__(self): 
        return self.name

            
class Membres(models.Model) :
    name = models.CharField(db_index=True, max_length=50, unique=True)
    pseudo = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    numeroAdherant = models.CharField(max_length=50, unique=True, null=True, blank=True)
    codePostal = models.IntegerField(null=True, blank=True)
    dateNaissance= models.DateField(null=True, blank=True)
    tel = models.CharField(max_length=15, null=True, blank=True)


    Status = models.ForeignKey(StatusMembres, null=True, blank=True,on_delete=models.SET_NULL)
    dateInscription = models.DateField(null=True, blank=True)
    dateDerniereCotisation = models.DateField(null=True, blank=True)
    dateAjout = models.DateField(auto_now_add=True)
    cotisation = models.FloatField(default=5)

    ajout_2_PeakSu_Cadeau = models.BooleanField(default=True)
    adhesion_auto = models.BooleanField(default=True)

    def aJourCotisation(self) :
        now = datetime.now(tz=runZone)

        dateProchaineCotisationMax =  datetime(now.year,12,31).date()
        datePrecedenteCotisationMax =  datetime(now.year - 1,10,1).date()

        if self.dateDerniereCotisation :
            return datePrecedenteCotisationMax < self.dateDerniereCotisation < dateProchaineCotisationMax
        else :
            return False 

    class Meta:
        ordering = ('name',)
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'

    def __str__(self): 
        if self.pseudo :
            return self.pseudo
        else :
            return self.name



class pointOfSale(models.Model):
    name = models.CharField(db_index=True, max_length=30)
    wallet = models.CharField(max_length=38, blank=True, null=True)
    cash = models.FloatField(default=0)
    peaksu = models.FloatField(default=0)
    articles = models.ManyToManyField('Articles', blank=True)
    responsable = models.ForeignKey(Membres, null=True, blank=True, related_name='membreResponsable',on_delete=models.SET_NULL)
    membre = models.ForeignKey(Membres, null=True, blank=True, related_name='membre' ,on_delete=models.SET_NULL)
    dernierArticles = models.CharField(max_length=200, blank=True, null=True)
    # history = HistoricalRecords()

    def __str__(self):              # __unicode__ on Python 2
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Point de vente'
        verbose_name_plural = 'Points de vente'

class PageArticle(models.Model):
    name = models.CharField(max_length=30)
    poids = models.IntegerField(default=0, null=True)
    
    def __str__(self): 
        return self.name

    class Meta:
        # ordering = ( '-page','poidListe',)
        ordering = ( 'poids',)


class Articles(models.Model):
    name = models.CharField(db_index=True, max_length=30)
    prix = models.FloatField(default=0, null=True)
    prixAchat = models.FloatField(default=0, null=True)
    page = models.ForeignKey(PageArticle, blank=True, null=True, on_delete=models.SET_NULL)
    poidListe = models.IntegerField(default=0, null=True)
    alcool = models.BooleanField(default=False)
    def __str__(self): 
        return self.name

    def page_name(self) :
        if self.page :
            return self.page.name
        else :
            return ""

    def page_poids(self) :
        if self.page :
            return self.page.poids
        else :
            return ""

    class Meta:
        ordering = ( 'page', 'poidListe',)
        verbose_name = 'article'
        verbose_name_plural = 'Tarifs et articles'

class moyenPaiement(models.Model):
    name = models.CharField(db_index=True, max_length=30)

    def __str__(self):              # __unicode__ on Python 2
        return self.name


class CarteCashless(models.Model):
    tagId = models.CharField(db_index=True, max_length=8, unique=True)
    number = models.CharField(db_index=True, max_length=5, blank=True, null=True, unique=True)
    wallet = models.CharField(max_length=38, blank=True, null=True, unique=True)
    peaksu = models.FloatField(default=0)
    Last_changeBy = models.ForeignKey(pointOfSale, blank=True, null=True, on_delete=models.SET_NULL)
    membre = models.ForeignKey(Membres, blank=True, null=True, on_delete=models.SET_NULL)
    peaksuCadeau = models.FloatField(default=0)
    # history = HistoricalRecords()
    rpg = models.BooleanField(default=False)
    
    def changeByName(self):
        if self.Last_changeBy :
            return self.Last_changeBy.name
        else :
            return ""

    def membreName(self):
        if self.membre :
            if self.membre.pseudo :
                return self.membre.pseudo
            else :
                return self.membre.name

        else :
            return ""

    def membreCotisationAJour(self):
        if self.membre :
            if self.membre.dateDerniereCotisation :
                if self.membre.aJourCotisation() :
                    return "A Jour "+str(self.membre.dateDerniereCotisation.strftime('%d-%m-%Y'))
                else :
                    return "PAS A Jour "+str(self.membre.dateDerniereCotisation.strftime('%d-%m-%Y'))
            else :
                return False

        else :
            return False


    def __str__(self):
        if self.number and self.membre :
            return self.number+" : "+self.membre.name
        elif self.number :
            return self.number+" : "+self.tagId
        else :
            return self.tagId

    class Meta:
        ordering = ('number',)
        verbose_name = 'Carte cashless'
        verbose_name_plural = 'Cartes cashless'


class tagIdCardMaitresse(models.Model):
    CarteCashless = models.ForeignKey(CarteCashless, related_name='CardMaitresse', blank=True, null=True, on_delete=models.SET_NULL)
    pos = models.ForeignKey(pointOfSale,on_delete=models.PROTECT)
    
    def __str__(self):              # __unicode__ on Python 2
        try:
            return self.CarteCashless.tagId+" "+self.pos.name
        except Exception as e:
            return self.pos.name

    def strNumber(self):
        if self.CarteCashless :
            return self.CarteCashless.number
        else :
            return ""

    def strtagId(self):
        if self.CarteCashless :
            return self.CarteCashless.tagId
        else :
            return ""

    def membreName(self):
        if self.CarteCashless :
            if self.CarteCashless.membre :
                if self.CarteCashless.membre.pseudo :
                    return self.CarteCashless.membre.pseudo
                else :
                    return self.CarteCashless.membre.name
            else :
                return ""
        else :
            return ""

    class Meta:
        verbose_name = 'Carte maîtresse'
        verbose_name_plural = 'Cartes maîtresses'



class ArticlesVendus(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.PROTECT)
    prix = models.FloatField(default=0, null=True)
    qty = models.FloatField(default=0, null=True)
    pos = models.ForeignKey(pointOfSale, on_delete=models.PROTECT)
    BoitierUser = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    dateTps = models.DateTimeField(default=timezone.now)
    membre = models.ForeignKey(Membres, null=True, blank=True, on_delete=models.SET_NULL)
    carte = models.ForeignKey(CarteCashless, null=True, blank=True, on_delete=models.SET_NULL)
    responsable = models.ForeignKey(Membres, null=True, blank=True, related_name='responsableBar', on_delete=models.SET_NULL )
    moyenPaiement = models.ForeignKey(moyenPaiement, null=True, blank=True, on_delete=models.SET_NULL)
    comptabilise = models.BooleanField(default=False)

    class Meta:
        ordering = ('-dateTps',)
        verbose_name = 'Article vendu'
        verbose_name_plural = 'Articles vendus'

class rapportBar(models.Model):
    responsable = models.ForeignKey(Membres, on_delete=models.PROTECT)
    pos = models.ForeignKey(pointOfSale, on_delete=models.PROTECT)
    date = models.DateField(blank=True, null=True)
    totalBarResto = models.FloatField(default=0, null=True)
    totalCashless = models.FloatField(default=0, null=True)
    totalCashCB = models.FloatField(default=0, null=True)
    benefice = models.FloatField(default=0, null=True)
    ardoise = models.FloatField(default=0, null=True)
    gratuit = models.FloatField(default=0, null=True)
    recup = models.BooleanField(default=False)
    caisse = models.FloatField(default=0, null=True)

    def pourcentage(self):
        return round(((10 * float(self.benefice)) / 100) ,2)

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Rapport caisse'
        verbose_name_plural = 'Rapports caisse'

class rapportArticlesVendu(models.Model):
    date = models.DateField()
    article = models.ForeignKey(Articles, on_delete=models.PROTECT)
    qty = models.SmallIntegerField(default=0, null=True)

    class Meta:
        ordering = ('-date',)
        verbose_name = 'Rapport quantités vendus'
        verbose_name_plural = 'Rapports quantités vendus'

class BoissonCoutant(models.Model):
    CarteCashless = models.ForeignKey(CarteCashless, related_name='BoissonCoutantCarteM', blank=True, null=True, on_delete=models.SET_NULL)
    nbrBoisson = models.IntegerField(default=0)
    date = models.DateField(blank=True,null=True)

    class Meta(object):
        ordering =('-date',)

    def __str__(self):              # __unicode__ on Python 2
        return str(self.nbrBoisson)

@receiver(post_save, sender=Membres)
def Membres_creation_si_cotisation(sender, instance, created, **kwargs):
    if created:
        if instance.adhesion_auto and instance.cotisation :
            if instance.cotisation > 0 :
                instance.dateDerniereCotisation = datetime.now().date()

                if instance.dateInscription :
                    pass
                else :
                    instance.dateInscription = datetime.now().date()

                if instance.cotisation >= 15 :
                    mActif, created = StatusMembres.objects.get_or_create(name="A2")
                    instance.Status = mActif
                else :
                    mLoisir, created = StatusMembres.objects.get_or_create(name="L")
                    instance.Status = mLoisir

                instance.adhesion_auto = False

                instance.save()

                ArticlesVendus.objects.create(
                        article=Articles.objects.get(name='Adhésion'), 
                        prix=instance.cotisation, 
                        qty=1, 
                        pos=pointOfSale.objects.get(name="Bar3PeaksQuotidientCashLess"), 
                        membre=instance, 
                        moyenPaiement=moyenPaiement.objects.get(name='Cash/CB'),
                        responsable=Membres.objects.get(name="3Peaks"))


@receiver(post_save, sender=rapportBar)
def valeurCaisseFaite(sender, instance, created, **kwargs):
    # if instance.caisse > 0 :
    #     # rapportBar = instance
    #     print("receiver valeurCaisseFaite : ",instance)

    #     ArtVendus = ArticlesVendus.objects.filter(comptabilise=False, dateTps__date__lte=instance.date)
    #     for x in ArtVendus :
    #         print(x)
    #         x.comptabilise = True
    #         x.save()

    #     print("compta ok")
    if instance.recup == False :
        if instance.caisse > 0 :
            instance.recup = True
            instance.save()

