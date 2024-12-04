from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy  
from django.views.generic import CreateView 
from .models import TemplateRelatorio, Foto, Sitio, RelatorioFinal, Tecnico  # Imports corrigidos e
from .Methods.handles import _handle_template_selection, _handle_report_name_submission, _handle_site_selection, _handle_tecnico_selection, _handle_data_selection, _handle_upload_photos
import os
from django.conf import settings
from fpdf import FPDF  # Biblioteca para gerar PDF
from django.template.loader import render_to_string
from .Methods.report_generator import create_final_report
from .Methods.pdf_generator import generate_pdf_report



@login_required
def criar_relatorioFinal(request):
    # Initialize context data
    context = {
        'templates': TemplateRelatorio.objects.all(),
        'tecnicos': Tecnico.objects.all(),
        'sitios': Sitio.objects.all(),
        'template_selecionado': None,
        'template_fotos': None,
        'tecnico_selecionado': None,
        'sitio_selecionado': None,
    }

    if request.method == 'POST':
        response_or_context = None

        if 'template' in request.POST:
            response_or_context = _handle_template_selection(request, context)
        elif 'template_nome' in request.POST:
            response_or_context = _handle_report_name_submission(request, context)
        elif 'sitio' in request.POST:
            response_or_context = _handle_site_selection(request, context)
        elif 'tecnico' in request.POST:
            response_or_context = _handle_tecnico_selection(request, context)
        elif 'data' in request.POST:
            response_or_context = _handle_data_selection(request, context)
        elif 'criar' in request.POST:
            response_or_context = create_final_report(request,context)
        elif 'foto' in request.POST:
            response_or_context = _handle_upload_photos(request, context)
        elif 'pdf' in request.POST:
            relatorio = RelatorioFinal.objects.get(idrelatorio_final=request.session.get('relatorio_id'))
            response_or_context = generate_pdf_report(relatorio)        

        if isinstance(response_or_context, HttpResponse):
            return response_or_context

        if response_or_context is not None:
            context.update(response_or_context)

    return render(request, 'PDF.html', context)


def delete_foto(request, idfoto):  # Alterado para foto_id
    foto = get_object_or_404(Foto, idfoto=idfoto)  # usa o campo idfoto
    foto.delete()
    return redirect('fotos_por_sitio')


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "reporter/signup.html"

def index(request):
    return HttpResponse("Reporter Index")

def templates(request):
    return HttpResponse("Você está vendo templates existentes")

def templates_id(request, idtemplate_relatorio):
    return HttpResponse(f"Você está no template {idtemplate_relatorio}")


def fotos_por_sitio(request):
    sitios = Sitio.objects.all()  # Obtém todos os sitios
    fotos = None
    nome_sitio = None
    sitio_selecionado = None

    if request.method == 'POST':
        # Obtém o id do Sitio selecionado a partir do formulário
        sitio_id = request.POST.get('sitio')
        if sitio_id:
            sitio_selecionado = sitio_id
            sitio = get_object_or_404(Sitio, idsitio=sitio_id)
            fotos = Foto.objects.filter(idsitio=sitio)  # Filtra fotos relacionadas ao Sitio selecionado
            nome_sitio = sitio.nome  # Nome do sitio para exibir na tela

    return render(request, 'fotos_por_sitio.html', {
        'sitios': sitios,
        'sitio_selecionado': sitio_selecionado,
        'fotos': fotos,
        'nome_sitio': nome_sitio
    })
