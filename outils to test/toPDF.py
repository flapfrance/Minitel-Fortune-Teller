from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas

# Funktion zum Erstellen der PDF
def create_pdf(output_filename):
    # Dokument erstellen mit benutzerdefinierten Seitenmaßen
    width, height = 152 , 600
    doc = SimpleDocTemplate(output_filename, pagesize=(width, height), leftMargin=0, rightMargin=0, topMargin=0, bottomMargin=0)

    # Styles für den Text
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        'CustomStyle',
        parent=styles['Normal'],
        fontSize=6,
        leftIndent=10,
        topIndent=height - 30
    )

    # Inhalt des Dokuments
    content = []

    # Text hinzufügen
    text = "Hallo, dies ist ein Beispieltext für die PDF."
    content.append(Paragraph(text, custom_style))

    # Grafik hinzufügen
    image_path = "fortune.png"
    image = Image(image_path, width=300, height=200)
    
    # Position der Grafik anpassen
    image.drawWidth = 140
    image.drawHeight = 30
    content.append(image)

    # Das Dokument erstellen und speichern
    doc.build(content)

# PDF erstellen
output_filename = "beispiel.pdf"
create_pdf(output_filename)


