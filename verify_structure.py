#!/usr/bin/env python3
"""Verify ORIN project structure without external dependencies."""

import os
import sys

def verify_file_exists(path):
    """Verify a file exists."""
    if os.path.exists(path):
        print(f"✓ {path}")
        return True
    else:
        print(f"✗ {path}")
        return False

def verify_directory_structure():
    """Verify the complete directory structure."""
    print("Verifying ORIN AI Agent System structure...")
    
    # Core files
    files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "Dockerfile",
        "docker-compose.yml",
        ".gitignore"
    ]
    
    # App directories
    directories = [
        "app/",
        "app/agents/",
        "app/auth/",
        "app/rag/",
        "app/api/",
        "app/config/",
        "app/models/",
        "app/utils/",
        "uploads/",
        "tests/"
    ]
    
    # App files
    app_files = [
        "app/__init__.py",
        "app/config/__init__.py",
        "app/config/settings.py",
        "app/models/__init__.py",
        "app/models/user.py",
        "app/auth/__init__.py",
        "app/auth/auth.py",
        "app/rag/__init__.py",
        "app/rag/vectorstore.py",
        "app/rag/retriever.py",
        "app/agents/__init__.py",
        "app/agents/orin_agent.py",
        "app/agents/tools.py",
        "app/api/__init__.py",
        "app/api/auth.py",
        "app/api/chat.py",
        "app/utils/__init__.py",
        "tests/__init__.py",
        "tests/test_api.py",
        "uploads/.gitkeep"
    ]
    
    all_items = files + directories + app_files
    verified = 0
    
    for item in all_items:
        if verify_file_exists(item):
            verified += 1
    
    print(f"\nVerification complete: {verified}/{len(all_items)} items found")
    
    if verified == len(all_items):
        print("✓ All required files and directories are present!")
        return True
    else:
        print("✗ Some files or directories are missing")
        return False

def check_python_syntax():
    """Check Python syntax of main files."""
    print("\nChecking Python syntax...")
    
    python_files = [
        "main.py",
        "app/config/settings.py"
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✓ {file_path} - syntax OK")
        except SyntaxError as e:
            print(f"✗ {file_path} - syntax error: {e}")
            return False
        except Exception as e:
            print(f"? {file_path} - {e}")
    
    return True

if __name__ == "__main__":
    structure_ok = verify_directory_structure()
    syntax_ok = check_python_syntax()
    
    if structure_ok and syntax_ok:
        print("\n🎉 ORIN AI Agent System verification successful!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure environment: cp .env.example .env")
        print("3. Run the application: python main.py")
        sys.exit(0)
    else:
        print("\n❌ Verification failed")
        sys.exit(1)