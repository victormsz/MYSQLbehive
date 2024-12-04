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
from reporter.Methods.handles import _handle_upload_photos
from reporter.Methods.report_generator import create_final_report
from reporter import views
from django.urls import path


urlpatterns = [

    #admin, contas e home
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("signup/", views.SignUpView.as_view(), name="signup"),

    #criar pdf's
    path('reporter_info/', views.criar_relatorioFinal, name='reporter_info'),
    path('create_report/', create_final_report, name='create_report'),  
    path('pdf/', views.generate_pdf_report, name='pdf'),

    #configurar fotos
    path('fotos/', views.fotos_por_sitio, name='fotos_por_sitio'),
    path('upload_photo/', _handle_upload_photos, name='upload_photo'),
    path('delete-foto/<int:idfoto>/', views.delete_foto, name='delete_foto'),

    #configurar templates
    #path('templates/', views.lista_templates, name='lista_templates'),
    

    #configurar RelatorioFinal
    #path('adicionar-relatorio/', views.adicionar_relatorio, name='adicionar_relatorio'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:  # Apenas durante o desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)