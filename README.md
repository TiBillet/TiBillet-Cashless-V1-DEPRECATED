# Application de système cashless et de gestion clientèle et/ou membres associatifs pour café/bar et évènements culturels.

### https://www.tibillet.re

##### Si vous habitez ou passez sur l'île de la réunion, venez voir l'association des 3Peaks de Manapany dans le Sud Sauvage qui maintient et utilise cette application au quotidien, pendant les "Dimanches du Sud Sauvage" et surtout pour le Manapany Festival !

##### Nous avons créé cette application pour une utilisation sur mesure. Certaines fonctionnalités ne vous seront probablement pas utiles. N'hésitez pas à nous contacter ! ( https://www.3peaks.fr/ )

## Autre dépots du projets :
- https://github.com/Nasjoe/TiBillet-Cashless
- https://github.com/Nasjoe/TiBillet-LandingPage

## Comprend :
- Un module Cashless basé sur une cryptomonnaie et une base de données interne.
- Une api pour interagir avec des boitiers et lecteurs de cartes NFC 
- Une gestion de membre et d'adhésion associative
- Un suivi d'inventaire des rapports de ventes d'un café-bar
- Une intégration au système de newsletter Mailchimp
- Un backup horaire des données & une synchronisation avec BorgBackup et Syncthing.

## Les technologies utilisées :
- Docker pour l'infrastructure serveur.
- Django pour le backend, l'API REST et l'interface d'administration
- PostgreSQL pour la base de données.
- Nginx, Traefik & LetsEncrypt coté serveur WEB.
- Cryptomonnaie basée sur Ethereum.
- Python/Kivy pour l'interface graphique pour boîtier cashless sur raspberry ou tout système Linux.

## Conseil pour une bonne mise en production :
- Creez un compte sur Sentry et rajoutez sur votre settings.py et dans les scripts de vos clients les infos nécéssaire. Cela vous aidera beaucoup en cas de bug. Et ça nous aidera aussi de notre coté si vous voulez qu'on vous file un coup de main !
- Faites un backup de vos backups ! Une solution à base de syncthing, un borgbackup, un raid5, un cluster de postgres, etc. N'attendez pas d'avoir des soucis de hardware ! Copiez sur clef usb régulièrement le dossier SaveDb de Postgres par exemple !
- Vos applications clients rament ? Mettez le serveur sur le réseau local. 
- Évitez le wifi sur les appli clients. Et surtout sur le serveur. Lorsqu'il n'y a personne dans votre salle pendant votre évènement, ça passe bien, mais des qu'elle est remplie, le wifi va s'écrouler !
- Séparez le réseau internet et le réseau du cashless si vous le pouvez ! C'est la meilleure façon de se prémunir des personnes mal intentionnées.
- Séparez bien le point recharge du point de vente. C'est la clef pour un service au bar fluide !
- N'hésitez surtout pas à nous contacter à la moindre question ! On vous donnera plein de conseils :)

## Feuille de route et TODO List :
- Full intégration de la Cryptomonnaie.
- Compilation de l'application front pour Android.
- Passage en full Open Source.
- Script d'installations et documentation.
- Migrations vers dernière version Django
- Audit de sécurité.
- Passage en python3 de l'application Kivy lorsque nfcpy sera compatible.
- Création de tests unitaires
- Automatisation de syncthing.

## Prérequis :
- Docker
- docker-compose
- Un lecteur de cartes NFC compatible avec la librairie nfcpy https://github.com/nfcpy/nfcpy ( par ex: KKmoon ACR122U NFC RFID )

## Installation ( en cours de rédaction ) :

Nous vous proposons deux façons d'utiliser Ti Billet. La première est une installation par vous-même, expliquée ci-dessous. À réserver aux personnes connaissant les environnements Linux, docker, Django et python. Rien de compliqué, mais nous nous proposons aussi de vous aider dès le début de votre projet avec une solution clef en main et une personnalisation sur-mesure. N'hésitez pas à nous contacter !


### Backend Django / Docker :

- Clone project  : 
    ```git clone https://github.com/Nasjoe/TiBillet-Cashless.git```
- Create strong password for the database and paste it within the Docker/docker-compose.yml. ex : 
    ```pwgen 30 -yC``` 
- Build docker image for Django : 
    ```docker build -t cashless_django ./Docker```
- Init Django Project : 
    ```
    cd Docker
    docker-compose run -u 1000 --rm cashless_django django-admin startproject Cashless /DjangoFiles
    ```
- You should have new files within the DjangoFiles folder. 
- Edit the DjangoFiles/Cashless/settings.py file ( RTFM of Django or ask for help if you don't know ) :
    - ```Debug = False```
    - ```ALLOWED_HOSTS = ['YOUR DNS OR LOCAL IP ONLY !']```
    - Add Jet, Jet Dashboard and APIcashless to the INSTALLED_APPS list ( be careful of the order ) :
    ```
    INSTALLED_APPS = [
        'jet.dashboard',
        'jet',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'APIcashless',
    ]
    JET_SIDE_MENU_COMPACT = True
    JET_CHANGE_FORM_SIBLING_LINKS = False
    ```
    - Postgres integration ( replace existing DATABASE information ) :
    ```
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'cashless_postgres_db',
            'USER': 'cashless_postgres_user',
            'PASSWORD': 'YOUR STRONG PASSW WITHIN THE docker-compose file',
            'HOST': 'cashless_postgres',
            'PORT': '5432',
        }
    }
    ```
    - Set the REST_FRAMEWORK settings :

    ```
    REST_FRAMEWORK = {
        # Use Django's standard `django.contrib.auth` permissions,
        # or allow read-only access for unauthenticated users.
        'DEFAULT_PERMISSION_CLASSES': [
            # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
            'rest_framework.permissions.IsAuthenticated',
        ]
    }
    ```

    - Configure language and time zone.

    ```
    #( for french Reunion island : )
    LANGUAGE_CODE = 'fr-fr'
    TIME_ZONE = 'Indian/Reunion'
    ```

    - set the STATIC_ROOT and MEDIA_ROOT :
    ```
    STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")
    MEDIA_ROOT = 'MEDIA_ROOT'
    ```

- Edit the DjangoFiles/Cashless/urls.py and replace ALL the lines (!) by :

    ```
    from django.conf.urls import url, include
    from APIcashless import urls

    urlpatterns = [
        url(r'^', include(urls)),
    ]
    ```

- Start all the container ( use -d if you want detached mode. ) :
    ```
    cd Docker
    docker-compose up
    ``` 

- Launch the makemigrations, migrate, collecstatic and create superuser inside the django container :
     ``` 
     docker exec -ti cashless_django bash
     python manage.py makemigrations APIcashless jet
     python manage.py migrate
     python manage.py collectstatic
     python manage.py createsuperuser
     ``` 
     - Detach from the container ( ctrl + d )

- Restart all the container :
     ``` 
     docker-compose down
     docker-compose up -d
     ``` 

- log in to the admin panel in http://localhost:8000

- Create one user for each Kivy Client.
- Create Master Card for each point of sale.
- Créate articles.

- La suite bientôt :) ...


### Client pour Raspberry Pi :

- Booter sur KivyPie : http://kivypie.mitako.eu/ puis :
- Brancher le lecteur NFC

```
sudo apt-get update; 
sudo apt-get install python2-kivypie
sudo apt-get install xclip xsel
sudo pip install --upgrade pip
sudo pip install -U nfcpy
sudo pip install --upgrade sentry-sdk
python -m nfc
```

- changer le hostname et les mots de passe user par défaut ( sysop / posys ).
- rentrer les creds dans le fichier configClient.py .
- Si écran tactile, regarder du coté de : https://github.com/goodtft/LCD-show.git
- Cred wifi à changer dans /boot/interfaces. Possibilité de le faire directement sur la carte SD
- Remplir le fichier configClient.py avec les cred crées sur Django via l'interface admin. Attention, evitez le superuser...
- Lancer le script dans le dossier Kivy ``` python2 Client_Kivy.py ```
- Pour lancer un script au démarrage : sudo nano /etc/rc.local 

### Client pour Desktop Ubuntu/Debian :

- Brancher le lecteur NFC

```
sudo apt-get update
sudo apt-get install libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0
sudo python2 -m pip install install --upgrade pip
sudo python2 -m pip install kivy
sudo python2 -m pip install -U nfcpy
sudo adduser $USER plugdev
```
- Puis un ```python -m nfc``` et suivre les indications.
- Remplir le fichier configClient.py avec les cred crée sur Django. Attention, evitez le superuser...
- Lancer le script dans le dossier Kivy ``` python2 Client_Kivy.py ```


### Client pour Desktop Windows :
- A suivre...

### Client pour Desktop MacOs :
- A suivre...

## Infos utiles :
- Les logs des serveurs web Nginx & python Gunicorn sont dans le répertoire www/ de DjangoFiles.
- Un cron est sur le conteneur du Postgres. il fait un dump toutes les heures dans le dossier Postgres/SaveDb. Puis supprime les sauvegarde agée de 10 jours ou plus. Pour le modifier, c'est le script cron.sh dans le dossier Postgres. Si vous voulez backuper toute les 5 mins, c'est possible. ( https://crontab.guru peut vous aider ) 
- Pour restaurer une sauvegarde de DB : ``` cat dump_trucmuche.sql | docker exec -i cashlessoi_postgres psql -U postgres ```. Puis lancer un makemigration et migrate --fake avec Django.
- Les conteneurs sont lancés avec restart=always. Ce qui veut dire qu'ils se relanceront tout le temps, même après un reboot de l'hôte. Pour les stopper définitivement, lancer un ```docker-compose down```.


## Licence :

	Copyright 2017 2019+* - Jonas TURBEAUX - GDNA - 3Peaks.
	La distribution et l'utilisation de ce programme sont régies par la GPL version 3 ou ultérieure.
	Les auteurs demandent juste à être invités à chaque évènement où ce système est mis en place ! :) 
	Et puis si vous en faites une utilisation commerciale et que vous gagnez du fric avec, 
	soyez sympa, faites un don ! https://www.3peaks.fr/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.