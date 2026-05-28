# working_backend.py
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Sample data
products = [
    {
        'id': 1,
        'name': 'Mount Kenya Fresh Milk',
        'category': 'Fresh Milk',
        'description': 'Pure, fresh milk from the slopes of Mount Kenya. Pasteurized and packed fresh daily.',
        'benefits': 'Rich in calcium and protein, supports bone health',
        'packaging_sizes': '500ml, 1L, 2L',
        'nutritional_info': 'High in calcium, vitamin D',
        'ingredients': '100% fresh cow milk',
        'image_url': None,
        'featured': True
    },
    {
        'id': 2,
        'name': 'Mount Kenya Yoghurt',
        'category': 'Yoghurt',
        'description': 'Creamy, delicious yoghurt made from fresh milk. Available in multiple flavors.',
        'benefits': 'Contains probiotics for gut health',
        'packaging_sizes': '200ml, 500ml, 1L',
        'nutritional_info': 'Rich in protein and calcium',
        'ingredients': 'Fresh milk, live cultures',
        'image_url': None,
        'featured': True
    },
    {
        'id': 3,
        'name': 'Mount Kenya Lala',
        'category': 'Lala',
        'description': 'Traditional fermented milk drink, rich and tangy.',
        'benefits': 'Natural probiotics, aids digestion',
        'packaging_sizes': '500ml, 1L',
        'nutritional_info': 'Contains beneficial bacteria',
        'ingredients': 'Fresh milk, traditional cultures',
        'image_url': None,
        'featured': True
    },
    {
        'id': 4,
        'name': 'Mount Kenya Ghee',
        'category': 'Ghee',
        'description': 'Pure clarified butter, perfect for cooking and traditional dishes.',
        'benefits': 'Lactose-free, high smoke point for cooking',
        'packaging_sizes': '500g, 1kg',
        'nutritional_info': 'Rich in healthy fats',
        'ingredients': 'Pure butterfat',
        'image_url': None,
        'featured': True
    }
]

statistics = [
    {'label': 'Our Farmers', 'value': '120,000', 'suffix': '+', 'order': 1},
    {'label': 'Cooperative Societies', 'value': '120', 'suffix': '+', 'order': 2},
    {'label': 'Litres of Milk Processed per day', 'value': '600,000', 'suffix': '+', 'order': 3},
    {'label': 'Customers Served', 'value': '10,000,000', 'suffix': '+', 'order': 4}
]

testimonials = [
    {
        'id': 1,
        'name': 'John M.',
        'role': 'Director',
        'content': 'Mount Kenya Milk has transformed our school feeding program. The quality is consistently excellent.',
        'rating': 5,
        'is_approved': True
    },
    {
        'id': 2,
        'name': 'Sarah W.',
        'role': 'Trader',
        'content': 'My customers love Mount Kenya products. The yoghurt is especially popular!',
        'rating': 5,
        'is_approved': True
    },
    {
        'id': 3,
        'name': 'Grace K.',
        'role': 'Business Woman',
        'content': 'I trust Mount Kenya Milk for my family. The quality is unmatched.',
        'rating': 5,
        'is_approved': True
    }
]

blog_posts = [
    {
        'id': 1,
        'title': 'Meru Dairy Wins Industry Excellence Award 2024',
        'slug': 'meru-dairy-wins-award-2024',
        'excerpt': 'We are proud to announce that Meru Central Dairy has been recognized as the best dairy cooperative in Kenya.',
        'content': 'Full article content here...',
        'featured_image': None,
        'views': 1250,
        'created_at': datetime.now().isoformat(),
        'author': 'Communications Team',
        'status': 'published',
        'category': 'News'
    },
    {
        'id': 2,
        'title': 'Empowering Farmers: New Training Program Launched',
        'slug': 'empowering-farmers-training-program',
        'excerpt': 'Our latest initiative aims to equip farmers with modern dairy farming techniques.',
        'content': 'Full article content here...',
        'featured_image': None,
        'views': 890,
        'created_at': datetime.now().isoformat(),
        'author': 'Farmer Support Team',
        'status': 'published',
        'category': 'Stories'
    },
    {
        'id': 3,
        'title': 'Sustainable Farming Practices at Meru Dairy',
        'slug': 'sustainable-farming-practices',
        'excerpt': 'Learn about our commitment to environmental sustainability and eco-friendly farming.',
        'content': 'Full article content here...',
        'featured_image': None,
        'views': 567,
        'created_at': datetime.now().isoformat(),
        'author': 'Sustainability Team',
        'status': 'published',
        'category': 'Sustainability'
    }
]

# API Routes
@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(products)

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(statistics)

@app.route('/api/testimonials', methods=['GET'])
def get_testimonials():
    approved = [t for t in testimonials if t.get('is_approved', True)]
    return jsonify(approved[:6])

@app.route('/api/blog', methods=['GET'])
def get_blog_posts():
    published = [p for p in blog_posts if p.get('status') == 'published']
    return jsonify(published)

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    print(f"Contact form submission: {data}")
    return jsonify({'message': 'Message sent successfully'}), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running!'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting Meru Dairy Backend Server")
    print("=" * 50)
    print("📍 API Endpoints:")
    print("   GET  /api/products     - List all products")
    print("   GET  /api/statistics   - Get statistics")
    print("   GET  /api/testimonials - Get testimonials")
    print("   GET  /api/blog         - Get blog posts")
    print("   POST /api/contact      - Send contact message")
    print("   GET  /api/health       - Health check")
    print("=" * 50)
    print("🌐 Server running at: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)