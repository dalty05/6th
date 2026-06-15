import sqlite3

# Connect to database
conn = sqlite3.connect('instance/meru_dairy.db')
cursor = conn.cursor()

# View current destinations
print("Current destinations:")
cursor.execute("SELECT id, link_code, destination_url FROM referral_links")
rows = cursor.fetchall()
for row in rows:
    print(f"  ID: {row[0]}, Code: {row[1]}, Dest: {row[2]}")

# Update all to home page
print("\nUpdating all links to home page...")
cursor.execute("UPDATE referral_links SET destination_url = 'http://localhost:5173/#products")
conn.commit()
print(f"✅ Updated {cursor.rowcount} links")

# Verify update
print("\nUpdated destinations:")
cursor.execute("SELECT id, link_code, destination_url FROM referral_links")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Dest: {row[2]}")

conn.close()