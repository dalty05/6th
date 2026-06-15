import sqlite3
import os

db_path = 'meru_dairy.db'

print(f"Checking database at: {os.path.abspath(db_path)}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    if tables:
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("\nNo tables found in database.")
    
    conn.close()
else:
    print("\nDatabase file doesn't exist yet.")
    print("Start your Flask app first: python app.py")
    