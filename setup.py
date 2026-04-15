#!/usr/bin/env python3
"""
Smart Budget Planner - Setup Script
Automates the setup process for the application
"""

import os
import sys
import subprocess
import sqlite3

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_step(step, text):
    print(f"[{step}] {text}")

def create_virtual_environment():
    print_step("1", "Creating virtual environment...")
    if os.path.exists("venv"):
        print("     Virtual environment already exists.")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("     ✓ Virtual environment created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"     ✗ Failed to create virtual environment: {e}")
        sys.exit(1)

def install_dependencies():
    print_step("2", "Installing dependencies...")
    
    # Determine pip path based on OS
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # macOS/Linux
        pip_path = os.path.join("venv", "bin", "pip")
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("     ✓ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"     ✗ Failed to install dependencies: {e}")
        sys.exit(1)

def initialize_database():
    print_step("3", "Initializing database...")
    
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                monthly_salary REAL DEFAULT 0,
                savings_goal REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Savings goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        print("     ✓ Database initialized successfully!")
    except Exception as e:
        print(f"     ✗ Failed to initialize database: {e}")
        sys.exit(1)

def print_completion():
    print_header("Setup Complete!")
    print("To start the application, run:\n")
    
    if os.name == 'nt':  # Windows
        print("    venv\\Scripts\\activate")
        print("    python app.py\n")
    else:  # macOS/Linux
        print("    source venv/bin/activate")
        print("    python3 app.py\n")
    
    print("Then open your browser and navigate to:")
    print("    http://localhost:5000\n")
    print("Default login: Register a new account at /register")
    print("="*60 + "\n")

def main():
    print_header("Smart Budget Planner - Setup")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    
    print(f"Python version: {sys.version}\n")
    
    # Run setup steps
    create_virtual_environment()
    install_dependencies()
    initialize_database()
    
    print_completion()

if __name__ == "__main__":
    main()
