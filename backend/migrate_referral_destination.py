"""One-off script to update referral link destinations in the SQLite DB.

Usage:
  python backend/migrate_referral_destination.py

This updates all rows in referral_links.destination_url.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "meru_dairy.db")

# Destination: products page of the project (frontend route/hash)
DESTINATION_URL = "http://localhost:5173/#products"




def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"DB: {DB_PATH}")
    print("Current destinations (sample):")
    cursor.execute("SELECT id, link_code, destination_url FROM referral_links LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Code: {row[1]}, Dest: {row[2]}")

    print("\nUpdating all links to destination...")
    cursor.execute(
        "UPDATE referral_links SET destination_url = ?",
        (DESTINATION_URL,),
    )
    conn.commit()
    print(f"✅ Updated {cursor.rowcount} links")

    print("\nUpdated destinations (sample):")
    cursor.execute("SELECT id, link_code, destination_url FROM referral_links LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Dest: {row[2]}")

    conn.close()


if __name__ == "__main__":
    main()

