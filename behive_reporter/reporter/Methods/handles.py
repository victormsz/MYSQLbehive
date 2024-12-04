from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from ..models import TemplateRelatorio, Sitio, Tecnico, RelatorioFinal, Foto
from django.shortcuts import render


def _handle_template_selection(request, context):
    try:
        template_id = request.POST.get('template')
        template_selecionado = TemplateRelatorio.objects.get(idtemplate_relatorio=template_id)
        
        request.session['selected_template_id'] = template_id
        
        context['template_selecionado'] = template_selecionado
        context['template_fotos'] = template_selecionado.pedidos_fotos
        
        if request.headers.get('HX-Request'):
            return HttpResponse(render_to_string('partials/template_selected.html', context))
        
    except TemplateRelatorio.DoesNotExist:
        messages.error(request, 'Template não encontrado.')
    
    return context

def _handle_report_name_submission(request, context):
    template_id = request.session.get('selected_template_id')
    
    if not template_id:
        messages.error(request, 'Nenhum template selecionado.')
        return context
    
    try:
        template_selecionado = TemplateRelatorio.objects.get(idtemplate_relatorio=template_id)
        relatorio_nome = request.POST.get('template_nome')
        
        # Validate report name
        if not relatorio_nome or len(relatorio_nome) < 3 or len(relatorio_nome) > 100:
            error_message = 'O nome do relatório deve ter entre 3 e 100 caracteres.'
            
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="alert alert-danger">{error_message}</div>', 
                    status=400
                )
            
            messages.error(request, error_message)
            return context
        
        # Store in session
        request.session['relatorio_nome'] = relatorio_nome
        context['relatorio_nome'] = relatorio_nome
        success_message = f'Nome "{relatorio_nome}" salvo na sessão com sucesso!'
        
        # HTMX partial response
        if request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="alert alert-success">{success_message}</div>'
            )
        
        messages.success(request, success_message)
        
    except TemplateRelatorio.DoesNotExist:
        messages.error(request, 'Template não encontrado.')
    except Exception as e:
        messages.error(request, f'Erro ao salvar o nome: {str(e)}')
    
    return context

def _handle_tecnico_selection(request, context):
    try:
        tecnico_id = request.POST.get('tecnico')
        
        if  tecnico_id:
            tecnico_selecionado = Tecnico.objects.get (idtecnico = tecnico_id)
            request.session['tecnico_selecionado'] = tecnico_id
            print(tecnico_selecionado.idtecnico)
            print(request.session.get('tecnico_selecionado'))
            success_message = f'tecnico "{tecnico_selecionado.nome}" selecionado com sucesso!'
            
            # If it's an HTMX request, return a partial response
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="alert alert-success">{success_message}</div>'
                )
            messages.success(request, success_message)
        else:
            error_message = 'Por favor, selecione um tecnico.'
            
            # If it's an HTMX request, return a partial response
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f'<div class="alert alert-danger">{error_message}</div>', 
                    status=400
                )
            
            messages.error(request, error_message)
    except Tecnico.DoesNotExist:
        messages.error(request, 'Tecnico não encontrado.')
    except Exception as e:
        messages.error(request, f'Erro ao selecionar tecnico: {str(e)}')
    return context

def _handle_site_selection(request, context):
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


def _handle_data_selection(request, context):
        
        data = request.POST.get('data')
        request.session['data'] = data
        success_message = f'Data "{data}" salva com sucesso!'

        request.session['selected_data'] = data

        # If it's an HTMX request, return a partial response
        if request.headers.get('HX-Request'):
            return HttpResponse(
                f'<div class="alert alert-success">{success_message}</div>'
            )

        messages.success(request, success_message)
    
        return context 

def _handle_upload_photos(request, context):
    try:
        # Retrieve session and related objects
        relatorio_id = request.session.get('relatorio_id')
        if not relatorio_id:
            messages.error(request, 'Sessão inválida. Por favor, recarregue a página.')
            return context

        # Fetch related objects with error handling
        try:
            relatorio = RelatorioFinal.objects.select_related('idsitio', 'idtemplate_relatorio').get(idrelatorio_final=relatorio_id)
        except RelatorioFinal.DoesNotExist:
            messages.error(request, 'Relatório não encontrado.')
            return context

        # Get template photo requirements
        template_fotos = relatorio.idtemplate_relatorio.pedidos_fotos.filter(descricao__isnull=False)
        
        # Validate file uploads
        uploaded_files = request.FILES.getlist('foto')
        if not uploaded_files:
            messages.error(request, 'Nenhuma foto foi enviada.')
            return context

        # Limit uploads to template requirements
        if len(uploaded_files) > template_fotos.count():
            messages.warning(request, f'Limite de {template_fotos.count()} foto(s) excedido. Serão consideradas apenas as primeiras.')
            uploaded_files = uploaded_files[:template_fotos.count()]

        # Process uploaded files
        fotos_adicionadas = []
        for uploaded_file, pedido_foto in zip(uploaded_files, template_fotos):
            # Validate file type and size if needed
            # Example: 
            # if not _is_valid_image(uploaded_file):
            #     messages.error(request, f'Arquivo inválido: {uploaded_file.name}')
            #     continue

            # Create and save Foto instance
            foto = Foto.objects.create(
                foto=uploaded_file,
                idsitio=relatorio.idsitio,
                nome=uploaded_file.name,
                descricao=pedido_foto.descricao
            )
            
            # Add foto to RelatorioFinal
            relatorio.fotos.add(foto)
            fotos_adicionadas.append(foto)

        # Ensure many-to-many relationship is saved
        if fotos_adicionadas:
            relatorio.save()
            messages.success(request, f'{len(fotos_adicionadas)} foto(s) adicionada(s) com sucesso.')
            context['fotos_adicionadas'] = fotos_adicionadas

        # Handle HTMX request
        if request.headers.get('HX-Request'):
            return render_to_string('partials/template_selected.html', context)

        return context

    except Exception as e:
        # Log the full exception for debugging
        messages.error(request, f'Erro ao fazer upload das fotos. Por favor, tente novamente.')
        return context