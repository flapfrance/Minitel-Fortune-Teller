#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# V1.4 database prefs replaced by settings.ini file
# Thanks to Oceane, JS, Montaulab, Claudine, CQuest, Musée du minitel....
# And the Wishwizardteam Olli, Holger, Mephy und allen anderen.
# *************************************************************
import configparser
import csv
import json
import os
import random
import socket
import subprocess
import sys
import time
import unicodedata
from io import BytesIO
from datetime import datetime
from threading import Thread

import pyhid_usb_relay
import pynitel
import qrcode
import requests
import serial
import serial.tools.list_ports
from numpy import array
from PIL import Image as Image1
from PIL import ImageFilter, ImageOps
from openai import OpenAI
from escpos.printer import Usb
from kerykeion import AstrologicalSubjectFactory, ChartDataFactory, ChartDrawer, to_context
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Image, Spacer, HRFlowable,
    Table, TableStyle, PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from xml.sax.saxutils import escape


kanye = None
kanye_partner = None
natal_chart_data = None
astrology_context = ""
analysis_mode = "individual"
partner_people = []
current_person_index = 1
ser = None
run = True
coin_counter_enabled = False
coin_reset_until = 0.0
COIN_RESET_GUARD_SECONDS = 2.0
PRINTER_WARMUP_SECONDS = 0.5
PRINTER_DRAIN_SECONDS = 1.0
PDF_UPLOAD_ATTEMPTS = 3
PDF_UPLOAD_RETRY_SECONDS = 2.0

# Runtime objects are initialized explicitly and populated during main()/stateInit().
m = None
p = None
pV = False
relay = None
client = None
thread_0 = None
thread_1 = None
data = {}
dataCC = {}
data_p = []
lang = 'FR'
lang2 = 'FR'
sltime = 120
answer = ''
pdf_answer = ''
upload = False
link = ''
z = None
pdf_delivery_thread = None
pdf_delivery_error = ''
pending_pdf_filename = ''
pdf_delivery_job = None
chart_cache_subject = None
chart_pdf_png_cache = None
chart_thermal_image_cache = None


OUTPUT_CHARACTER_REPLACEMENTS = str.maketrans({
    # OpenAI commonly returns typographic punctuation which neither the
    # Minitel nor the printer's CP850 code page can represent reliably.
    '\u2018': "'", '\u2019': "'", '\u201a': "'", '\u201b': "'",
    '\u02bc': "'", '\u00b4': "'", '`': "'",
    '\u201c': '"', '\u201d': '"', '\u201e': '"', '\u201f': '"',
    '\u2013': '-', '\u2014': '-', '\u2212': '-',
    '\u2026': '...', '\u2022': '*',
    '\u00a0': ' ', '\u202f': ' ', '\u200b': '', '\u00ad': '',
    '\u0153': 'oe', '\u0152': 'Oe',
})


def normalize_output_text(text):
    """Convert Unicode typography to characters supported by all outputs."""
    if text is None:
        return ""
    text = unicodedata.normalize('NFC', str(text))
    return text.translate(OUTPUT_CHARACTER_REPLACEMENTS)


def strip_analysis_markup(text):
    """Remove PDF section markers for the plain-text Minitel output."""
    lines = []
    for line in normalize_output_text(text).splitlines():
        stripped = line.lstrip()
        if stripped.startswith('## '):
            prefix_length = len(line) - len(stripped)
            line = line[:prefix_length] + stripped[3:]
        lines.append(line)
    return '\n'.join(lines)


####

# Utility functions
####
PDF_TEXT = {
    'DE': {
        'individual': 'Deine astrologische Analyse',
        'partner': 'Eure astrologische Partneranalyse',
        'section': 'Deutung & Ausblick',
        'chart': 'Astrologische Konstellation',
        'data': 'Basisdaten',
        'sun': 'Sonne',
        'ascendant': 'Aszendent',
    },
    'FR': {
        'individual': 'Votre analyse astrologique',
        'partner': 'Votre analyse astrologique de couple',
        'section': 'Interpretation & perspectives',
        'chart': 'Constellation astrologique',
        'data': 'Donnees de naissance',
        'sun': 'Soleil',
        'ascendant': 'Ascendant',
    },
    'ES': {
        'individual': 'Tu analisis astrologico',
        'partner': 'Vuestro analisis astrologico de pareja',
        'section': 'Interpretacion y perspectivas',
        'chart': 'Constelacion astrologica',
        'data': 'Datos de nacimiento',
        'sun': 'Sol',
        'ascendant': 'Ascendente',
    },
    'EN': {
        'individual': 'Your astrological analysis',
        'partner': 'Your astrological partner analysis',
        'section': 'Interpretation & outlook',
        'chart': 'Astrological constellation',
        'data': 'Birth details',
        'sun': 'Sun',
        'ascendant': 'Ascendant',
    },
}

PDF_ZODIAC = {
    'DE': {'Ari': 'Widder', 'Tau': 'Stier', 'Gem': 'Zwillinge', 'Can': 'Krebs', 'Leo': 'Loewe', 'Vir': 'Jungfrau', 'Lib': 'Waage', 'Sco': 'Skorpion', 'Sag': 'Schuetze', 'Cap': 'Steinbock', 'Aqu': 'Wassermann', 'Pis': 'Fische'},
    'FR': {'Ari': 'Belier', 'Tau': 'Taureau', 'Gem': 'Gemeaux', 'Can': 'Cancer', 'Leo': 'Lion', 'Vir': 'Vierge', 'Lib': 'Balance', 'Sco': 'Scorpion', 'Sag': 'Sagittaire', 'Cap': 'Capricorne', 'Aqu': 'Verseau', 'Pis': 'Poissons'},
    'ES': {'Ari': 'Aries', 'Tau': 'Tauro', 'Gem': 'Geminis', 'Can': 'Cancer', 'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Escorpio', 'Sag': 'Sagitario', 'Cap': 'Capricornio', 'Aqu': 'Acuario', 'Pis': 'Piscis'},
    'EN': {'Ari': 'Aries', 'Tau': 'Taurus', 'Gem': 'Gemini', 'Can': 'Cancer', 'Leo': 'Leo', 'Vir': 'Virgo', 'Lib': 'Libra', 'Sco': 'Scorpio', 'Sag': 'Sagittarius', 'Cap': 'Capricorn', 'Aqu': 'Aquarius', 'Pis': 'Pisces'},
}

ANALYSIS_DISCLAIMER = {
    'DE': (
        "Diese astrologische Analyse dient ausschließlich der Unterhaltung und "
        "persönlichen Reflexion, ist unverbindlich und ersetzt keine medizinische, "
        "psychologische, rechtliche oder finanzielle Beratung; deine Entscheidungen "
        "triffst du eigenverantwortlich."
    ),
    'FR': (
        "Cette analyse astrologique est proposée uniquement à des fins de divertissement "
        "et de réflexion personnelle, reste sans engagement et ne remplace aucun conseil "
        "médical, psychologique, juridique ou financier ; vous prenez vos décisions sous "
        "votre propre responsabilité."
    ),
    'ES': (
        "Este análisis astrológico se ofrece únicamente con fines de entretenimiento y "
        "reflexión personal, no es vinculante ni sustituye el asesoramiento médico, "
        "psicológico, jurídico o financiero; tomas tus decisiones bajo tu propia "
        "responsabilidad."
    ),
    'EN': (
        "This astrological analysis is provided solely for entertainment and personal "
        "reflection, is non-binding, and does not replace medical, psychological, legal, "
        "or financial advice; you remain responsible for your own decisions."
    ),
}


PRINT_INFO_TEXT = {
    'DE': 'Weitere Informationen unter:',
    'FR': "Plus d'informations sur :",
    'ES': 'Mas informacion en:',
    'EN': 'More information at:',
}

THERMAL_DATA_BOX_WIDTH = 48


def analysis_disclaimer(language_code=None):
    """Return the friendly scope notice in the selected output language."""
    code = str(language_code or lang2 or 'EN').upper()
    return ANALYSIS_DISCLAIMER.get(code, ANALYSIS_DISCLAIMER['EN'])


def print_info_text(language_code=None):
    """Return the website prompt in the selected output language."""
    code = str(language_code or lang2 or 'EN').upper()
    return PRINT_INFO_TEXT.get(code, PRINT_INFO_TEXT['EN'])


def thermal_birth_data_box(language_code=None):
    """Build a compact receipt box matching the PDF birth-data panel."""
    code = str(language_code or lang2 or 'EN').upper()
    labels = PDF_TEXT.get(code, PDF_TEXT['EN'])
    zodiac_names = PDF_ZODIAC.get(code, PDF_ZODIAC['EN'])
    subjects = [kanye] if kanye is not None else []
    if analysis_mode == 'partner' and kanye_partner is not None:
        subjects.append(kanye_partner)
    if not subjects:
        return []

    inner_width = THERMAL_DATA_BOX_WIDTH - 2
    border = '+' + '-' * inner_width + '+'

    def boxed(text='', centered=False):
        chunks = split_string_into_lines(
            normalize_output_text(text), max_line_length=inner_width - 2
        ) or ['']
        rows = []
        for chunk in chunks:
            content = chunk.center(inner_width) if centered else (' ' + chunk).ljust(inner_width)
            rows.append('|' + content[:inner_width] + '|')
        return rows

    lines = [border]
    lines.extend(boxed(labels['data'].upper(), centered=True))
    lines.append(border)
    for index, subject in enumerate(subjects):
        if index:
            lines.append('|' + '-' * inner_width + '|')
        lines.extend(boxed(normalize_output_text(subject.name), centered=True))
        lines.extend(boxed(
            f"{int(subject.day):02d}.{int(subject.month):02d}.{int(subject.year):04d}  "
            f"{int(subject.hour):02d}:{int(subject.minute):02d}",
            centered=True,
        ))
        place = ' / '.join(
            part for part in (
                normalize_output_text(subject.city or '').strip(),
                normalize_output_text(subject.nation or '').strip(),
            ) if part
        )
        if place:
            lines.extend(boxed(place, centered=True))
        sun = zodiac_names.get(subject.sun.sign)
        if sun is None:
            sun = signs(subject.sun.sign)
        ascendant = zodiac_names.get(subject.first_house.sign)
        if ascendant is None:
            ascendant = signs(subject.first_house.sign)
        lines.extend(boxed(
            f"{labels['sun']}: {sun}  |  {labels['ascendant']}: {ascendant}",
            centered=True,
        ))
    lines.append(border)
    return lines


def register_pdf_fonts():
    """Use DejaVu when available and otherwise fall back to built-in fonts."""
    regular = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    if os.path.isfile(regular) and os.path.isfile(bold):
        if 'FortuneSans' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('FortuneSans', regular))
            pdfmetrics.registerFont(TTFont('FortuneSans-Bold', bold))
            pdfmetrics.registerFontFamily(
                'FortuneSans', normal='FortuneSans', bold='FortuneSans-Bold'
            )
        return 'FortuneSans', 'FortuneSans-Bold'
    return 'Helvetica', 'Helvetica-Bold'


def create_pdf(output_filename, text, pdf_context=None):
    """Create a polished, standard A4 PDF for upload and download."""
    global lang2, analysis_mode
    pdf_context = pdf_context or {}
    text = normalize_output_text(text)
    zz = random.randint(1, 24)
    language_code = str(pdf_context.get('language_code', lang2)).upper()
    labels = PDF_TEXT.get(language_code, PDF_TEXT['EN'])
    pdf_analysis_mode = pdf_context.get('analysis_mode', analysis_mode)
    title = labels['partner' if pdf_analysis_mode == 'partner' else 'individual']
    subject_name = normalize_output_text(
        pdf_context.get('subject_name', data_p[0] if data_p else '')
    )
    regular_font, bold_font = register_pdf_fonts()

    page_width, page_height = A4
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=19 * mm,
        rightMargin=19 * mm,
        topMargin=17 * mm,
        bottomMargin=20 * mm,
        title=title,
        author='Wish Wizard',
        subject=subject_name,
    )

    dark = colors.HexColor('#17202A')
    muted = colors.HexColor('#66707A')
    accent = colors.HexColor('#3A8D72')
    gold = colors.HexColor('#B28A52')

    styles = getSampleStyleSheet()
    kicker_style = ParagraphStyle(
        'FortuneKicker', parent=styles['Normal'], fontName=bold_font,
        fontSize=8.5, leading=11, textColor=accent, alignment=TA_CENTER,
        spaceAfter=3 * mm,
    )
    title_style = ParagraphStyle(
        'FortuneTitle', parent=styles['Title'], fontName=bold_font,
        fontSize=23, leading=28, textColor=dark, alignment=TA_CENTER,
        spaceAfter=2.5 * mm,
    )
    subject_style = ParagraphStyle(
        'FortuneSubject', parent=styles['Normal'], fontName=regular_font,
        fontSize=12, leading=16, textColor=muted, alignment=TA_CENTER,
        spaceAfter=5 * mm,
    )
    chart_caption_style = ParagraphStyle(
        'FortuneChartCaption', parent=styles['Normal'], fontName=bold_font,
        fontSize=8.5, leading=11, textColor=muted, alignment=TA_CENTER,
        spaceBefore=2 * mm, spaceAfter=5 * mm,
    )
    data_heading_style = ParagraphStyle(
        'FortuneDataHeading', parent=styles['Normal'], fontName=bold_font,
        fontSize=8.5, leading=11, textColor=gold, alignment=TA_CENTER,
        spaceAfter=2.5 * mm,
    )
    data_style = ParagraphStyle(
        'FortuneData', parent=styles['Normal'], fontName=regular_font,
        fontSize=8.5, leading=12.5, textColor=dark, alignment=TA_CENTER,
    )
    section_style = ParagraphStyle(
        'FortuneSection', parent=styles['Heading2'], fontName=bold_font,
        fontSize=14, leading=18, textColor=dark,
        spaceBefore=2 * mm, spaceAfter=3.5 * mm,
    )
    body_style = ParagraphStyle(
        'FortuneBody', parent=styles['BodyText'], fontName=regular_font,
        fontSize=10.5, leading=16, textColor=dark, alignment=TA_JUSTIFY,
        spaceAfter=3.5 * mm,
    )
    analysis_heading_style = ParagraphStyle(
        'FortuneAnalysisHeading', parent=styles['Heading3'], fontName=bold_font,
        fontSize=11.5, leading=15, textColor=accent,
        spaceBefore=3.5 * mm, spaceAfter=1.5 * mm,
    )
    disclaimer_style = ParagraphStyle(
        'FortuneDisclaimer', parent=styles['Normal'], fontName=regular_font,
        fontSize=8.2, leading=12, textColor=muted, alignment=TA_CENTER,
    )
    content = []
    logo = Image('./WM/fortune.png', width=104 * mm, height=(104 * 70 / 380) * mm)
    logo.hAlign = 'CENTER'
    content.extend([
        logo,
        Spacer(1, 3 * mm),
        Paragraph('PERSONAL ASTROLOGY', kicker_style),
        Paragraph(escape(title), title_style),
        Paragraph(escape(subject_name), subject_style),
        HRFlowable(width='100%', thickness=0.7, color=gold, spaceAfter=5 * mm),
    ])

    primary_subject = pdf_context.get('primary_subject', kanye)
    partner_subject = pdf_context.get('partner_subject', kanye_partner)
    subjects = [primary_subject]
    if pdf_analysis_mode == 'partner' and partner_subject is not None:
        subjects.append(partner_subject)
    zodiac_names = PDF_ZODIAC.get(language_code, PDF_ZODIAC['EN'])
    data_cells = []
    for subject in subjects:
        birth_date = (
            f"{int(subject.day):02d}.{int(subject.month):02d}.{int(subject.year):04d}"
            f" &nbsp;&middot;&nbsp; {int(subject.hour):02d}:{int(subject.minute):02d}"
        )
        place_parts = [str(subject.city or '').strip(), str(subject.nation or '').strip()]
        place = ' &nbsp;&middot;&nbsp; '.join(
            escape(part) for part in place_parts if part
        )
        sun = zodiac_names.get(subject.sun.sign)
        if sun is None:
            sun = signs(subject.sun.sign)
        ascendant = zodiac_names.get(subject.first_house.sign)
        if ascendant is None:
            ascendant = signs(subject.first_house.sign)
        details = (
            '<b>' + escape(normalize_output_text(subject.name)) + '</b><br/>' +
            birth_date + '<br/>' + place + '<br/>' +
            escape(labels['sun']) + ': ' + escape(sun) +
            ' &nbsp;&middot;&nbsp; ' + escape(labels['ascendant']) + ': ' + escape(ascendant)
        )
        data_cells.append(Paragraph(details, data_style))

    content.append(Paragraph(escape(labels['data']).upper(), data_heading_style))
    data_table = Table(
        [data_cells],
        colWidths=[doc.width / len(data_cells)] * len(data_cells),
    )
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F3EE')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#D8C5A7')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#D8C5A7')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5 * mm),
        ('TOPPADDING', (0, 0), (-1, -1), 3 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3 * mm),
    ]))
    content.extend([data_table, Spacer(1, 4 * mm)])

    try:
        chart_stream = create_pdf_chart_image(pdf_context)
        if chart_stream is not None:
            chart = Image(chart_stream, width=126 * mm, height=126 * mm)
            chart.hAlign = 'CENTER'
            content.append(chart)
            content.append(Paragraph(escape(labels['chart']).upper(), chart_caption_style))
    except Exception as error:
        # The analysis PDF remains available even if an optional renderer is
        # missing on a development machine.
        print('PDF astrology chart was not included:', error)

    # The cover page intentionally contains only title, birth data, and chart.
    content.append(PageBreak())
    content.append(Paragraph(escape(labels['section']), section_style))
    content.append(HRFlowable(width='100%', thickness=0.5, color=gold, spaceAfter=3 * mm))

    body_lines = []

    def append_body_lines():
        if not body_lines:
            return
        paragraph = ' '.join(part.strip() for part in body_lines if part.strip())
        if paragraph:
            content.append(Paragraph(escape(paragraph), body_style))
        body_lines.clear()

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('## '):
            append_body_lines()
            heading = stripped[3:].strip()
            if heading:
                content.append(Paragraph(escape(heading), analysis_heading_style))
        elif not stripped:
            append_body_lines()
        else:
            body_lines.append(stripped)
    append_body_lines()

    disclaimer_box = Table(
        [[Paragraph(escape(analysis_disclaimer(language_code)), disclaimer_style)]],
        colWidths=[doc.width],
    )
    disclaimer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F3EE')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D8C5A7')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6 * mm),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6 * mm),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5 * mm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5 * mm),
    ]))
    content.extend([Spacer(1, 5 * mm), disclaimer_box])

    def decorate_page(pdf_canvas, document):
        pdf_canvas.saveState()
        pdf_canvas.setFillColor(accent)
        pdf_canvas.rect(0, page_height - 3 * mm, page_width, 3 * mm, fill=1, stroke=0)
        if document.page > 1:
            pdf_canvas.setFont(bold_font, 7.5)
            pdf_canvas.setFillColor(muted)
            pdf_canvas.drawString(19 * mm, page_height - 10 * mm, title.upper())
            pdf_canvas.setFont(regular_font, 7.5)
            pdf_canvas.drawRightString(
                page_width - 19 * mm, page_height - 10 * mm, subject_name
            )
        pdf_canvas.setStrokeColor(colors.HexColor('#D8D4CC'))
        pdf_canvas.setLineWidth(0.4)
        pdf_canvas.line(19 * mm, 13 * mm, page_width - 19 * mm, 13 * mm)
        pdf_canvas.setFont(regular_font, 7.5)
        pdf_canvas.setFillColor(muted)
        pdf_canvas.drawString(19 * mm, 8.5 * mm, 'www.x-tra.art | FORTUNE TELLER')
        pdf_canvas.drawRightString(
            page_width - 19 * mm, 8.5 * mm, str(document.page)
        )
        pdf_canvas.restoreState()

    doc.build(content, onFirstPage=decorate_page, onLaterPages=decorate_page)
    return(zz)

def generate_unique_filename(file_path):
    # Holen Sie den Basisnamen der Datei ohne Pfad
    file_name = os.path.basename(file_path)
    file_name = file_name.replace(" ", "_")
    # Generieren Sie einen eindeutigen Dateinamen basierend auf dem aktuellen Datum und der Uhrzeit
    unique_name = datetime.now().strftime("%Y-%m-%d_%H-%M_") + file_name
    return unique_name


def pdf_delivery_settings():
    """Return normalized upload and public PDF URLs from settings.ini."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    upload_url = config.get('pdf', 'upload_url', fallback='').strip()
    public_base_url = config.get('pdf', 'public_base_url', fallback='').strip()
    if not upload_url or not public_base_url:
        raise RuntimeError(
            "PDF upload_url and public_base_url must be set in settings.ini"
        )
    return upload_url, public_base_url.rstrip('/') + '/'


def public_pdf_link(filename):
    """Build the public download link using the configured base URL."""
    _, public_base_url = pdf_delivery_settings()
    return public_base_url + str(filename).lstrip('/')

def upload_pdf_to_server(pdf_file_path, unique_filename=None, publish_state=True):
    global upload, link
    upload_url, public_base_url = pdf_delivery_settings()

    if unique_filename is None:
        unique_filename = generate_unique_filename(pdf_file_path)

    if publish_state and upload and link:
        return link

    for attempt in range(1, PDF_UPLOAD_ATTEMPTS + 1):
        try:
            # Reopen the file for every attempt so a failed request can never
            # leave the stream positioned partway through the PDF.
            with open(pdf_file_path, 'rb') as pdf_file:
                files = {'file': (unique_filename, pdf_file)}
                response = requests.post(upload_url, files=files, timeout=30)
            response.raise_for_status()
            break
        except requests.RequestException as error:
            if attempt >= PDF_UPLOAD_ATTEMPTS:
                print(
                    f"PDF upload failed after {attempt} attempts: {error}"
                )
                raise
            print(
                f"PDF upload attempt {attempt}/{PDF_UPLOAD_ATTEMPTS} "
                f"failed: {error}; retrying"
            )
            time.sleep(PDF_UPLOAD_RETRY_SECONDS)

    uploaded_link = public_base_url + unique_filename
    print("Datei erfolgreich hochgeladen.")
    print("Die Datei ist unter folgendem Link verfügbar:", uploaded_link)
    os.remove(pdf_file_path)
    print("Ursprüngliche Datei erfolgreich gelöscht:", pdf_file_path)
    if publish_state:
        link = uploaded_link
        upload = True
    return uploaded_link

def listener():
    """Wait for the coin counter to authorize one consultation."""
    global run, ser, coin_reset_until
    if ser is None:
        return

    print("Coin counter listener started:", ser.port)
    try:
        while True:
            data = ser.readline().decode('utf-8').strip()
            if not data:
                continue
            print("Read from coin counter:", data)

            # Firmware variants use CMD:WAIT, WAIT or WAIT_FOR_OK once the
            # required credit has been reached. OK is deliberately excluded:
            # it is our reset command and must not grant another consultation.
            if data in ("CMD:WAIT", "WAIT", "WAIT_FOR_OK"):
                if time.monotonic() < coin_reset_until:
                    print("Ignoring coin signal generated during counter reset")
                else:
                    run = True
                    print("Coin accepted; consultation enabled")
    except (serial.SerialException, UnicodeDecodeError) as error:
        run = False
        print("Coin counter listener stopped:", error)


def find_arduino_port():
    """Open the first serial device identified as an Arduino."""
    global ser
    print("Looking for coin counter")
    try:
        arduino_ports = [
            port.device for port in serial.tools.list_ports.comports()
            if 'Arduino' in port.description
        ]
    except serial.SerialException as error:
        print("Could not scan serial ports:", error)
        return None

    if not arduino_ports:
        print("Coin counter Arduino not found")
        return None
    if len(arduino_ports) > 1:
        print("More than one Arduinos found. Use the first one.")
    arduino_port = arduino_ports[0]
    try:
        ser = serial.Serial(arduino_port, 19200)
        print("Coin counter connected:", arduino_port)
        return ser
    except serial.SerialException as error:
        print("Could not open coin counter:", error)
        ser = None
        return None


def complete_coin_transaction():
    """Consume the current credit and prepare the counter for the next coin."""
    global run, coin_reset_until
    if not coin_counter_enabled:
        run = True
        return

    run = False
    # Some firmware revisions emit one stale WAIT directly after processing
    # OK. Do not let that reset artifact authorize a free consultation.
    coin_reset_until = time.monotonic() + COIN_RESET_GUARD_SECONDS
    if ser is not None and ser.is_open:
        try:
            ser.write(b"OK\n")
            ser.flush()
            print("Coin counter transaction completed")
        except serial.SerialException as error:
            print("Could not complete coin counter transaction:", error)

def get_data_astro(dat_ast, lan):
    global kanye, language, natal_chart_data, astrology_context
    kanye = None
    try:
        # The factory API is the supported Kerykeion v5 interface. With city and
        # country set and online=True, Kerykeion resolves coordinates/timezone.
        kanye = AstrologicalSubjectFactory.from_birth_data(*dat_ast, online=True)
        natal_chart_data = ChartDataFactory.create_natal_chart_data(kanye)
        astrology_context = to_context(natal_chart_data)
        print("Astrological subject:", kanye.name)

    except Exception as error:
        m.home()
        m.message(20, 5, 3, "There is an issue with your data, please try again")
        print("Kerykeion error:", error)
        return("Error")

    try:
        print("In try: ", lan)
        language = get_language_by_country_code(lan)
        print("language", language)
    except Exception as error:
        print("Language lookup error:", error)
        m.home()
        m.message(20, 5, 3, "There is an issue with your language data, please try again")
        return("Error")


def get_partner_data_astro(first_subject, second_subject, lan):
    """Prepare Kerykeion synastry data and AI context for two subjects."""
    global kanye, kanye_partner, language, natal_chart_data, astrology_context
    try:
        natal_chart_data = ChartDataFactory.create_synastry_chart_data(
            first_subject,
            second_subject,
            include_relationship_score=True,
            include_house_comparison=True,
        )
        astrology_context = to_context(natal_chart_data)
        kanye = first_subject
        kanye_partner = second_subject
        language = get_language_by_country_code(lan)
        print("Synastry subjects:", kanye.name, "and", kanye_partner.name)
        return None
    except Exception as error:
        m.home()
        m.message(20, 5, 3, "There is an issue with your data, please try again")
        print("Kerykeion synastry error:", error)
        return "Error"


def astrology_chart_enabled():
    """Return the optional thermal-chart setting, defaulting safely to off."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.getboolean('astrology', 'print_chart', fallback=False)


def prepare_thermal_chart(chart, chart_width, threshold=200, line_boost=1):
    """Flatten, resize and binarize a chart for a 1-bit thermal printer."""
    rgba_chart = chart.convert('RGBA')
    white_background = Image1.new('RGB', rgba_chart.size, 'white')
    white_background.paste(rgba_chart, mask=rgba_chart.getchannel('A'))

    chart = white_background.convert('L')
    if chart.size != (chart_width, chart_width):
        resampling = getattr(Image1, 'Resampling', Image1).LANCZOS
        chart = chart.resize((chart_width, chart_width), resampling)
    chart = ImageOps.autocontrast(chart)

    # Expanding dark pixels by one dot keeps fine aspect and house lines visible.
    line_boost = max(0, min(line_boost, 2))
    if line_boost:
        chart = chart.filter(ImageFilter.MinFilter(line_boost * 2 + 1))

    threshold = max(0, min(threshold, 255))
    return chart.point(lambda pixel: 255 if pixel > threshold else 0, mode='1')


def render_astrology_chart_png(
        theme, style, render_width, show_zodiac_background, pdf_context=None):
    """Render the active natal or synastry chart to high-resolution PNG bytes."""
    pdf_context = pdf_context or {}
    primary_subject = pdf_context.get('primary_subject', kanye)
    chart_data = pdf_context.get('chart_data', natal_chart_data)
    if primary_subject is None:
        raise RuntimeError("No astrological subject is available")

    try:
        import cairosvg
    except ImportError as error:
        raise RuntimeError(
            "Astrology chart rendering needs CairoSVG (pip install cairosvg)"
        ) from error

    config = configparser.ConfigParser()
    config.read('settings.ini')
    chart_language = config.get('astrology', 'chart_language', fallback='AUTO').upper()
    if chart_language == 'AUTO':
        chart_language = str(pdf_context.get('language_code', lang2)).upper()
    if chart_language not in {'EN', 'FR', 'PT', 'IT', 'CN', 'ES', 'RU', 'TR', 'DE', 'HI'}:
        chart_language = 'EN'

    valid_themes = {'light', 'dark', 'dark-high-contrast', 'classic', 'strawberry', 'black-and-white'}
    if theme not in valid_themes:
        theme = 'classic'
    style = str(style).lower()
    if style not in {'classic', 'modern'}:
        style = 'modern'
    render_width = max(600, min(int(render_width), 3000))
    chart_data = (
        chart_data
        if chart_data is not None
        else ChartDataFactory.create_natal_chart_data(primary_subject)
    )
    drawer = ChartDrawer(
        chart_data,
        theme=theme,
        chart_language=chart_language,
        transparent_background=False,
    )
    svg = drawer.generate_wheel_only_svg_string(
        remove_css_variables=True,
        style=style,
        show_zodiac_background_ring=show_zodiac_background,
    )
    return cairosvg.svg2png(
        bytestring=svg.encode('utf-8'),
        output_width=render_width,
        output_height=render_width,
    )


def create_pdf_chart_image(pdf_context=None):
    """Return a high-resolution color chart stream for the upload PDF."""
    global chart_pdf_png_cache
    pdf_context = pdf_context or {}
    config = configparser.ConfigParser()
    config.read('settings.ini')
    if not config.getboolean('pdf', 'include_chart', fallback=True):
        return None

    if pdf_context:
        cached_png = pdf_context.get('chart_pdf_png')
    else:
        reset_chart_cache_for_current_subject()
        cached_png = chart_pdf_png_cache
    if cached_png is not None:
        return BytesIO(cached_png)

    theme = config.get('pdf', 'chart_theme', fallback='classic')
    style = config.get('pdf', 'chart_style', fallback='modern')
    resolution = config.getint('pdf', 'chart_resolution', fallback=1600)
    show_zodiac_background = config.getboolean(
        'pdf', 'chart_zodiac_background', fallback=True
    )
    png = render_astrology_chart_png(
        theme, style, resolution, show_zodiac_background, pdf_context
    )
    if pdf_context:
        pdf_context['chart_pdf_png'] = png
    else:
        chart_pdf_png_cache = png
    stream = BytesIO(png)
    stream.seek(0)
    return stream


def create_astrology_chart_image():
    """Render the current natal or synastry wheel for the thermal printer."""
    global chart_thermal_image_cache
    if not astrology_chart_enabled():
        return None

    reset_chart_cache_for_current_subject()
    if chart_thermal_image_cache is not None:
        return chart_thermal_image_cache.copy()

    config = configparser.ConfigParser()
    config.read('settings.ini')
    theme = config.get('astrology', 'chart_theme', fallback='black-and-white')
    style = config.get('astrology', 'chart_style', fallback='modern')
    chart_width = config.getint('astrology', 'chart_width', fallback=380)
    chart_width = max(200, min(chart_width, 1024))
    render_scale = config.getint('astrology', 'chart_render_scale', fallback=3)
    render_scale = max(1, min(render_scale, 4))
    threshold = config.getint('astrology', 'chart_threshold', fallback=200)
    line_boost = config.getint('astrology', 'chart_line_boost', fallback=1)
    show_zodiac_background = config.getboolean(
        'astrology', 'chart_zodiac_background', fallback=False
    )
    png = render_astrology_chart_png(
        theme,
        style,
        chart_width * render_scale,
        show_zodiac_background,
    )
    with Image1.open(BytesIO(png)) as chart:
        chart_thermal_image_cache = prepare_thermal_chart(
            chart, chart_width, threshold, line_boost
        )
    return chart_thermal_image_cache.copy()


def reset_chart_cache_for_current_subject():
    """Discard rendered assets when a new natal or synastry chart is active."""
    global chart_cache_subject, chart_pdf_png_cache, chart_thermal_image_cache
    if chart_cache_subject is natal_chart_data:
        return
    chart_cache_subject = natal_chart_data
    chart_pdf_png_cache = None
    chart_thermal_image_cache = None


def pre_render_thermal_chart():
    """Prepare only the receipt chart while the OpenAI request is in flight."""
    started = time.monotonic()
    try:
        create_astrology_chart_image()
    except Exception as error:
        print("Thermal astrology chart pre-render failed:", error)
    print(f"Thermal chart prepared in {time.monotonic() - started:.1f} seconds")

def get_language_by_country_code(country_code):
    global  dataCC
    print(dataCC[country_code]) 
    print("Given CCode: " + country_code)
    return dataCC[country_code]["Language"]
    #try:
        #url = f"https://restcountries.com/v2/alpha/{str(country_code)}"
        #response = requests.get(url)

        #if response.status_code == 200:
            #data_count = response.json()
            #languages = data_count.get("languages", [])
            #if languages:
                #return languages[0].get("name", "Unbekannte Sprache")
            #else:
                #return "English"
       # else:
            #return "English"
    #except Exception as e:
        #return "English"


def signs(sign):
    x = ""
    signdata = [["Can", "Cancer"], ["Leo", "Lion"], ["Vir", "Virgo"], ["Lib", "Libra"],
                ["Sco", "Scorpio"], ["Sag", "Sagittarius"], ["Cap", "Capricorn"],
                ["Aqu", "Aquarius"], ["Pis", "Pisces"], ["Ari", "Aries"],
                ["Tau", "Taurus"], ["Gem", "Gemini"]
                ]

    search1 = sign
    for i, sign in enumerate(signdata):
        if search1 in sign[0]:
            x = sign[1]
            print(x)
    return x


# ****** prepare USB relays
def usbRelaysCheck():
    global relay
    relay = None
    try:
        relay = pyhid_usb_relay.find()
        print("USB RELAY connected")
        return True
    except Exception as error:
        print("No USB RELAY found:", error)
        relay = None
        return False


# ****** Write csv datafile to dataobject "data"
def create_data(csv_dateipfad):
    data = {}
    # CSV-Datei öffnen und auslesen
    with open(csv_dateipfad, "r") as csv_datei:
        csv_reader = csv.reader(csv_datei, delimiter=";")
        spaltenueberschriften = next(csv_reader)
        for zeile in csv_reader:
            beschreibung = zeile[0]
            spalten_werte = {}
            for i in range(1, len(zeile)):
                spaltenueberschrift = spaltenueberschriften[i]
                wert = zeile[i]
                spalten_werte[spaltenueberschrift] = wert
            data[beschreibung] = spalten_werte
    return data


# ************Find actual IP in network
def getNetworkIp():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as network_socket:
            network_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            network_socket.connect(('<broadcast>', 0))
            return network_socket.getsockname()[0]
    except OSError as error:
        print("Could not determine network IP:", error)
        return '127.0.0.1'


def getMilliseconds():
    return int(round(time.time() * 1000))


def transl(beschreibung, la = ""):
    global lang, data, lang2
    # Überprüfen, ob die Beschreibung im Datenobjekt vorhanden ist

    if beschreibung in data:
        # Überprüfen, ob die Spaltenüberschrift im Datenobjekt vorhanden ist
        if la == "":
            if lang in data[beschreibung]:
                # Wert aus dem Datenobjekt abrufen und zurückgeben
                wert = data[beschreibung][lang]
                return wert
            else:
                print("Spaltenüberschrift nicht gefunden: ")
                return "problem"
        else:
            if la in data[beschreibung]:
                # Wert aus dem Datenobjekt abrufen und zurückgeben
                wert = data[beschreibung][la]
                return wert
            else:
                print("Spaltenüberschrift nicht gefunden: ")
                return "problem"
    else:
        print("Beschreibung nicht gefunden: ", beschreibung)


def randomFileFromFolder(dossier):  # ****Random audiofile from directory
    lst = os.listdir(dossier)
    f = random.randint(0, len(lst) - 1)
    path = dossier + "%s" % lst[f]  # .split(".")[0]
    print(path)
    return path


# ******Format to left and to right
def strformat(left='', right='', fill=' ', width=40):
    # " formattage de texte "
    total = width - len(left + right)
    if total > 0:
        out = left + fill * total + right
    else:
        out = left + right
    return out


# ******Screenprint centered
def strcenter(row=0, pos=20, txt=' ', width=40, size=0):
    out = pos - len(txt) // 2
    if out < 1:
        out = 1
    m.pos(row, out)
    m.scale(size)
    m._print(txt)
    m.scale(1)
    return ()


def printCheck():
    global p, pV, sltime
    config = configparser.ConfigParser()
    config.read('settings.ini')
    # check the time before the screen automaticly changes ( Screensaver)
    sltime = int(config['prefs']['timer'])

    # A handle opened while showing an earlier page or during startup may have
    # gone stale by the next analysis. Always close it before a real reconnect;
    # keeping that stale handle caused the special-code image transfer to hang.
    if p is not None:
        try:
            p.close()
        except Exception as error:
            print("Old printer connection could not be closed:", error)
    p = None
    pV = False

    # lang = config['prefs']['lang_code']  *****************************************???????????????? oder anders????

    vendor_id = int(config.get('printer', 'p_idvend', fallback='0x0456'), 0)
    product_id = int(config.get('printer', 'p_idprod', fallback='0x0808'), 0)

    try:
        p = Usb(
            vendor_id, product_id, timeout=10000,
            in_ep=0x81, out_ep=0x03, profile='TM-P80'
        )
        pV = True
        p.charcode = 'CP850'
        p.codepage = 'CP850'
        print(f"USB printer connected: {vendor_id:#06x}:{product_id:#06x}")
    except Exception as error:
        pV = False
        print("USB printer unavailable:", error)
    return pV


def automatic_print_enabled():
    """Return whether a completed analysis should be printed immediately."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.getboolean('printer', 'auto_print', fallback=True)


def special_code_enabled():
    """Return whether the detachable special-code coupon should be printed."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    return config.getboolean('printer', 'print_special_code', fallback=True)


def special_code_path():
    """Return an existing special-code image for the current consultation."""
    global z
    if not isinstance(z, int) or not 1 <= z <= 24:
        z = random.randint(1, 24)
    path = "./WM/pics/code_" + str(z) + ".png"
    if not os.path.isfile(path):
        raise FileNotFoundError("Special-code image is missing: " + path)
    return path


def finish_receipt_after_qr(printer):
    """Cut after the QR code, optionally adding the special-code coupon."""
    if special_code_enabled():
        printer.cut("PART")
        printer.set(font='a', height=2, width=2, align='center')
        printer.text("_________________________")
        printer.text("\n \n")
        printer.text(transl("p11t1"))
        printer.text(transl("p11t2"))
        printer.ln()
        printer.image(special_code_path(), impl='bitImageColumn')
        printer.text("\n")
        printer.text("_________________________")
        printer.cut()
    else:
        # No detachable coupon: finish the main receipt directly after the QR.
        printer.text("\n")
        printer.cut()


def normalize_boolean_setting(value):
    """Return an INI-compatible yes/no value, or None for invalid input."""
    normalized = str(value).strip().lower()
    if normalized in ('1', 'yes', 'true', 'on', 'ja'):
        return 'yes'
    if normalized in ('0', 'no', 'false', 'off', 'nein'):
        return 'no'
    return None


def execute_system_action(action):
    """Request an explicitly allowed service or system action."""
    commands = {
        'reboot': ['sudo', '-n', '/usr/bin/systemctl', 'reboot'],
        'poweroff': ['sudo', '-n', '/usr/bin/systemctl', 'poweroff'],
        'restart_service': [
            'sudo', '-n', '/usr/bin/systemctl', '--no-block',
            'restart', 'fortunestart.service',
        ],
    }
    command = commands.get(action)
    if command is None:
        return False
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except OSError as error:
        print("Could not execute system action:", error)
        return False
    if result.returncode != 0:
        print("System action denied:", result.stderr.strip())
        return False
    return True


def partner_extra_question_enabled():
    """Return whether partner analyses should show the extra-question page."""
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        return config.getboolean('IA', 'partner_extra_question', fallback=False)
    except ValueError:
        print("Invalid IA.partner_extra_question value; using no")
        return False


def print_fortune_receipt(print_lines):
    """Print the complete fortune receipt on the currently opened printer."""
    global p, pV, relay, z
    print_light_on = False

    if not pV or p is None:
        print("Automatic print skipped: no printer available")
        return False

    print("Printstart")
    try:
        if relay is None:
            usbRelaysCheck()
        if relay is not None:
            try:
                relay.set_state(3, True)
                print_light_on = True
                print("Printer light switched on")
            except Exception as error:
                print("Printer light could not be switched on:", error)

        # The TM-P80 needs a brief settling period after the first USB open.
        # Without it, the first large receipt after a service restart can lose
        # the tail of the second image and consequently the final cut command.
        time.sleep(PRINTER_WARMUP_SECONDS)

        p.set(font='b', height=2, width=2, align='center')
        logo = Image1.open("./WM/fortune.png")
        print_width = p.profile.profile_data["media"]["width"]["pixels"]
        logo_height = round(logo.height * print_width / logo.width)
        logo = logo.resize(
            (print_width, logo_height),
            Image1.Resampling.LANCZOS,
        )
        p.image(logo, impl="bitImageColumn", center=True)

        # Mirror the PDF's birth-data panel directly above the chart. Font B
        # leaves enough columns for one box in both individual and partner mode.
        birth_data_lines = thermal_birth_data_box(lang2)
        if birth_data_lines:
            p.set(font='b', height=1, width=1, align='center')
            p.text("\n")
            for line in birth_data_lines:
                p.text(line + "\n")
            p.text("\n")

        try:
            chart_image = create_astrology_chart_image()
            if chart_image is not None:
                labels = PDF_TEXT.get(str(lang2).upper(), PDF_TEXT['EN'])
                chart_title = labels['chart']
                p.text("\n" + chart_title + "\n")
                p.image(chart_image, impl='bitImageColumn', center=True)
        except Exception as error:
            # A missing optional renderer or an unsupported printer must never
            # prevent the fortune text from being printed.
            print("Astrology chart was not printed:", error)

        p.set(font='a', height=2, width=1, align='center')
        # Keep the transition from chart to analysis compact. The image
        # command already finishes its raster row, so one feed is sufficient.
        p.text("\n")
        p.set(font='a', height=1, width=1, align='center')
        try:
            for line in print_lines:
                p.text(normalize_output_text(line) + "\n")
        except Exception as error:
            print("Fortune text could not be encoded:", error)
            p.text("Can't print this language, \n sorry \n ")

        # Use the printer's smaller font B for the legal scope notice.
        p.set(font='b', height=1, width=1, align='center')
        p.text("\n--------------------------------\n")
        for line in split_string_into_lines(
            analysis_disclaimer(lang2), max_line_length=56
        ):
            p.text(normalize_output_text(line) + "\n")
        p.text("--------------------------------\n")
        p.set(font='a', height=1, width=1, align='center')

        p.text("\n" + normalize_output_text(print_info_text(lang2)) + "\n")
        p.text("https://www.x-tra.art\n")
        p.set(font='b', height=2, width=2, align='center')
        p.image("./WM/base.png", impl='bitImageColumn')

        finish_receipt_after_qr(p)
        # Let the printer consume the final image and cut command before the
        # USB interface is released. This is especially important on the first
        # job after a restart, while the device buffers are still cold.
        time.sleep(PRINTER_DRAIN_SECONDS)
        print("Print completed")
        return True
    except Exception as error:
        print("Printing failed:", error)
        return False
    finally:
        if p is not None:
            try:
                p.close()
            except Exception as error:
                print("Printer connection could not be closed:", error)
        p = None
        pV = False
        if print_light_on and relay is not None:
            try:
                relay.set_state(3, False)
                print("Printer light switched off")
            except Exception as error:
                print("Printer light could not be switched off:", error)


# Function to send a message to the OpenAI chatbot model and return its response
def send_message(message_log):
    global answer, client, elem
    config = configparser.ConfigParser()
    config.read('settings.ini')
    model = config['IA']['ia_model'].strip()
    visible_token_target = config.getint('IA', 'max_tok', fallback=600)
    completion_token_budget = config.getint(
        'IA',
        'max_completion_tok',
        fallback=max(visible_token_target * 2, visible_token_target + 512),
    )

    request = {
        'model': model,
        'messages': message_log,
        'max_completion_tokens': completion_token_budget,
        'temperature': 1.0,
    }
    # GPT-5.6 Luna defaults to medium reasoning. For this short creative text,
    # disabling reasoning leaves the completion budget available for visible text.
    if model.startswith('gpt-5.6'):
        request['reasoning_effort'] = config.get(
            'IA', 'reasoning_effort', fallback='none'
        )

    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response = client.chat.completions.create(**request)

    token_usage = response.usage.total_tokens
    print("Anzahl der verwendeten Tokens:", token_usage)
    choice = response.choices[0]
    completion_details = getattr(response.usage, 'completion_tokens_details', None)
    reasoning_tokens = getattr(completion_details, 'reasoning_tokens', 0) or 0
    print(
        "OpenAI finish reason:", choice.finish_reason,
        "Reasoning tokens:", reasoning_tokens,
    )

    content = choice.message.content
    if content and content.strip():
        return content

    raise RuntimeError(
        "OpenAI returned no visible text "
        f"(model={model}, finish_reason={choice.finish_reason}, "
        f"reasoning_tokens={reasoning_tokens}, budget={completion_token_budget})"
    )


def _chatbot(messa):
    global answer, pdf_answer, client, elem, data_p, analysis_mode
    global link, pending_pdf_filename, z

    config = configparser.ConfigParser()
    config.read('settings.ini')
    # Prepare only the receipt chart before printing. The slower PDF chart is
    # deliberately deferred until the physical receipt has completed.
    chart_thread = Thread(target=pre_render_thermal_chart, daemon=True)
    chart_thread.start()
    # Initialize the conversation history with a message from the chatbot
    if analysis_mode == "partner":
        txt = (
            "Create a relationship and compatibility analysis for the two people in the supplied data. "
            "Use the precise Kerykeion synastry context as the astrological source. "
            "Explain their emotional connection, communication, affection, attraction, cooperation, "
            "potential conflicts, growth opportunities, and long-term potential. "
            "Use both names and clearly distinguish the two people. Include their signs and ascendants "
            "near the beginning and incorporate the relationship score without presenting astrology as certainty. "
            "Use familiar, magical and mystical language like an old fortuneteller at a fairy fair. "
            "Use an extra question only when one is supplied. Answer in the requested language. "
            "Structure the answer into 5 to 7 concise thematic sections. Put every section heading "
            "on its own line prefixed exactly with '## ', followed by its paragraph. Use no other Markdown. "
            "The answer shouldn't use more than approximately " + config['IA']['max_tok'] + " tokens. "
            "Always finish the sentences."
        )
    else:
        txt = ("Make a prediction for the next 6 month. Use the given data. " +
               "Use familiar, magical and mystical language full of fantasy like an old fortuneteller on a fairy fair. " +
               "Use the astrologic and numerologic  informations from the personal data. " +
               "Talk also about Work, relationship, and love" +
               "Use the extra text only if given as special question. " +
               "Integrate in the beginning the sign, ascendent and the most important data from the numerological results. " +
               "If a different language is asked for, please translate. " +
               "Structure the answer into 5 to 7 concise thematic sections. Put every section heading " +
               "on its own line prefixed exactly with '## ', followed by its paragraph. Use no other Markdown. " +
               "The answer shouldn't use more than approximately " + config['IA']['max_tok'] + " tokens. " +
               "Always finish the sentences.")
    message_log = [
        {"role": "system", "content": txt},
        {"role": "user", "content": messa},
    ]
    response = send_message(message_log)
    chart_thread.join()
    pdf_answer = normalize_output_text(response)
    answer = strip_analysis_markup(pdf_answer)
    # Select the printed special code as part of this consultation. It must be
    # available before the receipt starts and must not depend on the deferred
    # PDF worker, which may finish much later.
    z = random.randint(1, 24)
    # Reserve the final URL now so the receipt can already contain its valid
    # QR code. The actual PDF is created and uploaded after the receipt.
    output_filename = str(data_p[0]) + ".pdf"
    pending_pdf_filename = generate_unique_filename(output_filename)
    link = public_pdf_link(pending_pdf_filename)
    qrmaker(link)


def create_and_upload_pdf(job):
    """Build and upload one immutable PDF job without touching UI state."""
    started = time.monotonic()
    try:
        print("Deferred PDF creation started:", job['output_filename'])
        job['result'] = create_pdf(
            job['output_filename'], job['text'], job['context']
        )
        job['link'] = upload_pdf_to_server(
            job['output_filename'], job['remote_filename'], publish_state=False
        )
        job['ready'] = True
        print(f"Deferred PDF ready in {time.monotonic() - started:.1f} seconds")
    except Exception as error:
        job['error'] = f"{type(error).__name__}: {error}"
        print("Deferred PDF creation failed:", job['error'])


def start_pdf_delivery(text):
    """Start one background PDF job for the current consultation."""
    global pdf_delivery_thread, pdf_delivery_error, pending_pdf_filename
    global pdf_delivery_job
    if pdf_delivery_thread is not None and pdf_delivery_thread.is_alive():
        return
    pdf_delivery_error = ''
    output_filename = str(data_p[0]) + ".pdf"
    # All values used by ReportLab and the chart renderer are captured here.
    # stateWelcome may consequently reset the live consultation immediately.
    context = {
        'language_code': str(lang2),
        'analysis_mode': analysis_mode,
        'subject_name': str(data_p[0]) if data_p else '',
        'primary_subject': kanye,
        'partner_subject': kanye_partner,
        'chart_data': natal_chart_data,
        'chart_pdf_png': chart_pdf_png_cache,
    }
    pdf_delivery_job = {
        'text': str(text),
        'output_filename': output_filename,
        'remote_filename': str(pending_pdf_filename),
        'link': str(link),
        'context': context,
        'ready': False,
        'error': '',
        'result': None,
    }
    pdf_delivery_thread = Thread(
        target=create_and_upload_pdf,
        args=(pdf_delivery_job,),
        daemon=True,
    )
    pdf_delivery_job['thread'] = pdf_delivery_thread
    pdf_delivery_thread.start()


def chatbot(messa):
    global chatbot_error
    try:
        _chatbot(messa)
    except Exception as error:
        chatbot_error = f"{type(error).__name__}: {error}"
        print("Chatbot error:", chatbot_error)


def split_string_into_lines(text, max_line_length=40):
    words = text.split()  # Teile den Text in Worte auf
    lines = []
    current_line = ""

    for word in words:
        # Wenn das Hinzufügen des aktuellen Wortes zur aktuellen Zeile die maximale Länge
        # überschreiten würde, füge die Zeile zu den Zeilen hinzu und starte eine neue Zeile.
        if len(current_line) + len(word) + 1 <= max_line_length:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def format_thermal_analysis(text, max_line_length=48):
    """Wrap an analysis while retaining its PDF section structure.

    The generated analysis uses ``##`` headings and blank lines to delimit
    thematic sections.  The generic word wrapper intentionally flattens all
    whitespace, so the receipt used to lose those boundaries.  On paper each
    heading is now framed by rules and paragraphs remain separated by one
    blank line.
    """
    formatted_lines = []
    paragraph_lines = []
    divider = '-' * max_line_length

    def wrap(value):
        return [
            line for line in split_string_into_lines(
                normalize_output_text(value).strip(),
                max_line_length=max_line_length,
            )
            if line
        ]

    def separate_blocks():
        if formatted_lines and formatted_lines[-1] != '':
            formatted_lines.append('')

    def flush_paragraph():
        if not paragraph_lines:
            return
        # The lower heading rule already separates the title from its text;
        # start the paragraph immediately below it to save receipt paper.
        if not formatted_lines or formatted_lines[-1] != divider:
            separate_blocks()
        formatted_lines.extend(wrap(' '.join(paragraph_lines)))
        paragraph_lines.clear()

    for source_line in normalize_output_text(text).splitlines():
        stripped = source_line.strip()
        if stripped.startswith('## '):
            flush_paragraph()
            separate_blocks()
            heading_lines = wrap(stripped[3:])
            if heading_lines:
                formatted_lines.append(divider)
                formatted_lines.extend(heading_lines)
                formatted_lines.append(divider)
        elif not stripped:
            flush_paragraph()
        else:
            paragraph_lines.append(stripped)
    flush_paragraph()

    while formatted_lines and formatted_lines[0] == '':
        formatted_lines.pop(0)
    while formatted_lines and formatted_lines[-1] == '':
        formatted_lines.pop()
    return formatted_lines


def konvertiere_zu_8_graustufen(quellpfad, max_breite, max_hoehe, ziel_pfad):
    bild = Image1.open(quellpfad)
    bild.thumbnail((max_breite, max_hoehe))
    bild = bild.convert('L')
    bild = bild.quantize(colors=2)
    bild.save(ziel_pfad)

def convert_to_minitel(image_data, width, height, block_width):
    minitel_data = []
    for y in range(0, height, 3):
        for x in range(0, width, 2):
            minitel_value = 0
            for i in range(3):
                for j in range(2):
                    if (y + i) * width + x + j < len(image_data):
                        pixel_value = int(image_data[(y + i) * width + x + j])
                        minitel_value += pixel_value * (2 ** (i * 2 + j))
            minitel_data.append(minitel_value)
    # Format to lines
    formatted_data = [minitel_data[i:i + block_width] for i in range(0, len(minitel_data), block_width)]
    return formatted_data

def array_to_hex(row):
    hex_row = [hex(value)[2:].zfill(2) for value in row]
    return ' '.join(hex_row)

def send_to_mini(result):
    for row in result:
        hex_row = array_to_hex(row)
        print(hex_row)

def code(user_input):
    x = ""
    data = [[0, '0x20'], [1, '0x21'], [2, '0x22'], [3, '0x23'], [4, '0x24'], [5, '0x25'], [6, '0x26'], [7, '0x27'],
            [8, '0x28'], [9, '0x29'], [10, '0x2a'], [11, '0x2b'], [12, '0x2c'], [13, '0x2d'], [14, '0x2e'],
            [15, '0x2f'],
            [16, '0x30'], [17, '0x31'], [18, '0x32'], [19, '0x33'], [20, '0x34'], [21, '0x35'], [22, '0x36'],
            [23, '0x37'],
            [24, '0x38'], [25, '0x39'], [26, '0x3a'], [27, '0x3b'], [28, '0x3c'], [29, '0x3d'], [30, '0x3e'],
            [31, '0x3f'],
            [32, '0x60'], [33, '0x61'], [34, '0x62'], [35, '0x63'], [36, '0x64'], [37, '0x65'], [38, '0x66'],
            [39, '0x67'],
            [40, '0x68'], [41, '0x69'], [42, '0x6a'], [43, '0x6b'], [44, '0x6c'], [45, '0x6d'], [46, '0x6e'],
            [47, '0x6f'],
            [48, '0x70'], [49, '0x71'], [50, '0x72'], [51, '0x73'], [52, '0x74'], [53, '0x75'], [54, '0x76'],
            [55, '0x77'],
            [56, '0x78'], [57, '0x79'], [58, '0x7a'], [59, '0x7b'], [60, '0x7c'], [61, '0x7d'], [62, '0x7e'],
            [63, '0x7f']
            ]
    user_input = int(user_input)
    hex_value, decimal_value = data[int(user_input)]
    return decimal_value
def qrmaker(address):
    img = qrcode.make('URL:' + address, border=0)
    img.save("./WM/base.png")
    #*********************** resize for Print
    img1 = Image1.open("./WM/base.png")
    # Skaliere das Bild
    img1 = img1.resize((int(img1.width * 0.5), int(img1.width * 0.5)))#, Image.ANTIALIAS)
    # Speichere das skalierte Bild temporär
    img1.save("./WM/base.png")
    #****************
    quellpfad = './WM/base.png'  # Passe dies an den Dateipfad deines Bildes an
    zielbreite = 80
    zielhöhe = 72 #72, 66, (60, 48, 36 depends on data)
    ziel_pfad = './WM/target.png'  # Passe dies an den gewünschten Dateipfad für das Ausgabebild an

    konvertiere_zu_8_graustufen(quellpfad, zielbreite, zielhöhe, ziel_pfad)
def qrshow(address):

    image = Image1.open("./WM/target.png")
    image_width = image.size[0]
    image_height = image.size[1]
    block_width = int(image_width / 2) # Anzahl der Bytes pro Zeile im resultierenden Array
    image_array = array(image.getdata())
    minitel_result = convert_to_minitel(image_array, image_width, image_height, block_width)

    # Prepare output minitel*****************
    center_side_h = int((40 - image_width/2) / 2)+1 # horizoantal
    center_side_w = int((24 - image_height/3) / 2)+1 # Vertical
    r = center_side_w
    print("Widht: ", image_width, " Height: ", image_height, " Centerside: " ,center_side_h, center_side_w)

    # Write to Minitel ********************************

    m.home()
    m.pos(0)
    m._print('Scan for Download:')
    m.pos(r,center_side_h)
    for row in minitel_result:
        for entry in row:
            m.gr()
            m.sendchr(int(code(entry),16))
        r = r+1
        m.pos(r,center_side_h)
        #print()
    m.text()
    while True:
        (choix1, touche) = m.input(0, 40, 1, sltime, "")

        if touche != "":
            break
        elif choix1 != "":
            break

    if touche != "" or choix1 != "":
            return


###
# State machine aka "The brain"
###
class StateMachine:
    def __init__(self):
        self.stack = []
        self.push(self.stateInit)
        self.radarCount = 0
        self.time = 0
        self.time1 = 0
        self.halftime = 0
        self.offStageLimit = 0
        self.offStageMessage = 0
        self._mess = ""

    def mess_change(self):
        return self._mess

    def push(self, state):
        self.stack.append(state)
        self.changing = True

    def pop(self):
        self.stack.pop()

    def changeState(self, state):
        self.pop()
        self.push(state)

    def update(self):
        if (len(self.stack) <= 0):
            return

        entering = self.changing
        self.changing = False
        self.stack[-1](entering)

    # *****************************************************

    def stateInit(self, entering):

        print("~~~ Initialisation ~~~")
        print("Minitel init")
        global m, lang, th1, data, sltime, p, pV, answer, client, zone
        zone = 1
        print("Officielle IP: ", getNetworkIp())
        config = configparser.ConfigParser()
        config.read('settings.ini')
        sltime = config['prefs']['timer']
        lang = config['prefs']['lang_code']
        lang2 = ""
        speed = int(config['prefs']['speed'])
        print("Language: ", lang, " Screensaver/s: ", sltime)
        m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 1200, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
        # os.system("echo -en '\x1b\x3a\x6b\x64' > /dev/ttyUSB0")
        os.system("stty -F /dev/ttyUSB0 speed 1200")
        if speed == 4800:
            os.system("echo -en '\x1b\x3a\x6b\x76' > /dev/ttyUSB0")
            m.end()
            os.system("stty -F /dev/ttyUSB0 speed 4800")
            m = pynitel.Pynitel(serial.Serial('/dev/ttyUSB0', 4800, parity=serial.PARITY_EVEN, bytesize=7, timeout=2))
            print("Baudrate: ", speed)
        else:  # speed == 1200:
            print("Baudrate: ", speed)

        # ###*******Prepare usb relais
        r = usbRelaysCheck()
        if r:
            print("Relais to true")
            relay.set_state(1, True)
            relay.set_state(4, True)
            time.sleep(2)
            print("Relais to False")
            relay.set_state(1, False)
            relay.set_state(4, False)
            print("Printer light test on relay 3")
            relay.set_state(3, True)
            time.sleep(2)
            relay.set_state(3, False)
            print("Printer light test completed")

        # ###*******Prepare prefs :sltime, printer
        printCheck()

        # ###***** Prepa ChatGPT API
        os.system("echo -en '\x1b\x3a\x6A\x43' > /dev/ttyUSB0")

        api_key = os.environ.get('OPENAI_API_KEY', '').strip()
        if api_key:
            # The OpenAI SDK reads OPENAI_API_KEY from the environment.
            client = OpenAI()
        else:
            client = None
            m.message(10, 5, 4, "OPENAI_API_KEY missing in service environment", True)
            time.sleep(5)

        answer = ""
        print("~~~ Initialisation Done ~~~", "\n")
        self.changeState(self.stateFortunePic)

    def stateFortunePic(self, entering):
        global lang, sltime, ver

        print("Fortune Teller picture")
        rd = random.randint(1, 5)
        if rd == 1:
            r = usbRelaysCheck()
            if r:
                relay.set_state(1, True)
                relay.set_state(4, True)
                time.sleep(1)
                relay.set_state(4, False)
                time.sleep(4)
                relay.set_state(1, False)
        m.home()

        m.load(1, './WM/fortune.vdt')
        m.draw(1)
        while True:
            # ligne finale
            m.pos(24, 1)
            m.color(m.vert)
            m._print(transl("p0t1"))
            m.pos(24, 19)
            m.inverse()
            m.color(m.cyan)
            m._print('  ENVOI ')
            # attente saisie
            m.cursor(False)
            (choix1, touche) = m.input(23, 1, 1, sltime, "")

            if touche != "":
                break
            elif choix1 != "":
                break

        if touche != "" or choix1 != "":
            self.changeState(self.stateWelcome)

    def stateLanguage(self, entering):  # p0t1
        print("State language")
        global lang, th1, sltime, ver, choix1
        choix1 = ""
        touche = ""
        m._del(0, 0)
        while True:  # t2 > time.time():#True:
            if True:  # affichage
                # entête sur 2 lignes + séparation
                m.home()
                m.pos(0)
                m.pos(0, 0)
                m._print("V" + ver + " / " + lang)
                m.pos(2)
                m.pos(2, 1)
                m.scale(3)
                m._print(transl("p1t1"))
                m.pos(4, 1)
                m.scale(3)
                m._print(transl("p1t2"))
                m.scale(0)
                strcenter(row=3, pos=27, txt=transl("p1t3"), width=40, size=0)
                strcenter(row=4, pos=27, txt=transl("p1t3a"), width=40, size=0)
                m.pos(5)
                m.color(m.bleu)
                m.plot('̶', 40)
                strcenter(row=8, pos=20, txt=transl("p1t4"), width=40, size=0)
                # strcenter(row = 9,pos=20, txt = 'choice', width = 40, size = 0)
                strcenter(row=11, pos=10, txt=transl("p1t5"), width=40, size=0)
                strcenter(row=11, pos=30, txt=transl("p1t6"), width=40, size=0)
                strcenter(row=13, pos=10, txt=transl("p1t7"), width=40, size=0)
                strcenter(row=13, pos=30, txt=transl("p1t8"), width=40, size=0)
                # ligne finale
                m.pos(21)
                m.color(m.bleu)
                m.plot('̶', 40)
                m.pos(22, 1)

                m.pos(24, 1)
                m.color(m.vert)
                m._print(transl("p1t9"))
                m.pos(24, 8)
                m.inverse()
                m.color(m.cyan)
                m._print("GUIDE")

                m.pos(24, 22)
                m.color(m.vert)
                m._print(transl("p1t10"))
                m.pos(24, 36)
                m.inverse()
                m.color(m.cyan)
                m._print("ENVOI")
            else:
                break
                # page = abs(page)

            (choix1, touche) = m.input(24, 33, 2, sltime)
            m.cursor(False)

            if touche == m.suite:
                return (touche)

            elif touche == m.chariot:
                break

            elif touche == m.retour or touche == m.annulation:
                break
            elif touche == m.envoi:
                break
            elif touche == m.sommaire:
                # print("touche sommaire")
                break

            elif touche == m.guide:
                break
            elif touche == m.correction:  # retour saisie pour correction
                return (touche)

        if choix1 == "":
            choix1 = lang
        if touche == m.sommaire and choix1 == "sleep":
            # choix1 = ""
            print("Go to sleeper")
            self.changeState(self.stateWelcome)
        if touche == m.envoi and choix1 == "FR":
            lang = "FR"
            m.message(16, 7, 2, transl("p1t11"), bip=False)
            self.changeState(self.stateWelcome)
        elif touche == m.envoi and choix1 == "EN":
            lang = "EN"
            m.message(16, 7, 2, transl("p1t11"), bip=False)
            self.changeState(self.stateWelcome)
        elif touche == m.envoi and choix1 == "DE":
            lang = "DE"
            m.message(16, 7, 2, transl("p1t11"), bip=False)
            self.changeState(self.stateWelcome)
        elif touche == m.envoi and choix1 == "ES":
            lang = "ES"
            m.message(16, 7, 2, transl("p1t11"), bip=False)
            self.changeState(self.stateWelcome)

        elif touche == m.envoi:
            if choix1 != "FR" or choix1 != "EN" or choix1 != "DE" or choix1 != "ES":
                m.home()
                m.message(15, 7, 3, "Wrong CODE, try again ", bip=True)
        elif touche == m.guide:
            self.changeState(self.stateInfo1)  # TODO HELPPAGE

    def stateInfo1(self, entering):
        print("Infopage")
        time.sleep(2)
        self.changeState(self.stateWelcome)

    def statePrefs(self, entering):  # Prefs: timer screensave, perhaps, Printer
        print("State Preferences")
        global lang, sltime

        m.resetzones()
        config = configparser.ConfigParser()
        config.read('settings.ini')

        m.zone(7, 15, 23, config['prefs']['ip_adr'], m.blanc)
        m.zone(7, 36, 23, config['prefs']['speed'], m.blanc)
        m.zone(9, 15, 23, config['prefs']['timer'], m.blanc)
        m.zone(9, 36, 23, config['prefs']['lang_code'], m.blanc)
        m.zone(11, 15, 23, config['printer']['p_idvend'], m.blanc)
        m.zone(12, 15, 23, config['printer']['p_idprod'], m.blanc)
        m.zone(13, 15, 23, config['printer']['p_timer'], m.blanc)
        m.zone(14, 15, 23, config['printer']['p_3'], m.blanc)
        m.zone(15, 15, 3, "NO", m.blanc)
        m.zone(16, 15, 3, config.get('printer', 'auto_print', fallback='yes'), m.blanc)
        m.zone(17, 15, 3, config.get('printer', 'print_special_code', fallback='yes'), m.blanc)
        m.zone(18, 15, 3, config.get('coin_counter', 'enabled', fallback='no'), m.blanc)
        m.zone(19, 10, 23, config['IA']['ia_model'], m.blanc)
        m.zone(19, 36, 23, config['IA']['max_tok'], m.blanc)
        m.zone(20, 15, 3, "NO", m.blanc)
        m.zone(20, 35, 3, "NO", m.blanc)
        # r = res[0]
        touche = m.repetition
        zone = 1
        system_action = None
        m.home()

        while True:
            m.home()
            m.pos(0, 1)
            m._print("Version " + ver)
            m.pos(2, 1)
            m.scale(3)
            m._print(transl("p3t1"))
            m.pos(4, 1)
            m.scale(3)
            m._print(transl("p3t2"))
            m.scale(0)
            strcenter(row=1, pos=28, txt=transl("p3t3"), width=40, size=0)
            strcenter(row=3, pos=28, txt=transl("p3t4"), width=40, size=0)
            strcenter(row=4, pos=28, txt=transl("p3t5"), width=40, size=0)
            m.pos(5)
            m.color(m.bleu)
            m.plot('̶', 40)
            m.pos(7)
            m._print('' + strformat(left="Local / IP"[:11], right="*                        ", width=39))
            strcenter(row=7, pos=30, txt="Bauds ", width=20, size=0)
            m.pos(9)
            m._print('' + strformat(left="Time sleep"[:11], right="*                        ", width=39))
            strcenter(row=9, pos=30, txt="Language ", width=20, size=0)
            m.pos(11)
            m._print('' + strformat(left="Print Val1"[:11], right="-                        ", width=39))
            m.pos(12)
            m._print('' + strformat(left="Print Val2"[:11], right="-                        ", width=39))
            m.pos(13)
            m._print('' + strformat(left="Print Val3"[:11], right="-                        ", width=39))
            m.pos(14)
            m._print('' + strformat(left="Print Val4"[:11], right="-                        ", width=39))
            m.pos(15)
            m._print('' + strformat(left="Restart App"[:11], right="*                        ", width=39))
            m.pos(16)
            m._print('' + strformat(left="Auto Print"[:11], right="*                        ", width=39))
            m.pos(17)
            m._print('' + strformat(left="Spec. Code"[:11], right="*                        ", width=39))
            m.pos(18)
            m._print('' + strformat(left="Coin Count"[:11], right="*                        ", width=39))
            m.pos(19)
            m._print('' + strformat(left="Model"[:11], right="*                        ", width=39))
            strcenter(row=19, pos=30, txt="Max Token: ", width=20, size=0)
            m.pos(20)
            m._print('' + strformat(left="Reboot"[:11], right="*........................", width=39))
            strcenter(row=20, pos=30, txt="Shutdown ", width=40, size=0)
            # ligne finale
            m.pos(21)
            m.color(m.bleu)
            m.plot('̶', 40)
            m.pos(22, 1)
            m._print(transl("p3t11"))
            m.pos(23, 1)

            m.color(m.vert)
            m._print(transl("p3t12"))
            m.pos(23, 12)
            m.inverse()
            m.color(m.cyan)
            m.underline()
            m._print("_SUITE ")

            m.pos(24, 1)
            m.color(m.vert)
            m._print(transl("p3t13"))
            m.pos(24, 12)
            m.inverse()
            m.color(m.cyan)
            m._print(" RETOUR")
            m.pos(24, 25)
            m._print(transl("p3t15"))
            m.pos(24, 33)
            m.inverse()
            m.color(m.cyan)
            m._print("SOMMAIRE")
            m.pos(22, 21)
            m._print(transl("p3t14"))
            m.pos(22, 33)
            m.inverse()
            m.color(m.cyan)
            m._print('  ENVOI ')
            m.pos(24, 28)

            # gestion de la zone de saisie courante
            (zone, touche) = m.waitzones(zone, sltime)
            # print(touche)

            if touche == 1:
                print("Touche ENVOI: " + str(touche))
                auto_print_value = normalize_boolean_setting(m.zones[9]['texte'])
                special_code_value = normalize_boolean_setting(m.zones[10]['texte'])
                coin_counter_value = normalize_boolean_setting(m.zones[11]['texte'])
                service_restart_value = normalize_boolean_setting(m.zones[8]['texte'])
                if (auto_print_value is None or special_code_value is None
                        or coin_counter_value is None
                        or service_restart_value is None):
                    m.message(18, 2, 3, "Options require YES or NO", bip=True)
                    continue
                service_restart_requested = service_restart_value == 'yes'
                reboot_requested = normalize_boolean_setting(m.zones[14]['texte']) == 'yes'
                shutdown_requested = normalize_boolean_setting(m.zones[15]['texte']) == 'yes'
                if sum((service_restart_requested, reboot_requested, shutdown_requested)) > 1:
                    m.message(18, 2, 3, "Choose only one system action", bip=True)
                    continue
                if service_restart_requested:
                    system_action = 'restart_service'
                elif reboot_requested:
                    system_action = 'reboot'
                elif shutdown_requested:
                    system_action = 'poweroff'
                if m.zones[0] == "":
                    m.zones[0] = "localhost"
                config['prefs'] = {
                    'IP_adr': m.zones[0]['texte'],
                    'speed': m.zones[1]['texte'],
                    'timer': m.zones[2]['texte'],
                    'lang_code': m.zones[3]['texte']}
                config['printer'] = {
                    'p_idvend': m.zones[4]['texte'],
                    'p_idprod': m.zones[5]['texte'],
                    'auto_print': auto_print_value,
                    'print_special_code': special_code_value,
                    'p_timer': m.zones[6]['texte'],
                    'p_3': m.zones[7]['texte'],
                    'p_4': config.get('printer', 'p_4', fallback='')}
                if not config.has_section('coin_counter'):
                    config.add_section('coin_counter')
                config['coin_counter']['enabled'] = coin_counter_value
                config['IA']['ia_model'] = m.zones[12]['texte']
                config['IA']['max_tok'] = m.zones[13]['texte']
                with open('settings.ini', 'w') as configfile:
                    config.write(configfile)

                sltime = int(m.zones[2]['texte'])
                lang = m.zones[3]['texte']

                break
            if touche == 3:
                break
            if touche == 5:
                break
            if touche == 6:
                break
        if touche == 1:
            print("check & prepare data ")
            m.resetzones()
            if system_action is not None:
                action_label = {
                    'restart_service': 'restart app',
                    'reboot': 'reboot',
                    'poweroff': 'shutdown',
                }[system_action]
                m.home()
                m.message(15, 7, 2, "Go to " + action_label, bip=True)
                if not execute_system_action(system_action):
                    m.message(15, 4, 4, "System action denied - check sudoers", bip=True)
                    self.changeState(self.stateWelcome)
            else:
                self.changeState(self.stateWelcome)
        elif touche == 6:
            m.resetzones()
            self.changeState(self.stateWelcome)
        else:
            # print(m.zones[2], " ", m.zones[3])
            print("stay in stream")

    def stateWelcome(self, entering):
        print("State Welcome")
        global lang, sltime, data, answer, pdf_answer, run, zone, upload, z
        global pdf_delivery_thread, pdf_delivery_error, pending_pdf_filename
        global pdf_delivery_job
        global analysis_mode, partner_people, current_person_index
        global kanye, kanye_partner, natal_chart_data, astrology_context
        if relay:
            relay.set_state(3, False)
        # The worker owns a snapshot of all PDF data. Never wait for it here:
        # Sommaire and a new page selection must remain immediately responsive.
        pdf_delivery_thread = None
        pdf_delivery_job = None
        pdf_delivery_error = ''
        pending_pdf_filename = ''
        zone = 1
        upload = False
        answer = ""
        pdf_answer = ""
        z = None
        analysis_mode = "individual"
        partner_people = []
        current_person_index = 1
        kanye = None
        kanye_partner = None
        natal_chart_data = None
        astrology_context = ""
        touche = 0
        choix1 = ""
        m.home()
        while True:
            if True:  # affichage
                # entête sur 2 lignes + séparation
                m.home()
                m.pos(2)
                m.pos(2, 1)
                m.scale(3)
                m._print(transl("p2t1"))
                m.pos(4, 1)
                m.scale(3)
                m._print(transl("p2t2"))
                m.scale(0)
                strcenter(row=3, pos=28, txt=transl("p2t3"), width=40, size=0)
                strcenter(row=4, pos=28, txt=transl("p2t3a"), width=40, size=0)
                m.pos(5)
                m.color(m.bleu)
                m.plot('̶', 40)
                strcenter(row=8, pos=20, txt=transl("p2t4"), width=40, size=1)
                strcenter(row=11, pos=20, txt=transl("p2t5"), width=40, size=1)
                strcenter(row=15, pos=20, txt=transl("p2t6"), width=40, size=0)
                # strcenter(row = 13,pos=20, txt = transl("p2t8"), width = 40, size = 3)
                # strcenter(row = 8,pos=30, txt = transl("p2t9"), width = 40, size = 0)
                # strcenter(row = 9,pos=30, txt = transl("p2t10"), width = 40, size = 0)
                # strcenter(row = 10,pos=30, txt = transl("p2t11"), width = 40, size = 0)
                # strcenter(row = 13,pos=30, txt = transl("p2t12"), width = 40, size = 3)
                strcenter(row=17, pos=20, txt=transl("p2t14"), width=40, size=0)

                # ligne finale
                m.pos(21)
                m.color(m.bleu)
                m.plot('̶', 40)
                m.pos(22, 1)

                m.color(m.vert)
                m.pos(24, 1)
                m._print(transl("p2t15"))
                m.pos(24, 10)
                m.inverse()
                m.color(m.cyan)
                m._print("SOMMAIRE")
                m.pos(23, 1)
                m._print(transl("p2t16"))
                m.pos(23, 10)
                m.inverse()
                m.color(m.cyan)
                m._print("GUIDE")
                m.pos(24, 24)
                m.color(m.vert)
                m._print(transl("p2t17"))
                m.pos(24, 36)
                m.inverse()
                m.color(m.cyan)
                m._print("ENVOI")

            else:
                break
                # page = abs(page)

            (choix1, touche) = m.input(24, 33, 2, sltime)
            # ****** check for integer
            if choix1 != "sleep":
                if not isinstance(choix1, int):
                    if not choix1.isdigit():
                        choix1 = 0
                    choix1 = int(choix1)

            m.cursor(False)
            if touche == m.suite:
                return touche
            elif touche == m.chariot:
                break
            elif touche == m.retour or touche == m.annulation:
                break
            elif touche == m.envoi:
                break
            elif touche == m.sommaire:
                break
            elif touche == m.guide:
                break
            elif touche == m.correction:  # retour saisie pour correction
                return touche
            elif touche != m.repetition:
                m.bip()
        # print("Bin hier")
        if touche == m.envoi and choix1 in (1, 2):
            analysis_mode = "partner" if choix1 == 2 else "individual"
            partner_people = []
            current_person_index = 1
            m.home()
            self.changeState(self.stateEnterData1)

        elif touche == m.envoi and choix1 == 98:

            self.changeState(self.statePrefs)
        elif touche == m.envoi:
            if choix1 < 1 or choix1 > 2 or choix1 == 99:
                m.resetzones()
                m.message(15, 7, 1.5, "Wrong Number, try again ", bip=True)
        elif touche == m.sommaire and choix1 == "sleep":
            print("sommaire to sleep")
            self.changeState(self.stateFortunePic)  # ***new ?????
            # return
        elif touche == m.sommaire and choix1 == 0:
            print("sommaire to Language")
            m.resetzones()
            self.changeState(self.stateLanguage)
        if touche == m.guide:
            self.changeState(self.stateInfo1)

    def stateEuro(self, entering):
        print("Europage")
        m.home()
        m.pos(0)
        center_side_h = int(0)  + 1  # horizoantal
        center_side_w = int(2) + 1  # Vertical
        r = center_side_w
        m._print('Fortune Teller')
        m.pos(r, center_side_h)
        # Liste aus Datei laden
        with open('./WM/1EURO.json', 'r') as f:
            loaded_list = json.load(f)

        for row in loaded_list:  # minitel_result:
            for entry in row:
                m.gr()
                m.sendchr(int(code(entry), 16))
            r = r + 1
            m.pos(r, center_side_h)

        time.sleep(5)
        self.changeState(self.stateWelcome)
    # ****************************************  ASTRO DATA
    def stateEnterData1(self, entering):  # Enter Name and Sexe
        global data, lang, sltime, data_p, data_gender, run, zone, link
        global analysis_mode, current_person_index
        print("State DATA1", run)
        # data_p = ()
        link = ""
        annu_save = ""
        print("State Enter Name / Sexe")



        m.home()
        if entering:
            # A new person always starts with a clean zone list and the name
            # field selected. This is essential when partner person 1 used
            # three zones on the preceding place/language page.
            m.resetzones()
            zone = 1
            m.zone(10, 8, 23, '', m.blanc)
            m.zone(17, 20, 1, '', m.blanc)


        while True:
            if not run:
                print("datafalse")
                m.resetzones()
                m.home()
                touche = 0
                break

            # HEADLINE ******************
            m.pos(2)
            m.pos(2, 1)
            m.scale(3)
            m._print(transl("p10t1"))
            m.pos(4, 1)
            m.scale(3)
            m._print(transl("p10t2"))
            m.scale(0)
            # strcenter(row = 1,pos=28, txt = transl("p10t3"), width = 40, size = 0)
            strcenter(row=3, pos=28, txt=transl("p10t3"), width=40, size=0)
            strcenter(row=4, pos=28, txt=transl("p10t3a"), width=40, size=0)
            m.pos(5)
            m.color(m.bleu)
            m.plot('̶', 40)
            if analysis_mode == "partner":
                strcenter(
                    row=6,
                    pos=20,
                    txt=transl("p10t23") + " " + str(current_person_index) + " / 2",
                    width=40,
                    size=0,
                )
            # DATA LINE ****************

            strcenter(row=8, pos=20, txt=transl("p10t4"), width=40, size=1)
            strcenter(row=10, pos=20, txt="*........................", width=40, size=0)
            strcenter(row=15, pos=20, txt=transl("p10t5"), width=40, size=1)
            strcenter(row=17, pos=20, txt="*", width=40, size=0)
            # m._print('' + strformat(left=transl("p10t4")[:11], right="*........................", width=39))
            # m.pos(9)
            # m._print('' + strformat(left=transl("p10t5")[:11], right="*........................", width=39))
            # m.pos(11)
            # FINAL LINE ***************
            m.pos(21)
            m.color(m.bleu)
            m.plot('̶', 40)
            m.pos(22, 1)
            m._print(transl("p10t17"))
            m.pos(23, 1)

            m.color(m.vert)
            m._print(transl("p10t18"))
            m.pos(23, 12)
            m.inverse()
            m.color(m.cyan)
            m.underline()
            m._print("_SUITE ")

            m.pos(24, 1)
            m.color(m.vert)
            m._print(transl("p10t19"))
            m.pos(24, 12)
            m.inverse()
            m.color(m.cyan)
            m._print(" RETOUR")
            m.pos(24, 25)
            m._print(transl("p10t21"))
            m.pos(24, 33)
            m.inverse()
            m.color(m.cyan)
            m._print("SOMMAIRE")
            m.pos(22, 21)
            m._print(transl("p10t20"))
            m.pos(22, 33)
            m.inverse()
            m.color(m.cyan)
            m._print('  ENVOI ')
            m.pos(24, 28)

            # gestion de la zone de saisie courante******
            (zone, touche) = m.waitzones(zone, sltime)
            if touche == 1:
                # CHECK Input
                if m.zones[0]['texte'] == "":
                    m.message(20, 15, 3, "Name required")
                    zone = 1
                    break
                elif m.zones[1]['texte'] == "":
                    m.message(20, 15, 3, "Sexe required")
                    zone = 2
                    break
                elif m.zones[1]['texte'] not in ["m", "M", "h", "H", "f", "F", "w", "W", "d", "D"]:
                    m.message(20, 5, 3, "Sexe only M, H, F, W allowed")
                    zone = 2
                    break
                else:  # All ok
                    break
            elif touche == 6:  # Sommaire
                break
            elif touche == 5:
                break

        if touche == 1:
            if m.zones[0]['texte']  and  m.zones[1]['texte' ]:
                data_p = [m.zones[0]['texte']]
                print("data1", [m.zones[0]['texte']], "data2", [m.zones[1]['texte']], )
                if m.zones[1]['texte'] in ["m", "M", "h", "H"]:
                    data_gender = "The questioner is a man"
                elif m.zones[1]['texte'] in ["f", "F", "w", "W"]:
                    data_gender = "The questioner is a woman"
                elif m.zones[1]['texte'] in ["d", "D"]:
                    data_gender = "Use gender-neutral language"
                else:
                    return
                m.resetzones()
                zone = 1
                self.changeState(self.stateEnterData2)

        elif touche == 6:  # Sommaire
            m.resetzones()
            zone = 1
            self.changeState(self.stateWelcome)
        else:
            self.changeState(self.stateEuro)

    def stateEnterData2(self, entering):  # Enter Birthday and hour
        x=1
        print("State Enter Birthday / Hour")
        m.canblock(6, 20, 1)
        global lang, sltime, data_p, data, zone
        if entering:
            m.resetzones()
            zone = 1
            m.zone(10, 11, 2, '', m.blanc)
            m.zone(10, 20, 2, '', m.blanc)
            m.zone(10, 30, 4, '', m.blanc)
            m.zone(19, 15, 2, '', m.blanc)
            m.zone(19, 28, 2, '', m.blanc)
        while True:
            # DATA LINE ****************

            strcenter(row=8, pos=20, txt=transl("p10t6"), width=40, size=1)
            # strcenter(row=10, pos=20, txt=(transl("p10t7") + " .. " + transl("p10t8") + " .. " + transl("p10t9") + " .... "), width=40, size=0)
            m.pos(10, 4)
            m._print(transl("p10t7") + "  ..")
            m.pos(10, 14)
            m._print(transl("p10t8") + " ..")
            m.pos(10, 24)
            m._print(transl("p10t9") + " ....")
            m.pos(13)

            strcenter(row=15, pos=20, txt=transl("p10t10"), width=40, size=1)
            strcenter(row=16, pos=20, txt=transl("p10t12a"), width=40, size=0)

            # strcenter(row=18, pos=20, txt = transl("p10t11") + " .. " + transl("p10t12") + " .. ", width=40, size=0)
            m.pos(19, 8)
            m._print(transl("p10t11") + " ..")
            m.pos(19, 19)
            m._print(transl("p10t12") + " ....")
            # m._print('' + strformat(left=transl("p10t10")[:6], right=transl("p10t11")+" .. "+transl("p10t12")+" .. ", width=39))
            # strcenter(row=16, pos=20, txt=transl("p10t12a"), width=40, size=0)
            # strcenter() leaves the Minitel in a scaled text mode. Existing
            # values are redrawn by waitzones() after a validation error, so
            # force normal text attributes first to avoid overwriting labels.
            m.scale(0)
            m.normal()
            m.underline(False)
            m.color(m.blanc)
            # gestion de la zone de saisie courante******
            (zone, touche) = m.waitzones(zone, sltime)
            if touche == 1:
                break
            if touche == 6:  # Sommaire
                break
            if touche == 5:
                break
        if touche == 1:
            # CHECK Input
            n = ["day", "month", "year", "hours", "minutes"]
            for x in range(0, 5):
                if m.zones[x]['texte'] == "":
                    m.message(20, 15, 3, n[x] + " required")
                    zone = x + 1
                    return
            for x in range(0, 5):
                # print("Range x:", m.zones[x]['texte'])
                if not m.zones[x]['texte'].isdigit():
                    m.message(20, 7, 3, "Only digits allowed in " + n[x])
                    zone = x + 1
                    return
            if not int(m.zones[0]['texte']) in range(1, 32):
                m.message(20, 7, 3, "Not in range " + n[0])
                zone =  1
                return
            if not int(m.zones[1]['texte']) in range(1, 13):
                m.message(20, 7, 3, "Not in range " + n[1])
                zone = 2
                return
            if not int(m.zones[2]['texte']) in range(1800, 2400):
                m.message(20, 7, 3, "Not in range " + n[2])
                zone = 3
                return
            if not int(m.zones[3]['texte']) in range(0, 24):
                m.message(20, 7, 3, "Not in range " + n[3])
                zone = 4
                return
            if not int(m.zones[4]['texte']) in range(0, 60):
                m.message(20, 7, 3, "Not in range " + n[4])
                zone = 5
                return

            data_p.extend(
                [int(m.zones[2]['texte']), int(m.zones[1]['texte']),
                 int(m.zones[0]['texte']), int(m.zones[3]['texte']),
                 int(m.zones[4]['texte'])]
            )
            # print(" + Datum DATA_p: ", data_p)
            m.resetzones()
            self.changeState(self.stateEnterData3)

        if touche == 6:  # Sommaire
            m.resetzones()
            self.changeState(self.stateWelcome)

    def stateEnterData3(self, entering):  # Enter Town and country
        print("State Enter Town / Country")
        m.canblock(6, 20, 1)
        global lang, sltime, data_p, data_astro, data, data_gender, kanye, language, lang2, zone
        global analysis_mode, partner_people, current_person_index
        global kanye_partner, natal_chart_data, astrology_context
        answer_language = (
            lang2
            if analysis_mode == "partner" and current_person_index == 2
            else ''
        )
        if entering:
            m.resetzones()
            zone = 1
            m.zone(10, 8, 23, '', m.blanc)
            m.zone(15, 19, 2, '', m.blanc)
            m.zone(20, 19, 2, answer_language, m.blanc)
        while True:
            # DATA LINE ****************
            strcenter(row=8, pos=20, txt=transl("p10t13"), width=40, size=1)
            strcenter(row=10, pos=20, txt="*........................", width=40, size=0)
            strcenter(row=13, pos=20, txt=transl("p10t14"), width=40, size=1)
            strcenter(row=14, pos=20, txt=transl("p10t16"), width=20, size=0)
            strcenter(row=15, pos=20, txt="*.", width=40, size=0)
            strcenter(row=18, pos=20, txt=transl("p10t15"), width=20, size=1)
            strcenter(row=19, pos=20, txt=transl("p10t16a"), width=20, size=0)
            strcenter(row=20, pos=20, txt="*.", width=40, size=0)

            # Keep previously entered values in normal size when waitzones()
            # redraws them after an early ENVOI.
            m.scale(0)
            m.normal()
            m.underline(False)
            m.color(m.blanc)
            # gestion de la zone de saisie courante******
            (zone, touche) = m.waitzones(zone, sltime)
            if touche == 1:
                break
            if touche == 6:  # Sommaire
                break
            if touche == 5:
                break
        if touche == 1: #### GUCKENHIER
            print("CHECK Input")
            city = m.zones[0]['texte'].strip()
            country = m.zones[1]['texte'].strip().upper()
            answer_language_code = m.zones[2]['texte'].strip().upper()

            if not city:
                zone = 1
                m.message(21, 10, 3, "Place of Birth required")
                return
            if not country:
                zone = 2
                m.message(21, 10, 3, "Country of Birth required")
                return
            if len(country) != 2 or not country.isalpha():
                zone = 2
                m.message(21, 8, 3, "Country needs a two letter code")
                return
            if answer_language_code not in ["FR", "DE", "EN", "ES"]:
                zone = 3
                m.message(21, 8, 3, "Language must be FR/DE/EN/ES")
                return

            m.zones[0]['texte'] = city
            m.zones[1]['texte'] = country
            m.zones[2]['texte'] = answer_language_code
            data_p.extend([city, country])
            get_language_by_country_code(answer_language_code)

            lang2 = answer_language_code
            print("Zweite Sprache: " + lang2)
            dat_ast = [data_p[0], data_p[1], data_p[2], data_p[3], data_p[4], data_p[5], data_p[6], data_p[7]]
            if analysis_mode == "partner":
                try:
                    subject = AstrologicalSubjectFactory.from_birth_data(
                        *dat_ast, online=True
                    )
                except Exception as error:
                    print("Kerykeion subject error:", error)
                    m.message(20, 5, 3, "There is an issue with your data, please try again")
                    m.resetzones()
                    self.changeState(self.stateWelcome)
                    return

                partner_people.append({
                    'data': data_p.copy(),
                    'gender': data_gender,
                    'subject': subject,
                })

                if current_person_index == 1:
                    current_person_index = 2
                    m.resetzones()
                    zone = 1
                    self.changeState(self.stateEnterData1)
                    return

                first_person = partner_people[0]
                second_person = partner_people[1]
                x = get_partner_data_astro(
                    first_person['subject'],
                    second_person['subject'],
                    str(m.zones[2]['texte']),
                )
                if x == "Error":
                    m.resetzones()
                    self.changeState(self.stateWelcome)
                    return

                first_subject = first_person['subject']
                second_subject = second_person['subject']
                relationship_score = natal_chart_data.relationship_score
                score_text = "not available"
                if relationship_score is not None:
                    score_text = (
                        str(relationship_score.score_value) +
                        " (" + relationship_score.score_description + ")"
                    )

                data_p = [first_subject.name + " & " + second_subject.name]
                data_astro = (
                    "Answer in " + language + ". This is a partner synastry analysis. " +
                    "Person 1: " + first_subject.name + ", " + first_person['gender'] +
                    ", Sign: " + signs(first_subject.sun.sign) +
                    ", Ascendent: " + signs(first_subject.first_house.sign) +
                    ", Element Sun: " + first_subject.sun.element +
                    ", Element Moon: " + first_subject.moon.element + ". " +
                    "Person 2: " + second_subject.name + ", " + second_person['gender'] +
                    ", Sign: " + signs(second_subject.sun.sign) +
                    ", Ascendent: " + signs(second_subject.first_house.sign) +
                    ", Element Sun: " + second_subject.sun.element +
                    ", Element Moon: " + second_subject.moon.element + ". " +
                    "Kerykeion relationship score: " + score_text + ". " +
                    "Use also numerological data derived from both names and birth dates. " +
                    "Use this precise Kerykeion synastry context as the astrological source: " +
                    astrology_context
                )
            else:
                x = get_data_astro(dat_ast, str(m.zones[2]['texte']))

                if x == "Error":
                    print("Ausgabe X: ",x)
                    m.resetzones()
                    self.changeState(self.stateWelcome)
                    return

                data_astro = ("Answer in " + language +
                                  ", " + data_gender +
                                  ", Sign: " + signs(kanye.sun.sign) +
                                  ", Ascendent: " + signs(kanye.first_house.sign) +
                                  ", Element Sun: " + kanye.sun.element +
                                  ", Element Moon: " + kanye.moon.element +
                                  ", Use also numerological Data. "
                                  "Use this precise Kerykeion natal-chart context as the astrological source: " +
                                  astrology_context
                                  )
            print(data_astro)
            m.resetzones()
            if analysis_mode == "partner" and not partner_extra_question_enabled():
                self.startAnalysis()
            else:
                self.changeState(self.stateEnterQuest)
        elif touche == 6:  # Sommaire
            m.resetzones()
            self.changeState(self.stateWelcome)

    def stateWaitForAnswer1(self, entering):
        global answer, message, thread_1, relay, data
        print("State Wait")
        answer = ""
        usbRelaysCheck()
        # while answer == "":
        y = False
        while thread_1.is_alive():

            for x in range(0, 200):
                m.pos(10, 18)
                m.scale(3)
                m._print(str(x))
                time.sleep(1)
                if not thread_1.is_alive():
                    if relay:
                        relay.set_state(1, False)
                    break

        self.changeState(self.stateSend)

    # ****************************************  Extra DATA (Question

    def startAnalysis(self, extra_text=""):
        """Start AI generation with an optional question appended to the context."""
        global message, thread_1, data_astro, chatbot_error
        message = data_astro + extra_text
        m.home()
        chatbot_error = ""
        thread_1 = Thread(target=chatbot, args=(message,))
        thread_1.start()
        self.changeState(self.stateWaitForAnswer2)

    def stateEnterQuest(self, entering):

        global message, data_p, answer, thread_1, data_astro, data, chatbot_error
        m.home()
        m.resetzones()
        touche = 0
        m.pos(3, 2)
        m.scale(1)
        m._print(transl("p10t17a"))

        # m.zone(ligne, colonne, longueur, texte, couleur)
        m.zone(6, 2, 38, "", m.blanc)
        m.zone(8, 2, 38, "", m.blanc)
        m.zone(10, 2, 38, "", m.blanc)
        m.zone(12, 2, 38, "", m.blanc)
        m.zone(14, 2, 38, "", m.blanc)
        m.zone(16, 2, 38, "", m.blanc)
        m.zone(18, 2, 38, "", m.blanc)
        #m.zone(21, 2, 38, "", m.blanc)

        while True:
            x = 6
            while x <= 18:
                if  x % 2 == 0:
                    # print(x)
                    m.pos(x, 2)
                    m.plot('.', 37)
                x = x + 1
            #********
            # ligne finale
            m.pos(21, 1)
            m.color(m.bleu)
            m.plot('̶', 40)
            m.pos(22, 22)
            m.color(m.vert)
            m._print("Ligne prec.")
            m.pos(22, 33)
            m.underline()
            m._print(' ')
            m.inverse()
            m.color(m.cyan)
            m._print('_RETOUR')
            m.pos(23, 22)
            m.color(m.vert)
            m._print("Ligne suiv.")
            m.pos(23, 33)
            m.underline()
            m._print(' ')
            m.inverse()
            m.color(m.cyan)
            m._print('_SUITE_')
            m.pos(24, 22)
            m.color(m.vert)
            m._print("Send: →")
            m.pos(24, 34)
            m.inverse()
            m.color(m.cyan)
            m._print(' ENVOI ')

            #m.pos(23, 1)
            #m.color(m.vert)
            #m._print("Aide: →")
            #m.pos(23, 10)
            #m.inverse()
            #m.color(m.cyan)
            #m._print('GUIDE')
            m.inverse()
            m.color(m.cyan)
            m.pos(24, 1)
            m.color(m.vert)
            m._print("Home: →")
            m.pos(24, 10)
            m.inverse()
            m.color(m.cyan)
            m._print("SOMMAIRE")
            #*******
            zone = 1
            (zone, touche) = m.waitzones(zone, sltime)

            if touche == 1:
                break
            if touche == 6:
                break
        if touche == 1:

            mess = str("")
            for y in range(7):
                if not m.zones[y]['texte'] == "":
                    mess = str(mess) + " Extra text: " + str(m.zones[y]['texte'] + " ")
            print(mess)
            self.startAnalysis(mess)
        if touche == m.sommaire and zone == "sleep":
            # choix1 = ""
            print("Go to sleeper")
            self.changeState(self.stateWelcome)
        if touche == 6:  # Sommaire
            m.resetzones()
            self.changeState(self.stateWelcome)

    # ****************************************
    def stateWaitForAnswer2(self, entering):
        global answer, message, thread_1, data, data_p, chatbot_error
        print("State Wait2")
        #print(data_p)
        answer = ""
        r = usbRelaysCheck()
        print("What says relais? ", r)

        # while answer == "":
        y = False
        while thread_1.is_alive():
            if r:
                print("Relais to true")
                relay.set_state(1, True)
                # relay.set_state(4, True)
            for x in range(0, 200):
                m.pos(10, 18)
                m.scale(3)
                m._print(str(x))
                time.sleep(1)

                if 2 < x < 5 and r:
                    relay.set_state(4, True)
                elif r:
                    relay.set_state(4, False)

                if not thread_1.is_alive():

                    if r:
                        relay.set_state(1, False)
                    break

        if chatbot_error:
            print("Fortune generation failed:", chatbot_error)
            m.home()
            m.message(10, 3, 5, "AI connection failed - try again", True)
            self.changeState(self.stateEnterQuest)
            return

        self.changeState(self.stateSend)

    # ****************************************
    def stateSend(self, entering):
        global message, p, pV, answer, pdf_answer, lang, data, data_p, run, upload, z, link
        global pdf_delivery_thread, pdf_delivery_error
        global pdf_delivery_job



        print("State Send")

        # Defensive normalization also covers answers restored or assigned by
        # code paths other than the normal OpenAI response handler.
        file_content = normalize_output_text(answer)
        answer = file_content
        lines = split_string_into_lines(file_content, max_line_length=39)
        # Use the marked-up answer for the receipt so its thematic headings
        # and paragraph boundaries match the PDF. The Minitel keeps using the
        # markup-free ``answer`` above.
        thermal_source = pdf_answer or file_content
        print_lines = format_thermal_analysis(
            thermal_source, max_line_length=48
        )

        # Defensive fallback for restored answers and exceptional paths which
        # did not pass through _chatbot(). Never attempt code_None.png.
        special_code_path()

        # The paid consultation is complete as soon as the generated result is
        # available. Reset the coin counter here instead of waiting until the
        # visitor leaves the result screen.
        if entering:
            complete_coin_transaction()

        # Print as soon as the completed analysis reaches the result state.
        # The existing P + ENVOI action below remains available for reprints.
        if entering and automatic_print_enabled():
            pV = printCheck()
            print_fortune_receipt(print_lines)

        # PDF rendering and upload are intentionally deferred until after the
        # automatic receipt. They continue in the background while the result
        # pages are already usable on the Minitel.
        if entering:
            start_pdf_delivery(pdf_answer or file_content)

        print("Anzahl Zeilen", len(lines))  # anzahl zeilen
        # print(pV)
        m.home()
        m.pos(1, 1)
        page = 1


        # plusieurs pages ?
        if len(lines) > 18:
            m.pos(0, 33)
            m._print(" " + str(int(abs(page))) + '/' + str(int((len(lines) + 17) / 18)))

        while True:
            m.home()
            pV = printCheck()
            if len(lines) > 0:  # affichage
                # entête sur 2 lignes + séparation
                m.pos(0)
                result_title = (
                    transl("p10t24")
                    if analysis_mode == "partner"
                    else transl("p10t22")
                )
                m._print(result_title)
                m.pos(1)
                m._print(str(data_p[0]))
                m.pos(2)
                m.color(m.bleu)
                m.plot('̶', 40)

                # plusieurs pages ?
                if len(lines) > 18:
                    m.pos(0, 33)
                    m._print(" " + str(int(abs(page))) + '/' + str(int((len(lines) + 17) / 18)))
                    m.pos(3)

                # première ligne de résultat
                y = 3
                m.pos(y)
                for a in range((page - 1) * 18, page * 18, ):
                    # for a in range( page*9,(page-1)*9, -1): # neu rückwärts
                    # print("Anzeige page:", (page - 1) * 18, "  ", page * 18)
                    y = y
                    m.pos(y, 1)
                    if a < len(lines):
                        r = lines[a]
                        # print(r, len(r))
                        m.color(m.blanc)
                        strcenter(row=y, pos=20, txt=r, width=40, size=0)
                        # m._print(r)
                        y = y + 1
                        m.pos(y, 1)
                        m.color(m.vert)
                        m.color(m.bleu)

                # ligne finale
                m.pos(21)
                m.color(m.bleu)
                m.plot('̶', 40)

                if page > 1:
                    if len(lines) > page * 18:  # place pour le SUITE
                        m.pos(22, 26)
                    else:
                        m.pos(22, 26)
                    m.color(m.vert)
                    m._print("prec.")
                    m.pos(22, 33)
                    m.underline()
                    m._print(' ')
                    m.inverse()
                    m.color(m.cyan)
                    m._print('_RETOUR')

                if len(lines) > page * 18:
                    m.pos(23, 26)
                    m.color(m.vert)
                    m._print("suiv.")
                    m.pos(23, 34)
                    m.underline()
                    m._print(' ')
                    m.inverse()
                    m.color(m.cyan)
                    m._print('_SUITE')
                pV = printCheck()

                if pV == True:
                    m.pos(22, 1)
                    m._print("Print:    P + → ")
                    m.pos(22, 17)
                    m.inverse()
                    m.color(m.cyan)
                    m._print("ENVOI")
                    m.cursor(True)
                m.pos(23, 1)
                m._print("Download: D + → ENVOI")
                m.pos(23, 17)
                m.inverse()
                m.color(m.cyan)
                m._print("ENVOI")

                m.pos(24, 1)
                m.color(m.vert)
                m._print("Aide: →")
                m.pos(24, 17)
                m.inverse()
                m.color(m.cyan)
                m._print('GUIDE')
                #m.underline()
                #m._print('')
                m.inverse()
                m.color(m.cyan)
                m.pos(24, 28)
                m.color(m.vert)
                m._print("Home")
                m.pos(24, 33)
                m.inverse()
                m.color(m.cyan)
                m._print("SOMMAIRE")

            else:
                page = abs(page)

                # attente saisie
            if pV == True:
                (choix, touche) = m.input(0, 38, 1, sltime)
            else:
                (choix, touche) = m.input(0, 38, 1, sltime)
                m.cursor(False)
            # ****** check for integer
            if choix == "y" or choix == "Y":
                choix1 = "Y"
            elif choix == "d" or choix == "D":
                choix1 = "D"
            elif choix == "p" or choix == "P":
                choix1 = "P"
            else:
                choix1 = ""
            if not isinstance(choix, int):
                if not choix.isdigit():
                    choix = 0
                choix = int(choix)

            if choix == "":
                choix = int(0)

            elif choix > len(lines):
                break
            else:
                choix = int(choix)
            m.cursor(False)
            if touche == m.suite:
                if page * 18 < len(lines):
                    page = page + 1
                else:
                    m.bip()
            elif touche == m.retour:
                if page > 1:
                    page = page - 1
                else:
                    m.bip()
                #**********************QRCODE und Data upload
            elif touche == m.envoi and choix1 == "D":
                # The final URL is reserved before rendering starts, so the QR
                # page never needs to wait for PDF creation or upload.
                if pdf_delivery_job and not pdf_delivery_job['error']:
                    qrshow(pdf_delivery_job['link'])
                else:
                    error = (
                        pdf_delivery_job['error']
                        if pdf_delivery_job else pdf_delivery_error
                    )
                    print("PDF download unavailable:", error)
                    m.bip()

            elif touche == m.envoi and choix1 == "P":
                print_fortune_receipt(print_lines)
                break
            elif touche == m.annulation:
                break
            elif touche == m.guide:
                break
            elif touche == m.sommaire:
                break
            elif touche == m.correction:  # retour saisie pour correction
                break
                # return(touche)
            elif touche == m.repetition:
                # print(print_lines)
                break

                # end while

        if touche == m.sommaire:
            m.resetzones()
            self.changeState(self.stateWelcome)


####
# Program entry point
###
def main():
    global data, ver, thread_0, run, dataCC, ser, coin_counter_enabled

    # Make runtime and coin-counter messages immediately visible in journalctl.
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
    except AttributeError:
        pass

    # Define Version
    ver = "2.1"
    print("Fortune Teller ", ver, "\n")
    # create state machine object
    stateMachine = StateMachine()

    # Create settings.ini if not exist
    ini_exists = os.path.isfile("settings.ini")
    # print("INI file exist? ", ini_exists)
    if not ini_exists:
        config = configparser.ConfigParser()
        config['prefs'] = {
            'IP_adr': '127.0.0.1',
            'speed': '1200',
            'timer': '120',
            'lang_code': 'FR'
        }
        config['printer'] = {
            'p_idvend': '0x0456',
            'p_idprod': '0x0808',
            'auto_print': 'yes',
            'print_special_code': 'yes',
            'p_timer': '',
            'p_3': '',
            'p_4': ''}
        config['IA'] = {
            'ia_model': 'gpt-3.5-turbo',
            'max_tok': '300',
            'max_completion_tok': '1000',
            'reasoning_effort': 'none',
            'partner_extra_question': 'no'}
        config['astrology'] = {
            'print_chart': 'no',
            'chart_language': 'AUTO',
            'chart_theme': 'black-and-white',
            'chart_style': 'modern',
            'chart_width': '560',
            'chart_render_scale': '3',
            'chart_threshold': '200',
            'chart_line_boost': '1',
            'chart_zodiac_background': 'no'}
        config['pdf'] = {
            'upload_url': '',
            'public_base_url': '',
            'include_chart': 'yes',
            'chart_theme': 'classic',
            'chart_style': 'modern',
            'chart_resolution': '1600',
            'chart_zodiac_background': 'yes'}
        config['coin_counter'] = {
            'enabled': 'no'}
        with open('settings.ini', 'w') as configfile:
            config.write(configfile)
        print("Ini file created")
    config = configparser.ConfigParser()
    config.read('settings.ini')

    # Prepare dataobject with all Screen txts in diff languages
    csv_dateipfad = './WM/lang.csv'
    data = create_data(csv_dateipfad)  # to function
    
    # Prepare dataobject with all Countrycodes
    csv_dateipfad = './WM/CC.csv'
    dataCC = create_data(csv_dateipfad)  # to function
    # Enable paid operation only when explicitly requested in settings.ini.
    coin_counter_enabled = config.getboolean(
        'coin_counter', 'enabled', fallback=False
    )
    run = not coin_counter_enabled
    if coin_counter_enabled:
        ser = find_arduino_port()
        if ser is not None:
            thread_0 = Thread(target=listener, daemon=True)
            thread_0.start()
        else:
            print("Coin counter enabled, but no Arduino is available")
    else:
        print("Coin counter disabled in settings.ini")
    print(" ")
    ###
    # Main loop
    ###
    while True:
        stateMachine.update()


# start
if __name__ == '__main__':
    main()
