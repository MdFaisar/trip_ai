from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch, mm
import tempfile
import os
import re
from utils import clean_text

# Register Arial Unicode MS for font support
FONT_PATH = os.path.join(os.path.dirname(__file__), './assets/Arial Unicode.ttf')
pdfmetrics.registerFont(TTFont('ArialUnicode', FONT_PATH))

def add_separator(story, width, color=colors.HexColor('#e0e0e0')):
    """Add a separator line using Table"""
    separator = Table([['']], colWidths=[width], rowHeights=[2])
    separator.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 1, color),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(separator)
    story.append(Spacer(1, 10))

def create_custom_styles():
    """
    Create custom styles for the PDF with enhanced visual appeal.
    """
    styles = getSampleStyleSheet()

    # Color palette
    primary_color = colors.HexColor('#1a237e')  # Dark Blue
    secondary_color = colors.HexColor('#0d47a1')  # Medium Blue
    accent_color = colors.HexColor('#2196f3')  # Light Blue
    text_color = colors.HexColor('#212121')  # Almost Black
    subtext_color = colors.HexColor('#757575')  # Gray

    # Title style with background
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontName='ArialUnicode',
        fontSize=28,
        spaceAfter=30,
        textColor=primary_color,
        alignment=TA_CENTER,
        leading=36,
        borderPadding=(10, 10, 10, 10),
        borderColor=primary_color,
        borderWidth=2,
        backColor=colors.HexColor('#f5f5f5')
    ))

    # Subtitle style
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        fontName='ArialUnicode',
        fontSize=20,
        spaceAfter=25,
        textColor=secondary_color,
        alignment=TA_CENTER,
        leading=26
    ))

    # Day Header style with gradient-like background
    styles.add(ParagraphStyle(
        name='DayHeader',
        fontName='ArialUnicode',
        fontSize=18,
        spaceBefore=20,
        spaceAfter=15,
        textColor=colors.white,
        leading=24,
        alignment=TA_LEFT,
        borderPadding=(8, 12, 8, 12),
        backColor=secondary_color
    ))

    # Section Header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='ArialUnicode',
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10,
        textColor=accent_color,
        leading=22,
        bold=True,
        borderPadding=(3, 0, 3, 10),
        leftIndent=5
    ))

    # Subsection Header style
    styles.add(ParagraphStyle(
        name='SubsectionHeader',
        fontName='ArialUnicode',
        fontSize=14,
        spaceBefore=12,
        spaceAfter=8,
        textColor=subtext_color,
        leading=20,
        leftIndent=15,
        bold=True
    ))

    # Enhanced bullet point style
    styles.add(ParagraphStyle(
        name='BulletPoint',
        fontName='ArialUnicode',
        fontSize=12,
        leftIndent=30,
        firstLineIndent=15,
        spaceBefore=3,
        spaceAfter=3,
        leading=18,
        textColor=text_color,
        bulletIndent=15,
        alignment=TA_LEFT
    ))

    # Info box style
    styles.add(ParagraphStyle(
        name='InfoBox',
        fontName='ArialUnicode',
        fontSize=12,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=10,
        spaceAfter=10,
        leading=16,
        textColor=text_color,
        borderPadding=(10, 10, 10, 10),
        borderColor=accent_color,
        backColor=colors.HexColor('#f3f9ff')
    ))

    # Footer style
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='ArialUnicode',
        fontSize=8,
        textColor=subtext_color,
        alignment=TA_CENTER
    ))

    return styles

def create_header_footer(canvas, doc):
    """Add header and footer to each page"""
    width, height = A4
    
    # Header
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#f5f5f5'))
    canvas.rect(0, height - 50, width, 50, fill=True)
    canvas.setFillColor(colors.HexColor('#1a237e'))
    canvas.setFont('ArialUnicode', 10)
    canvas.drawString(72, height - 30, "AI Trip Planner")
    canvas.drawRightString(width - 72, height - 30, f"Page {doc.page}")
    canvas.restoreState()
    
    # Footer
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#f5f5f5'))
    canvas.rect(0, 0, width, 30, fill=True)
    canvas.setFillColor(colors.HexColor('#757575'))
    canvas.setFont('ArialUnicode', 8)
    canvas.drawCentredString(width/2, 10, "Generated with ♥ by TripAI")
    canvas.restoreState()

def parse_section(content):
    """
    Parse content into sections and bullet points with improved formatting.
    """
    sections = []
    current_section = {'header': '', 'points': [], 'info': ''}
    
    lines = content.split('\n')
    info_block = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if info_block:
                current_section['info'] = ' '.join(info_block)
                info_block = []
            continue
            
        if ':' in line and not any(char.isdigit() for char in line.split(':')[0]):
            if current_section['header'] or current_section['points']:
                sections.append(current_section)
            current_section = {'header': line, 'points': [], 'info': ''}
            info_block = []
        elif line.startswith(('•', '-', '*')):
            point = clean_text(line.lstrip('•-* '))
            if point:
                current_section['points'].append(point)
        else:
            info_block.append(line)
    
    if info_block:
        current_section['info'] = ' '.join(info_block)
    
    if current_section['header'] or current_section['points']:
        sections.append(current_section)
    
    return sections

def create_overview_table(trip_details, styles):
    """Create a summary table for trip overview"""
    data = [
        ['Trip Summary', ''],
        ['Departure', trip_details['start_location']],
        ['Destination', trip_details['destination']],
        ['Start Date', trip_details['start_date']],
        ['End Date', trip_details['end_date']],
        ['Duration', f"{trip_details['duration']} days"]
    ]
    
    table = Table(data, colWidths=[120, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ArialUnicode'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
    ]))
    return table

def generate_trip_pdf(trip_plan, start_location, destination, start_date, end_date):
    """
    Generate a beautifully styled PDF file for the trip plan.
    """
    # Create a temporary file for the PDF
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = temp_pdf.name
    temp_pdf.close()

    # Create the PDF document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Get styles
    styles = create_custom_styles()

    # Build the PDF content
    story = []

    # Add title
    title = f"Travel Itinerary\n{start_location} to {destination}"
    story.append(Paragraph(title, styles['CustomTitle']))

    # Add date range
    date_range = f"Journey Dates: {start_date} - {end_date}"
    story.append(Paragraph(date_range, styles['CustomSubtitle']))

    # Add overview table
    trip_details = {
        'start_location': start_location,
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
        'duration': (end_date - start_date).days + 1
    }
    story.append(create_overview_table(trip_details, styles))
    story.append(Spacer(1, 20))

    # Add separator
    add_separator(story, 450)

    # Split content into days
    days = re.split(r'(?=Day \d+:|DAY \d+:)', trip_plan)

    for day in days:
        if day.strip():
            # Add day header
            if re.match(r'Day \d+:|DAY \d+:', day):
                header = day.split('\n')[0]
                content = '\n'.join(day.split('\n')[1:])
            else:
                header = "Trip Overview"
                content = day

            story.append(Paragraph(header, styles['DayHeader']))

            # Parse and add sections
            sections = parse_section(content)
            for section in sections:
                if section['header']:
                    story.append(Paragraph(section['header'], styles['SectionHeader']))
                
                if section['info']:
                    story.append(Paragraph(section['info'], styles['InfoBox']))
                
                for point in section['points']:
                    bullet_text = f"• {point}"
                    story.append(Paragraph(bullet_text, styles['BulletPoint']))
                
                story.append(Spacer(1, 8))

            add_separator(story, 450)

    # Build the PDF with header and footer
    doc.build(story, onFirstPage=create_header_footer, onLaterPages=create_header_footer)

    return pdf_path