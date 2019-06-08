# Application de système cashless et de gestion clientèle et ou membres associatifs pour café/bar et évènements culturels.

Si vous habitez ou passez sur l'île de la réunion, venez voir l'association des 3Peaks de Manapany dans le sud sauvage qui maintient et utilise cette application au quotidient, pendant les "Dimanches du Sud Sauvage" et surtout pour le Manapany Festival !

## Comprend :
- Un module Cashless basée sur une cryptomonnaie et une base de donnée interne.
- Une api pour intéragir avec des boitiers et lecteurs de carte NFC 
- Une gestion de membre et d'adhésion associative
- Un suivi d'inventaire des rapports de ventes d'un café/bar
- Une intégration au système de newletter Mailchimp
- Un backup horaire des données & une synchronisation avec BorgBackup et Thingsync

## Les technologies utilisées :
- Docker pour l'infrastructure serveur.
- Django pour le backend et l'interface d'administration
- PostgreSQL pour la base de donnée.
- Ngninx, Traefik & LetsEncrypt coté serveur WEB.
- Cryptomonnaie basée sur Ethereum.
- Python/Kivy pour l'interface graphique pour boitier cashless sur raspberry ou tout système Linux.

## Feuille de route et TODO List :
- Full intégration de la Cryptomonnaie.
- Compilation de l'application front pour Android.
- Passage en full OpenSource.
- Script d'installations et documentation.
- Migrations vers dernière version Django
- Audit de sécurité.

## Prérequis :
- Docker
- Docker Swarm ( optionnal )
- docker-compose
- Django 1.11

## Installation :

- Clone project  : ``` git clone https://github.com/Nasjoe/Cashless-oi.git ```
- Build docker image : ``` docker build -t cashlessoi_django -f dockerfile-Django ./Docker ```
- Init Django Project : ``` docker-compose run  -u 1000  --rm -f /Docker/docker-compose-django.yml django-admin startproject CashlessOi /DjangoFiles```