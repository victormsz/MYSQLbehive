from django.contrib import messages
from ..models import TemplateRelatorio, Sitio, Tecnico, RelatorioFinal
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

    
def create_final_report(request, context={}):
    try:
        # Get template and sitio from session or form
        template = TemplateRelatorio.objects.get(idtemplate_relatorio=request.session.get('selected_template_id'))
        sitio = Sitio.objects.get(idsitio=request.session.get('selected_sitio_id'))
        tecnico = Tecnico.objects.get(idtecnico=request.session.get('selected_tecnico_id'))

        if not template or not sitio:
            messages.error(request, 'Template ou Sítio não selecionados.')
            return context

        relatorio = RelatorioFinal.objects.create(
            nome=request.session.get('relatorio_nome'),
            tecnico_responsavel=tecnico,
            idsitio=sitio,
            idtemplate_relatorio=template,
            data=request.session.get('selected_data')
        )

        # Store relatorio_id in session for subsequent steps
        request.session['relatorio_id'] = relatorio.idrelatorio_final

        # Update context
        context['relatorio'] = relatorio
        
        messages.success(request, f'Relatório {relatorio.nome} criado com sucesso. Adicione as fotos agora')

        # Handle HTMX request if applicable
        if request.headers.get('HX-Request'):
            context['messages'] = messages.get_messages(request)
            return HttpResponse(render_to_string('partials/template_selected.html', context))

        return context

    except TemplateRelatorio.DoesNotExist:
        messages.error(request, 'Template não encontrado.')
    except Sitio.DoesNotExist:
        messages.error(request, 'Sítio não encontrado.')
    except Tecnico.DoesNotExist:
        messages.error(request, 'Técnico não encontrado.')
    except Exception as e:
        messages.error(request, f'Erro ao criar relatório: {str(e)}')

    return context