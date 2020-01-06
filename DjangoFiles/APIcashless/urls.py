"""cashlessDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from rest_framework import routers
from APIcashless import views
from django.contrib import admin
from django.conf import settings

router = routers.DefaultRouter()

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [

    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),  # Django JET dashboard URLS
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^PostGetIdCard/', views.PostGetIdCard),
    url(r'^PaimentCashlessBarResto/', views.PaimentCashlessBarResto),
    url(r'^PostArdoiseDemoniaque/', views.PostArdoiseDemoniaque),
    url(r'^PostPayCardAndCash/', views.PostPayCardAndCash),
    url(r'^PostViderCard/', views.PostViderCard),
    url(r'^AjoutPeaksu/', views.AjoutPeaksu),
    url(r'^PostPayCashOnly/', views.PostPayCashOnly),
    url(r'^PostNewNumero/', views.PostNewNumero),
    url(r'^PostGetArticles/', views.PostGetArticles),
    url(r'^PostGetCashlessName/', views.PostGetCashlessName),
    url(r'^PostRapportBar/', views.PostRapportBar),
    url(r'^PostCompteCaisse/', views.PostCompteCaisse),
    url(r'^PostRapportBarToday/', views.PostRapportBarToday),
    url(r'^derniereAction/', views.derniereAction),
    url(r'^deleteDerniereAction/', views.deleteDerniereAction),
    url(r'^addEmailToMailchimp/', views.addEmailToMailchimp),
    url(r'^reportsArticleVendus/', views.reportsArticleVendus),
    url(r'^PostChargeweb/', views.PostChargeweb),

    url(r'^', include(router.urls)),
]
