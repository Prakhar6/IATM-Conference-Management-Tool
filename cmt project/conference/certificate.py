import io
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def generate_certificate_pdf(user, conference, sessions_attended):
    """Generate an attendance certificate PDF and return the buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        leftMargin=1.5 * inch,
        rightMargin=1.5 * inch,
    )

    styles = getSampleStyleSheet()
    brand_color = HexColor('#667eea')
    gold_color = HexColor('#d4a843')

    # Custom styles
    org_style = ParagraphStyle(
        'OrgName', parent=styles['Normal'],
        fontSize=14, textColor=brand_color, alignment=TA_CENTER,
        spaceAfter=6, fontName='Helvetica-Bold',
    )
    cert_title = ParagraphStyle(
        'CertTitle', parent=styles['Title'],
        fontSize=36, textColor=gold_color, alignment=TA_CENTER,
        spaceAfter=20, fontName='Helvetica-Bold',
    )
    name_style = ParagraphStyle(
        'RecipientName', parent=styles['Title'],
        fontSize=28, textColor=HexColor('#1e293b'), alignment=TA_CENTER,
        spaceAfter=10, fontName='Helvetica-Bold',
    )
    body_style = ParagraphStyle(
        'CertBody', parent=styles['Normal'],
        fontSize=14, textColor=HexColor('#334155'), alignment=TA_CENTER,
        spaceAfter=8, leading=22,
    )
    footer_style = ParagraphStyle(
        'CertFooter', parent=styles['Normal'],
        fontSize=10, textColor=HexColor('#64748b'), alignment=TA_CENTER,
    )
    line_style = ParagraphStyle(
        'Line', parent=styles['Normal'],
        fontSize=6, alignment=TA_CENTER, textColor=gold_color,
    )

    elements = []

    # Header
    elements.append(Paragraph("IATM - International Association of Technology and Management", org_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Decorative line
    elements.append(Paragraph("_" * 80, line_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Title
    elements.append(Paragraph("Certificate of Attendance", cert_title))
    elements.append(Spacer(1, 0.2 * inch))

    # Body text
    elements.append(Paragraph("This is to certify that", body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Recipient name
    full_name = user.get_full_name()
    elements.append(Paragraph(full_name, name_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Details
    if user.organization:
        elements.append(Paragraph(f"from {user.organization}", body_style))

    elements.append(Paragraph(
        f"has successfully attended <b>{sessions_attended}</b> session{'s' if sessions_attended != 1 else ''} at",
        body_style,
    ))
    elements.append(Spacer(1, 0.05 * inch))
    elements.append(Paragraph(
        f"<b>{conference.conference_name}</b>",
        body_style,
    ))
    elements.append(Paragraph(
        f"held from {conference.start_date.strftime('%B %d, %Y')} to {conference.end_date.strftime('%B %d, %Y')}",
        body_style,
    ))
    if conference.location:
        elements.append(Paragraph(f"at {conference.location}", body_style))

    elements.append(Spacer(1, 0.4 * inch))

    # Decorative line
    elements.append(Paragraph("_" * 80, line_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Footer
    elements.append(Paragraph("IATM Conference Management System | iatm.us", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
