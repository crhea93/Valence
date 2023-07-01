"""cognitiveAffectiveMaps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from users.views import index
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

urlpatterns = [
    path('',index,name='home'),
    path('Realadmin/', admin.site.urls),
    path('block/',include('block.urls')),
    path('link/',include('link.urls')),
    path('users/',include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),  # Logout and Password reset
    path('config_admin/', include("config_admin.urls")),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
