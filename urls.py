from django.contrib import admin
from django.urls import include, path

from sermepa_test import views

urlpatterns = [
    path('sermepa/', include('sermepa.urls')),
    path('', views.form, name='form'),
    path('<str:trans_type>/', views.form, name='otros_forms'),
    path('end', views.end, name='end'),
    path('admin/', admin.site.urls),
]
