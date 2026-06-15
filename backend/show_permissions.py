# delete_user.py
import sys
from app import app
from models import db, User

def delete_user_by_email(email):
    """Delete a user by email"""
    with app.app_context():
        user = User.query.filter_by(email=email.lower().strip()).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        print(f"\n📋 User found:")
        print(f"   ID: {user.id}")
        print(f"   Name: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        print(f"   Active: {user.is_active}")
        
        confirm = input(f"\n⚠️ Are you sure you want to delete {user.email}? (yes/no): ")
        
        if confirm.lower() == 'yes':
            db.session.delete(user)
            db.session.commit()
            print(f"✅ User {email} deleted successfully")
            return True
        else:
            print("❌ Deletion cancelled")
            return False

def delete_user_by_id(user_id):
    """Delete a user by ID"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"❌ User with ID '{user_id}' not found")
            return False
        
        print(f"\n📋 User found:")
        print(f"   ID: {user.id}")
        print(f"   Name: {user.full_name}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.role}")
        
        confirm = input(f"\n⚠️ Are you sure you want to delete {user.email}? (yes/no): ")
        
        if confirm.lower() == 'yes':
            db.session.delete(user)
            db.session.commit()
            print(f"✅ User ID {user_id} deleted successfully")
            return True
        else:
            print("❌ Deletion cancelled")
            return False

def list_users():
    """List all users"""
    with app.app_context():
        users = User.query.all()
        print("\n📋 All Users:")
        print("-" * 60)
        for user in users:
            print(f"   ID: {user.id} | Name: {user.full_name} | Email: {user.email} | Role: {user.role}")
        print("-" * 60)

if __name__ == "__main__":
    print("=" * 50)
    print("USER DELETION SCRIPT")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Command line argument provided
        arg = sys.argv[1]
        if arg.isdigit():
            delete_user_by_id(int(arg))
        else:
            delete_user_by_email(arg)
    else:
        # Interactive mode
        print("\nOptions:")
        print("1. List all users")
        print("2. Delete user by email")
        print("3. Delete user by ID")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == '1':
            list_users()
        elif choice == '2':
            email = input("Enter user email: ")
            delete_user_by_email(email)
        elif choice == '3':
            user_id = input("Enter user ID: ")
            delete_user_by_id(int(user_id))
        else:
            print("Invalid choice")