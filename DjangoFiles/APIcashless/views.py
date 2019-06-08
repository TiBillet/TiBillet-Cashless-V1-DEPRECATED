#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404

# from APIcashless.models import ArticlesVendu, ArticlesVendus, CarteCashless, pointOfSale, tagIdCardMaitresse, Membres, Articles, StatusMembres, rapportBar, moyenPaiement
from APIcashless.models import *
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
# from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from APIcashless.serializers import CarteCashlessSerializer, ArticlesSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io
import json
import time
import re
import os
import uuid
from Savoir import Savoir
import requests
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
# from simple_history.utils import update_change_reason
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder 
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Min


from mailchimp3 import MailChimp






def calculRapportBar(jour, pos):
    # veille = datetime.now().date() - timedelta(days=1)
    # jour = datetime.now().date()

    ArticlesVendusJourDb = ArticlesVendus.objects.filter(dateTps__date=jour, pos=pos, comptabilise=False)
    if len(ArticlesVendusJourDb) > 0 :
        Activite = {}
        Activite['3Peaks'] = {'totalBarResto':float(0),'benefice':float(0), 'totalCashless':0, 'Cash/CB':0, 'ardoise':0, 'gratuit':0}
        pageBarResto = ('Bar','Resto')
        pagePeaksu = ('PeakSu','PeakSu2')
        moyenBar = ('Cash/CB','PeakSu','PeakSu Cadeau')

        for art in ArticlesVendusJourDb :
            Activite[art.responsable.name] = {'totalBarResto':float(0),'benefice':float(0), 'totalCashless':0, 'Cash/CB':0, 'ardoise':0, 'gratuit':0}


        # création du dict par responsable :
        for art in ArticlesVendusJourDb :
            if art.responsable :

                # On compte toute les ventes réalisée au bar et au resto :
                if art.article.page.name in pageBarResto and art.moyenPaiement.name in moyenBar and art.responsable != '3Peaks' :
                    print(art.article.name,
                        art.article.page.name,
                        art.moyenPaiement.name,round(art.prix * art.qty ,2),
                        round((art.prix - art.article.prixAchat )* art.qty , 2))

                    Activite[art.responsable.name]['totalBarResto'] += round(art.prix * art.qty, 2)
                    Activite[art.responsable.name]['benefice'] += round((art.prix - art.article.prixAchat )* art.qty , 2)
                    Activite['3Peaks']['totalBarResto'] += round(art.prix * art.qty, 2)
                    Activite['3Peaks']['benefice'] += round((art.prix - art.article.prixAchat )* art.qty ,2)
                    print('   ',Activite['3Peaks']['totalBarResto'])


                # On compte toute les ardoises :
                if art.moyenPaiement.name == "Ardoise" :
                    Activite[art.responsable.name]['ardoise'] += round(art.prix * art.qty ,2)
                    Activite['3Peaks']['ardoise'] += round(art.prix * art.qty ,2)
                    
                
                # On TOTALISE toute les achat réalisés sur la page cashless !
                if art.article.page.name in pagePeaksu :
                    Activite['3Peaks']['totalCashless'] += round(art.prix * art.qty ,2)

                # Total Cash/CB sensé etre en caisse :
                if art.moyenPaiement :
                    if art.moyenPaiement.name == "Cash/CB" :
                        Activite['3Peaks']['Cash/CB'] += round(art.prix * art.qty ,2)
                    if art.moyenPaiement.name == "PeakSu Cadeau" :
                        Activite['3Peaks']['gratuit'] += round(art.prix * art.qty ,2)



        # calcul des horaires :
        # for responsable in Activite :
            # if responsable != '3Peaks' :
                # responsableDb = Membres.objects.get(name=responsable)
                # Activite[responsable]['fin'] = ArticlesVendusJourDb.filter(responsable=responsableDb).aggregate(Max('dateTps'))['dateTps__max'].time()
                # Activite[responsable]['debut'] = ArticlesVendusJourDb.filter(responsable=responsableDb).aggregate(Min('dateTps'))['dateTps__min'].time()


        # inscription en dB :
        for responsable in Activite :
            if responsable != '3Peaks' :
                responsableDb = Membres.objects.get(name=responsable)

                rARdB, created = rapportBar.objects.get_or_create(responsable=responsableDb ,pos=pos ,date=jour, recup=False)
                rARdB.totalBarResto = Activite[responsable]['totalBarResto']
                rARdB.benefice = Activite[responsable]['benefice']
                rARdB.ardoise = Activite[responsable]['ardoise']

                rARdB.save()

            else :
               responsableDb = Membres.objects.get(name=responsable)

               rARdB, created = rapportBar.objects.get_or_create(responsable=responsableDb ,pos=pos ,date=jour, recup=False)
               rARdB.totalBarResto = Activite[responsable]['totalBarResto']
               rARdB.benefice = Activite[responsable]['benefice']
               rARdB.ardoise = Activite[responsable]['ardoise']
               rARdB.gratuit = Activite[responsable]['gratuit']

               rARdB.totalCashless = Activite[responsable]['totalCashless']
               rARdB.totalCashCB = Activite[responsable]['Cash/CB']

               rARdB.save() 

        return Activite





'''
BLOCKCHAIN
'''
def transactionBlockChain(depuis, vers, total):

    # pour simulation : 
    return {'statut': 1}



def CreateWallet():
    # pour simulation :
    return str(uuid.uuid4())



def balance(wallet):
    rep = api_blockchain.getaddressbalances(wallet)
    # t = json.dumps(rep[0])
    try:
        print('RETOUR BALANCE BLOCKCHAIN :',rep[0])
        return (rep[0]['qty'])
    except Exception as e:
        print('RETOUR BALANCE BLOCKCHAIN VIDE ')
        return(0)
    


def membreMasterouPas(tagId):
    listeMaster = []
    for carte in tagIdCardMaitresse.objects.all() :
        if carte.CarteCashless :
            listeMaster.append(carte.CarteCashless.tagId)

    if tagId in listeMaster :
        return(True)
    else :
        return(False)


@api_view(['POST','GET'])
def PostGetCashlessName(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        IdCardMaitresse = data['tagIdCardMaitresse']

        try:
            CarteCashlessDb = CarteCashless.objects.get(tagId = IdCardMaitresse)
            try:
                CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDb)
                PosDb = CarteMaitresseDb.pos

                data = {'cashlessName':PosDb.name, 'responsableName':CarteCashlessDb.membre.name}
                print("PostGetCashlessName : ",data)
                return JsonResponse(data, safe=False)
            except Exception as e:
                data = {'cashlessName':False, 'responsableName':False}
                return JsonResponse(data, safe=False)

        except Exception as e:
            print("PostGetCashlessName : ",e)
            return HttpResponseNotFound("You didn't say the magic word !")
    else :
        return HttpResponseNotFound("You didn't say the magic word !")

@api_view(['POST','GET'])
def PostGetArticles(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        IdCardMaitresse = data['tagIdCardMaitresse']

        try:
            CarteCashlessDb = CarteCashless.objects.get(tagId = IdCardMaitresse)
            try:
                CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDb)
                PosDb = CarteMaitresseDb.pos
                queryset = PosDb.articles.all().order_by('poidListe')

                serializer = ArticlesSerializer(queryset, many=True)
                return JsonResponse(serializer.data, safe=False)
            except Exception as e:
                data = {}
                return JsonResponse(data, safe=False)

        except Exception as e:
            print("PostGetArticles : ",e)
            return HttpResponseNotFound("You didn't say the magic word !")
    else :
        return HttpResponseNotFound("You didn't say the magic word !")



@api_view(['POST','GET'])
def PostGetIdCard(request):


    if request.method == 'POST':
        print(request.user)
        data = JSONParser().parse(request)
        print(data)
        POS = data['POS']
        tagId = data['tagId']

        try:
            carte, created = CarteCashless.objects.get_or_create(tagId=tagId)
        except Exception as e:
            return HttpResponseNotFound("Carte n'existe pas ou ne peux pas être crée")

        try:
            assert data['rpg']
            carte.rpg = True
            carte.save()
        except Exception as e:
            pass

        if created or not carte.wallet:
            newWallet = CreateWallet()
            print("!!!!!!!!!!!!!! newWallet",newWallet)
            carte.wallet = newWallet
            carte.save()


        if len(tagIdCardMaitresse.objects.filter(CarteCashless=carte)) > 0 :
            BoissonCoutantDb, created = BoissonCoutant.objects.get_or_create(CarteCashless=carte)
            if BoissonCoutantDb.date != datetime.now().date() :
                BoissonCoutantDb.nbrBoisson = 0
                BoissonCoutantDb.date = datetime.now().date()
                BoissonCoutantDb.save()

        serializer = CarteCashlessSerializer(carte)
        # modification du serializer pour ajouter les PeakSu Cadeau :
        serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data ['peaksuCadeau']
        # import ipdb; ipdb.set_trace()
        print("OUT PostGetIdCard dataCarte : ", JSONRenderer().render(serializer.data))
        return JsonResponse(serializer.data)
        
    else :
        return HttpResponseNotFound("You didn't say the magic word !")



# Pour du cash only :
@api_view(['POST','GET'])
def PostPayCashOnly(request):

    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)
        tagIdCartePOST = data['POS']
        total = float(data['total'])
        articles = data['articles']

        CarteCashlessDb = CarteCashless.objects.get(tagId = tagIdCartePOST)
        CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDb)
        
        responsable = CarteCashlessDb.membre
        pointOfSaleDb = CarteMaitresseDb.pos

        ListArticles = []
        for article in articles :
            ListArticles.append(str(articles[article])+str(article))
            articleDB =  Articles.objects.get(name=article)
            prix = articleDB.prix

            if articleDB.name == "Rtr Cons Cash" :
                total += -float(prix * articles[article] ) 

                Art = ArticlesVendus.objects.create(
                    article=articleDB, 
                    prix= -(prix), 
                    qty=int(articles[article]), 
                    pos=pointOfSaleDb, 
                    membre=None, 
                    carte=None,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiement.objects.get(name='Cash/CB'))

            else :

                Art = ArticlesVendus.objects.create(
                    article=articleDB, 
                    prix=prix, 
                    qty=int(articles[article]), 
                    pos=pointOfSaleDb, 
                    membre=None, 
                    carte=None,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiement.objects.get(name='Cash/CB'))

        return JsonResponse(data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


def gestionPeaksuArticle(carte, total, CarteCashlessDbMaitresse, articles, pos, cash, requestUser) :
    responsable = CarteCashlessDbMaitresse.membre
    
    peaksuCadeau = carte.peaksuCadeau
    peaksuVrai = carte.peaksu

    Cadeau = 0
    if peaksuCadeau > 0 :
        if peaksuCadeau >= float(total) :
            carte.peaksuCadeau += -float(total)
            Cadeau = float(total)    
        if peaksuCadeau < float(total) :
            Cadeau = peaksuCadeau  
            carte.peaksu += -( float(total) - peaksuCadeau )
            carte.peaksuCadeau += -peaksuCadeau
            # Cadeau = float(total) - peaksuCadeau     
    
        ArticlesVendus.objects.create(
            article=Articles.objects.get(name='GRATUIT'), 
            prix=round(float(Cadeau),2), 
            qty=-1, 
            pos=pos, 
            membre=carte.membre, 
            carte=carte,
            responsable=responsable,
            BoitierUser=requestUser,
            moyenPaiement=moyenPaiement.objects.get(name='PeakSu Cadeau'))
    
    else :
        carte.peaksu += -float(total) 

    carte.save()

    if carte.membre :
        adherant = carte.membre
    else :
        adherant = None

    # on fait comme si le cash avait acheté de nouveaux peaksu :
    if cash :
        try:
            PeaksuX = Articles.objects.get(name="PeakSu +x")
        except Exception as e:
            PeaksuX, created = Articles.objects.get_or_create(name="PeakSu +x", prix=1, page=PageArticle.objects.get(name='PeakSu'))

        ArticlesVendus.objects.create(
                article=PeaksuX, 
                prix=1, 
                qty=cash, 
                pos=pos, 
                membre=adherant, 
                carte=carte,
                responsable=responsable,
                BoitierUser=requestUser,
                moyenPaiement=moyenPaiement.objects.get(name='Cash/CB'))




    ListArticles = []
    for article in articles :
        ListArticles.append(str(articles[article])+str(article))
        articleDB =  Articles.objects.get(name=article)
        prix = articleDB.prix
        qty = articles[article]


        if len(tagIdCardMaitresse.objects.filter(CarteCashless=carte)) > 0 :
            if articleDB.name != "GRATUIT" :
                BoissonCoutantDb, created = BoissonCoutant.objects.get_or_create(CarteCashless=carte)
                if BoissonCoutantDb.date != datetime.now().date() :
                    BoissonCoutantDb.nbrBoisson = 0
                    BoissonCoutantDb.date = datetime.now().date()
                    BoissonCoutantDb.save()

                if BoissonCoutantDb.nbrBoisson < 4 :
                    prix = articleDB.prixAchat
                    for x in range(0,int(qty)) :
                        print('BoissonCoutantDb.nbrBoisson ',BoissonCoutantDb.nbrBoisson)
                        if BoissonCoutantDb.nbrBoisson == 4 :
                            print('BoissonCoutantDb.nbrBoisson BREAK')
                            break
                        BoissonCoutantDb.nbrBoisson += 1

                    BoissonCoutantDb.save()




        Art = ArticlesVendus.objects.create(
            article=articleDB, 
            prix=prix, 
            qty=int(qty), 
            pos=pos, 
            membre=adherant, 
            carte=carte,
            responsable=responsable,
            BoitierUser=requestUser,
            moyenPaiement=moyenPaiement.objects.get(name='PeakSu'))

    return True


#Lorsqu'il n'y a pas assez de peaksu sur la carte, le reste est payé en liquide.
@api_view(['POST','GET'])
def PostPayCardAndCash(request):
    # print('PostPayCardAndCash')

    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)

        cardIdMaitresse = data['cardIdMaitresse']
        CarteCashlessDbadherantId = data['tagId']
        total = float(data['total'])
        articles = data['articles']

        print("CarteCashlessDbadherantId data['tagId'] !!!!!!!!!!!!!!!!!!!!!!!!!!!!!",CarteCashlessDbadherantId)

        CarteCashlessDbadherant = CarteCashless.objects.get(tagId = CarteCashlessDbadherantId)
        
        print('CarteCashlessDbadherant',CarteCashlessDbadherant)
        peaksu = float(CarteCashlessDbadherant.peaksu)
        peaksuCadeau = float(CarteCashlessDbadherant.peaksuCadeau)

        totalCash = total - peaksu - peaksuCadeau
        totalPeaksu = total - totalCash

        print('totalCash :',totalCash)
        print('totalPeaksu :',totalPeaksu)

        CarteCashlessDbMaitresse = CarteCashless.objects.get(tagId = cardIdMaitresse)
        CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDbMaitresse)
        
        responsable = CarteCashlessDbMaitresse.membre
        pointOfSaleDb = CarteMaitresseDb.pos


        '''
        transaction BlockChain :
        '''
        BC_CarteVersPos = transactionBlockChain(CarteCashlessDbadherant.wallet, pointOfSaleDb.wallet, float(totalPeaksu) )
        if BC_CarteVersPos['statut'] == 1 :
            print('BC_CarteVersPos OK')

            result = gestionPeaksuArticle(CarteCashlessDbadherant, totalPeaksu, CarteCashlessDbMaitresse, articles, pointOfSaleDb, totalCash, request.user)


            serializer = CarteCashlessSerializer(CarteCashlessDbadherant)
            serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data ['peaksuCadeau']

            print("OUT PostAddCard dataCarte : ", JSONRenderer().render(serializer.data))
            return JsonResponse(serializer.data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")



# Paiement par carte cashless uniquement :
@api_view(['POST','GET'])
def PaimentCashlessBarResto(request):

    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)

        cardIdMaitresse = data['cardIdMaitresse']
        total = float(data['total'])
        articles = data['articles']

        CarteCashlessDbadherant = CarteCashless.objects.get(tagId = data['tagId'])
        peaksu = CarteCashlessDbadherant.peaksu


        CarteCashlessDbMaitresse = CarteCashless.objects.get(tagId = cardIdMaitresse)
        CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDbMaitresse)
        
        responsable = CarteCashlessDbMaitresse.membre
        pointOfSaleDb = CarteMaitresseDb.pos

        # if membreMasterouPas(CarteCashlessDbadherant.tagId) :
        #     total = ( total / 2 )

        # transaction BlockChain 
        # TODO: Gerer les peaksuCadeau
        blockchainResult = transactionBlockChain(CarteCashlessDbadherant.wallet, pointOfSaleDb.wallet, float(total))
        if blockchainResult['statut'] == 1 :

            result = gestionPeaksuArticle(CarteCashlessDbadherant, total, CarteCashlessDbMaitresse, articles, pointOfSaleDb, False, request.user)

            # Gestion pour deuxieme carte 
            try:
                data_seconde_carte = data['data_seconde_carte']
                secondeCarte = CarteCashless.objects.get(tagId=data_seconde_carte['tagId'])

                # transaction BC seconde carte :
                blockchainResult = transactionBlockChain(secondeCarte.wallet, pointOfSaleDb.wallet, int(data['total_seconde_carte']))
                
                if blockchainResult['statut'] == 1 :
                    
                    artVide = []
                    result = gestionPeaksuArticle(secondeCarte, data['total_seconde_carte'], CarteCashlessDbMaitresse, artVide, pointOfSaleDb, False, request.user)

                    print("secondeCarte : ",secondeCarte)
                    
                    # else :
                        # raise('ERREUR blockchainResult sur secondeCarte !!!! SOMME DIFFERENTE')

            except Exception as e:
                print(e)
                print('Pas de Seconde Carte')
                pass





        serializer = CarteCashlessSerializer(CarteCashlessDbadherant)
        serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data ['peaksuCadeau']

        print("OUT dataCarte : ", JSONRenderer().render(serializer.data))
        return JsonResponse(serializer.data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


# Ajout des Peaksu :
@api_view(['POST','GET'])
def AjoutPeaksu(request):

    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)

        cardIdMaitresse = data['cardIdMaitresse']
        total = float(data['total'])
        articles = data['articles']

        CarteCashlessDbadherant = CarteCashless.objects.get(tagId = data['tagId'])
        peaksu = CarteCashlessDbadherant.peaksu

        CarteCashlessDbMaitresse = CarteCashless.objects.get(tagId = cardIdMaitresse)
        CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDbMaitresse)
        
        responsable = CarteCashlessDbMaitresse.membre
        pointOfSaleDb = CarteMaitresseDb.pos

        moyenPaiementPeakSu = moyenPaiement.objects.get(name='PeakSu')
        moyenPaiementCashCb = moyenPaiement.objects.get(name='Cash/CB')
        moyenPaiementCadeau = moyenPaiement.objects.get(name='Cadeau')

        TotalCash = float(0)
        TotalPeaksuBanqueCentraleVersCarte = float(0)
        TotalPeaksuPosVersCarte = float(0)
        TotalAdhesion = float(0)
        TotalAdhesionLZE = float(0)
        TotalCadeau = float(0)

        ViderCarte = False

        ListArticles = []
        for article in articles :
            ListArticles.append(str(articles[article])+str(article))

            articleDB =  Articles.objects.get(name=article)
            prix = articleDB.prix
            qty = articles[article]

            if CarteCashlessDbadherant.membre :
                adherant = CarteCashlessDbadherant.membre
            else :
                adherant = None



            # Scenario I : Ajout de Peasku :
            if "PeakSu" in articleDB.name :
                print("articleDB.name : Peasku")
                TotalPeaksuBanqueCentraleVersCarte += float( (prix * articles[article] ) )
                
                ArticlesVendus.objects.create(
                    article=articleDB, 
                    prix=prix, 
                    qty=float(qty), 
                    pos=pointOfSaleDb, 
                    membre=adherant, 
                    carte=CarteCashlessDbadherant,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiementCashCb)

            # Scenario II : Retour Consigne en Cash :
            if articleDB.name == "Rtr Cons Cash" :
                # voir dans PostPayCashOnly !
                pass



            # Scenario III : Retour Consigne vers Carte CL :
            if articleDB.name == "Rtr Cons Carte" :
                print("articleDB.name : Rtr Cons Carte")
                TotalPeaksuPosVersCarte += float( (prix * articles[article] ) )
                Rtr, created = Articles.objects.get_or_create(name='Retour Consigne Carte', page=PageArticle.objects.get(name='Bar'))

                ArticlesVendus.objects.create(
                    article= Rtr, 
                    prix= -prix, 
                    qty=float(qty), 
                    pos=pointOfSaleDb, 
                    membre=adherant, 
                    carte=CarteCashlessDbadherant,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiementPeakSu)


            # Scenario IV : Erreur de Bar vers Carte CL :
            if articleDB.name == "Erreur" :
                print("articleDB.name : Erreur")
                TotalPeaksuPosVersCarte += float( (prix * articles[article] ) )
                Erreur, created = Articles.objects.get_or_create(name='Error', page=PageArticle.objects.get(name='Bar'))

                ArticlesVendus.objects.create(
                    article= Erreur, 
                    prix= -prix, 
                    qty=float(qty), 
                    pos=pointOfSaleDb, 
                    membre=adherant, 
                    carte=CarteCashlessDbadherant,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiementPeakSu)

            # Scenario IV : Vider Carte Cash de Bar vers Carte CL :
            if articleDB.name == "VIDER CARTE" :
                print("articleDB.name : VIDER CARTE")
                ViderCarte = True



            # Scenario V : Adhésion ! :
            if articleDB.name == "Adhésion" :
                print("articleDB.name : Adhésion")
                TotalAdhesion += float( (prix * qty ) )

                ArticlesVendus.objects.create(
                    article=articleDB, 
                    prix=prix, 
                    qty=float(qty), 
                    pos=pointOfSaleDb, 
                    membre=adherant, 
                    carte=CarteCashlessDbadherant,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiementCashCb)

            # Scenario VI : PeakSu Cadeau ! :
            if "Cadeau" in articleDB.name :
                print("articleDB.name : Cadeau")
                TotalCadeau += float( (prix * qty ) )

                ArticlesVendus.objects.create(
                    article=articleDB, 
                    prix=prix, 
                    qty=float(qty), 
                    pos=pointOfSaleDb, 
                    membre=adherant, 
                    carte=CarteCashlessDbadherant,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=moyenPaiementCadeau)



        if TotalPeaksuBanqueCentraleVersCarte > 0 :
            blockchainResultBanqueCentrale = transactionBlockChain("banqueCentrale", CarteCashlessDbadherant.wallet, TotalPeaksuBanqueCentraleVersCarte)
            if blockchainResultBanqueCentrale['statut'] == 1 :
                CarteCashlessDbadherant.peaksu += TotalPeaksuBanqueCentraleVersCarte
                CarteCashlessDbadherant.save()


        if TotalPeaksuPosVersCarte > 0 :
            blockchainResultPos = transactionBlockChain(pointOfSaleDb.wallet, CarteCashlessDbadherant.wallet, float(TotalPeaksuPosVersCarte))
            if blockchainResultPos['statut'] == 1 :
                CarteCashlessDbadherant.peaksu += TotalPeaksuPosVersCarte
                CarteCashlessDbadherant.save()


        if TotalCadeau > 0 :
            if CarteCashlessDbadherant.peaksu < 0 and CarteCashlessDbadherant.peaksu <= -(TotalCadeau) :
                CarteCashlessDbadherant.peaksu += TotalCadeau
            elif CarteCashlessDbadherant.peaksu < 0 :
                CarteCashlessDbadherant.peaksuCadeau += TotalCadeau + CarteCashlessDbadherant.peaksu
                CarteCashlessDbadherant.peaksu = 0
            else :
                CarteCashlessDbadherant.peaksuCadeau += TotalCadeau
            
            CarteCashlessDbadherant.save()
            
        if ViderCarte :
            print('VIDER CARTE !!!')

            CaisseRenduRetourCashDb = pointOfSale.objects.get(name='CaisseRenduRetourCash')
            PeaksuAVider = CarteCashlessDbadherant.peaksu

            blockchainResultViderCarteVersPos = transactionBlockChain(CarteCashlessDbadherant.wallet, pointOfSaleDb.wallet, float(PeaksuAVider) )

            if blockchainResultViderCarteVersPos['statut'] == 1 :
                CarteCashlessDbadherant.peaksu = 0
                CarteCashlessDbadherant.peaksuCadeau = 0
                CarteCashlessDbadherant.save()
                
                time.sleep(0.1)
                blockchainResultViderPosVersRendu = transactionBlockChain(pointOfSaleDb.wallet, CaisseRenduRetourCashDb.wallet, float(PeaksuAVider))
                if blockchainResultViderPosVersRendu['statut'] == 1 :
                    TotalCash += - PeaksuAVider

                    ArticlesVendus.objects.create(
                        article=Articles.objects.get(name='VIDER CARTE'), 
                        prix=-float(PeaksuAVider), 
                        qty=1, 
                        pos=pointOfSaleDb, 
                        membre=adherant, 
                        carte=CarteCashlessDbadherant,
                        responsable=responsable,
                        BoitierUser=request.user,
                        moyenPaiement=moyenPaiementCashCb)


        if TotalAdhesion > 0 :
            if CarteCashlessDbadherant.membre :
                adherant = CarteCashlessDbadherant.membre
                adherant.dateDerniereCotisation = datetime.now().date()

                if adherant.dateInscription :
                    pass
                else :
                    adherant.dateInscription = datetime.now().date()


                adherant.cotisation = TotalAdhesion
                # pointOfSaleDb.peaksu += TotalAdhesion

                if TotalAdhesion >= 15 :
                    mActif, created = StatusMembres.objects.get_or_create(name="A2")
                    adherant.Status = mActif
                else :
                    mLoisir, created = StatusMembres.objects.get_or_create(name="L")
                    adherant.Status = mLoisir

                adherant.save()






        serializer = CarteCashlessSerializer(CarteCashlessDbadherant)
        serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data ['peaksuCadeau']

        print("OUT PostAddCard dataCarte : ", JSONRenderer().render(serializer.data))
        return JsonResponse(serializer.data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


#Derniere Action
@api_view(['POST','GET'])
def derniereAction(request):

    if request.method == 'POST':

        dernierArticle = ArticlesVendus.objects.order_by('-pk')[0]
        dernierArticles = ArticlesVendus.objects.filter(dateTps__gte = dernierArticle.dateTps.replace(microsecond=0), 
            dateTps__lte = dernierArticle.dateTps.replace(microsecond=999999),
            responsable = dernierArticle.responsable,
            pos=dernierArticle.pos)

        fauxPeaksu = 0
        peaksuARembourser = 0
        cashARembourser = 0
        ardoiseARembourser = 0
        peaksuCadeauARembourser = 0
        moyenDePaiement = []
        articlesVdus = []
        pkArticlesVdus = []
        pkCarte = []
        nomCarte = []

        for art in dernierArticles :
            if art.article.name == "PeakSu +x" and art.moyenPaiement.name == "Cash/CB" :
                fauxPeaksu += art.qty
                cashARembourser += art.qty
                pkArticlesVdus.append(art.pk)
            elif "PeakSu" in art.article.name :
                cashARembourser += art.qty * art.prix
                articlesVdus.append(str(art.qty)+'x'+art.article.name)
                pkArticlesVdus.append(art.pk)
                peaksuARembourser += -(art.qty * art.prix)
            elif art.article.name == "VIDER CARTE" :
                peaksuARembourser += -(art.qty * art.prix)
                articlesVdus.append(str(art.qty)+'x'+art.article.name)
                pkArticlesVdus.append(art.pk)
            elif art.moyenPaiement.name == "PeakSu" :
                peaksuARembourser += art.qty * art.prix
                articlesVdus.append(str(art.qty)+'x'+art.article.name)
                pkArticlesVdus.append(art.pk)
            elif art.moyenPaiement.name == "Cash/CB" :
                cashARembourser += art.qty * art.prix
                articlesVdus.append(str(art.qty)+'x'+art.article.name)
                pkArticlesVdus.append(art.pk)
            elif art.moyenPaiement.name == "Ardoise" :
                ardoiseARembourser += art.qty * art.prix
                articlesVdus.append(str(art.qty)+'x'+art.article.name)
                pkArticlesVdus.append(art.pk)
            elif art.moyenPaiement.name == "Cadeau" :
                peaksuCadeauARembourser += -(art.qty * art.prix)
                articlesVdus.append(str(art.qty)+'x'+art.article.name)
                pkArticlesVdus.append(art.pk)

            if art.carte :
                pkCarte.append(art.carte.pk) if art.carte.pk not in pkCarte else pkCarte
                if art.carte.membre :
                    if art.carte.membre.name not in nomCarte :
                        nomCarte.append(art.carte.membre.name)



        if fauxPeaksu > 0 :   
            peaksuARembourser += -fauxPeaksu

        dictRetour = {
            'pkCarte' : pkCarte,
            'nomCarte' : nomCarte,
            'articlesVdus':articlesVdus,
            'pkArticlesVdus' : pkArticlesVdus,
            'fauxPeaksu' : fauxPeaksu,
            'peaksuARembourser' : peaksuARembourser,
            'cashARembourser' : cashARembourser,
            'ardoiseARembourser' : ardoiseARembourser,
            'peaksuCadeauARembourser' : peaksuCadeauARembourser,
            'moyenDePaiement' : moyenDePaiement,
        }
        print(dictRetour)

        return JsonResponse(dictRetour)

        # art.delete()

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


@api_view(['POST','GET'])
def deleteDerniereAction(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)

        if len(data['pkCarte']) > 0 :
            CarteCashlessDb = CarteCashless.objects.get(pk=int(data['pkCarte'][0]))

            if data['peaksuARembourser'] != 0 :
                CarteCashlessDb.peaksu += data['peaksuARembourser']

            if data['ardoiseARembourser'] != 0 :
                CarteCashlessDb.peaksu += data['ardoiseARembourser']
            
            if data['peaksuCadeauARembourser'] != 0 :
                CarteCashlessDb.peaksuCadeau += data['peaksuCadeauARembourser']
            
            CarteCashlessDb.save()

        for pkArt in data['pkArticlesVdus'] :
            artVendus = ArticlesVendus.objects.get(pk=int(pkArt))
            artVendus.prix = 0
            artVendus.qty = 0
            artVendus.save()

        return JsonResponse(data)
    
    else :
        return HttpResponseNotFound("You didn't say the magic word !")


# rapportbar:
@api_view(['POST','GET'])
def PostRapportBarToday(request):
    print('request PostRapportBar')
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            cardIdMaitresse = data['cardIdMaitresse']
            CarteCashlessDbMaitresse = CarteCashless.objects.get(tagId = cardIdMaitresse)
            CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDbMaitresse)
            pointOfSaleDb = CarteMaitresseDb.pos
        except Exception as e:
            pointOfSaleDb = pointOfSale.objects.get(name="Bar3PeaksQuotidientCashLess")

        calculRapportBar(datetime.now().date(), pointOfSaleDb)

        Aujourdhui, created = rapportBar.objects.get_or_create(date=datetime.now().date(),responsable=Membres.objects.get(name='3Peaks'),recup=False,pos=pointOfSaleDb)

        Data = {}
        Data['CAISSE1J'] = str(Aujourdhui.totalBarResto)
        Data['BENEF'] = str(Aujourdhui.benefice)

        return JsonResponse(Data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


@api_view(['POST','GET'])
def reportsArticleVendus(request) :
    print('request reportsArticleVendus')
    if request.method == 'POST':


        def calculTotalArticle(date) :
            print(date)
            ArticlesVendusJourDb = ArticlesVendus.objects.filter(dateTps__date=date, pos=pos)
            rapportArticlesVenduDb = rapportArticlesVendu.objects.filter(date=date)
            
            for x in rapportArticlesVenduDb :
                x.delete()


            for article in ArticlesVendusJourDb :
                print(article.article.name)
                rap, created = rapportArticlesVendu.objects.get_or_create(date=date, article=article.article)
                rap.qty += int(article.qty)
                rap.save()



        pos = pointOfSale.objects.get(name="Bar3PeaksQuotidientCashLess")
        jour =  datetime.now().date()
        veille =  datetime.now().date() - timedelta(days=1)

        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()

        calculTotalArticle(jour)
        calculTotalArticle(veille)

        Data = {"reportsArticleVendus":"OK"}
        return JsonResponse(Data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")



@api_view(['POST','GET'])
def addEmailToMailchimp(request) :
    print('request addEmailToMailchimp')
    if request.method == 'POST':
        for membre in Membres.objects.filter(dateAjout__gte=(datetime.now() - timedelta(days = 2))) :
            if membre.email :
                try:
                    FNAME = ' '.join(membre.name.split(' ')[1:])
                    LNAME = membre.name.split(' ')[0]
                except Exception as e:
                    FNAME = ""
                    LNAME = membre.name

                print(FNAME)
                print(LNAME)

                try:
                    mailchimpClient.lists.members.create('d07fd1d681', {
                        'email_address': membre.email,
                        'status': 'subscribed',
                        'merge_fields': {
                            'FNAME': FNAME,
                            'LNAME': LNAME,
                        },
                    })
                    pass
                except Exception as e:
                    print(e)


        Data = {"addEmailToMailchimp":"OK"}
        return JsonResponse(Data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


@api_view(['POST','GET'])
def PostRapportBar(request):
    print('request PostRapportBar')
    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)

        try:
            cardIdMaitresse = data['cardIdMaitresse']
            CarteCashlessDbMaitresse = CarteCashless.objects.get(tagId = cardIdMaitresse)
            CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDbMaitresse)
            pointOfSaleDb = CarteMaitresseDb.pos
        except Exception as e:
            pointOfSaleDb = pointOfSale.objects.get(name="Bar3PeaksQuotidientCashLess")

        peaks = Membres.objects.get(name='3Peaks')
        Jours_Recup = rapportBar.objects.filter(recup=True, responsable=peaks)

        if Jours_Recup :
            Jour_Recup = Jours_Recup.latest('date')
        else :
            Jour_Recup = rapportBar.objects.filter(responsable=peaks).earliest('date')
    
        start_date = Jour_Recup.date
        end_date = datetime.now().date()

        def daterange(start_date, end_date):
            for n in range(int ((end_date - start_date).days)+1):
                yield start_date + timedelta(n)

        for jour in daterange(start_date, end_date):
            print(jour)
            calculRapportBar(jour, pointOfSaleDb)

        Aujourdhui, created = rapportBar.objects.get_or_create(date=datetime.now().date(),responsable=peaks,recup=False,pos=pointOfSaleDb)

        CAISSETOTAL = 0
        for jour in daterange(start_date, end_date):
            try:
                CAISSETOTAL += rapportBar.objects.get(date=jour,responsable=peaks,recup=False).totalCashCB
                print('Total :',jour)
            except Exception as e:
                pass

        Data = {}
        Data['CAISSE1J'] = str(Aujourdhui.totalBarResto)
        Data['CAISSETOTAL'] = str(CAISSETOTAL)
        Data['DerniereDate'] = str(Jour_Recup.date)

        return JsonResponse(Data)
    
    else :
        return HttpResponseNotFound("You didn't say the magic word !")


# on note la caisse :
@api_view(['POST','GET'])
def PostCompteCaisse(request):
    print('request PostCompteCaisse')
    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(float(data['inputCaisse']))
        
        peaks = Membres.objects.get(name='3Peaks')
        rapportBarToday = rapportBar.objects.get(date=datetime.now().date(),responsable=peaks,recup=False)
        rapportBarToday.caisse = float(data['inputCaisse'])
        rapportBarToday.recup = True
        rapportBarToday.save()

        ArtVendus = ArticlesVendus.objects.filter(comptabilise=False)
        for x in ArtVendus :
            x.comptabilise = True
            x.save()

        Data = {'OK':'OK'}
        return JsonResponse(Data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")



# Pour l'ardoise démoniaque:
@api_view(['POST','GET'])
def PostArdoiseDemoniaque(request):

    if request.method == 'POST':
        data = JSONParser().parse(request)
        print(data)

        cardIdMaitresse = data['cardIdMaitresse']
        total = float(data['total'])
        articles = data['articles']

        CarteCashlessDbadherant = CarteCashless.objects.get(tagId = data['tagId'])
        peaksu = CarteCashlessDbadherant.peaksu


        CarteCashlessDbMaitresse = CarteCashless.objects.get(tagId = cardIdMaitresse)
        CarteMaitresseDb = tagIdCardMaitresse.objects.get(CarteCashless=CarteCashlessDbMaitresse)
        
        responsable = CarteCashlessDbMaitresse.membre
        pointOfSaleDb = CarteMaitresseDb.pos

        # TODO : Gerer sur la blockcahin l'ardoise

        blockchainResult = transactionBlockChain(CarteCashlessDbadherant.wallet, pointOfSaleDb.wallet, float(total))
        if blockchainResult['statut'] == 1 :
            
            carte = CarteCashlessDbadherant
            peaksuCadeau = carte.peaksuCadeau
            if peaksuCadeau > 0 :
                if peaksuCadeau >= float(total) :
                    carte.peaksuCadeau += -float(total)
                    # Cadeau = float(total)    
                if peaksuCadeau < float(total) :
                    # Cadeau = peaksuCadeau  
                    carte.peaksu += -( float(total) - peaksuCadeau )
                    carte.peaksuCadeau = 0
                    # Cadeau = float(total) - peaksuCadeau     
            else :
                carte.peaksu += -float(total) 
                
            # CarteCashlessDbadherant.peaksu += -float(total) 
            carte.save()


            ListArticles = []
            for article in articles :
                ListArticles.append(str(articles[article])+str(article))
                articleDB =  Articles.objects.get(name=article)
                prix = articleDB.prix
                qty = articles[article]

                if CarteCashlessDbadherant.membre :
                    adherant = CarteCashlessDbadherant.membre
                else :
                    adherant = None

                if len(tagIdCardMaitresse.objects.filter(CarteCashless=CarteCashlessDbadherant)) > 0 :
                    if articleDB.name != "GRATUIT" :
                        BoissonCoutantDb, created = BoissonCoutant.objects.get_or_create(CarteCashless=CarteCashlessDbadherant)
                        if BoissonCoutantDb.date != datetime.now().date() :
                            BoissonCoutantDb.nbrBoisson = 0
                            BoissonCoutantDb.date = datetime.now().date()
                            BoissonCoutantDb.save()

                        if BoissonCoutantDb.nbrBoisson < 4 :
                            prix = articleDB.prixAchat
                            for x in range(0,int(qty)) :
                                print('BoissonCoutantDb.nbrBoisson ',BoissonCoutantDb.nbrBoisson)
                                if BoissonCoutantDb.nbrBoisson == 4 :
                                    print('BoissonCoutantDb.nbrBoisson BREAK')
                                    break
                                BoissonCoutantDb.nbrBoisson += 1
                            BoissonCoutantDb.save()

                Ardoise, Created = moyenPaiement.objects.get_or_create(name='Ardoise')
                Art = ArticlesVendus.objects.create(
                    article=articleDB, 
                    prix=prix, 
                    qty=int(qty), 
                    pos=pointOfSaleDb, 
                    membre=adherant, 
                    carte=CarteCashlessDbadherant,
                    responsable=responsable,
                    BoitierUser=request.user,
                    moyenPaiement=Ardoise)


        serializer = CarteCashlessSerializer(CarteCashlessDbadherant)
        serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data ['peaksuCadeau']

        print("OUT dataCarte : ", JSONRenderer().render(serializer.data))
        return JsonResponse(serializer.data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


@api_view(['POST','GET'])
def PostViderCard(request):
    if request.method == 'POST':

        data = JSONParser().parse(request)
        POS = data['POS']
        tagId = data['tagId']
        total = data['total']

        tagIdCarteMaitresseDb = tagIdCardMaitresse.objects.get(tagIdCarte=POS)
        pointOfSaleDb = tagIdCarteMaitresseDb.pos
        print("pointOfSaleDb.cash avant : ",pointOfSaleDb.cash)

        carte = CarteCashless.objects.get(tagId=tagId)
        if carte.peaksu > 0 :

            blockchainResultViderCarte = transactionBlockChain(carte.wallet, pointOfSaleDb.wallet, carte.peaksu)
            if blockchainResultViderCarte['statut'] == 1 :
                carte.peaksu = 0
                carte.peaksuCadeau = 0
                carte.save()

            serializer = CarteCashlessSerializer(carte)
            serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data['peaksuCadeau']

            print("OUT dataCarte : ", JSONRenderer().render(serializer.data))
            return JsonResponse(serializer.data)

        else :
            carte.peaksu = 0
            carte.peaksuCadeau = 0
            carte.save()

            serializer = CarteCashlessSerializer(carte)
            serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data['peaksuCadeau']
            print("OUT dataCarte : ", JSONRenderer().render(serializer.data))
            return JsonResponse(serializer.data)
    else :
        return HttpResponseNotFound("You didn't say the magic word !")




@api_view(['POST','GET'])
def PostNewNumero(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        print("PostNewNumero : ",data)
        tagId = data['tagId']
        number = data['number']

        carte = CarteCashless.objects.get(tagId=tagId)
        carte.number = number
        carte.save()

        serializer = CarteCashlessSerializer(carte)
        serializer._data['peaksu'] = serializer.data['peaksu'] + serializer.data ['peaksuCadeau']
        
        print("OUT PostNewNumero dataCarte: ", JSONRenderer().render(serializer.data))
        return JsonResponse(serializer.data)

    else :
        return HttpResponseNotFound("You didn't say the magic word !")


