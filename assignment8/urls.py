from django.contrib import admin
from django.urls import path
from network import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.network_view, name='home'),
]
