# app_routes.py
from flask import Blueprint, jsonify
from models import db, Product, BlogPost, Testimonial, Statistic

products_bp = Blueprint('products', __name__)
blog_bp = Blueprint('blog', __name__)
testimonials_bp = Blueprint('testimonials', __name__)
statistics_bp = Blueprint('statistics', __name__)

# Products Routes
@products_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'category': p.category,
        'description': p.description,
        'benefits': p.benefits,
        'packaging_sizes': p.packaging_sizes,
        'nutritional_info': p.nutritional_info,
        'ingredients': p.ingredients,
        'image_url': p.image_url,
        'featured': p.featured
    } for p in products])

@products_bp.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'category': product.category,
        'description': product.description,
        'benefits': product.benefits,
        'packaging_sizes': product.packaging_sizes,
        'nutritional_info': product.nutritional_info,
        'ingredients': product.ingredients,
        'image_url': product.image_url
    })

# Blog Routes
@blog_bp.route('/blog', methods=['GET'])
def get_blog_posts():
    posts = BlogPost.query.filter_by(status='published').order_by(BlogPost.created_at.desc()).all()
    return jsonify([{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'excerpt': p.excerpt,
        'content': p.content,
        'featured_image': p.featured_image,
        'views': p.views,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'author': p.author.full_name if p.author else 'Admin'
    } for p in posts])

@blog_bp.route('/blog/<slug>', methods=['GET'])
def get_blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
    post.views += 1
    db.session.commit()
    return jsonify({
        'id': post.id,
        'title': post.title,
        'content': post.content,
        'featured_image': post.featured_image,
        'views': post.views,
        'created_at': post.created_at.isoformat() if post.created_at else None,
        'author': post.author.full_name if post.author else 'Admin'
    })

# Testimonials Routes
@testimonials_bp.route('/testimonials', methods=['GET'])
def get_testimonials():
    testimonials = Testimonial.query.filter_by(is_approved=True).order_by(Testimonial.created_at.desc()).limit(6).all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'role': t.role,
        'content': t.content,
        'rating': t.rating
    } for t in testimonials])

# Statistics Routes
@statistics_bp.route('/statistics', methods=['GET'])
def get_statistics():
    stats = Statistic.query.order_by(Statistic.order).all()
    return jsonify([{
        'label': s.label,
        'value': s.value,
        'suffix': s.suffix
    } for s in stats])