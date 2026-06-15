"""
Database Migration Script for Meru Dairy
Adds soft delete columns and other missing fields
Run with: python migrate_db.py
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    """Run database migration to add soft delete columns"""
    
    db_path = 'meru_dairy.db'
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Please run the app first to create it.")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("MERU DAIRY DATABASE MIGRATION")
    print("=" * 60)
    
    # Dictionary of tables and their columns to add
    migrations = {
        'product': {
            'columns': [
                ('is_deleted', 'BOOLEAN DEFAULT 0'),
                ('deleted_at', 'DATETIME'),
                ('deleted_by', 'INTEGER')
            ]
        },
        'blog_post': {
            'columns': [
                ('is_deleted', 'BOOLEAN DEFAULT 0'),
                ('deleted_at', 'DATETIME'),
                ('deleted_by', 'INTEGER')
            ]
        },
        'testimonial': {
            'columns': [
                ('is_deleted', 'BOOLEAN DEFAULT 0'),
                ('deleted_at', 'DATETIME'),
                ('deleted_by', 'INTEGER')
            ]
        },
        'user': {
            'columns': [
                ('is_active', 'BOOLEAN DEFAULT 1'),
                ('two_factor_enabled', 'BOOLEAN DEFAULT 0'),
                ('two_factor_secret', 'VARCHAR(255)'),
                ('phone', 'VARCHAR(20)'),
                ('last_login', 'DATETIME')
            ]
        }
    }
    
    # Execute migrations
    for table_name, config in migrations.items():
        print(f"\n📋 Checking table: {table_name}")
        
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add missing columns
        for col_name, col_type in config['columns']:
            if col_name not in existing_columns:
                try:
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    cursor.execute(alter_sql)
                    print(f"  ✅ Added column: {col_name}")
                except sqlite3.Error as e:
                    print(f"  ❌ Error adding {col_name}: {e}")
            else:
                print(f"  ⏭️  Column already exists: {col_name}")
    
    # Create index for soft delete queries
    print("\n📊 Creating indexes for better performance...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_product_is_deleted ON product(is_deleted)",
        "CREATE INDEX IF NOT EXISTS idx_product_category ON product(category)",
        "CREATE INDEX IF NOT EXISTS idx_blog_post_is_deleted ON blog_post(is_deleted)",
        "CREATE INDEX IF NOT EXISTS idx_blog_post_status ON blog_post(status)",
        "CREATE INDEX IF NOT EXISTS idx_blog_post_slug ON blog_post(slug)",
        "CREATE INDEX IF NOT EXISTS idx_testimonial_is_deleted ON testimonial(is_deleted)",
        "CREATE INDEX IF NOT EXISTS idx_testimonial_is_approved ON testimonial(is_approved)",
        "CREATE INDEX IF NOT EXISTS idx_user_is_active ON user(is_active)",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            print(f"  ✅ Created index: {index_sql.split('ON')[1].split('(')[0].strip()}")
        except sqlite3.Error as e:
            print(f"  ⚠️ Index creation warning: {e}")
    
    # Check and add sample data if needed
    print("\n📝 Checking sample data...")
    
    # Check if statistics exist
    cursor.execute("SELECT COUNT(*) FROM statistic")
    if cursor.fetchone()[0] == 0:
        print("  📊 Adding sample statistics...")
        sample_stats = [
            ('Our Farmers', '120,000', '+', 1),
            ('Cooperative Societies', '120', '+', 2),
            ('Litres of Milk Processed per day', '600,000', '+', 3),
            ('Customers Served', '10,000,000', '+', 4)
        ]
        for label, value, suffix, order in sample_stats:
            cursor.execute(
                "INSERT INTO statistic (label, value, suffix, \"order\") VALUES (?, ?, ?, ?)",
                (label, value, suffix, order)
            )
        print("  ✅ Sample statistics added")
    
    # Check if testimonials exist
    cursor.execute("SELECT COUNT(*) FROM testimonial")
    if cursor.fetchone()[0] == 0:
        print("  💬 Adding sample testimonials...")
        sample_testimonials = [
            ('John M.', 'Director', 'Mount Kenya Milk has transformed our dairy business. The quality is consistently excellent!', 5, 1),
            ('Sarah W.', 'Trader', 'My customers love the fresh taste of Mount Kenya Yoghurt. It sells out every day!', 5, 1),
            ('Peter K.', 'Business Owner', 'The cooperative model ensures farmers get fair prices while consumers get premium quality.', 4, 1)
        ]
        for name, role, content, rating, is_approved in sample_testimonials:
            cursor.execute(
                "INSERT INTO testimonial (name, role, content, rating, is_approved) VALUES (?, ?, ?, ?, ?)",
                (name, role, content, rating, is_approved)
            )
        print("  ✅ Sample testimonials added")
    
    # Commit changes
    conn.commit()
    
    # Verify migrations
    print("\n🔍 Verifying migrations...")
    for table_name in migrations.keys():
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"  📋 {table_name}: {len(columns)} columns")
    
    # Close connection
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nChanges made:")
    print("  • Added soft delete columns (is_deleted, deleted_at, deleted_by)")
    print("  • Added user account management fields")
    print("  • Created performance indexes")
    print("  • Added sample data (statistics and testimonials)")
    print("\nYou can now restart your Flask application.")
    
    return True

def rollback_migration():
    """Rollback soft delete columns (use with caution)"""
    print("\n⚠️ WARNING: This will remove soft delete columns!")
    confirm = input("Type 'CONFIRM' to proceed: ")
    
    if confirm != 'CONFIRM':
        print("Rollback cancelled.")
        return False
    
    db_path = 'meru_dairy.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQLite doesn't support DROP COLUMN directly, need to recreate tables
    print("Rolling back migrations...")
    
    # For SQLite, we'd need to recreate tables without the columns
    # This is more complex - recommend backup instead
    print("For SQLite, it's safer to restore from backup or keep the columns.")
    print("The soft delete columns don't affect existing functionality.")
    
    conn.close()
    return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback_migration()
    else:
        run_migration()