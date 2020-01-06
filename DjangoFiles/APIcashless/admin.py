from django.contrib import admin
# from simple_history.admin import SimpleHistoryAdmin
from .models import *
# from django.core.urlresolvers import reverse
from django.urls import reverse
from jet.admin import CompactInline
from django import forms
# from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
from jet.filters import DateRangeFilter
# admin.site.register(CarteCashless, SimpleHistoryAdmin)
# admin.site.register(ArticlesVendu)
# admin.site.register(pointOfSale)
# admin.site.register(tagIdCardMaitresse)
# admin.site.register(Membres)

# admin.site.register(inventaire)

# admin.site.register(moyenPaiement)

# class BoissonCoutantAdmin(admin.ModelAdmin):
#     list_display = ('date', 'nbrBoisson','CarteCashless')
#     # search_fields = ['name',]
# admin.site.register(BoissonCoutant, BoissonCoutantAdmin)




# Register your models here. 
# ('name' ,'wallet' ,'cash' ,'peaksu' ,'articles' ,'responsable' ,'membre' ,'dernierArticles' ,'history')



def moyenPaiementCadeau(modeladmin, request, queryset):
    queryset.update(moyenPaiement=moyenPaiement.objects.get(name='Cadeau'))
moyenPaiementCadeau.short_description = "Moyen de paiement = Cadeau"

def Decomptabiliser(modeladmin, request, queryset):
    queryset.update(comptabilise=False)
Decomptabiliser.short_description = "Comptabilise = False"

# class fermetureCaisseAdmin(admin.ModelAdmin):
    # list_display = ('date', 'chiffre_d_affaire', 'fond_de_caisse')

# admin.site.register(fermetureCaisse, fermetureCaisseAdmin)

class PageArticleAdmin(admin.ModelAdmin):
    list_display = ('name', 'poids')
    search_fields = ['name',]
admin.site.register(PageArticle, PageArticleAdmin)


# class posInlineForm(forms.ModelForm):
#     posInlineFormList = forms.ModelMultipleChoiceField(queryset=pointOfSale.objects.all(), required=False)
#     class Meta:
#         model = pointOfSale
#         fields = ['articles']


# class posInline(CompactInline):
    # model = pointOfSale.articles.through
    # extra = 3
    # max_num = 10
    # form = posInlineForm

class ArticlesAdmin(admin.ModelAdmin):
    list_display = ('name', 'prix','prixAchat', 'page', 'poidListe', 'alcool')
    search_fields = ['name',]
    # inlines = [ posInline, ]
    # form = posInlineForm

    # # list_editable = ('prix', 'prixAchat', 'page', 'poidListe')

admin.site.register(Articles, ArticlesAdmin)

class CarteCashlessAdmin(admin.ModelAdmin):
    list_display = ('number', 'tagId', 'peaksu','peaksuCadeau','membre','wallet')
    search_fields = ['tagId','number','membre__name']
    # readonly_fields = ("wallet", "tagId", "number")
    list_filter = ['membre','number']
    list_per_page = 20

admin.site.register(CarteCashless, CarteCashlessAdmin)


class DefaultFilterMixIn(admin.ModelAdmin):
    def changelist_view(self, request, *args, **kwargs):
        from django.http import HttpResponseRedirect
        if self.default_filters:
            #try:
                test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
                if test and test[-1] and not test[-1].startswith('?'):
                    url = reverse('admin:{}_{}_changelist'.format(self.opts.app_label, self.opts.model_name))
                    filters = []
                    for filter in self.default_filters:
                        key = filter.split('=')[0]
                        if not key in request.GET:
                            filters.append(filter)
                    if filters:                     
                        return HttpResponseRedirect("{}?{}".format(url, "&".join(filters)))
            #except: pass
        return super(DefaultFilterMixIn, self).changelist_view(request, *args, **kwargs)            



class ArticlesVendusAdmin(DefaultFilterMixIn):
    list_display = ('article', 'prix','qty','dateTps', 'carte', 'moyenPaiement', 'responsable','pos', 'BoitierUser')
    # readonly_fields = ('article', 'prix','qty','dateTps','membre', 'carte', 'moyenPaiement', 'responsable','pos' )
    # search_fields = ['dateTps']
    list_filter = ['article','membre', 'carte','responsable',('dateTps', DateRangeFilter), 'moyenPaiement','pos', 'BoitierUser']
    default_filters = ('pos__id__exact=48',)
    actions = [moyenPaiementCadeau, Decomptabiliser]
    list_per_page = 50
    

admin.site.register(ArticlesVendus, ArticlesVendusAdmin)

class rapportArticlesVenduAdmin(admin.ModelAdmin):
    list_display = ('date', 'article','qty')
    list_filter = ['article',('date', DateRangeFilter)]
    list_per_page = 100
admin.site.register(rapportArticlesVendu, rapportArticlesVenduAdmin)

class rapportBarAdmin(DefaultFilterMixIn):
    list_display = ('date', 'responsable', 'totalBarResto','totalCashless','totalCashCB', 'benefice', 'ardoise', 'gratuit', 'pos', 'caisse','recup')
    readonly_fields = ('date', 'responsable', 'totalBarResto','totalCashless','totalCashCB', 'benefice', 'ardoise', 'gratuit', 'pos','recup')

    list_filter = ['date', 'responsable']
    default_filters = ('responsable__id__exact=733',)
    list_per_page = 30

admin.site.register(rapportBar, rapportBarAdmin)

# class pointOfSaleAdmin(admin.ModelAdmin):
    # list_display = ('name','cash', 'wallet')
    # search_fields = ['name']
# admin.site.register(pointOfSale, pointOfSaleAdmin)

class pointOfSaleAdminHist(admin.ModelAdmin):
    list_display = ('name', 'cash','peaksu','dernierArticles','responsable','membre','wallet')
    readonly_fields = ('cash','peaksu','dernierArticles','responsable','membre')
    history_list_display = ('name', 'cash','peaksu','dernierArticles','responsable','membre')
    search_fields = ['name', 'wallet','responsable','membre']

admin.site.register(pointOfSale, pointOfSaleAdminHist)


class tagIdCardMaitresseAdmin(admin.ModelAdmin):
    list_display = ('membreName', 'strNumber', 'strtagId', 'pos','get_url')
    list_filter = ['pos',]

    # search_fields = ['tagIdCarte']


    def get_queryset(self, request):
        self.full_path = request.get_host()
        # import ipdb; ipdb.set_trace()
        return super(tagIdCardMaitresseAdmin, self).get_queryset(request)

    def get_url(self, obj):
        return self.full_path

admin.site.register(tagIdCardMaitresse, tagIdCardMaitresseAdmin)





class CarteCashlessForm(forms.ModelForm):
    class Meta:
        model = CarteCashless
        fields = ['membre']


    CarteCashlesss = forms.ModelChoiceField(queryset=CarteCashless.objects.filter(membre__isnull=True), required=False)

    def save(self, *args, **kwargs):
        # import ipdb; ipdb.set_trace()
        if self.cleaned_data :
            print("self.cleaned_data['CarteCashlesss'].number : ",self.cleaned_data['CarteCashlesss'] )
            print("self.cleaned_data['membre'].number : ",self.cleaned_data['membre'] )

            membreDb = self.cleaned_data['membre']
            carteDb = self.cleaned_data['CarteCashlesss']

            carteDb.membre = membreDb
            carteDb.save()

            if membreDb.ajout_2_PeakSu_Cadeau :
                carteDb.peaksu = 0
                carteDb.save()
                carteDb.peaksuCadeau = 2
                carteDb.save()
                membreDb.ajout_2_PeakSu_Cadeau = False
                membreDb.save()            



        return self.cleaned_data['CarteCashlesss']





class CarteCashlessInline(CompactInline):
    model = CarteCashless
    extra = 1
    max_num = 1
    form = CarteCashlessForm


class MembresAdmin(admin.ModelAdmin):
    fields = ('name', 'pseudo', 'email', 'tel', 'codePostal', 'dateNaissance','cotisation','ajout_2_PeakSu_Cadeau','adhesion_auto')
    
    list_display = ('name', 'pseudo', 'email', 'tel', 
        'codePostal', 'dateNaissance', 'dateInscription', 
        'dateDerniereCotisation', 'cotisation', 
        'dateAjout', 'aJourCotisation', 'numeroAdherant', 'Status')
    
    readonly_fields = ( 'numeroAdherant', 'Status','dateInscription',
        'dateAjout')


    search_fields = ['name','pseudo',]

    inlines = [
        CarteCashlessInline,
    ]
    list_per_page = 20

    # def save_related(self, request, form, formsets, change):
    #     print('change!!!!!!!!!!!!!!',change)
    #     super(type(self), self).save_related(request, form, formsets, change)
    #     if not change :
    #         if form.cleaned_data['ajout_2_PeakSu_Cadeau'] :
    #             membreDb = Membres.objects.get(name=form.cleaned_data['name'])
    #             carteDb = CarteCashless.objects.get(membre=membreDb)
    #             carteDb.peaksu = 0
    #             carteDb.save()
    #             carteDb.peaksuCadeau = 2
    #             carteDb.save()
    #             membreDb.ajout_2_PeakSu_Cadeau = False
    #             membreDb.save()

admin.site.register(Membres, MembresAdmin)


# class ouvertureBarHist(SimpleHistoryAdmin):
#     list_display = ( 'pos', 'ouverture','responsable','dateTime')
#     readonly_fields = ( 'pos', 'ouverture','responsable','dateTime')
#     history_list_display = ( 'pos', 'ouverture','responsable','dateTime')
#     search_fields = ('pos','responsable','dateTime')

# admin.site.register(ouvertureBar, ouvertureBarHist)
