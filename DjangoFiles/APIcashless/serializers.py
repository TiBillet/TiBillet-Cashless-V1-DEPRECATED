from rest_framework import serializers
from .models import CarteCashless, Articles


class CarteCashlessSerializer(serializers.HyperlinkedModelSerializer):

    CardMaitresse = serializers.StringRelatedField(many=True)   
    BoissonCoutantCarteM = serializers.StringRelatedField(many=True)

    class Meta:
        model = CarteCashless
        fields = ('tagId', 'number', 'wallet', 'peaksu', 'peaksuCadeau','changeByName', 'membreName', 'membreCotisationAJour', 'CardMaitresse', 'BoissonCoutantCarteM')



class ArticlesSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Articles
        fields = ('name', 'prix', 'poidListe', 'page_name', 'page_poids', 'alcool', 'prixAchat')



