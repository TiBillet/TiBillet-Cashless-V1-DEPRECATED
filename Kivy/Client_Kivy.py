#! /usr/bin/env python
# -*- coding: utf-8 -*-

import kivy

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, DictProperty
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from functools import partial
import requests
from requests.auth import HTTPBasicAuth
import json
import time
import nfc
import re
import os
import random
import traceback

from collections import OrderedDict

import textwrap

''' LOGGING '''
import logging
from logging.handlers import RotatingFileHandler
# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger()
# on met le niveau du logger à DEBUG, comme ça il écrit tout
logger.setLevel(logging.DEBUG)

# création d'un formateur qui va ajouter le temps, le niveau
# de chaque message quand on écrira un message dans le log
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
# création d'un handler qui va rediriger une écriture du log vers
# un fichier en mode 'append', avec 1 backup et une taille max de 1Mo
file_handler = RotatingFileHandler('activity.log', 'a', 1000000, 1)
# on lui met le niveau sur DEBUG, on lui dit qu'il doit utiliser le formateur
# créé précédement et on ajoute ce handler au logger
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


''' SENTRY :
try:
    import sentry_sdk
    sentry_sdk.init("")
except Exception as e:
    logger.error("import sentry_sdk failed. : "+ str(e))
    logger.error(str(traceback.format_exc()))
'''


'''CREDENTIALS'''
import configClient
username = configClient.username
password = configClient.password

import sys
try:
    ipServeur = sys.argv[1]
except Exception as e:
    ipServeur = configClient.ipServeur

'''nfc reader init'''
clf = nfc.ContactlessFrontend()

rowNum = 0

from kivy.core.window import Window
# Window.size = (480, 800)


os.environ['TZ'] = 'Indian/Reunion'
time.tzset()
print(time.asctime())

class ButtonUX_BAR1(FloatLayout):


    '''
    Construction du long Click :
    '''

    def create_clock(self, widget, touch, *args):
        print('create_clock')
        callback = partial(self.menu, touch)
        Clock.schedule_once(callback, 3)
        touch.ud['event'] = callback

    def delete_clock(self, widget, touch, *args):
        try:
            print('delete_clock')
            Clock.unschedule(touch.ud['event'])
        except Exception as e:
            pass




    def menu(self, touch, *args):
        # import ipdb; ipdb.set_trace()
        if self.popupValider_carteClRouge :
            self.popupValider_carteClRouge.dismiss()
            print('ON LANCE LE MENU ARMAGEDDON !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            
            self.layoutArdoiseViolette = GridLayout(
                    cols=2,
                )

            self.layoutArdoiseVioletteArdoise = Button(
                text = "ARDOISE\nDEMONIAQUE\nQUI ENGLOUTIRA\nL'ASSO")
            self.layoutArdoiseVioletteArdoise.bind(on_press=self.Valider_Panier_Ardoise_Demoniaque)
            self.layoutArdoiseViolette.add_widget(self.layoutArdoiseVioletteArdoise)    
            
            self.layoutArdoiseVioletteCash = Button(text = "PARDON !\nJE PAYE !")
            self.layoutArdoiseVioletteCash.bind(on_press=self.BtnlayoutArdoiseVioletteCash)
            self.layoutArdoiseViolette.add_widget(self.layoutArdoiseVioletteCash)  


            self.popuplayoutArdoiseViolette = Popup(title="ARMAGEDDON D'ASSUMPTA",
                content=self.layoutArdoiseViolette,
                size_hint=(0.7, 0.25), 
                background_color= (0.5,0,0.5,.5),
                auto_dismiss=False)

            self.popuplayoutArdoiseViolette.open()



    def close_menu(self, widget, *args):
        self.remove_widget(widget)

    '''
    FIN Construction du long Click :
    '''

    def build(self):

        # FOND D'ECRAN :
        self.backimg = Image(source='bkgimg2.jpg',
            norm_image=True)
        self.add_widget(self.backimg)

        logger.info("Lancement de Glob")

        class Glob(EventDispatcher):
            total = NumericProperty(0)
            Peaksu = NumericProperty(0)
            cardchecked = BooleanProperty(False)
            aPayer = BooleanProperty(False)
            reste = NumericProperty(0)
            SecondeCarte = BooleanProperty(False)
            PremiereCarteData = DictProperty()
            PeaksuSecondeCarte = NumericProperty(0)
            SecondeCarteData = DictProperty()
            items = DictProperty()
            membre = ObjectProperty(None, allownone=True)
            carteMaitresse = ObjectProperty(None, allownone=True)
            pointCashless = BooleanProperty(False)
            pointCashlessName = ObjectProperty(None, allownone=True)
            responsableName = ObjectProperty(None, allownone=True)
            ApiServeurVersCarte = ObjectProperty("/PaimentCashlessBarResto/", allownone=False)
            Ardoise = BooleanProperty(False)
            CalculCaisse = DictProperty()
            derniereActionData = DictProperty()
            
        # se declenche des que le InputCaisse change :
        def CalculCaisse_Callback(instance, value):
            print('self.panier.CalculCaisse callback is call from', instance)
            print('and the self.panier.CalculCaisse value changed to', value)
            
            try:
                self.textLayoutCaisseTopJour.text = value['CAISSE1J'].encode('utf8')+"€"
                self.textLayoutCaisseTopTotal.text = value['BENEF'].encode('utf8')+"€"
                # self.textLayoutCaisseDerniereDate.text = value['DerniereDate'].encode('utf8')
            except Exception as e:
                print(e)
                self.textLayoutCaisseTopJour.text = "666 666€"
                self.textLayoutCaisseTopTotal.text = "666 666€"
                # self.textLayoutCaisseDerniereDate.text = "Mathusalem"

            # self.panier.CalculCaisse = value

        # se declenche des que le total change :
        def total_callback(instance, value):
            print('self.panier.total callback is call from', instance)
            print('and the self.panier.total value changed to', value)
    
            if self.panier.pointCashless :
                self.Valider_carte.text = "VALIDER\nTotal : "+str(value)+"€"
            else :
                self.Valider_Cash.text = "VALIDER\nESPECE/CB\nTotal : "+str(value)+"€"
                self.Valider_carte.text = "VALIDER\n CARTE\nTotal : "+str(value)+"€"


        # se declanche lorsque la page cashless est ouverture
        # Permet de lancer la requete vers l'api serveur correspondant aux point Peaksu
        def pointCashless_callback(instance, value):
            print('pointCashless_callback is call from', instance)
            print('and the a value changed to', value)
            if value :
                self.panier.ApiServeurVersCarte = "/AjoutPeaksu/"
            else :
                self.panier.ApiServeurVersCarte = "/PaimentCashlessBarResto/"


        def pointCashlessName_callback(instance, value):
            print('pointCashlessName_callback : ',value)
            if value == "Bar3PeaksQuotidientCashLess" :
                self.backimg.source="bckGrndImgPeaks.jpg"



        self.panier = Glob()
        self.panier.bind(total=total_callback)
        self.panier.bind(pointCashless=pointCashless_callback)
        self.panier.bind(CalculCaisse=CalculCaisse_Callback)
        self.panier.bind(pointCashlessName=pointCashlessName_callback)


        '''
        Construction des layouts principaux :
        '''

        self.LayoutBut_page1 = GridLayout(
                cols=3,
                size_hint=(1,0.7),
                orientation='vertical',
                pos_hint={'x':0, 'y':0.2},
            )

        self.LayoutBut_page2 = GridLayout(
                cols=1,
                size_hint=(0.3,1),
                orientation='vertical',
                pos_hint={'x':0, 'y':0},
            )

        self.LayoutBut_page3 = GridLayout(
                cols=1,
                size_hint=(0.3,1),
                orientation='vertical',
                pos_hint={'x':0, 'y':0},
            )

        self.Footer = FloatLayout()

        self.add_widget(self.LayoutBut_page1)
        self.add_widget(self.Footer)


        '''
        Construction des layouts liste article :
        '''


        self.LayoutQtt = StackLayout(
                # cols=1,
                # row=len(articles),
                size_hint=(0.2,1),
                orientation='tb-lr',
                pos_hint={'x':0.4, 'y':0},
                # spacing=1,
                # padding=20
            )

        self.LayoutArt = StackLayout(
                # cols=1,
                # row=len(articles),

                size_hint=(0.2,1),
                orientation='tb-lr',
                pos_hint={'x':0.6, 'y':0},
                # spacing=1,
                # padding=20
            )

        self.LayoutPrx = StackLayout(
                # cols=1,
                # row=len(articles),
                size_hint=(0.2,1),
                orientation='tb-lr',
                pos_hint={'x':0.8, 'y':0},
                # spacing=1,
                # padding=20
            )

        self.add_widget(self.LayoutQtt)
        self.add_widget(self.LayoutArt)
        self.add_widget(self.LayoutPrx)
 


        
        '''
        construction du popup NFC
        '''
        self.NFCpopup = Popup(title='Attente de carte',
            content=Label(text='Posez la carte sur le lecteur NFC'),
            size_hint=(0.8, 0.8), size=(300, 200))
        self.NFCpopup.bind(on_open=self.nfcConnectFunc)



        '''
        construction du popup d'ouverture pour carte maitresse 
        '''

        self.popupMaitresse = Popup(title='Attente de Carte MAÎTRESSE',
            content=Label(text='Posez la carte MAÎTRESSE sur le lecteur NFC'),
            size_hint=(0.8, 0.8), size=(350, 200),
            auto_dismiss=False)
        self.popupMaitresse.bind(on_open=self.maitresseConnectFunc)


        '''
        Contruction du popup de demande de numéro pour input a la main
        '''

        self.layoutGetNumber = FloatLayout()
        self.layoutNumberBot = GridLayout(
                cols=2,
                # row=len(articles),
                size_hint=(1,0.15),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0},
                # spacing=1,
                # padding=20
            )

        self.cancelNumberButton = Button(text = "ANNULER")
        self.cancelNumberButton.bind(on_press=self.cancelNumberButtonDimiss)
        
        self.validerNumberButton = Button(text = "VALIDER")
        self.validerNumberButton.bind(on_press=self.requestServerNewNumero)
        
        self.layoutNumberBot.add_widget(self.cancelNumberButton)    
        self.layoutNumberBot.add_widget(self.validerNumberButton)    

        self.layoutGetNumber.add_widget(self.layoutNumberBot)       

        self.layoutGetNumberTop = GridLayout(
                cols=1,
                # row=len(articles),
                size_hint=(1,0.8),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0.2},
                # spacing=1,
                # padding=20
            )

        self.first_row_layoutNumberTop = StackLayout()

        self.Numbertextinput = TextInput(size_hint_y= .3,font_size='60sp',multiline=False)

        self.first_row_layoutNumberTop.add_widget(self.Numbertextinput)   

        self.LabelNumber = Label(
            text="CARTE VIERGE\nENTREZ LE NUMERO INSCRIT AU DOS", 
            )

        self.first_row_layoutNumberTop.add_widget(self.LabelNumber)

        self.layoutGetNumberTop.add_widget(self.first_row_layoutNumberTop)       

        self.layoutGetNumber.add_widget(self.layoutGetNumberTop)

        self.popupGetNumber = Popup(title='Carte VIERGE',
            content=self.layoutGetNumber,
            size_hint=(0.8, 0.8), size=(350, 200),
            auto_dismiss=False)
        
        # On instancie la fonction lorsque la touche entrée est appuyé dans l'input
        Window.bind(on_key_down=self._on_keyboard_down)

        '''
        Contruction du popup d'erreur reseau ou systeme
        '''

        popupErreurTop = GridLayout(
                cols=1,
                row=2,
                # pos_hint={'x':0, 'y':0.2},
                )

        popupErreurTop.add_widget(Label(text="Une erreur est survenue.\nMerci de réessayer !\nSi ça foire toujours, prévenez l'administrateur !"))

        self.messageError = Label(text="")
        popupErreurTop.add_widget(self.messageError)
        
        self.popupErreur = Popup(title='Erreur Systeme',
            content=popupErreurTop,
            size_hint=(0.8, 0.8), size=(300, 200))

        self.popupErreur.bind(on_dismiss=self.resetFunc)


        '''
        Contruction du popup de demande de page à afficher si la carte maitresse peut ajouter des peaksu
        '''

        self.layoutPageCashless = GridLayout(
                cols=2,
            )

        self.layoutPageCashlessVente = Button(text = "BAR & RESTO")
        self.layoutPageCashlessVente.bind(on_press=self.BtnlayoutPageCashlessVente_vers_Vente)
        self.layoutPageCashless.add_widget(self.layoutPageCashlessVente)    
        
        self.layoutPageCashlessPeaksu = Button(text = "PEAKSU")
        self.layoutPageCashlessPeaksu.bind(on_press=self.BtnlayoutPageCashlessVente_vers_Peaksu)
        self.layoutPageCashless.add_widget(self.layoutPageCashlessPeaksu)  


        # self.layoutPageCashlessCaisse = Button(text = "CAISSE")
        # self.layoutPageCashlessCaisse.bind(on_press=self.BtnlayoutPageCashlessCaisse_fin_Journee)
        # self.layoutPageCashless.add_widget(self.layoutPageCashlessCaisse)  

        self.popuplayoutPageCashless = Popup(title='CHOIX P.Vente',
            content=self.layoutPageCashless,
            size_hint=(0.7, 0.45), 
            # size=(350, 200),
            auto_dismiss=False)



        self.popupMaitresse.open()



    '''
    Première action du soft :
    Lancement de la popup de demande de carte maitresse qui retournera aussi la liste des articles
    '''

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if self.Numbertextinput.focus and keycode == 40:  # 40 - Enter key pressed
            self.requestServerNewNumero(self)
            print("ENTER")


    def maitresseConnectFunc(self,instance):
        global IDMAITRESSE
        print("MAITRESSE CONNECT")
        self.listArticlesDjango = False
        self.panier.cardIdMaitresse = ""

        # Le serveur renvoie la liste des articles correspondant à la carte maitresse
        while not self.listArticlesDjango :
            clf.open('usb')

            tag = clf.connect(rdwr={'on-connect': lambda tag: False})
            self.panier.cardIdMaitresse = str(tag).replace("Type2Tag ID=","")
            print("CARDID MAITRESSE : ",self.panier.cardIdMaitresse)

            clf.close()

            self.listArticlesDjango = self.requestArticle()
            if self.listArticlesDjango :
                PostGetCashlessNameJson = self.requestpointCashlessName()
                print("PostGetCashlessNameJson ; ",PostGetCashlessNameJson)
                self.panier.pointCashlessName = PostGetCashlessNameJson['cashlessName']
                
                try:
                    self.panier.responsableName = PostGetCashlessNameJson['responsableName']
                    self.popuplayoutPageCashless.title = str(self.panier.pointCashlessName.encode('utf-8'))+" - "+str(self.panier.responsableName.encode('utf-8'))
                except Exception as e:
                    self.panier.responsableName = "Inconnu"
                    self.popuplayoutPageCashless.title = str(self.panier.pointCashlessName.encode('utf-8'))+" - "+str(self.panier.responsableName.encode('utf-8'))
                    pass
                print("FUNC maitresseConnectFunc - self.listArticlesDjango : ",self.listArticlesDjango)
            else :
                time.sleep(1)


        if self.listArticlesDjango :
            
            # par default, le point de vente ne permet pas de rajouter des peaksu sur la carte 
            self.panier.pointCashless = False

            # on instencie les articles affichés :
            self.articles = OrderedDict()
            self.articlesPage = OrderedDict()

            for art in self.listArticlesDjango :
                # si page == 2, la carte maitresse permet de rajouter du cashless :
                if art['page_name'] == u'PeakSu' : 
                    print('self.panier.pointCashless = True')
                    self.panier.pointCashless = True

                self.articles[art['name'].encode('utf-8')] = art['prix']
                self.articlesPage[art['name'].encode('utf-8')] = art['page_name'].encode('utf-8')

            # on a la liste des articles, on envoie la création des boutons

            # si la carte permet le rajout de peaksu, on pose la question de quels articles afficher :
            if self.panier.pointCashless :
                self.popuplayoutPageCashless.open()
                self.popupMaitresse.dismiss()


            else :

                self.panier.pointCashless = False
                self.BoutonsArticles()
                self.popupMaitresse.dismiss()


    # on trie les articles pour n'avoir que des articles de bar / resto
    def BtnlayoutPageCashlessVente_vers_Vente(self,instance):
        self.panier.pointCashless = False

        ArticlesVentes = OrderedDict()
        ArticlesVentesPages = OrderedDict()
        for art in self.articles :
            if self.articlesPage[art] != 'PeakSu' and self.articlesPage[art] != 'PeakSu2':
                ArticlesVentes[art] = self.articles[art]
                ArticlesVentesPages[art] = self.articlesPage[art]

        self.articles = ArticlesVentes
        self.articlesPage = ArticlesVentesPages
        print(len(self.articles))
        print(self.articles)

        self.BoutonsArticles()
        self.popuplayoutPageCashless.dismiss()

        pass


    # on trie les articles pour n'avoir que des articles de point cashless peaksu
    def BtnlayoutPageCashlessVente_vers_Peaksu(self,instance):
        self.panier.pointCashless = True
        ArticlesVentes = OrderedDict()
        ArticlesVentesPages = OrderedDict()
        for art in self.articles :
            if self.articlesPage[art] == 'PeakSu' or self.articlesPage[art] == 'PeakSu2' :
                ArticlesVentes[art] = self.articles[art]
                ArticlesVentesPages[art] = self.articlesPage[art]
                
        self.articles = ArticlesVentes
        self.articlesPage = ArticlesVentesPages
        print(len(self.articles))
        print(self.articles)

        self.BoutonsArticles()
        self.popuplayoutPageCashless.dismiss()

        pass



    # les couleurs a la mano !
    def changeColor(self,instance):
        instance.background_color = (0, 0.5, 0.5, 1)

    def returnColorRouge(self,instance):
        instance.background_color = (255,0,0,0.5)

    def returnColorBleu(self,instance):
        instance.background_color = (0,0,255,0.5)

    def returnColorVert(self,instance):
        instance.background_color = (255,0,0,0.5)


    # creation de tout les boutons articles et validations
    def BoutonsArticles(self):

        # Vide la page1 au cas ou :
        self.LayoutBut_page1.clear_widgets()
        self.LayoutBut_page2.clear_widgets()
        self.LayoutBut_page3.clear_widgets()

        # Creation du tableau liste des articles :
        # self.LayoutQtt.add_widget(Label(text='[b]Quantités[/b]', markup=True, size_hint=(None, 0.20)))
        # self.LayoutArt.add_widget(Label(text="[b]Articles[/b]", markup=True, size_hint=(None, 0.20)))
        # self.LayoutPrx.add_widget(Label(text="[b]S-Total[/b]", markup=True, size_hint=(None, 0.20)))







        '''
        Creation des boutons page par page :
        Au click : self.AddArticle
        '''
        # btnNext = True
        for article in self.articles:
            # bar
            if self.articlesPage[article] == 'Bar' :
                print(article)
                but = Button(font_size='20sp')
                but.text = article+"\n"+str(self.articles[article])+"€"
                but.id = article
                but.bind(on_press=self.AddArticle)
                self.LayoutBut_page1.add_widget(but)

            # resto
            elif self.articlesPage[article] == 'Resto' :
                print(article)
                but = Button(background_color=(0.97,0.95,0.49,0.8), font_size='20sp')
                but.text = article+"\n"+str(self.articles[article])+"€"
                but.id = article
                but.bind(on_press=self.AddArticle)
                self.LayoutBut_page1.add_widget(but)

            # peaksu
            elif self.articlesPage[article] == 'PeakSu' :
                # btnNext = False
                print(article)

                if 'Cadeau' in article :
                    but = Button(background_color=(0.5,0,0.5,0.5),font_size='20sp')
                else :
                    but = Button(font_size='20sp')
                    pass
                
                if article == "VIDER CARTE" :
                    but.text = article
                else :
                    but.text = article+"\n"+str(self.articles[article])+"€"
                but.id = article
                but.bind(on_press=self.AddArticle)
                self.LayoutBut_page1.add_widget(but)

            elif self.articlesPage[article] == 'PeakSu2' :
                # btnNext = False
                print(article)
                
                if 'Cadeau' in article :
                    but = Button(background_color=(0.5,0,0.5,0.5),font_size='20sp')
                else :
                    but = Button(font_size='20sp')
                    pass

                if article == "VIDER CARTE" :
                    but.text = article
                else :
                    but.text = article+"\n"+str(self.articles[article])+"€"

                but.id = article
                but.bind(on_press=self.AddArticle)
                self.LayoutBut_page1.add_widget(but)

        '''
        Creation du bouton page suivante :
        Au click : self.nextPage
        '''
        self.pageSuivante = Button(
            size_hint=(.2, .05),
            pos_hint={'x':.4, 'y':0.93},
            )

        self.pageSuivante.text = "PAGE 2 >"
        self.pageSuivante.id = "nextpage"
        self.pageSuivante.bind(on_press=self.nextPage)
        # if btnNext :
            # self.Footer.add_widget(self.pageSuivante)


        '''
        Creation des boutons resets par page
        Au click : self.resetFunc
        '''

        self.resetBut = Button(background_color=(255,0,0,0.5),font_size='20sp')
        self.resetBut.text = "RESET"
        self.resetBut.id = "resetId"
        self.resetBut.bind(on_press=self.resetFunc)
        self.resetBut.bind(
            on_press=self.changeColor,
            on_release=self.returnColorRouge,
            )

        self.LayoutBut_page1.add_widget(self.resetBut)


        # self.resetBut2 = Button(background_color=(255,0,0,0.5),font_size='20sp')
        # self.resetBut2.text = "RESET"
        # self.resetBut2.id = "resetId"
        # self.resetBut2.bind(on_press=self.resetFunc)

        # self.LayoutBut_page2.add_widget(self.resetBut2)


        # self.resetBut3 = Button(background_color=(255,0,0,0.5),font_size='20sp')
        # self.resetBut3.text = "RESET"
        # self.resetBut3.id = "resetId"
        # self.resetBut3.bind(on_press=self.resetFunc)

        # self.LayoutBut_page3.add_widget(self.resetBut3)

        '''
        Creation du bouton Annul Derniere Action :
        Uniquement sur page PeakSu
        '''

        if self.panier.pointCashless :
            self.annulBut = Button(background_color=(255,0,0,0.5),font_size='20sp')
            self.annulBut.text = "ANULLER\nDERNIERE ACTION"
            self.annulBut.id = "annulBut"
            self.annulBut.bind(on_press=self.annulFunc)
            self.annulBut.bind(
                on_press=self.changeColor,
                on_release=self.returnColorRouge,
                )

            self.LayoutBut_page1.add_widget(self.annulBut)

        '''
        Creation du bouton flotant CHECK CARTE :
        Au click : self.CheckCarteBtn
        '''
        self.Check_Card = Button(
                size_hint=(.3, .15),
                font_size='23sp',
                background_color=(0,0,255,0.5),
                pos_hint={'x':.02, 'y':0.04})
        self.Check_Card.text = "CHECK CARTE"
        self.Check_Card.id = "CheckCard"
        self.Check_Card.bind(on_press=self.CheckCarteBtn)
        self.Check_Card.bind(
            on_press=self.changeColor,
            on_release=self.returnColorBleu,
            )

        self.Footer.add_widget(self.Check_Card)

        '''
        Creation du bouton flotant VALIDER ESPECE ou CB :
        Au Click : self.ValiderPanier_cash_Only
        '''

        self.Valider_Cash = Button(
                size_hint=(.3, .15),
                font_size='23sp',
                background_color=(0,0,255,0.5),
                pos_hint={'x':.35, 'y':0.04})

        self.Valider_Cash.text = "VALIDER\nESPECE/CB\nTotal : "+str(self.panier.total)+"€"
        self.Valider_Cash.id = "validerBut"
        self.Valider_Cash.bind(on_press=self.popup_Btn_cash_only_Valider)
        self.Valider_Cash.bind(
            on_press=self.changeColor,
            on_release=self.returnColorBleu,
            )

        if 'PeakSu' not in self.articlesPage[article] :
            self.Footer.add_widget(self.Valider_Cash)



        '''
        Creation du bouton flotant VALIDER CARTE CASHLESS :
        Au Click : self.ValiderPanier_carte
        '''

        self.Valider_carte = Button(background_color=(0,0,255,0.5),
                size_hint=(.3, .15),
                font_size='23sp',
                pos_hint={'x':.68, 'y':0.04})
        
        if self.panier.pointCashless :
            self.Valider_carte.text = "VALIDER\nTotal : "+str(self.panier.total)+"€"
        else :
            self.Valider_carte.text = "VALIDER\n CARTE\nTotal : "+str(self.panier.total)+"€"

        self.Valider_carte.id = "validerCarteCL"
        self.Valider_carte.bind(on_press=self.Valider_carte_Btn)
        self.Valider_carte.bind(
            on_press=self.changeColor,
            on_release=self.returnColorBleu,
            )
        self.Footer.add_widget(self.Valider_carte)


        '''
        Creation du label flotant texte d'indication du responsable:
        '''

        self.Footer.add_widget(Label(text='Responsable : [b]'+str(self.panier.responsableName.encode('utf-8'))+' [/b]', 
            markup=True, 
            size_hint=(None, 0.04),
            pos_hint={'x':.45, 'y':0}
            ))


        '''
        construction horloge
        '''
        Clocktext = Label(text=str(time.strftime('%H:%M')), 
            markup=True, 
            font_size='45sp',
            size_hint=(None, 0.05),
            pos_hint={'x':.1, 'y':0.93}
            )

        def updateClock(self, *args):
            Clocktext.text = str(time.strftime('%H:%M'))

        # self.crudeclock = IncrediblyCrudeClock()
        Clock.schedule_interval(updateClock, 60)


        self.Footer.add_widget(Clocktext)


        '''
        Creation du bouton flotant EXIT :
        Au Click : self.resetFunc
        '''

        self.deco = Button(
            size_hint=(.15, .05),
            pos_hint={'x':.85, 'y':0.93},
            background_color=(255,0,0,0.5)
            )

        self.deco.text = "EXIT"
        self.deco.id = "DECO"
        self.deco.bind(on_press=self.resetFunc)
        self.deco.bind(
            on_press=self.changeColor,
            on_release=self.returnColorRouge,
            )
        self.Footer.add_widget(self.deco)


    # fonction pour savoir quel est le nom du point de vente
    def requestpointCashlessName(self):
        data = {}
        data['tagIdCardMaitresse'] = self.panier.cardIdMaitresse

        try:
            logger.debug("requestpointCashlessName")

            r = requests.post(ipServeur+'/PostGetCashlessName/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=10)


            if r.status_code == 200 :
                logger.debug("requestpointCashlessName JSON : "+str(r.json()))
                PostGetCashlessNameJson = r.json()
                if PostGetCashlessNameJson['cashlessName'] :
                    print("PostGetCashlessNameJson :",PostGetCashlessNameJson)
                    return PostGetCashlessNameJson
                else :
                    return False

            else :
                logger.error("requestpointCashlessName failed."+ str(r))

        except Exception as e:
            logger.error("requestpointCashlessName failed : "+ str(e))
            logger.error(str(traceback.format_exc()))
            return False


    # Fonction de requete pour la demande d'article liés a la carte Maitresse :
    def requestArticle(self):

        # ipServeur = "https://cashless3peaks.gdna.eu" 
        # 'D9512143'
        data = {}
        data['tagIdCardMaitresse'] = self.panier.cardIdMaitresse

        try:
            r = requests.post(ipServeur+'/PostGetArticles/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=10)
            
            # logger.debug("requestArticle JSON : "+str(r.json()))

            if r.status_code == 200 :
                listArticles = r.json()
                if len(listArticles) > 0 :
                    return listArticles
                else :
                    print('Carte non maitresse !')
                    return False
            else :
                logger.error("requestArticle failed.  response : "+ str(r))
                return False
            
        except Exception as e:
            logger.error("requestArticle failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))
            return False

    '''
    Fonction appelée lors du clic sur la page suivante
    '''
    def nextPage(self,instance):
        if self.LayoutBut_page1 in self.children :
            self.remove_widget(self.LayoutBut_page1)
            self.add_widget(self.LayoutBut_page2)
            # if not self.Valider_carte in self.Footer.children :
                # self.Footer.add_widget(self.Valider_carte)
            self.pageSuivante.text = "PAGE 1 >"

        elif self.LayoutBut_page2 in self.children :
            self.remove_widget(self.LayoutBut_page2)
            self.add_widget(self.LayoutBut_page1)
            # if self.Valider_carte in self.Footer.children :
                # self.Footer.remove_widget(self.Valider_carte)
            self.pageSuivante.text = "PAGE 2 >"

        # elif self.LayoutBut_page3 in self.children :
        #     self.remove_widget(self.LayoutBut_page3)
        #     self.add_widget(self.LayoutBut_page1)
        #     if not self.Valider_carte in self.Footer.children :
        #         self.Footer.add_widget(self.Valider_carte)
        #     self.pageSuivante.text = "RESTO >"


    '''
    GESTION DU CHECK CART 
    '''

    # fonction appellée lors du click sur CHECK CARTE
    # ls NFCpopup lance self.nfcConnectFunc a l'ouverture
    def CheckCarteBtn(self,instance):
        self.panier.aPayer = False
        self.panier.cardchecked = False

        print("Check Carte !")
        print("self.panier.cardchecked : ",self.panier.cardchecked)

        self.NFCpopup.content=Label(text='Posez la carte sur le lecteur NFC')
        self.NFCpopup.open()

    # Ouverture du lecteur NFC.
    # Si scan reussit, il lance self.requestServerCheck(carteData)
    def nfcConnectFunc(self,instance):
        print("NFC CONNECT")
        
        clf.open('usb')

        if self.panier.SecondeCarte :
            premiere_cardID = self.panier.PremiereCarteData['tagId']
            seconde_cardID = self.panier.PremiereCarteData['tagId']
            print('premiere_cardID :', premiere_cardID)
            while premiere_cardID == seconde_cardID :
                print('seconde_cardID :', seconde_cardID)
                tag = clf.connect(rdwr={'on-connect': lambda tag: False})
                seconde_cardID = str(tag).replace("Type2Tag ID=","")   
                cardID = seconde_cardID  
        else :
            tag = clf.connect(rdwr={'on-connect': lambda tag: False})
            cardID = str(tag).replace("Type2Tag ID=","")
            

        print(str(tag))
        print(str(cardID))

        # print(self.panier.Peaksu)
        clf.close()

        # return cardID

        if cardID :
            # self.NFCpopup.content=Label(text='Carte OK\nCheck Serveur\nMerci de patienter\n \n \nClickez ailleurs pour annuler')
            carteData = {}
            carteData['tagId'] = cardID
            self.requestServerCheck(carteData)


    # Requete principale automatiquemeent lancée apres l'ouverture de la popupNFC et en cas de carte ID.
    def requestServerCheck(self, CarteData):
        print("requestServerCheck", CarteData)

        data = {}
        data['tagId'] = CarteData['tagId']
        data['POS'] = self.panier.cardIdMaitresse


        try:
            # print('on lance la requete requests.post('+ipServeur+'/PostGetIdCard/')
            logger.debug('on lance la requete requests.post('+ipServeur+'/PostGetIdCard/')

            r = requests.post(ipServeur+'/PostGetIdCard/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=60)

            logger.debug("requestServerCheck JSON : "+str(r.json()))

            if r.status_code != 200 :
                logger.error("requestServerCheck failed. response : "+ str(r))
                self.messageError.text = textwrap.fill(str(r),60)
                self.popupErreur.open()
            else :
                print(r)
                print(r.json())
                carteJson = r.json()
                print("carteJson['number'] : ",carteJson['number'])
                
                
                # Si la carte est vierge, on lance la demande de renseignement pour le numéro
                # Attention, risque de bug sur raspberry tactile, mieux vaut annuller et faire depuis un PC standard.
                if not carteJson['number'] :
                    self.popupGetNumber.open()


                if self.panier.SecondeCarte :
                    self.panier.SecondeCarteData = r.json()
                    self.panier.PeaksuSecondeCarte = self.panier.SecondeCarteData['peaksu']
                    self.panier.Secondecardchecked = True
                else :
                    self.panier.PremiereCarteData = r.json()
                    self.panier.Peaksu = self.panier.PremiereCarteData['peaksu']
                    self.panier.cardchecked = True
                
                self.NFCpopup.dismiss()
                
                if carteJson['number'] :
                    print("requestServerCheck(self, CarteData) carteJson['number']", carteJson['number'])

                    
                    '''
                    SI FONCTION APPELLEE DEPUIS LE BOUTON VALIDATION CARTE CASHLESS :
                    '''
                    print("self.panier.aPayer : ",self.panier.aPayer )
                    if self.panier.aPayer :
                        print("Pour paiement !")
                        if self.panier.SecondeCarte :
                            print("on test le paiement avec deux cartes !")
                            self.ValiderPanier_seconde_carte_checked()
                        else :
                            print("on test le paiement avec une seul carte !")
                            self.ValiderPanier_carte_checked()
                    
                        '''
                        SI FONCTION APPELLEE DEPUIS LE BOUTON CHECK CARTE :
                        '''
                    else :
                        print("pas pour paiement !")
                        self.PopupCheckInfoShow()

                else :
                    print('PAS DE NUMERO')

                # import ipdb; ipdb.set_trace()

        except Exception as e :
            logger.error("requestServerCheck failed. : "+ str(e))
            logger.error("requestServerCheck failed. : "+ str(traceback.format_exc()))

            self.messageError.text = textwrap.fill(str(e),60)
            self.NFCpopup.dismiss()
            self.popupErreur.open()

            # import ipdb; ipdb.set_trace()
            # if "Max retries exceeded with url" in str(e) :
                # print("Max retries exceeded with url , requestServerCheck : ",e)
                # self.popup.content=Label(text='MaxRetryError\nProblème de connection Serveur\nContacter un administrateur systeme\n (Jonas ou Christophe par exemple...)')




    # Creation et ouverture du popup CHECK CARTE INFO
    # Ouverture apres la requeteserveurCheck et si self.panier.aPayer = False
    def PopupCheckInfoShow(self):
        print("FUNC PopupCheckInfoShow - self.panier.PremiereCarteData : ",self.panier.PremiereCarteData)
        
        if self.panier.Peaksu >= 0 :
            txtInfo = "SUR CARTE"
            mutation = ""
        else :
            txtInfo = "ARDOISE"
            mutation = "MUTATION :\n"+random.choice(list(open('mutations'))).decode('utf-8').rstrip()

        self.popupCheckInfoLabel = Label(text=str(
            self.panier.PremiereCarteData['membreName'].encode('utf-8'))+
            "\n"+str(self.panier.PremiereCarteData['membreCotisationAJour']).encode('utf-8')+
            "\n"+txtInfo+" : "+str(self.panier.Peaksu)+" €\n"+
            "\n"+mutation.encode('utf-8') , font_size='45sp')

        if self.panier.PremiereCarteData['membreCotisationAJour'] :
            if "PAS" in str(self.panier.PremiereCarteData['membreCotisationAJour']) :
                popupCheckInfobackground_color = (255,0,0,.5)
            else :
                popupCheckInfobackground_color = (0,255,0,.5)
        else :
            popupCheckInfobackground_color = (255,0,0,.5)


        if self.panier.Peaksu < 0 :
            popupCheckInfobackground_color = (0.5,0,0.5,.8)

        self.popupCheckInfo = Popup(title="Check Carte",
            size_hint=(1, 0.6), size=(200, 200),
            content=self.popupCheckInfoLabel,
            background_color= popupCheckInfobackground_color,
            auto_dismiss=True)

        self.popupCheckInfo.bind(on_dismiss=self.popupCheckInfoDimiss)
        self.popupCheckInfo.open()


    # RESET a la fermeture du popup
    def popupCheckInfoDimiss(self,instance):
        # self.panier.cardchecked = False
        # self.resetFunc(self)
        pass


    '''
    FUNCTION RESET
    '''
    def resetFunc(self,instance):
       
        self.panier.items = {}
        global row
        rowNum = 0

        try:
            global carteJson
            carteJson = {}
        except Exception as e:
            print('reset : pas de carteJson',e)
            pass

        # print("LEN : ",len(self.LayoutArt.children))
        while len(self.LayoutArt.children) > 1 :
            for x in self.LayoutArt.children :
                if x.text :
                    print("x LayoutArt : ",x.id)
                    if "_name" in str(x.id) :
                        self.LayoutArt.remove_widget(x)

            for x in self.LayoutQtt.children :
                if x.text :
                    print("x LayoutQtt : ",x.id)
                    if "_qtt" in str(x.id) :
                        self.LayoutQtt.remove_widget(x)

            for x in self.LayoutPrx.children :
                if x.text :
                    print("x LayoutPrx : ",x.id)
                    if "_prix" in str(x.id) :
                        self.LayoutPrx.remove_widget(x)

        self.panier.total = float(0)
        self.panier.Peaksu = float(0)
        self.panier.cardchecked = False
        self.panier.aPayer = False
        self.panier.reste = float(0)
        self.panier.SecondeCarte = False
        self.panier.PeaksuSecondeCarte = float(0)
        self.panier.Secondecardchecked = False
        self.panier.PremiereCarteData = {}
        self.panier.SecondeCarteData = {}
        self.panier.membre = None
        self.panier.Ardoise = False
        self.panier.CalculCaisse = {}
        self.messageError.text = ""

        try:
            self.Numbertextinput.text = ''
        except Exception as e:
            pass
        
        try:
            self.Valider_carte.background_color=(0,0,255,0.5)

            if self.panier.pointCashless :
                self.Valider_carte.text = "VALIDER\nTotal : "+str(self.panier.total)+"€"
            else :
                self.Valider_carte.text = "VALIDER\n CARTE\nTotal : "+str(self.panier.total)+"€"
        
            self.Valider_carte.unbind(on_press=self.AddArticle) 
            self.Valider_carte.unbind(on_press=self.Valider_carte_Btn) 
            self.Valider_carte.unbind(on_press=self.CheckCarteBtn) 
            self.Valider_carte.bind(on_press=self.Valider_carte_Btn)

            self.Valider_Cash.text = "VALIDER\nESPECE/CB\nTotal : "+str(self.panier.total)+"€"
            self.Valider_Cash.background_color=(0,0,255,0.5)

        except Exception as e:
            pass


        # if self.panier.cardIdMaitresse in CarteCashlessMaitre :
            # self.Valider_Cash.text = ""
            # self.Valider_carte.text = "AJOUTER\n"+str(self.panier.total)+"€"
            # self.Valider_Cash.unbind(on_press=self.ValiderPanier_cash_Only)
            # self.Valider_Cash.bind(on_press=self.passF)

        if self.LayoutBut_page2 in self.children :
            self.remove_widget(self.LayoutBut_page2)
            self.add_widget(self.LayoutBut_page1)
            # if self.Valider_carte in self.Footer.children :
                # self.Footer.remove_widget(self.Valider_carte)
            self.pageSuivante.text = "PAGE 2 >"


        print("RESET !")
        print(self.panier.total)
        print(self.panier.Peaksu)
        print(self.panier.cardchecked)
        print(self.panier.items)


        for butt in self.LayoutBut_page1.children :
            try:
                if self.articlesPage[butt.id] == 'Resto' :
                    butt.background_color = (0.97,0.95,0.49,0.8)
                    butt.text = butt.id+"\n"+str(self.articles[butt.id])+"€"
                elif butt.id == "resetId" :
                    self.resetBut.background_color=(255,0,0,0.5)
                else :
                    if 'Cadeau' in butt.text :
                        butt.background_color = (0.5,0,0.5,0.5)
                    else :
                        butt.background_color = (1,1,1,1)
                    butt.text = butt.id+"\n"+str(self.articles[butt.id])+"€"
                #     butt.background_color = ''
                
                # else :
                    # butt.background_color = ''
            except Exception as e:
                pass

        # if self.LayoutBut_page1 in self.children :
            # self.resetBut.background_color=(255,0,0,0.5)


        if instance.id == "DECO" :
            self.LayoutBut_page1.clear_widgets()
            self.LayoutBut_page2.clear_widgets()
            self.LayoutBut_page3.clear_widgets()
            self.LayoutQtt.clear_widgets()
            self.LayoutArt.clear_widgets()
            self.LayoutPrx.clear_widgets()
            self.Footer.clear_widgets()

            try:
                self.popupCaisse.dismiss()
            except Exception as e:
                pass

            self.popupMaitresse.open()


    '''
    FUNCTION ANULL DERNIERE ACTION
    '''
    def annulFunc(self,instance):
        def popupAnnulDimiss(instance):
            self.popupAnnul.dismiss()


        layoutAnnul = FloatLayout()

        layoutAnnulTop = GridLayout(
                cols=2,
                # row=len(articles),
                size_hint=(1,0.8),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0.2},
                # spacing=1,
                # padding=20
            )

        listItems =[]

        listItems.append(Label(text='Carte :', font_size='45sp'))
        self.CarteAnnul = Label(text='...', font_size='45sp')
        listItems.append(self.CarteAnnul)

        listItems.append(Label(text='Article :', font_size='45sp'))
        self.ArticleAnnul = Label(text='...', font_size='35sp')
        listItems.append(self.ArticleAnnul)

        listItems.append(Label(text='PeakSu :', font_size='45sp'))
        self.peaskyAnnul = Label(text='...', font_size='45sp')
        listItems.append(self.peaskyAnnul)

        listItems.append(Label(text='Cash/CB :', font_size='45sp'))
        self.cashAnnul = Label(text='...', font_size='45sp')
        listItems.append(self.cashAnnul)

        for x in listItems :
            layoutAnnulTop.add_widget(x)

        layoutAnnul.add_widget(layoutAnnulTop)



        layoutAnnulBot = GridLayout(
                cols=2,
                # row=len(articles),
                size_hint=(1,0.2),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0},
                # spacing=1,
                # padding=20
            )



        DisAnnulButton = Button(background_color=(255,0,0,0.5),font_size='20sp')
        DisAnnulButton.text = "NE PAS ANNULLER"
        DisAnnulButton.bind(
            on_press=self.changeColor,
            on_release=self.returnColorRouge,
            )    
        DisAnnulButton.bind(
            on_press=popupAnnulDimiss
            )
        layoutAnnulBot.add_widget(DisAnnulButton)
        
        ConfirmAnnulButton = Button(background_color=(0,0,255,0.5),font_size='20sp')
        ConfirmAnnulButton.text = "CONFIRMER\nANNULATION"
        ConfirmAnnulButton.bind(on_press=self.deleteDerniereAction)
        ConfirmAnnulButton.bind(
            on_press=self.changeColor,
            on_release=self.returnColorBleu,
            ) 
        # self.CashButton.bind(on_press=self.Popup_Valider_Carte_Bouton_Cash,
            # on_touch_up=self.delete_clock)
        layoutAnnulBot.add_widget(ConfirmAnnulButton)

        layoutAnnul.add_widget(layoutAnnulBot)


        self.popupAnnul = Popup(title='ANNULER DERNIERE ACTION',
                    size_hint=(1, .8),
                    content=layoutAnnul,
                    background_color=(0,0,255,.2))  
        self.popupAnnul.bind(on_open=self.requestderniereAction,
            on_dismiss=self.resetFunc)

                      #content=(Label(text='This is a demo pop-up')))
        # self.popupValider_carteClVert.bind(on_dismiss=self.resetFunc)
        self.popupAnnul.open()  


    def deleteDerniereAction(self,instance):

        data = self.panier.derniereActionData
        try:
            r = requests.post(ipServeur+'/deleteDerniereAction/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=40)

            DataR = r.json()
            logger.debug("deleteDerniereAction JSON : "+str(DataR))

            if r.status_code == 200 :
                self.popupAnnul.dismiss()
            else :
                logger.error("deleteDerniereAction failed. response: "+ str(r))
                self.popupAnnul.dismiss()
                self.messageError.text = textwrap.fill(str(r),60)
                self.popupErreur.open()

            return(r)

        except Exception as e:
            logger.error("deleteDerniereAction failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))

            self.popupAnnul.dismiss()
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()
            # TODO : RETURN PROPRE

    def requestderniereAction(self,instance):

        data = {}
        try:
            r = requests.post(ipServeur+'/derniereAction/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=40)

            logger.debug("requestderniereAction JSON : "+str(r.json()))


            if r.status_code == 200 :

                DataR = r.json()
                self.panier.derniereActionData = DataR

                print(DataR)    
                self.CarteAnnul.text = str((' ').join(DataR['nomCarte']).encode('utf8'))
                self.ArticleAnnul.text = str(('\n').join(DataR['articlesVdus']).encode('utf8'))
                self.peaskyAnnul.text = str(DataR['peaksuARembourser'] + DataR['peaksuCadeauARembourser']) 
                self.cashAnnul.text = str(DataR['cashARembourser'])
                # import ipdb; ipdb.set_trace()
                # if r.status_code == 200 :
                    # self.resetFunc(self)

                return(r)

            else :
                logger.error("requestderniereAction failed. response : "+ str(r))
                self.popupAnnul.dismiss()
                self.messageError.text = textwrap.fill(str(r),60)
                self.popupErreur.open()

        except Exception as e:
            logger.error("requestderniereAction failed : "+ str(e))
            logger.error(str(traceback.format_exc()))
            self.popupAnnul.dismiss()
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()

    '''
    GESTION AJOUT ET REMOVE DANS PANIER ITEM
    '''

    def AddArticle(self,instance):
        # global total
        try:
            self.panier.items[instance.id] += 1
            self.panier.total += float(self.articles[instance.id])
            print(self.panier.items)


            for article in self.LayoutQtt.children :
                if article.id == instance.id+"_qtt" :
                    article.text = str(self.panier.items[instance.id])

            newSTotal = float(self.panier.items[instance.id]) * self.articles[instance.id]
            
            for article in self.LayoutPrx.children :
                if article.id == instance.id+"_prix" :
                    article.text = str(newSTotal)


        except Exception as e:
            print(e)
            self.panier.items[instance.id] = 1
        
            self.panier.total += float(self.articles[instance.id])

        instance.background_color = (0,1,0,0.5)
        
        txtOriginal = re.sub(r'^\d*\ ','',instance.text)
        instance.text = str(self.panier.items[instance.id]) +" "+ txtOriginal

            # row = self.VersTable(instance.id)

            # self.LayoutQtt.add_widget(row[0])
            # self.LayoutArt.add_widget(row[1])
            # self.LayoutPrx.add_widget(row[2])
        
        pass


    def RmvArticle(self,instance):
        
        nameArt = instance.id.replace("_qtt","")
        print(nameArt)

        if nameArt == "Peaksu" or nameArt == "Cash" :
            for x in self.LayoutPrx.children :
                if x.id == instance.id.replace("_qtt","_prix") :
                    valeur = x.text
                    print("valeur :",valeur)
                    self.panier.total += -float(valeur)
                    self.LayoutPrx.remove_widget(x)


            for x in self.LayoutArt.children :
                if x.id == instance.id.replace("_qtt","_name") :
                    self.LayoutArt.remove_widget(x)

            for x in self.LayoutQtt.children :
                if x.id == instance.id :
                    self.LayoutQtt.remove_widget(x)
                    
            self.panier.items.pop(nameArt, None)


        else :
            if float(instance.text) > 1 :
                self.panier.items[nameArt] += -1
                instance.text = str(self.panier.items[nameArt])
                self.panier.total += -float(self.articles[nameArt])


                newSTotal = float(self.panier.items[nameArt]) * float(self.articles[nameArt])

                for x in self.LayoutPrx.children :
                    if x.id == instance.id.replace("_qtt","_prix") :
                        x.text = str(newSTotal)

            elif float(instance.text) == 1 :
                self.panier.items[nameArt] += -1
                self.panier.items.pop(nameArt, None)
                self.panier.total += -float(self.articles[nameArt])

                for x in self.LayoutPrx.children :
                    if x.id == instance.id.replace("_qtt","_prix") :
                        self.LayoutPrx.remove_widget(x)

                for x in self.LayoutArt.children :
                    if x.id == instance.id.replace("_qtt","_name") :
                        self.LayoutArt.remove_widget(x)

                for x in self.LayoutQtt.children :
                    if x.id == instance.id :
                        self.LayoutQtt.remove_widget(x)




    # Cancel Bouton sur popup :
    def popup_Btn_cash_only_cancel(self,instance):
        self.panier.SecondeCarte = False
        self.popupValider_cash.dismiss()
        pass

    # Valider Bouton sur popup :
    def popup_Btn_cash_only_Valider(self,instance):
        print('Valider_cash_only_valider_button')
        # self.popupValider_cash.dismiss()

        layout = StackLayout()
        layout.add_widget(Label(text="TOTAL Cash/CB : "+str(self.panier.total)+"€", font_size='45sp'))
        
        self.popupValider_Carte_Bouton_Cash = Popup(title='CASH/CB',
                    size_hint=(1, .2),
                    content=layout)
                      #content=(Label(text='This is a demo pop-up')))
        self.popupValider_Carte_Bouton_Cash.bind(on_open=self.requestServerPayCashOnly)
        self.popupValider_Carte_Bouton_Cash.bind(on_dismiss=self.resetFunc)
        self.popupValider_Carte_Bouton_Cash.open()  



    # Requete au serveur pour cash only :
    def requestServerPayCashOnly(self,instance):
        print('requestServerPayCashOnly TotalCash : ', self.panier.total)

        data={}
        data['articles'] = self.panier.items
        data['total'] = float(self.panier.total)
        data['POS'] = self.panier.cardIdMaitresse

        print('requestServerPayCashOnly data : ', data)
        print('requestServerPayCashOnly json.dumps(data) : ', json.dumps(data))

        try:
            r = requests.post(ipServeur+'/PostPayCashOnly/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=10)

            logger.debug("requestServerPayCashOnly JSON : "+ str(r.json()))

            if r.status_code != 200 :
                logger.error("requestServerPayCashOnly failed. response : "+ str(r))
                self.popupValider_Carte_Bouton_Cash.dismiss()
                self.messageError.text = textwrap.fill(str(r),60)
                self.popupErreur.open()
            else :
                return r

        except Exception as e:
            logger.error("requestServerPayCashOnly failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))
            self.popupValider_Carte_Bouton_Cash.dismiss()
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()
            # TODO : RETURN PROPRE


    '''
    GESTION PAIEMENT CARTE CASHLESS
    on lance GESTION DU CHECK CART 
    PopupNFC ->  Mais avec la variable self.panier.aPayer == True
        -> ValiderPanier_carte_checked 
    EXEPTION : Si "Rtr Cons Cash", on par sur   ValiderPanier_cash_Only     
    '''

    # Ouverture du popup NFC :
    def Valider_carte_Btn(self,instance):
        print('Valider_carte_Btn',instance.text)

        if self.panier.total > 0 :

            # Retour consigne en cash,on part sur ValiderPanier_cash_Only 
            if "Rtr Cons Cash" in self.panier.items :
                print("EXEPTION : Si Rtr Cons Cash, on par sur   ValiderPanier_cash_Only   !!!!!!!!!!")
                self.popup_Btn_cash_only_Valider(instance)

            else :
                self.panier.aPayer = True
                self.panier.SecondeCarte = False

                self.NFCpopup.content=Label(text='Posez la carte sur le lecteur NFC')
                self.NFCpopup.open()

        else :
            if 'VIDER CARTE' in self.panier.items :
                print('VIDER CARTE in self.panier.items')
                self.panier.aPayer = True
                self.panier.SecondeCarte = False

                self.NFCpopup.content=Label(text='Posez la carte A VIDER sur le lecteur NFC')
                self.NFCpopup.open()


    '''
    RE-Calcul du total 
    '''
    def reCalculTotal(self):
        self.panier.total = float(0)
        for art in self.panier.items :
            for x in self.listArticlesDjango :
                if x['name'] == art.decode('utf8') :
                    prix = float(x['prix']) 
                    break

            self.panier.total += float(prix * int(self.panier.items[art]))
    '''
    Gestion des popup ROUGE ou VERT apres PopupNFCavec la variable self.panier.aPayer == True
    '''
    def ValiderPanier_carte_checked(self):

        # reduction pour carte maitresse :
        if self.panier.PremiereCarteData["CardMaitresse"] and not self.panier.pointCashless :

            # recalcul du total si annulation :
            self.reCalculTotal()
            
            # logger.debug('reduction pour carte maitresse :'+str(self.panier.PremiereCarteData["BoissonCoutantCarteM"][0]))
            nbr = int(self.panier.PremiereCarteData["BoissonCoutantCarteM"][0])


            if nbr < 4 :
                for art in self.panier.items :
                    if art != "GRATUIT" :

                        for x in self.listArticlesDjango :
                            if x['name'] == art.decode('utf8') :
                                prixCoutant = float(x['prixAchat'])
                                prix = float(x['prix'])

                        qty = int(self.panier.items[art])

                        for x in range(0,qty):
                            print("ARTICLE COUTANT : ",art,prixCoutant)
                            self.panier.total += -prix
                            self.panier.total += prixCoutant
                            nbr += 1
                            if nbr == 4 :
                                break
                    
                    if nbr == 4 :
                        break

            # import ipdb; ipdb.set_trace()


        # calcul du reste sur carte :
        self.panier.reste = float(float(self.panier.Peaksu) - float(self.panier.total))
        # logger.debug("FUNC ValiderPanier_carte_checked - self.panier.reste : ",self.panier.reste)

        # Si ce sont des peaksu :
        

        if self.panier.reste >= 0 or self.panier.pointCashless : 
            
            # logger.debug("FUNC ValiderPanier_carte_checked - self.panier.reste >= 0 ")
            # logger.debug("FUNC ValiderPanier_carte_checked - self.panier.pointCashless : ",self.panier.pointCashless)
            
            response = self.requestServerPaimentCashless()

            # logger.debug("FUNC ValiderPanier_carte_checked - requestServerPaimentCashless - response : ",response.json())

            if response.status_code == 200 :

                jresponse = response.json()
                layoutValider = FloatLayout()

                layoutValiderTopInfoMembre = GridLayout(
                        cols=1,
                        # row=len(articles),
                        size_hint=(1,0.2),
                        # orientation='horizontal',
                        pos_hint={'x':0, 'y':0.7},
                        spacing=20,
                        # padding=20
                    )

                try:
                    membreName = str(self.panier.PremiereCarteData['membreName']).encode('utf-8')
                except Exception as e:
                    print(e)
                    try:
                        membreName = str(self.panier.PremiereCarteData['membreName'].encode('utf-8'))
                    except Exception as e:
                        print(e)
                        try:
                            membreName = str(self.panier.PremiereCarteData['membreName'])
                        except Exception as e:
                            print(e)
                            membreName = "False"

                layoutValiderTopInfoMembre.add_widget(Label(text=membreName, font_size='45sp'))
                layoutValiderTopInfoMembre.add_widget(Label(text=str(self.panier.PremiereCarteData['membreCotisationAJour']).encode('utf-8'), font_size='45sp'))

                layoutValider.add_widget(layoutValiderTopInfoMembre)


                layoutValiderTop = GridLayout(
                        cols=2,
                        # row=len(articles),
                        size_hint=(1,0.5),
                        # orientation='horizontal',
                        pos_hint={'x':0, 'y':0.1},
                        # spacing=1,
                        # padding=20
                    )

                first_column_layoutValiderTop = StackLayout()
                second_column_layoutValiderTop = StackLayout()



                listItemsFirst =[]
                listItemsSecond =[]

                listItemsFirst.append('CARTE :')
                listItemsSecond.append(str(self.panier.Peaksu)+"€")

                listItemsFirst.append('TOTAL :')
                listItemsSecond.append(str(self.panier.total)+"€")

                listItemsFirst.append('RESTE :')
                listItemsSecond.append(str(jresponse['peaksu'])+"€")

                print(listItemsFirst)
                print(listItemsSecond)

                # adonfButton = Label(text  = "Cacaboudin", font_size='30sp')
                # adonfButton2 = Label(text  = "3€", font_size='30sp')

                first_column_layoutValiderTop.add_widget(Label(text="\n".join(listItemsFirst), font_size='45sp'))

                second_column_layoutValiderTop.add_widget(Label(text="\n".join(listItemsSecond), font_size='45sp'))  

                layoutValiderTop.add_widget(first_column_layoutValiderTop)       
                layoutValiderTop.add_widget(second_column_layoutValiderTop)       


                layoutValider.add_widget(layoutValiderTop)


                self.popupValider_carteClVert = Popup(title='VALIDATION',
                            size_hint=(1, .8),
                            content=layoutValider,
                            background_color=(0,255,0,.5))  
                              #content=(Label(text='This is a demo pop-up')))
                self.popupValider_carteClVert.bind(on_dismiss=self.resetFunc)
                self.popupValider_carteClVert.open()   
            
            else :
                logger.error("ValiderPanier_carte_checked failed. response : "+ str(response))
                self.messageError.text = textwrap.fill(str(response),60)
                self.popupErreur.open()
                # layoutValiderTop.add_widget(Label(text='PROBLEME VALIDATION CARTE\nREBOOTEZ LA MACHINE\nContacter un administrateur systeme si ça continue\n (Jonas ou Christophe par exemple...)'))

                # import ipdb; ipdb.set_trace()


            print("VALIDER : ",self.panier.items)

        elif self.panier.reste < 0 :
            print('PAS ASSEZ DE PEAKSU')
            
            # layoutValider = FloatLayout(cols=1, padding=05)
                    
            self.layoutValider = FloatLayout()

            self.layoutValiderBot = GridLayout(
                    cols=3,
                    # row=len(articles),
                    size_hint=(1,0.2),
                    # orientation='horizontal',
                    pos_hint={'x':0, 'y':0},
                    # spacing=1,
                    # padding=20
                )

            self.AutreCarteButton = Button(text = "+ CARTE")
            # self.CashButton.bind(on_press=self.Popup_Valider_Carte_Bouton_AutreCarte)
            self.AutreCarteButton.bind(on_press=self.Popup_Valider_Carte_Bouton_AutreCarte,
                on_touch_up=self.delete_clock)
            
            self.CashButton = Button(text = "CASH")
            self.CashButton.bind(on_press=self.Popup_Valider_Carte_Bouton_Cash,
                on_touch_up=self.delete_clock)

            self.cancelButton = Button(text = "ANNULER")
            self.cancelButton.bind(on_press=self.Popup_Valider_Carte_Bouton_Annuler,
                on_touch_up=self.delete_clock)    


            self.layoutValiderBot.add_widget(self.cancelButton)
            
            # on ne rajoute pas le bouton autre carte si Ardoise
            if self.panier.Peaksu < 0 : 
                self.CashButton = Button(text = "REMBOURSER : \n"+str(-self.panier.reste)+"€", background_color=(1,0,0,1), font_size='30sp')
                self.CashButton.bind(on_press=self.Popup_Valider_Carte_Bouton_Cash,
                    on_touch_up=self.delete_clock)
                self.layoutValiderBot.add_widget(self.CashButton)       
            else :
                self.layoutValiderBot.add_widget(self.CashButton)       
                self.layoutValiderBot.add_widget(self.AutreCarteButton)       

            self.layoutValider.add_widget(self.layoutValiderBot)

            print('PAS ASSEZ DE PEAKSU')

            # print(self.panier.PremiereCarteData)


            self.layoutValiderTopInfoMembre = GridLayout(
                    cols=1,
                    # row=len(articles),
                    size_hint=(1,0.2),
                    # orientation='horizontal',
                    pos_hint={'x':0, 'y':0.8},
                    # spacing=1,
                    # padding=20
                )


            try:
                membreName = str(self.panier.PremiereCarteData['membreName'].encode('utf-8'))
            except Exception as e:
                print(e)

            print(membreName)
            # import ipdb; ipdb.set_trace()


            if self.panier.Peaksu < 0 :
                self.layoutValiderTopInfoMembre.add_widget(Label(text="PAYE TON ARDOISE\nD'ABORD !!!", font_size='44sp'))
            else :
                self.layoutValiderTopInfoMembre.add_widget(Label(text=membreName, font_size='45sp'))
                self.layoutValiderTopInfoMembre.add_widget(Label(text=str(self.panier.PremiereCarteData['membreCotisationAJour']).encode('utf-8'), font_size='45sp'))
            
            self.layoutValider.add_widget(self.layoutValiderTopInfoMembre)

            self.layoutValiderTop = GridLayout(
                    cols=2,
                    # row=len(articles),
                    size_hint=(1,0.6),
                    # orientation='horizontal',
                    pos_hint={'x':0, 'y':0.2},
                    # spacing=1,
                    # padding=20
                )

            self.first_column_layoutValiderTop = StackLayout()
            self.second_column_layoutValiderTop = StackLayout()

            self.listItemsFirst =[]
            self.listItemsSecond =[]
            # for item in items :
            #     listItemsFirst.append(str(item))
            #     listItemsSecond.append("X "+str(items[item]))

            # listItemsFirst.append('--------------------------')
            # listItemsSecond.append('-------')




            if self.panier.cardchecked :
                if self.panier.Peaksu < 0 :
                    self.listItemsFirst.append('ARDOISE :')
                    self.listItemsSecond.append(str(self.panier.Peaksu)+"€")
                else :
                    self.listItemsFirst.append('CARTE :')
                    self.listItemsSecond.append(str(self.panier.Peaksu)+"€")

            self.listItemsFirst.append('TOTAL :')
            self.listItemsSecond.append(str(self.panier.total)+"€")

            if self.panier.cardchecked :
                self.listItemsFirst.append('MANQUE :')
                self.listItemsSecond.append(str(self.panier.reste)+"€")


            print(self.listItemsFirst)
            print(self.listItemsSecond)
            # adonfButton = Label(text  = "Cacaboudin", font_size='30sp')
            # adonfButton2 = Label(text  = "3€", font_size='30sp')

            self.first_column_layoutValiderTop.add_widget(Label(text="\n".join(self.listItemsFirst), font_size='45sp'))

            self.second_column_layoutValiderTop.add_widget(Label(text="\n".join(self.listItemsSecond), font_size='45sp'))  

            self.layoutValiderTop.add_widget(self.first_column_layoutValiderTop)       
            self.layoutValiderTop.add_widget(self.second_column_layoutValiderTop)       


            self.layoutValider.add_widget(self.layoutValiderTop)


            if self.panier.Peaksu < 0 :
                self.popupValider_carteClRouge = Popup(title='ATTENTION ARDOISE',
                            size_hint=(1, .7),
                            content=self.layoutValider,
                            background_color=(0.5,0,0.5,.5),
                            auto_dismiss=False)  
                              #content=(Label(text='This is a demo pop-up')))
                
            else :
                self.popupValider_carteClRouge = Popup(title='VALIDATION',
                            size_hint=(1, .7),
                            content=self.layoutValider,
                            background_color=(255,0,0,.5),
                            auto_dismiss=False)  
                              #content=(Label(text='This is a demo pop-up')))
            
            # Bind qui permet de lancer l'ARMAGEDDON :
            self.popupValider_carteClRouge.bind(
                on_touch_down=self.create_clock,
                on_touch_up=self.delete_clock)

            self.popupValider_carteClRouge.open()   

            print("VALIDER : ",self.panier.items)
        
        else:
            pass


    '''
    Gestion de l'ardoise démoniaque :
    '''
      
    def BtnlayoutArdoiseVioletteCash(self,instance):
        print('BtnlayoutArdoiseVioletteCash')
        self.popuplayoutArdoiseViolette.dismiss()
        self.popupValider_carteClRouge.open()    

    def Valider_Panier_Ardoise_Demoniaque(self, instance):
        self.panier.Ardoise = True
        self.popuplayoutArdoiseViolette.dismiss()

        response = self.requestServerPaimentCashless()

        if response.status_code == 200 :

            jresponse = response.json()
            print("FUNC ValiderPanier_carte_checked - requestServerPaimentCashless - response : ",response.json())

            layoutValider = FloatLayout()

            layoutValiderTopInfoMembre = GridLayout(
                    cols=1,
                    # row=len(articles),
                    size_hint=(1,0.2),
                    # orientation='horizontal',
                    pos_hint={'x':0, 'y':0.7},
                    spacing=20,
                    # padding=20
                )

            try:
                membreName = str(self.panier.PremiereCarteData['membreName']).encode('utf-8')
            except Exception as e:
                print(e)
                try:
                    membreName = str(self.panier.PremiereCarteData['membreName'].encode('utf-8'))
                except Exception as e:
                    print(e)
                    try:
                        membreName = str(self.panier.PremiereCarteData['membreName'])
                    except Exception as e:
                        print(e)
                        membreName = "False"

            layoutValiderTopInfoMembre.add_widget(Label(text="MUTATION PROVOQUÉE :", font_size='35sp'))

            mutation = random.choice(list(open('mutations'))).decode('utf-8').rstrip()
            layoutValiderTopInfoMembre.add_widget(Label(text=mutation.encode('utf-8'), font_size='35sp'))

            layoutValider.add_widget(layoutValiderTopInfoMembre)


            layoutValiderTop = GridLayout(
                    cols=2,
                    # row=len(articles),
                    size_hint=(1,0.5),
                    # orientation='horizontal',
                    pos_hint={'x':0, 'y':0.1},
                    # spacing=1,
                    # padding=20
                )

            first_column_layoutValiderTop = StackLayout()
            second_column_layoutValiderTop = StackLayout()



            listItemsFirst =[]
            listItemsSecond =[]

            listItemsFirst.append('TOTAL :')
            listItemsSecond.append(str(self.panier.total)+"€")

            listItemsFirst.append('ARDOISE :')
            listItemsSecond.append(str(jresponse['peaksu'])+"€")

            print(listItemsFirst)
            print(listItemsSecond)

            # adonfButton = Label(text  = "Cacaboudin", font_size='30sp')
            # adonfButton2 = Label(text  = "3€", font_size='30sp')

            first_column_layoutValiderTop.add_widget(Label(text="\n".join(listItemsFirst), font_size='45sp'))

            second_column_layoutValiderTop.add_widget(Label(text="\n".join(listItemsSecond), font_size='45sp'))  

            layoutValiderTop.add_widget(first_column_layoutValiderTop)       
            layoutValiderTop.add_widget(second_column_layoutValiderTop)       


            layoutValider.add_widget(layoutValiderTop)


            self.popupValider_carteClVert = Popup(title='PORTAIL CHAOTIQUE OUVERT',
                        size_hint=(1, .5),
                        content=layoutValider,
                        background_color=(0.5,0,0.5,.8))  
                          #content=(Label(text='This is a demo pop-up')))
            self.popupValider_carteClVert.bind(on_dismiss=self.resetFunc)
            self.popupValider_carteClVert.open()   
        
        else :
            logger.error("Valider_Panier_Ardoise_Demoniaque failed. response : "+ str(r))
            self.popupValider_carteClVert.dismiss()
            self.messageError.text = textwrap.fill(str(r),60)
            self.popupErreur.open()
            
            # import ipdb; ipdb.set_trace()

    '''
    ASSEZ DE PEASKU, Ok avec check carte, on lance la requete de paiement
    '''

    def requestServerPaimentCashless(self):

        print("FUNC requestServerPaimentCashless")

        data = self.panier.PremiereCarteData
        data['cardIdMaitresse'] = self.panier.cardIdMaitresse
        data['total'] = float(self.panier.total)
        data['articles'] = self.panier.items
        assert data['tagId']
        
        try:
            if self.panier.Secondecardchecked :
                print("Ajout de la seconde carte au data POST")
                if self.panier.PeaksuSecondeCarte + self.panier.reste >= 0 :
                    data['total'] = self.panier.Peaksu
                    print("data['total] : ",data['total'])
                    data['total_seconde_carte'] = -float(self.panier.reste)
                    print("data['total_seconde_carte']" ,data['total_seconde_carte'])
                    data['data_seconde_carte'] = self.panier.SecondeCarteData
                    print("data['data_seconde_carte']" ,data['data_seconde_carte'])
        except Exception as e:
            pass

        try:

            if self.panier.Ardoise :
                r = requests.post(ipServeur+"/PostArdoiseDemoniaque/", 
                    auth=HTTPBasicAuth(username, password), 
                    data = json.dumps(data),
                    timeout=15)


            else :
                r = requests.post(ipServeur+str(self.panier.ApiServeurVersCarte), 
                    auth=HTTPBasicAuth(username, password), 
                    data = json.dumps(data),
                    timeout=15)

            return(r)

            # if r.status_code != 200 :
            #     logger.error("requestServerPaimentCashless failed. response : "+ str(r))
            #     self.messageError.text = textwrap.fill(str(r),60)
            #     self.popupErreur.open()
            #     return(r)
            # logger.debug("requestServerPay JSON : "+str(r.json()))

    
        except Exception as e:
            logger.error("requestServerPaimentCashless failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()

 
    '''
    PEAKSU INSUFISANTS
    Bouton ANNULLER sur popup Valider Carte ROUGE.
    '''
    def Popup_Valider_Carte_Bouton_Annuler(self,instance):
        self.panier.SecondeCarte = False
        self.popupValider_carteClRouge.dismiss()
        pass


    '''
    PEAKSU INSUFISANTS
    Bouton CASH pour payer ce qu'il manque sur la carte ROUGE.
    '''

    def Popup_Valider_Carte_Bouton_Cash(self,instance):
        print('Popup_Valider_Carte_Bouton_Cash')
        self.popupValider_carteClRouge.dismiss()

        layout = StackLayout()
        layout.add_widget(Label(text="Ajout Dans Cash\nA ENCAISSER : "+str(-self.panier.reste)+"€", font_size='45sp'))
        
        self.popupValider_Carte_Bouton_Cash = Popup(title='VIDER CARTE ET AJOUT CASH',
                    size_hint=(1, .2),
                    content=layout)
                      #content=(Label(text='This is a demo pop-up')))
        self.popupValider_Carte_Bouton_Cash.bind(on_open=self.requestServerPayCashAndCard)
        self.popupValider_Carte_Bouton_Cash.bind(on_dismiss=self.resetFunc)
        self.popupValider_Carte_Bouton_Cash.open()  

        
        # self.requestServerPay(self.panier.PremiereCarteData)
        


    def requestServerPayCashAndCard(self,instance):

        data = self.panier.PremiereCarteData
        # print(data['tagId'])
        data['cardIdMaitresse'] = self.panier.cardIdMaitresse
        data['total'] = self.panier.total
        data['articles'] = self.panier.items

        # print("requestServerPayCashAndCard data : ",data)
        logger.debug("requestServerPayCashAndCard : "+str(data))

        try:
            r = requests.post(ipServeur+'/PostPayCardAndCash/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=4)

            logger.debug("requestServerPayCashAndCard JSON : "+str(r.json()))

            # if r.status_code == 200 :
                # self.resetFunc(self)

            if r.status_code != 200 :
                logger.error("requestServerPayCashAndCard failed. response : "+ str(r))
                self.messageError.text = textwrap.fill(str(r),60)
                self.popupErreur.open()
            else :
                return(r)

        except Exception as e:
            logger.error("requestServerPayCashAndCard failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()



    '''
    PEAKSU INSUFISANTS, PAIEMENT DEUXIEME CARTE :
    PopupNFC ->  Mais avec la variable self.panier.aPayer == True
                                    & self.panier.SecondeCarte = True

    '''

    # ouverture du NFCpopup avec variable SecondeCarte
    def Popup_Valider_Carte_Bouton_AutreCarte(self, instance):

        print("AutreCarteButtonFunc self.panier.reste : ",self.panier.reste)
        self.panier.SecondeCarte = True

    
        self.NFCpopup.content=Label(text='Posez la seconde \ncarte sur le lecteur NFC')
        self.NFCpopup.open()

        pass


    # Fonction appellée apres le scan de la seconde carte
    # Création du popup Rouge ou Vert :
    def ValiderPanier_seconde_carte_checked(self):
        print('RESTE : ',self.panier.reste)
        
        if self.panier.PeaksuSecondeCarte + self.panier.reste >= 0 :
            self.listItemsFirst.append('CARTE2 :')
            self.listItemsSecond.append(str(self.panier.PeaksuSecondeCarte)+"€")

            self.listItemsFirst.append('RESTE :')
            self.listItemsSecond.append(str(self.panier.PeaksuSecondeCarte + self.panier.reste)+"€")

            self.first_column_layoutValiderTop.clear_widgets()
            self.second_column_layoutValiderTop.clear_widgets()

            self.first_column_layoutValiderTop.add_widget(Label(text="\n".join(self.listItemsFirst), font_size='50sp'))
            self.second_column_layoutValiderTop.add_widget(Label(text="\n".join(self.listItemsSecond), font_size='50sp')) 

            self.popupValider_carteClRouge.background_color=(0,255,0,.5)

            self.layoutValiderBot.clear_widgets()

            self.validButton = Button(text = "VALIDER")
            self.validButton.bind(on_press=self.AutreCarteButtonValiderBut)

            # self.layoutValiderBot.col = 2
            self.layoutValiderBot.add_widget(self.cancelButton)    
            self.layoutValiderBot.add_widget(self.validButton)    
        
        else :

            self.listItemsFirst.append('CARTE2 :')
            self.listItemsSecond.append(str(self.panier.PeaksuSecondeCarte)+"€")

            self.listItemsFirst.append('MANQUE :')
            self.listItemsSecond.append(str(self.panier.PeaksuSecondeCarte + self.panier.reste)+"€")

            self.first_column_layoutValiderTop.clear_widgets()
            self.second_column_layoutValiderTop.clear_widgets()

            self.first_column_layoutValiderTop.add_widget(Label(text="\n".join(self.listItemsFirst), font_size='50sp'))
            self.second_column_layoutValiderTop.add_widget(Label(text="\n".join(self.listItemsSecond), font_size='50sp')) 

            # self.popupValider_cash.background_color=(0,255,0,.5)

            self.layoutValiderBot.clear_widgets()


            self.layoutValiderBot.add_widget(self.cancelButton)    
            # self.layoutValiderBot.add_widget(self.validButton)   

            # print("self.listItemsFirst"+str(self.listItemsFirst))
            # print("self.listItemsSecond"+str(self.listItemsSecond))

            # print("ValiderPanier_seconde_carte_checked")


    # Fonction appellée lors de la validation du popup seconde carte Verte
    # On lance la requete requestServerPaimentCashless, mais avec la variable SecondeCarte
    def AutreCarteButtonValiderBut(self, instance):
        
        self.requestServerPaimentCashless()
        self.resetFunc(self)
        self.popupValider_carteClRouge.dismiss()


    '''
    GESTION CREATION NOUVELLE CARTE
    '''

    # Bouton VALIDER sur popupGetNumber :
    def requestServerNewNumero(self, instance):
        data = self.panier.PremiereCarteData
        validRegex = re.compile(r"[\dazer]{5}")
        if validRegex.match(self.Numbertextinput.text) :
            self.LabelNumber.text = "OK !\nOn envoie au serveur"
            data['number'] = self.Numbertextinput.text
            print(self.panier.PremiereCarteData)
            # self.popupGetNumber

            try:
                r = requests.post(ipServeur+'/PostNewNumero/', 
                    auth=HTTPBasicAuth(username, password), 
                    data = json.dumps(data),
                    timeout=10)

                DataR = r.json()
                logger.debug("requestServerNewNumero JSON : "+str(r.json()))

                if DataR['number'] == data['number'] :
                    self.popupGetNumber.dismiss()
                    print('NOUVEAU NUMERO OK, ON LANCE LE self.ValiderPanier_carte_checked()')
                    self.ValiderPanier_carte_checked()
                else :
                    self.LabelNumber.text = "Erreur Numero de carte"

            except Exception as e:
                logger.error("requestServerNewNumero failed. : "+ str(e))
                logger.error(str(traceback.format_exc()))
                popupGetNumber.dismiss()
                self.messageError.text = textwrap.fill(str(e),60)
                self.popupErreur.open()


        else :
            self.LabelNumber.text = "NUMERO INVALIDE"

        pass




    def cancelNumberButtonDimiss(self,instance):
        self.resetFunc(self)
        self.popupGetNumber.dismiss()


    '''
    GESTION CAISSE FIN DE JOURNEE
    '''
    def requestRapportBar(self,instance):
        self.panier.pointCashless = False
        self.popuplayoutPageCashless.dismiss()

        # Vide les au cas ou :
        self.LayoutBut_page1.clear_widgets()
        self.LayoutBut_page2.clear_widgets()
        self.LayoutBut_page3.clear_widgets()

        try:
            data = {}
            data['cardIdMaitresse'] = self.panier.cardIdMaitresse

            print("PostRapportBarToday !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            r = requests.post(ipServeur+'/PostRapportBarToday/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=60)

            logger.debug("requestRapportBar JSON : "+str(r.json()))


            if r.status_code == 200 :
                DataR = r.json()
                print("requestRapportBar JSON : ",DataR)
                self.panier.CalculCaisse = DataR
            else :
                self.TextInputInfo.text = "LA CAISSE SEMBLE DEJA FAITE. ELLE EST VIDE !"
                self.textLayoutCaisseTopJour.text = "VIDE"
                self.textLayoutCaisseTopTotal.text = "VIDE"
                # self.textLayoutCaisseDerniereDate.text = "VIDE"
                print(r.status_code)


        except Exception as e:
            self.panier.CalculCaisse = {}
            self.TextInputInfo.text = "Problème Serveur."

            logger.error("requestServerPayCashAndCard failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()


    def callbackKey(self, instance):
        print("callbackKey :",instance)
        print("callbackKey :",instance.text)

        if instance.text == "Supr" :
            self.NumberCaisseinput.text = ""
        else :
            try:
                self.NumberCaisseinput.text += instance.text
            except Exception as e:
                self.NumberCaisseinput.text = instance.text


    def BtnlayoutPageCashlessCaisse_fin_Journee(self,instance):


        layoutParentCaisse = FloatLayout()


        '''
        MID
        '''
        layoutCaisseMid = GridLayout(
                cols=1,
                # row=len(articles),
                size_hint=(1,0.5),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0.18},
                # spacing=1,
                # padding=20
            )

        first_row_layoutNumberTop = StackLayout()

        self.TextInputInfo = Label(
            text="ENTREZ LE TOTAL DE LA VRAIE CAISSE", size_hint_y= .10,font_size='20sp'
            )
        self.NumberCaisseinput = TextInput(size_hint_y= .20,font_size='50sp',multiline=False)

        first_row_layoutNumberTop.add_widget(self.TextInputInfo)
        first_row_layoutNumberTop.add_widget(self.NumberCaisseinput)   



        layoutCaisseMid.add_widget(first_row_layoutNumberTop)       

        '''
        KEY
        '''
        layoutKey = GridLayout(
                cols=3,
                # row=len(articles),
                size_hint=(1,0.4),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0.11},
                # spacing=1,
                # padding=20
            )

        key1 = Button(text = "1", font_size='45sp')
        key2 = Button(text = "2", font_size='45sp')
        key3 = Button(text = "3", font_size='45sp')
        key4 = Button(text = "4", font_size='45sp')
        key5 = Button(text = "5", font_size='45sp')
        key6 = Button(text = "6", font_size='45sp')
        key7 = Button(text = "7", font_size='45sp')
        key8 = Button(text = "8", font_size='45sp')
        key9 = Button(text = "9", font_size='45sp')
        key0 = Button(text = "0", font_size='45sp')
        keyP = Button(text = ".", font_size='45sp')
        keyE = Button(text = "Supr", font_size='45sp', background_color=(1,0,0,1))

        layoutKey.add_widget(key1)
        layoutKey.add_widget(key2)
        layoutKey.add_widget(key3)
        layoutKey.add_widget(key4)
        layoutKey.add_widget(key5)
        layoutKey.add_widget(key6)
        layoutKey.add_widget(key7)
        layoutKey.add_widget(key8)
        layoutKey.add_widget(key9)
        layoutKey.add_widget(key0)
        layoutKey.add_widget(keyP)
        layoutKey.add_widget(keyE)

        key1.bind(on_press=self.callbackKey)
        key2.bind(on_press=self.callbackKey)
        key3.bind(on_press=self.callbackKey)
        key4.bind(on_press=self.callbackKey)
        key5.bind(on_press=self.callbackKey)
        key6.bind(on_press=self.callbackKey)
        key7.bind(on_press=self.callbackKey)
        key8.bind(on_press=self.callbackKey)
        key9.bind(on_press=self.callbackKey)
        key0.bind(on_press=self.callbackKey)
        keyP.bind(on_press=self.callbackKey)
        keyE.bind(on_press=self.callbackKey)

        '''
        BOT
        '''
        layoutCaisseBot = GridLayout(
                cols=2,
                # row=len(articles),
                size_hint=(1,0.1),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0},
                # spacing=1,
                # padding=20
            )
        validButton = Button(text = "VALIDER")
        validButton.bind(on_press=self.popupCompteCaisse)

        cancelButton = Button(text = "ANNULER")
        cancelButton.id = "DECO"
        cancelButton.bind(on_press=self.resetFunc)


        layoutCaisseBot.add_widget(cancelButton)       
        layoutCaisseBot.add_widget(validButton)    




        '''
        TOP
        '''
        layoutCaisseTop = GridLayout(
                cols=2,
                row=2,
                size_hint=(1,0.2),
                # orientation='horizontal',
                pos_hint={'x':0, 'y':0.8},
                # spacing=1,
                # padding=20
            )


        layoutCaisseTop.add_widget(Label(text="BAR/RESTO 1J:", font_size='30sp'))   
        self.textLayoutCaisseTopJour = Label(text="Calcul en cours", font_size='30sp')
        layoutCaisseTop.add_widget(self.textLayoutCaisseTopJour)     


        # layoutCaisseTop.add_widget(Label(text="Depuis dernière relève de caisse le : "))
        # self.textLayoutCaisseDerniereDate =Label(text="Calcul en cours")
        # layoutCaisseTop.add_widget(self.textLayoutCaisseDerniereDate)

        layoutCaisseTop.add_widget(Label(text="BENEFICE :", font_size='30sp'))       
        self.textLayoutCaisseTopTotal = Label(text="Calcul en cours", font_size='30sp')
        layoutCaisseTop.add_widget(self.textLayoutCaisseTopTotal)       



        layoutParentCaisse.add_widget(layoutCaisseTop)
        layoutParentCaisse.add_widget(layoutCaisseMid)
        layoutParentCaisse.add_widget(layoutKey)
        layoutParentCaisse.add_widget(layoutCaisseBot)

        self.popupCaisse = Popup(title='CAISSE',
                    size_hint=(1, 1), size=(300, 200),
                    content=layoutParentCaisse)  
                      #content=(Label(text='This is a demo pop-up')))

        self.popupCaisse.bind(on_open=self.requestRapportBar)
        self.popupCaisse.open()   

        # cancelButton.bind(on_press=self.popup_Btn_cash_only_cancel)    
        # validButton.bind(on_press=self.popup_Btn_cash_only_Valider)    


    def popupCompteCaisse(self,instance):
        if len(self.NumberCaisseinput.text) > 0 :
            self.panier.CalculCaisse['inputCaisse'] = self.NumberCaisseinput.text

            layout = StackLayout()
            self.textPopupCompte = Label(text="ENVOI VERS SERVEUR :\n"+str(self.NumberCaisseinput.text)+" €", font_size='45sp')
            layout.add_widget(self.textPopupCompte)
            
            self.popuprequestPostCompteCaisse = Popup(title='MERCI POUR LA CAISSE !',
                        size_hint=(1, .2),
                        content=layout)
                          #content=(Label(text='This is a demo pop-up')))
            self.popuprequestPostCompteCaisse.bind(on_open=self.requestPostCompteCaisse)
            self.popuprequestPostCompteCaisse.bind(on_dismiss=self.PostCompteCaisseDimiss)
            self.popuprequestPostCompteCaisse.open()  
        else :
            print('self.NumberCaisseinput.text vide',self.NumberCaisseinput.text)


    def PostCompteCaisseDimiss(self,instance):
            instance.id = "DECO"
            self.resetFunc(instance)
    
    def requestPostCompteCaisse(self,instance):

        try:
            data = self.panier.CalculCaisse
            # data['cardIdMaitresse'] = self.panier.cardIdMaitresse

            print("requestPostCompteCaisse !!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            r = requests.post(ipServeur+'/PostCompteCaisse/', 
                auth=HTTPBasicAuth(username, password), 
                data = json.dumps(data),
                timeout=10)

            logger.debug("requestPostCompteCaisse JSON : "+str(r.json()))

            if r.status_code == 200 :
                DataR = r.json()
                print("requestRapportBar JSON : ",DataR)
                self.textPopupCompte.text=(str(self.NumberCaisseinput.text)+'€ BIEN COMPTABILISÉ, MERCI DE METTRE \nLA SOMME DANS LA BOITE AU LETTRE !')

            else :
                logger.error("requestPostCompteCaisse failed. response : "+ str(r))
                self.messageError.text = textwrap.fill(str(r),60)
                self.popupErreur.open()


        except Exception as e:
            logger.error("requestPostCompteCaisse failed. : "+ str(e))
            logger.error(str(traceback.format_exc()))
            self.messageError.text = textwrap.fill(str(e),60)
            self.popupErreur.open()




class cashlessApp(App):
 
    def build(self):
        root=ButtonUX_BAR1()
        root.build()
        return root

if __name__ == '__main__':
    try:
        cashlessApp().run()
    except Exception as e:
        logger.critical("cashlessApp().run() failed. : "+ str(e))

    