from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from io import BytesIO
from django.shortcuts import get_object_or_404, render, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .FotoForm import FotoForm
from django.urls import reverse_lazy  
from django.views.generic import CreateView 
from .models import TemplateRelatorio, Foto, Sitio  # Imports corrigidos e
import os
from django.conf import settings
from fpdf import FPDF  # Biblioteca para gerar PDF


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

def Create_pdf(request, sitio_id):
    # Recupera o sitio com base no ID
    sitio = get_object_or_404(Sitio, idsitio=sitio_id)
    fotos = Foto.objects.filter(idsitio=sitio)

    # Cria um objeto FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Define a fonte e o título
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Relatório de Fotos do Sitio: " + sitio.nome, ln=True, align="C")
    pdf.ln(10)

    # Define a fonte para o conteúdo
    pdf.set_font("Arial", size=12)
    for foto in fotos:
        pdf.cell(200, 10, txt=f"Nome: {foto.nome}", ln=True)
        pdf.multi_cell(200, 10, txt=f"Descrição: {foto.descricao}")
        
        # Tenta carregar a imagem e adicionar no PDF
        try:
            caminho_imagem = foto.foto.path
            pdf.image(caminho_imagem, x=10, w=100)
        except Exception as e:
            pdf.cell(200, 10, txt="Imagem não encontrada ou erro ao carregar.", ln=True)
        
        pdf.ln(5)

    # Caminho para salvar o PDF no diretório 'media/pdf/'
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdf')
    os.makedirs(pdf_dir, exist_ok=True)  # Cria o diretório se não existir

    # Defina o nome do arquivo
    pdf_filename = f"relatorio_fotos_sitio_{sitio.idsitio}.pdf"
    pdf_filepath = os.path.join(pdf_dir, pdf_filename)

    # Salva o PDF fisicamente
    pdf.output(pdf_filepath)

    # Retorna o caminho do arquivo gerado
    # Caso queira retornar o PDF como link para download, use o seguinte:
    pdf_url = os.path.join(settings.MEDIA_URL, 'pdf', pdf_filename)
    
    return HttpResponse(f'O PDF foi gerado e salvo em: <a href="{pdf_url}">{pdf_url}</a>')

def gerar_pdf_view(request):
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

    return render(request, 'Create_pdf.html', {
        'sitios': sitios,
        'sitio_selecionado': sitio_selecionado,
        'fotos': fotos,
        'nome_sitio': nome_sitio
    })
def gerar_pdf(request):
    if request.method == 'POST':
        form = FotoForm(request.POST, request.FILES)  # Não se esqueça de passar request.FILES
        if form.is_valid():
            form.save()  # Salva o novo objeto Foto no banco de dados
            return redirect('gerar_pdf_view')  # Redireciona para a mesma página após salvar
    else:
        form = FotoForm()

    return render(request, 'pdf.html', {'form': form})


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

def delete_foto(request, foto_id):  # Alterado para foto_id
    foto = get_object_or_404(Foto, idfoto=foto_id)  # usa o campo idfoto
    foto.delete()
    return redirect('fotos_por_sitio')