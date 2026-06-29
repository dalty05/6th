
import os
import csv
from datetime import datetime
from io import StringIO

class TourReportService:
    """Service for generating reports"""
    
    def __init__(self):
        """Initialize the report service"""
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    
    def generate_revenue_report(self, bookings, start_date, end_date):
        """Generate a revenue report PDF"""
        try:
            # Try to use reportlab
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_CENTER
            
            filename = f"revenue_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(self.static_dir, 'reports', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            doc = SimpleDocTemplate(
                filepath,
                pagesize=landscape(A4),
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            story = []
            
            title_style = ParagraphStyle(
                'Title',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#1e3a8a'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            
            story.append(Paragraph("Revenue Report", title_style))
            story.append(Paragraph(
                f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}",
                getSampleStyleSheet()['Normal']
            ))
            story.append(Spacer(1, 20))
            
            # Summary stats
            total_revenue = sum(b.total_amount for b in bookings if b.status == 'completed')
            total_bookings = len(bookings)
            confirmed = len([b for b in bookings if b.status == 'confirmed'])
            pending = len([b for b in bookings if b.status == 'pending'])
            
            summary_data = [
                ['Total Revenue', 'Total Bookings', 'Confirmed', 'Pending'],
                [f"KES {total_revenue:,.0f}", str(total_bookings), str(confirmed), str(pending)]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, 1), [colors.HexColor('#f8fafc')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 30))
            
            doc.build(story)
            
            return filepath, filename
            
        except ImportError:
            # Fallback: Generate CSV instead
            filename = f"revenue_report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"
            filepath = os.path.join(self.static_dir, 'reports', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            csv_data = self.generate_csv_export(bookings)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            
            return filepath, filename
    
    def generate_csv_export(self, bookings):
        """Generate CSV export of bookings"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Reference', 'Customer Name', 'Customer Email', 'Customer Phone',
            'Package', 'Tour Date', 'People Count', 'Total Amount',
            'Status', 'Payment Status', 'Created At'
        ])
        
        # Data
        for b in bookings:
            writer.writerow([
                b.reference,
                b.customer_name,
                b.customer_email,
                b.customer_phone,
                b.package.name if b.package else 'N/A',
                b.tour_date.strftime('%Y-%m-%d %H:%M') if b.tour_date else 'N/A',
                b.people_count,
                b.total_amount,
                b.status,
                b.payment_status,
                b.created_at.strftime('%Y-%m-%d %H:%M') if b.created_at else 'N/A'
            ])
        
        return output.getvalue()