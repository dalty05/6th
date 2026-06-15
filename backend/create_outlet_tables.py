# create_outlet_tables.py
from app import app, db
from models import Outlet

with app.app_context():
    db.create_all()
    print("✅ Outlet tables created successfully!")
    
    # Optional: Add sample outlets for testing
    sample_outlets = [
        {
            'name': 'Meru Main Office',
            'category': 'office_branch',
            'description': 'Headquarters and main administrative office',
            'address': 'P.O. Box 2919, Meru Town',
            'city': 'Meru',
            'latitude': 0.0500,
            'longitude': 37.6500,
            'phone': '+254 710 901376',
            'email': 'info@merudairy.co.ke',
            'working_hours': 'Mon-Fri: 8:00 AM - 5:00 PM, Sat: 9:00 AM - 1:00 PM',
            'services': '["Customer Support", "Bulk Orders", "Account Services"]'
        },
        {
            'name': 'Nairobi Depot',
            'category': 'depot',
            'description': 'Main distribution center for Nairobi region',
            'address': 'Industrial Area, Nairobi',
            'city': 'Nairobi',
            'latitude': -1.2921,
            'longitude': 36.8219,
            'phone': '+254 720 123456',
            'email': 'nairobi@merudairy.co.ke',
            'working_hours': 'Mon-Sat: 7:00 AM - 6:00 PM',
            'services': '["Bulk Orders", "Product Pickup"]'
        },
        {
            'name': 'Mombasa Outlet',
            'category': 'outlet',
            'description': 'Retail shop for individual customers',
            'address': 'CBD, Mombasa',
            'city': 'Mombasa',
            'latitude': -4.0435,
            'longitude': 39.6682,
            'phone': '+254 741 234567',
            'email': 'mombasa@merudairy.co.ke',
            'working_hours': 'Mon-Sun: 8:00 AM - 8:00 PM',
            'services': '["Product Purchase", "Order Pickup"]'
        }
    ]
    
    for outlet_data in sample_outlets:
        existing = Outlet.query.filter_by(name=outlet_data['name']).first()
        if not existing:
            outlet = Outlet(
                name=outlet_data['name'],
                category=outlet_data['category'],
                description=outlet_data.get('description', ''),
                address=outlet_data['address'],
                city=outlet_data.get('city', ''),
                latitude=outlet_data['latitude'],
                longitude=outlet_data['longitude'],
                phone=outlet_data.get('phone', ''),
                email=outlet_data.get('email', ''),
                working_hours=outlet_data.get('working_hours', ''),
                services=outlet_data.get('services', '[]'),
                is_active=True
            )
            db.session.add(outlet)
    
    db.session.commit()
    print(f"✅ Added {len(sample_outlets)} sample outlets")