import sqlite3
import os

# Look for database in instance folder
db_path = os.path.join('instance', 'meru_dairy.db')

if not os.path.exists(db_path):
    print(f"Database not found at: {db_path}")
    # Try alternative location
    db_path = 'meru_dairy.db'

print(f"Using database: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Clear images
cursor.execute("UPDATE products SET image_url = NULL")
cursor.execute("UPDATE blog_posts SET featured_image = NULL")

conn.commit()
print("Images cleared!")
conn.close()