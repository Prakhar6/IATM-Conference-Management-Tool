import io
import qrcode
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


BADGE_SIZE = (4 * inch, 3 * inch)


def generate_qr_code(data):
    """Generate a QR code image and return as bytes buffer."""
    qr = qrcode.QRCode(version=1, box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf


def generate_badge_pdf(membership):
    """Generate a printable name badge with QR code."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(BADGE_SIZE), topMargin=0.3 * inch, bottomMargin=0.2 * inch, leftMargin=0.3 * inch, rightMargin=0.3 * inch)

    styles = getSampleStyleSheet()
    brand_color = HexColor('#667eea')

    title_style = ParagraphStyle('BadgeTitle', parent=styles['Title'], fontSize=10, textColor=brand_color, alignment=TA_CENTER, spaceAfter=2)
    name_style = ParagraphStyle('BadgeName', parent=styles['Title'], fontSize=16, textColor=HexColor('#1e293b'), alignment=TA_CENTER, spaceAfter=2)
    org_style = ParagraphStyle('BadgeOrg', parent=styles['Normal'], fontSize=10, textColor=HexColor('#64748b'), alignment=TA_CENTER, spaceAfter=2)
    role_style = ParagraphStyle('BadgeRole', parent=styles['Normal'], fontSize=9, textColor=HexColor('#ffffff'), alignment=TA_CENTER, backColor=brand_color)

    user = membership.user
    conference = membership.conference

    # QR code with membership info
    qr_data = f"IATM|{user.email}|{conference.slug}|{membership.id}"
    qr_buf = generate_qr_code(qr_data)
    qr_image = Image(qr_buf, width=0.8 * inch, height=0.8 * inch)

    elements = []
    elements.append(Paragraph(conference.conference_name, title_style))
    elements.append(Paragraph(user.get_full_name(), name_style))
    if user.organization:
        elements.append(Paragraph(user.organization, org_style))

    roles = membership.role1
    if membership.role2 != 'N/A':
        roles += f" | {membership.role2}"
    elements.append(Paragraph(roles, role_style))
    elements.append(Spacer(1, 0.1 * inch))
    elements.append(qr_image)

    doc.build(elements)
    buffer.seek(0)
    return buffer
