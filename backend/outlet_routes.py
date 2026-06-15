# backend/outlet_routes.py
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Outlet
from datetime import datetime
import json









outlet_bp = Blueprint('outlet', __name__)

# ========== PUBLIC ROUTES ==========

@outlet_bp.route('/outlets', methods=['GET'])
def get_outlets():
    """Get all active outlets for public display"""
    try:
        category = request.args.get('category')
        
        query = Outlet.query.filter_by(is_active=True)
        
        if category and category != 'all':
            query = query.filter_by(category=category)
        
        outlets = query.order_by(Outlet.display_order, Outlet.name).all()
        
        return jsonify([{
            'id': o.id,
            'name': o.name,
            'category': o.category,
            'category_display': get_category_display(o.category),
            'description': o.description,
            'address': o.address,
            'city': o.city,
            'latitude': o.latitude,
            'longitude': o.longitude,
            'phone': o.phone,
            'email': o.email,
            'working_hours': o.working_hours,
            'services': o.get_services_list()
        } for o in outlets]), 200
    except Exception as e:
        print(f"Error in get_outlets: {e}")
        return jsonify([]), 200

@outlet_bp.route('/outlets/categories', methods=['GET'])
def get_outlet_categories():
    """Get all outlet categories with counts"""
    try:
        categories = [
            {'value': 'office_branch', 'label': '🏢 Office Branch', 'color': '#1e3a8a'},
            {'value': 'depot', 'label': '🚚 Depot / Distribution Center', 'color': '#f59e0b'},
            {'value': 'outlet', 'label': '🏪 Retail Outlet', 'color': '#10b981'}
        ]
        
        for cat in categories:
            cat['count'] = Outlet.query.filter_by(category=cat['value'], is_active=True).count()
        
        return jsonify(categories), 200
    except Exception as e:
        print(f"Error in get_outlet_categories: {e}")
        return jsonify([]), 200

def get_category_display(category):
    """Convert category code to display name"""
    categories = {
        'office_branch': '🏢 Office Branch',
        'depot': '🚚 Depot',
        'outlet': '🏪 Retail Outlet'
    }
    return categories.get(category, category)

# ========== ADMIN ROUTES ==========

@outlet_bp.route('/admin/outlets', methods=['GET'])
@login_required



def admin_get_outlets():
    """Get all outlets for admin panel"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        outlets = Outlet.query.order_by(Outlet.display_order, Outlet.name).all()
        
        return jsonify([{
            'id': o.id,
            'name': o.name,
            'category': o.category,
            'description': o.description,
            'address': o.address,
            'city': o.city,
            'latitude': o.latitude,
            'longitude': o.longitude,
            'phone': o.phone,
            'email': o.email,
            'working_hours': o.working_hours,
            'services': o.get_services_list(),
            'is_active': o.is_active,
            'display_order': o.display_order,
            'created_at': o.created_at.isoformat() if o.created_at else None
        } for o in outlets]), 200
    except Exception as e:
        print(f"Error in admin_get_outlets: {e}")
        return jsonify([]), 200

@outlet_bp.route('/admin/outlets', methods=['POST'])
@login_required

def admin_create_outlet():
    """Create a new outlet"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.json
        
        # Validate required fields
        required_fields = ['name', 'category', 'address', 'latitude', 'longitude']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        outlet = Outlet(
            name=data['name'],
            category=data['category'],
            description=data.get('description', ''),
            address=data['address'],
            city=data.get('city', ''),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            working_hours=data.get('working_hours', ''),
            is_active=data.get('is_active', True),
            display_order=data.get('display_order', 0)
        )
        
        if data.get('services'):
            outlet.set_services_list(data['services'])
        
        db.session.add(outlet)
        db.session.commit()
        
        return jsonify({'message': 'Outlet created', 'id': outlet.id}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating outlet: {e}")
        return jsonify({'error': str(e)}), 500

@outlet_bp.route('/admin/outlets/<int:outlet_id>', methods=['PUT'])
@login_required

def admin_update_outlet(outlet_id):
    """Update an outlet"""
    try:
        if current_user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Permission denied'}), 403
        
        outlet = Outlet.query.get_or_404(outlet_id)
        data = request.json
        
        updatable_fields = ['name', 'category', 'description', 'address', 'city',
                           'latitude', 'longitude', 'phone', 'email', 'working_hours',
                           'is_active', 'display_order']
        
        for field in updatable_fields:
            if field in data:
                if field in ['latitude', 'longitude']:
                    setattr(outlet, field, float(data[field]))
                else:
                    setattr(outlet, field, data[field])
        
        if 'services' in data:
            outlet.set_services_list(data['services'])
        
        outlet.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Outlet updated'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@outlet_bp.route('/admin/outlets/<int:outlet_id>', methods=['DELETE'])
@login_required

def admin_delete_outlet(outlet_id):
    """Delete an outlet"""
    try:
        if current_user.role != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        
        outlet = Outlet.query.get_or_404(outlet_id)
        db.session.delete(outlet)
        db.session.commit()
        
        return jsonify({'message': 'Outlet deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

       