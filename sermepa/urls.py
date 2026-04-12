from django.urls import path

from .views import sermepa_ipn


urlpatterns = [
    path('', sermepa_ipn, name='sermepa_ipn'),
]
