# backend/add_missing_components.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, DashboardComponent

with app.app_context():
    print("🔍 Adding missing components...")
    
    missing_components = [
        {
            'key': 'partner-dashboard',
            'label': 'Partner Dashboard',
            'icon': 'fas fa-handshake',
            'component_name': 'PartnerDashboard',
            'path': '/partner/dashboard',
            'description': 'Partner dashboard with referral stats',
            'section': 'Main',
            'order': 1
        },
        {
            'key': 'partner-links',
            'label': 'Referral Links',
            'icon': 'fas fa-link',
            'component_name': 'PartnerReferralLinks',
            'path': '/partner/links',
            'description': 'Manage your referral links',
            'section': 'Main',
            'order': 2
        },
        {
            'key': 'partner-analytics',
            'label': 'Analytics',
            'icon': 'fas fa-chart-line',
            'component_name': 'PartnerAnalytics',
            'path': '/partner/analytics',
            'description': 'View your referral analytics',
            'section': 'Main',
            'order': 3
        },
        {
            'key': 'tour-reports',
            'label': 'Tour Reports',
            'icon': 'fas fa-chart-bar',
            'component_name': 'TourManagerReports',
            'path': '/tour-manager/reports',
            'description': 'Tour analytics and reports',
            'section': 'Tours',
            'order': 5
        }
    ]
    
    added_count = 0
    for comp_data in missing_components:
        existing = DashboardComponent.query.filter_by(key=comp_data['key']).first()
        if existing:
            print(f"⚠️ {comp_data['key']} already exists, updating...")
            # Update existing
            for key, value in comp_data.items():
                setattr(existing, key, value)
        else:
            print(f"✅ Adding {comp_data['key']}")
            comp = DashboardComponent(**comp_data)
            db.session.add(comp)
            added_count += 1
    
    db.session.commit()
    print(f"✅ Added {added_count} new components")
    
    # Verify
    components = DashboardComponent.query.all()
    print(f"\n📋 Total components: {len(components)}")
    for comp in components:
        print(f"  - {comp.key}: {comp.label} ({comp.section})")