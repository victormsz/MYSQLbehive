from django.test import TestCase
from django.http import HttpResponse

# yourapp/tests/test_views.py

from django.test import TestCase, Client
from django.urls import reverse
from reporter.models import TemplateRelatorio, Administrador, Empresa

class TemplateRelatorioViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create related objects for foreign keys
        administrador = Administrador.objects.create(nome="Admin Test")
        empresa = Empresa.objects.create(nome="Empresa Test")

        # Create mock TemplateRelatorio objects
        cls.template1 = TemplateRelatorio.objects.create(
            nome="Template 1",
            pedidos_fotos=[{'descricao': 'Foto 1'}, {'descricao': 'Foto 2'}],
            administrador=administrador,
            idempresa=empresa
        )
        cls.template2 = TemplateRelatorio.objects.create(
            nome="Template 2",
            pedidos_fotos=[{'descricao': 'Foto 3'}],
            administrador=administrador,
            idempresa=empresa
        )

    def test_template_relatorio_view_get(self):
        client = Client()

        # Test the GET request
        response = client.get(reverse('selecionar_template')) 
        self.assertEqual(response.status_code, 200, "View did not return a 200 status code.")

        # Check if templates are passed in the context
        templates = response.context['templates']
        self.assertEqual(templates.count(), 2, "The view should pass 2 templates to the context.")

        # Validate the content of the templates
        self.assertIn(self.template1, templates, "Template 1 should be in the context.")
        self.assertIn(self.template2, templates, "Template 2 should be in the context.")

    def test_template_relatorio_view_post(self):
        client = Client()

        # Test the POST request with a selected template
        response = client.post(reverse('selecionar_template'), data={'template': self.template1.idtemplate_relatorio})
        self.assertEqual(response.status_code, 200, "View did not return a 200 status code on POST.")

        # Check selected template in the context
        selected_template = response.context['template_selecionado']
        self.assertEqual(selected_template, self.template1, "Selected template is incorrect.")

        # Check template_fotos data
        template_fotos = response.context['template_fotos']
        self.assertEqual(len(template_fotos), 2, "Template 1 should have 2 fotos.")
        self.assertEqual(template_fotos[0]['descricao'], 'Foto 1', "First foto description is incorrect.")

