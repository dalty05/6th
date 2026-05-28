# create_sample_data.py
from app import app, db
from models import User, Product, BlogPost, Testimonial, Statistic
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Create sample statistics
    if Statistic.query.count() == 0:
        stats = [
            Statistic(label='Our Farmers', value='120,000', suffix='+', order=1),
            Statistic(label='Cooperative Societies', value='120', suffix='+', order=2),
            Statistic(label='Litres of Milk Processed per day', value='600,000', suffix='+', order=3),
            Statistic(label='Customers Served', value='10,000,000', suffix='+', order=4)
        ]
        for stat in stats:
            db.session.add(stat)
        print("✅ Statistics created")
    
    # Create sample products
    if Product.query.count() == 0:
        products = [
            Product(
                name='Mount Kenya Fresh Milk',
                category='Fresh Milk',
                description='Pure, fresh milk from the slopes of Mount Kenya. Pasteurized and packed fresh daily.',
                benefits='Rich in calcium and protein, supports bone health',
                packaging_sizes='500ml, 1L, 2L',
                featured=True
            ),
            Product(
                name='Mount Kenya Yoghurt',
                category='Yoghurt',
                description='Creamy, delicious yoghurt made from fresh milk.',
                benefits='Contains probiotics for gut health',
                packaging_sizes='200ml, 500ml, 1L',
                featured=True
            ),
            Product(
                name='Mount Kenya Lala',
                category='Lala',
                description='Traditional fermented milk drink, rich and tangy.',
                benefits='Natural probiotics, aids digestion',
                packaging_sizes='500ml, 1L',
                featured=True
            ),
            Product(
                name='Mount Kenya Ghee',
                category='Ghee',
                description='Pure clarified butter, perfect for cooking.',
                benefits='Lactose-free, high smoke point',
                packaging_sizes='500g, 1kg',
                featured=True
            )
        ]
        for product in products:
            db.session.add(product)
        print("✅ Products created")
    
    # Create sample testimonials
    if Testimonial.query.count() == 0:
        testimonials = [
            Testimonial(
                name='John M.',
                role='Director',
                content='Mount Kenya Milk has transformed our school feeding program. The quality is consistently excellent.',
                rating=5,
                is_approved=True
            ),
            Testimonial(
                name='Sarah W.',
                role='Trader',
                content='My customers love Mount Kenya products. The yoghurt is especially popular!',
                rating=5,
                is_approved=True
            ),
            Testimonial(
                name='Grace K.',
                role='Business Woman',
                content='I trust Mount Kenya Milk for my family. The quality is unmatched.',
                rating=5,
                is_approved=True
            )
        ]
        for testimonial in testimonials:
            db.session.add(testimonial)
        print("✅ Testimonials created")
    
    # Create sample blog posts
    if BlogPost.query.count() == 0:
        posts = [
            BlogPost(
                title='Welcome to Meru Dairy',
                slug='welcome-to-meru-dairy',
                excerpt='Learn about our journey and commitment to quality',
                content='Full content here...',
                status='published',
                views=150
            ),
            BlogPost(
                title='Farmer Success Stories',
                slug='farmer-success-stories',
                excerpt='Read inspiring stories from our cooperative members',
                content='Full content here...',
                status='published',
                views=89
            )
        ]
        for post in posts:
            db.session.add(post)
        print("✅ Blog posts created")
    
    db.session.commit()
    print("\n" + "="*50)
    print("✅ Sample data created successfully!")
    print("="*50)