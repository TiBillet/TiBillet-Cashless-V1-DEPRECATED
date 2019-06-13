# Application de système cashless et de gestion clientèle et/ou membres associatifs pour café/bar et évènements culturels.

##### Si vous habitez ou passez sur l'île de la réunion, venez voir l'association des 3Peaks de Manapany dans le Sud Sauvage qui maintient et utilise cette application au quotidien, pendant les "Dimanches du Sud Sauvage" et surtout pour le Manapany Festival !

##### Nous avons créé cette application pour une utilisation sur mesure. Certaines fonctionnalités ne vous seront probablement pas utile. N'hésitez pas à nous contacter ! ( https://www.3peaks.fr/ )

## Comprend :
- Un module Cashless basée sur une cryptomonnaie et une base de donnée interne.
- Une api pour intéragir avec des boitiers et lecteurs de carte NFC 
- Une gestion de membre et d'adhésion associative
- Un suivi d'inventaire des rapports de ventes d'un café/bar
- Une intégration au système de newsletter Mailchimp
- Un backup horaire des données & une synchronisation avec BorgBackup et Thingsync

## Les technologies utilisées :
- Docker pour l'infrastructure serveur.
- Django pour le backend, l'API Rest et l'interface d'administration
- PostgreSQL pour la base de donnée.
- Nginx, Traefik & LetsEncrypt coté serveur WEB.
- Cryptomonnaie basée sur Ethereum.
- Python/Kivy pour l'interface graphique pour boîtier cashless sur raspberry ou tout système Linux.

## Feuille de route et TODO List :
- Full intégration de la Cryptomonnaie.
- Compilation de l'application front pour Android.
- Passage en full OpenSource.
- Script d'installations et documentation.
- Migrations vers dernière version Django
- Audit de sécurité.
- Passage en python3 de l'application Kivy lorsque nfcpy sera compatible.
- Création de tests unitaires

## Prérequis :
- Docker
- Docker Swarm ( optionnal )
- docker-compose
- Django 1.11
- Un lecteur de cartes NFC compatible avec la librairie nfcpy https://github.com/nfcpy/nfcpy

## Installation ( en cours de rédaction ) :

### Backend Django / Docker :

- Clone project  : ``` git clone https://github.com/Nasjoe/Cashless-oi.git ```
- Create strong password for the database and paste it within the docker-compose.yml. ex : ```pwgen 30 -yC``` 
- Build docker image for Django : ``` docker build -t cashlessoi_django -f dockerfile-Django ./Docker ```
- Build docker image for Postgres/Cron : ``` docker build -t cashlessoi_postgres ./Postgres ```
- Init Django Project : ``` docker-compose run  -u 1000  --rm -f /Docker/docker-compose-django.yml django-admin startproject CashlessOi /DjangoFiles```
- Edit the settings.py file for  ( RTFM of Django or ask for help if you don't know ) :
    - Debug, allowed host and PostgresDatabase integration.
    - Add Jet, Jet Dashboard and Cashless-oi to the INSTALLED_APPS list.
    - Set the REST_FRAMEWORK settings.
    - Configure language and time zone.
    - set the STATIC_ROOT = os.path.join(BASE_DIR, "www", "static")
- Start all the container : ``` docker-compose up -f ./Docker/docker-compose.yml ``` use -d if you want detached mode.
- Launch the makemigrations, migrate and collecstatic inside the django container.
- Creer un super user sous django.
- La suite bientôt :) ...


### Client pour Raspberry Pi :
- Booter sur KivyPie : http://kivypie.mitako.eu/ et mettre à jour :

```
sudo apt-get update; 
sudo apt-get install python2-kivypie
sudo apt-get install xclip xsel
sudo pip install --upgrade pip
sudo pip install -U nfcpy
sudo pip install --upgrade sentry-sdk
python -m nfc
```
- changer le hostname et les mots de passe user par defaut ( sysop / posys ).
- rentrer les creds dans le configClient.

### Client pour Desktop Ubuntu/Debian :


## Infos utiles :
- Les logs des serveurs web Nginx & python Gunicorn sont dans le répertoire www/ de DjangoFiles.
- Un cron est sur le conteneur du Postgres. il fait un dump toute les heures dans le dossier Postgres/SaveDb
- Pour restaurer une sauvegarde de DB : ``` cat dump_trucmuche.sql | docker exec -i cashlessoi_postgres psql -U postgres ```. Puis lancer un makemigration et migrate --fake avec Django.



## Licence :

	Copyright 2017 - 2019 Jonas TURBEAUX.
	La distribution et l'utilisation de ce programme est régie par la GPL version 3 ou ultérieure.
	L'auteur demande juste à être invité à chaque évènement ou son système est mis en place ! :) 
	Et puis si vous en faites une utilisation commerciale et que vous gagnez du fric avec, 
	soyez sympa, faites un don !

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