import os
from datetime import datetime
from io import BytesIO

class TourPDFService:
    """Service for generating PDF documents"""
    
    def __init__(self):
        """Initialize the PDF service"""
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        
    def generate_certificate(self, booking):
        """Generate a clearance certificate PDF"""
        try:
            # Try to use reportlab
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_CENTER
            from reportlab.pdfgen import canvas
            
            # Create filename
            filename = f"certificate_{booking.reference}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.static_dir, 'certificates', filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create PDF
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            # Styles
            title_style = ParagraphStyle(
                'Title',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e3a8a'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=getSampleStyleSheet()['Heading2'],
                fontSize=18,
                textColor=colors.HexColor('#f59e0b'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            body_style = ParagraphStyle(
                'Body',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=12,
                leading=16,
                spaceAfter=10
            )
            
            # Title
            story.append(Paragraph("TOUR CLEARANCE CERTIFICATE", title_style))
            story.append(Paragraph("Mount Kenya Milk - Factory Tour", subtitle_style))
            story.append(Spacer(1, 20))
            
            # Content
            content = f"""
            <para align="center" fontSize="14" leading="20">
            This is to certify that
            </para>
            <para align="center" fontSize="18" leading="24" spaceAfter="20">
            <b>{booking.customer_name}</b>
            </para>
            <para align="center" fontSize="14" leading="20">
            has successfully completed the factory tour at
            </para>
            <para align="center" fontSize="16" leading="24" spaceAfter="20">
            <b>Mount Kenya Milk Factory</b>
            </para>
            """
            story.append(Paragraph(content, body_style))
            
            # Booking details table
            data = [
                ['Booking Reference', booking.reference],
                ['Tour Package', booking.package.name if booking.package else 'N/A'],
                ['Tour Date', booking.tour_date.strftime('%B %d, %Y at %I:%M %p') if booking.tour_date else 'N/A'],
                ['Number of People', str(booking.people_count)],
                ['Total Amount', f"KES {booking.total_amount:,.0f}"],
                ['Payment Status', booking.payment_status.upper()]
            ]
            
            table = Table(data, colWidths=[2.5*inch, 3.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, -1), 10),
                ('FONTSIZE', (1, 0), (1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            
            story.append(Spacer(1, 20))
            story.append(table)
            
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#6b7280'),
                alignment=TA_CENTER
            )
            
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                footer_style
            ))
            story.append(Paragraph(
                "This certificate is the property of Meru Central Dairy Co-operative Union Ltd.",
                footer_style
            ))
            
            doc.build(story)
            
            return filepath, filename
            
        except ImportError:
            filename = f"certificate_{booking.reference}_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = os.path.join(self.static_dir, 'certificates', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            content = f"""
            ================================================
                    TOUR CLEARANCE CERTIFICATE
            ================================================
            
            This is to certify that
            
            {booking.customer_name}
            
            has successfully completed the factory tour at
            
            Mount Kenya Milk Factory
            
            ------------------------------------------------
            Booking Reference: {booking.reference}
            Tour Package: {booking.package.name if booking.package else 'N/A'}
            Tour Date: {booking.tour_date.strftime('%B %d, %Y') if booking.tour_date else 'N/A'}
            Number of People: {booking.people_count}
            Total Amount: KES {booking.total_amount:,.0f}
            Payment Status: {booking.payment_status.upper()}
            ------------------------------------------------
            
            Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            
            This certificate is the property of 
            Meru Central Dairy Co-operative Union Ltd.
            ================================================
            """
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            return filepath, filename