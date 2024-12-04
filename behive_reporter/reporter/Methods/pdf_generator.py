from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import os

def generate_pdf_report(relatorio):
    """
    Generate PDF from the created report
    """
    try:
        # Generate a unique filename
        filename = f"relatorio_{relatorio.id}_{relatorio.nome}.pdf"
        filepath = os.path.join('media', 'relatorios', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # Styles
        styles = getSampleStyleSheet()

        # Add report details
        story.append(Paragraph(f"Relatório: {relatorio.nome}", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Template: {relatorio.template.nome}", styles['Normal']))
        story.append(Paragraph(f"Técnico: {relatorio.tecnico.nome}", styles['Normal']))
        story.append(Paragraph(f"Sítio: {relatorio.sitio.nome}", styles['Normal']))
        story.append(Paragraph(f"Data: {relatorio.data}", styles['Normal']))

        # Add photos if available
        photos = relatorio.fotos.all()
        for photo in photos:
            try:
                story.append(Paragraph(f"Foto: {photo.nome}", styles['Normal']))
                story.append(Image(photo.arquivo.path, width=4*inch, height=3*inch))
                story.append(Paragraph(f"Foto: {photo.descricao}", styles['Normal']))
            except Exception as img_err:
                print(f"Erro ao adicionar imagem: {img_err}")

        # Build PDF
        doc.build(story)

        return filepath

    except Exception as e:
        print(f"Erro ao gerar PDF: {str(e)}")
        return None