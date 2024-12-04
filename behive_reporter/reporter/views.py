from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy  
from django.views.generic import CreateView 
from .models import TemplateRelatorio, Foto, Sitio, RelatorioFinal, Tecnico  # Imports corrigidos e
import os
from django.conf import settings
from fpdf import FPDF  # Biblioteca para gerar PDF
from django.template.loader import render_to_string


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

from fpdf import FPDF
from django.http import HttpResponse
from django.conf import settings
import os

@login_required
def create_pdf(request):
    # Recupera os dados necessários da sessão ou do banco
    sitio_id = request.session.get('selected_sitio_id')
    if not sitio_id:
        messages.error(request, 'Nenhum sítio selecionado.')
        return redirect('home')  # ou qualquer página que deseje redirecionar

    sitio = Sitio.objects.get(idsitio=sitio_id)
    fotos = Foto.objects.filter(sitio=sitio)  # Assumindo que há uma relação de fotos com o sitio

    # Cria um objeto FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Define a fonte e o título
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=f"Relatório de Fotos do Sitio: {sitio.nome}", ln=True, align="C")
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
    pdf_url = os.path.join(settings.MEDIA_URL, 'pdf', pdf_filename)
    
    # Retorna uma resposta com o link do PDF gerado
    return HttpResponse(f'O PDF foi gerado e salvo em: <a href="{pdf_url}">{pdf_url}</a>', content_type='text/html')



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

@login_required
def selecionar_template(request):
    # Initialize variables
    templates = TemplateRelatorio.objects.all()
    tecnicos = Tecnico.objects.all()
    sitios = Sitio.objects.all()
    template_selecionado = None
    template_fotos = None
    tecnico_selecionado = None
    sitio_selecionado = None
    
    # Handle template selection
    if request.method == 'POST' and 'template' in request.POST:
        try:
            template_id = request.POST.get('template')
            template_selecionado = TemplateRelatorio.objects.get(idtemplate_relatorio=template_id)
            template_fotos = template_selecionado.pedidos_fotos
            request.session['selected_template_id'] = template_id
            
            # If it's an HTMX request, return a partial response
            if request.headers.get('HX-Request'):
                context = {
                    'template_selecionado': template_selecionado,
                    'template_fotos': template_fotos,
                    'tecnicos': tecnicos,
                    'sitios': sitios,
                }
                return HttpResponse(render_to_string('partials/template_selected.html', context))
        
        except TemplateRelatorio.DoesNotExist:
            messages.error(request, 'Template não encontrado.')
    
    # Handle report name submission
    if request.method == 'POST' and 'template_nome' in request.POST:
        template_id = request.session.get('selected_template_id')
        
        if template_id:
            try:
                template_selecionado = TemplateRelatorio.objects.get(idtemplate_relatorio=template_id)
                relatorio_nome = request.POST.get('template_nome')  # Changed from 'nome'
                
                if relatorio_nome:
                    if 3 <= len(relatorio_nome) <= 100:
                        request.session['relatorio_nome'] = relatorio_nome
                        success_message = f'Nome "{relatorio_nome}" salvo na sessão com sucesso!'
                        
                        # If it's an HTMX request, return a partial response
                        if request.headers.get('HX-Request'):
                            return HttpResponse(
                                f'<div class="alert alert-success">{success_message}</div>'
                            )
                        
                        messages.success(request, success_message)
                    else:
                        error_message = 'O nome do relatório deve ter entre 3 e 100 caracteres.'
                        
                        # If it's an HTMX request, return a partial response
                        if request.headers.get('HX-Request'):
                            return HttpResponse(
                                f'<div class="alert alert-danger">{error_message}</div>', 
                                status=400
                            )
                        
                        messages.error(request, error_message)
                else:
                    error_message = 'Por favor, insira um nome válido.'
                    
                    # If it's an HTMX request, return a partial response
                    if request.headers.get('HX-Request'):
                        return HttpResponse(
                            f'<div class="alert alert-danger">{error_message}</div>', 
                            status=400
                        )
                    
                    messages.error(request, error_message)

            except TemplateRelatorio.DoesNotExist:
                messages.error(request, 'Template não encontrado.')
            except Exception as e:
                messages.error(request, f'Erro ao salvar o nome: {str(e)}')
    
    # Handle technician selection
    if request.method == 'POST' and 'tecnico' in request.POST:
        try:
            tecnico_id = request.POST.get('tecnico')
            
            if tecnico_id:
                tecnico_selecionado = get_object_or_404(Tecnico, idtecnico=tecnico_id)
                request.session['selected_tecnico_id'] = tecnico_id
                success_message = f'Técnico "{tecnico_selecionado.nome}" selecionado com sucesso!'
                
                # If it's an HTMX request, return a partial response
                if request.headers.get('HX-Request'):
                    return HttpResponse(
                        f'<div class="alert alert-success">{success_message}</div>'
                    )
                
                messages.success(request, success_message)
            else:
                error_message = 'Por favor, selecione um técnico.'
                
                # If it's an HTMX request, return a partial response
                if request.headers.get('HX-Request'):
                    return HttpResponse(
                        f'<div class="alert alert-danger">{error_message}</div>', 
                        status=400
                    )
                
                messages.error(request, error_message)

        except Exception as e:
            error_message = f'Erro ao selecionar técnico: {str(e)}'
            messages.error(request, error_message)
            # Optionally, return an HTMX response with an error message
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="alert alert-danger">{error_message}</div>',
                    status=500
                )
    # Handle site selection
    if request.method == 'POST' and 'sitio' in request.POST:
        try:
            sitio_id = request.POST.get('sitio')
            
            if sitio_id:
                sitio_selecionado = Sitio.objects.get(idsitio=sitio_id)
                request.session['selected_sitio_id'] = sitio_id
                success_message = f'Sitio "{sitio_selecionado.nome}" selecionado com sucesso!'
                
                # If it's an HTMX request, return a partial response
                if request.headers.get('HX-Request'):
                    return HttpResponse(
                        f'<div class="alert alert-success">{success_message}</div>'
                    )
                
                messages.success(request, success_message)
            else:
                error_message = 'Por favor, selecione um sitio.'
                
                # If it's an HTMX request, return a partial response
                if request.headers.get('HX-Request'):
                    return HttpResponse(
                        f'<div class="alert alert-danger">{error_message}</div>', 
                        status=400
                    )
                
                messages.error(request, error_message)

        except Sitio.DoesNotExist:
            messages.error(request, 'Sitio não encontrado.')
        except Exception as e:
            messages.error(request, f'Erro ao selecionar sitio: {str(e)}')

    if request.method == 'POST' and 'data' in request.POST:
        data = request.POST.get('data')
        request.session['data'] = data
        success_message = f'Data "{data}" salva com sucesso!'

        # If it's an HTMX request, return a partial response
        if request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="alert alert-success">{success_message}</div>'
            )

        messages.success(request, success_message)

    if request.method == 'POST' and 'uploadFoto' in request.POST:
        foto = request.FILES.get('foto')
        descricao = request.POST.get('template_fotos')
        sitio_id = request.session.get('selected_sitio_id')
        if not sitio_id:
            messages.error(request, 'Nenhum sítio selecionado.')
        if foto and descricao and sitio_id:
            try:
                foto = Foto.objects.create(
                    foto=foto,
                    descricao=request.POST.get('template_fotos'),
                    idsitio_id=sitio_id
                )
                success_message = f'Foto "{foto.descricao}" salva com sucesso!'
                messages.success(request, success_message)
            except Exception as e:
                messages.error(request, f'Erro ao salvar a foto: {str(e)}')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')

    if request.method == 'POST' and 'criar' in request.POST:
        # Pega os dados selecionados da sessão
        template_id = request.session.get('selected_template_id')
        tecnico_id = request.session.get('selected_tecnico_id')
        sitio_id = request.session.get('selected_sitio_id')
        data = request.session.get('data')
        relatorio_nome = request.session.get('relatorio_nome')

        # Verifique se todos os dados necessários foram armazenados na sessão
        if not all([template_id, tecnico_id, sitio_id, data, relatorio_nome]):
            messages.error(request, 'Faltam dados para criar o relatório.')
            return HttpResponse(status=400)

        # Aqui você pode criar o relatório ou fazer a lógica necessária
    
        # Crie o relatório final
        relatorio = RelatorioFinal.objects.create(
            data=data,
            tecnico_responsavel_id=tecnico_id,
            idsitio_id=sitio_id,
            idtemplate_relatorio_id=template_id,
            nome=relatorio_nome
        )

        # Limpe os dados da sessão
        request.session.flush()
        messages.success(request, f'Relatório "{relatorio_nome}" criado com sucesso!')
        return redirect('home')

    # Prepare context for rendering
    context = {
        'templates': templates,
        'template_selecionado': template_selecionado,
        'template_fotos': template_fotos,
        'messages': messages.get_messages(request),
        'tecnico_selecionado': tecnico_selecionado,
        'tecnicos': tecnicos,
        'sitios': sitios,
    }
    
    return render(request, 'PDF.html', context)

def delete_foto(request, idfoto):  # Alterado para foto_id
    foto = get_object_or_404(Foto, idfoto=idfoto)  # usa o campo idfoto
    foto.delete()
    return redirect('fotos_por_sitio')


"""def adicionar_relatorio(request):
    if request.method == "POST":
        if 'adicionar_relatorio' in request.POST:
            form = RelatorioForm(request.POST)
            if form.is_valid():
                # Salvar a instância do Relatório Final
                relatorio = form.save()

                # Mensagem de sucesso
                success_message = f"Relatório '{relatorio.nome}' salvo com sucesso!"
                
                # Renderizar a página com a mensagem de sucesso
                return render(request, 'PDF.html', {'form': form, 'success_message': success_message})
    else:
        form = RelatorioForm()

    return render(request, 'PDF.html', {'form': form})"""