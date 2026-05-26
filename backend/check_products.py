from app import app, db, Product

with app.app_context():
    products = Product.query.all()
    print(f'Total products: {len(products)}')
    for p in products:
        print(f'  - ID:{p.id} {p.name} ({p.category})')
