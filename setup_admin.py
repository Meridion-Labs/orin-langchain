"""Setup script to create admin user and initialize the system."""

import os
import sys
from getpass import getpass

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth import get_password_hash, create_access_token
from app.config import settings


def create_admin_user():
    """Create an admin user interactively."""
    print("🤖 ORIN Admin Setup")
    print("==================")
    
    # Get admin details
    email = input("Enter admin email: ").strip()
    if not email:
        print("Email is required!")
        return False
    
    password = getpass("Enter admin password: ")
    if not password:
        print("Password is required!")
        return False
    
    full_name = input("Enter admin full name (optional): ").strip()
    
    # Hash password
    hashed_password = get_password_hash(password)
    
    # For this demo, we'll just print the details
    # In a real application, you'd save this to a database
    print(f"\n✅ Admin user created successfully!")
    print(f"Email: {email}")
    print(f"Hashed Password: {hashed_password}")
    if full_name:
        print(f"Full Name: {full_name}")
    
    # Add to admin emails in settings if not already there
    admin_emails_list = settings.admin_emails if isinstance(settings.admin_emails, list) else settings.admin_emails.split(',')
    admin_emails_list = [e.strip() for e in admin_emails_list]
    
    if email not in admin_emails_list:
        admin_emails_list.append(email)
        print(f"\n📝 Add this email to your .env file:")
        print(f"ADMIN_EMAILS={','.join(admin_emails_list)}")
    
    # Generate a test token
    token = create_access_token(data={"sub": email})
    print(f"\n🔑 Test Admin Token (valid for {settings.access_token_expire_minutes} minutes):")
    print(f"{token}")
    
    return True


def setup_directories():
    """Create necessary directories."""
    directories = [
        settings.upload_dir,
        "static",
        "logs"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")


def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        ("OPENAI_API_KEY", settings.openai_api_key),
        ("PINECONE_API_KEY", settings.pinecone_api_key),
        ("SECRET_KEY", settings.secret_key)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value or var_value == "your-secret-key-here":
            missing_vars.append(var_name)
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease add these to your .env file")
        return False
    
    print("✅ Environment variables configured")
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up ORIN AI Agent System...")
    print("=" * 40)
    
    # Setup directories
    setup_directories()
    
    # Check environment
    env_ok = check_environment()
    
    # Create admin user
    if input("\nCreate admin user? (y/n): ").lower().startswith('y'):
        create_admin_user()
    
    print("\n" + "=" * 40)
    print("🎉 Setup complete!")
    
    if env_ok:
        print("\n🏃 You can now start the server with:")
        print("   python main.py")
        print("\n🌐 Access the admin panel at:")
        print("   http://localhost:8000/admin")
    else:
        print("\n⚠️  Please configure environment variables before starting the server")


if __name__ == "__main__":
    main()