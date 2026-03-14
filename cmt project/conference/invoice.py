import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


def generate_invoice_pdf(payment):
    """Generate a PDF invoice for a payment and return the buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

    styles = getSampleStyleSheet()
    brand_color = HexColor('#667eea')

    # Custom styles
    title_style = ParagraphStyle('InvoiceTitle', parent=styles['Title'], fontSize=24, textColor=brand_color)
    heading_style = ParagraphStyle('InvoiceHeading', parent=styles['Heading2'], textColor=brand_color, fontSize=14)
    right_style = ParagraphStyle('RightAlign', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)
    center_style = ParagraphStyle('CenterAlign', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)

    elements = []

    # Header
    elements.append(Paragraph("IATM Conference", title_style))
    elements.append(Paragraph("Invoice / Receipt", styles['Heading3']))
    elements.append(Spacer(1, 0.3 * inch))

    # Invoice details
    invoice_data = [
        ['Invoice Number:', f'INV-{payment.id:06d}'],
        ['Date:', payment.created_at.strftime('%B %d, %Y')],
        ['Status:', payment.get_status_display()],
    ]
    if payment.paypal_order_id:
        invoice_data.append(['PayPal Order ID:', payment.paypal_order_id])

    invoice_table = Table(invoice_data, colWidths=[2 * inch, 4 * inch])
    invoice_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Bill To
    elements.append(Paragraph("Bill To:", heading_style))
    user = payment.user
    elements.append(Paragraph(f"{user.get_full_name()}", styles['Normal']))
    elements.append(Paragraph(f"{user.email}", styles['Normal']))
    if user.organization:
        elements.append(Paragraph(f"{user.organization}", styles['Normal']))
    if user.country:
        elements.append(Paragraph(f"{user.country}", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))

    # Items table
    elements.append(Paragraph("Items:", heading_style))
    tier_name = payment.tier.name if payment.tier else "Registration"
    items_data = [
        ['Description', 'Qty', 'Amount'],
        [f'{payment.conference.conference_name}\n{tier_name} Registration', '1', f'${payment.amount:.2f}'],
        ['', '', ''],
        ['', 'Total:', f'${payment.amount:.2f} {payment.currency}'],
    ]
    items_table = Table(items_data, colWidths=[3.5 * inch, 1.5 * inch, 1.5 * inch])
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), brand_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        # Body
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        # Total row
        ('FONTNAME', (1, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (1, -1), (-1, -1), 12),
        ('LINEABOVE', (1, -1), (-1, -1), 1, brand_color),
        # Grid
        ('GRID', (0, 0), (-1, 1), 0.5, HexColor('#e2e8f0')),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Footer
    elements.append(Paragraph("Thank you for your registration!", center_style))
    elements.append(Paragraph("IATM Conference Management System | iatm.us", center_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
