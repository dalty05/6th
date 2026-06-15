# diagnose.py
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    for table in inspector.get_table_names():
        print(f"\n{table}:")
        for col in inspector.get_columns(table):
            print(f"  - {col['name']} ({col['type']})")