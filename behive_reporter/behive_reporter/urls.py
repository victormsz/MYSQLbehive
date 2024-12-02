"""
URL configuration for behive_reporter project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from django.views.generic.base import TemplateView
from reporter.views import SignUpView , gerar_pdf, fotos_por_sitio , Create_pdf , gerar_pdf_view, delete_foto
from django.urls import path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path('generate-pdf/', gerar_pdf, name='generate_pdf'),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('fotos/', fotos_por_sitio, name='fotos_por_sitio'),
    path('gerar_pdf/', gerar_pdf_view, name='gerar_pdf_view'),
    path('create_pdf/<int:sitio_id>/', Create_pdf, name='create_pdf'),
    path('delete-foto/<int:idfoto>/', delete_foto, name='delete_foto'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:  # Apenas durante o desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)