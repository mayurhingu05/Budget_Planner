"""
Smart Budget Planner & AI Financial Advisor
A comprehensive web-based financial management application

Author: AI Assistant
Stack: Flask + SQLite + HTML/CSS/JS + Chart.js
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
import json
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['DATABASE'] = 'database.db'

@app.context_processor
def inject_datetime():
    """Make datetime available in all templates."""
    return {'datetime': datetime}

# Database Helper Functions
def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
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

# Authentication Decorator
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_data(user_id):
    """Get user data from database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_transactions(user_id, limit=None, date_from=None, date_to=None, category=None, search=None):
    """Get transactions with optional filters"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM transactions WHERE user_id = ?'
    params = [user_id]
    
    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)
    
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    if search:
        query += ' AND (description LIKE ? OR category LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += ' ORDER BY date DESC, created_at DESC'
    
    if limit:
        query += f' LIMIT {limit}'
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_financial_summary(user_id):
    """Calculate financial summary for user"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total Income
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'income'
    ''', (user_id,))
    total_income = cursor.fetchone()['total']
    
    # Total Expenses
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'expense'
    ''', (user_id,))
    total_expenses = cursor.fetchone()['total']
    
    # Monthly expenses
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'expense' AND strftime('%Y-%m', date) = ?
    ''', (user_id, current_month))
    monthly_expenses = cursor.fetchone()['total']
    
    # Category-wise expenses
    cursor.execute('''
        SELECT category, COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'expense'
        GROUP BY category
        ORDER BY total DESC
    ''', (user_id,))
    category_expenses = cursor.fetchall()
    
    # Weekly expenses (last 7 days)
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT date, COALESCE(SUM(amount), 0) as total 
        FROM transactions 
        WHERE user_id = ? AND type = 'expense' AND date >= ?
        GROUP BY date
        ORDER BY date
    ''', (user_id, week_ago))
    weekly_expenses = cursor.fetchall()
    
    # Get user salary
    user = get_user_data(user_id)
    monthly_salary = user['monthly_salary'] if user else 0
    
    # Calculate daily spending limit
    today = datetime.now()
    last_day_of_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    days_remaining = max(1, (last_day_of_month - today).days + 1)
    
    remaining_budget = monthly_salary - monthly_expenses
    daily_spending_limit = remaining_budget / days_remaining if days_remaining > 0 else 0
    
    conn.close()
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'monthly_expenses': monthly_expenses,
        'monthly_salary': monthly_salary,
        'remaining_budget': remaining_budget,
        'daily_spending_limit': daily_spending_limit,
        'days_remaining': days_remaining,
        'category_expenses': category_expenses,
        'weekly_expenses': weekly_expenses
    }

def generate_ai_advice(user_id):
    """Generate AI financial advice based on spending patterns"""
    summary = get_financial_summary(user_id)
    advice = []
    
    # Get category breakdown
    category_expenses = summary['category_expenses']
    category_dict = {item['category']: item['total'] for item in category_expenses}
    
    total_expenses = summary['total_expenses']
    monthly_salary = summary['monthly_salary']
    monthly_expenses = summary['monthly_expenses']
    balance = summary['balance']
    
    # Rule-based AI analysis
    if monthly_salary > 0:
        expense_ratio = monthly_expenses / monthly_salary
        
        if expense_ratio > 0.9:
            advice.append({
                'type': 'danger',
                'icon': 'warning',
                'title': 'Critical Spending Alert',
                'message': f'You have spent {expense_ratio*100:.1f}% of your monthly salary. Consider immediate cost-cutting measures.'
            })
        elif expense_ratio > 0.75:
            advice.append({
                'type': 'warning',
                'icon': 'alert-triangle',
                'title': 'High Spending Warning',
                'message': f'You have used {expense_ratio*100:.1f}% of your monthly budget. Slow down on non-essential expenses.'
            })
        elif expense_ratio < 0.5:
            advice.append({
                'type': 'success',
                'icon': 'check-circle',
                'title': 'Excellent Savings!',
                'message': 'You are saving more than 50% of your income. Great financial discipline!'
            })
    
    # Category-specific advice
    if total_expenses > 0:
        for category, amount in category_dict.items():
            percentage = (amount / total_expenses) * 100
            
            if percentage > 40:
                advice.append({
                    'type': 'warning',
                    'icon': 'trending-up',
                    'title': f'High {category} Spending',
                    'message': f'{category} accounts for {percentage:.1f}% of your total expenses. Consider reducing spending in this category.'
                })
    
    # Balance advice
    if balance < 0:
        advice.append({
            'type': 'danger',
            'icon': 'minus-circle',
            'title': 'Negative Balance',
            'message': 'Your expenses exceed your income. Create a strict budget and cut unnecessary spending immediately.'
        })
    elif balance > monthly_salary * 3:
        advice.append({
            'type': 'info',
            'icon': 'piggy-bank',
            'title': 'Investment Opportunity',
            'message': 'You have a healthy surplus. Consider investing in stocks, mutual funds, or retirement accounts.'
        })
    
    # Daily spending limit advice
    daily_limit = summary['daily_spending_limit']
    if daily_limit < 10 and monthly_salary > 0:
        advice.append({
            'type': 'warning',
            'icon': 'clock',
            'title': 'Low Daily Budget',
            'message': f'Your daily spending limit is only ₹{daily_limit:.2f} for the rest of the month.'
        })
    
    # Default advice if no specific triggers
    if not advice:
        advice.append({
            'type': 'info',
            'icon': 'info',
            'title': 'Steady Progress',
            'message': 'Your finances look stable. Continue monitoring your spending and look for small savings opportunities.'
        })
    
    return advice

# Routes
@app.route('/')
def index():
    """Home page - redirect to dashboard if logged in"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                (username, email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user_id = session['user_id']
    user = get_user_data(user_id)
    summary = get_financial_summary(user_id)
    recent_transactions = get_transactions(user_id, limit=5)
    ai_advice = generate_ai_advice(user_id)
    
    return render_template('dashboard.html', 
                         user=user, 
                         summary=summary, 
                         transactions=recent_transactions,
                         ai_advice=ai_advice)

@app.route('/transactions')
@login_required
def transactions():
    """Transaction history page"""
    user_id = session['user_id']
    
    # Get filter parameters
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    # Get all transactions with filters
    all_transactions = get_transactions(user_id, date_from=date_from, date_to=date_to, 
                                       category=category, search=search)
    
    # Get unique categories for filter dropdown
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM transactions WHERE user_id = ? ORDER BY category', 
                   (user_id,))
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    
    return render_template('transactions.html',
                         transactions=all_transactions,
                         categories=categories,
                         date_from=date_from,
                         date_to=date_to,
                         selected_category=category,
                         search=search)

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    """Add new transaction"""
    user_id = session['user_id']
    
    transaction_type = request.form.get('type')
    category = request.form.get('category')
    amount = float(request.form.get('amount', 0))
    date = request.form.get('date')
    description = request.form.get('description', '')
    
    if amount <= 0:
        flash('Amount must be greater than 0', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, type, category, amount, date, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, transaction_type, category, amount, date, description))
    conn.commit()
    conn.close()
    
    flash('Transaction added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_transaction/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    """Delete a transaction"""
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', 
                   (transaction_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('transactions'))

@app.route('/update_salary', methods=['POST'])
@login_required
def update_salary():
    """Update monthly salary"""
    user_id = session['user_id']
    salary = float(request.form.get('monthly_salary', 0))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET monthly_salary = ? WHERE id = ?', (salary, user_id))
    conn.commit()
    conn.close()
    
    flash('Monthly salary updated!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/api/chart_data')
@login_required
def chart_data():
    """API endpoint for chart data"""
    user_id = session['user_id']
    summary = get_financial_summary(user_id)
    
    # Prepare category data for pie chart
    categories = []
    amounts = []
    for item in summary['category_expenses']:
        categories.append(item['category'])
        amounts.append(item['total'])
    
    # Prepare weekly data for bar chart
    dates = []
    daily_amounts = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime('%Y-%m-%d')
        dates.append(datetime.strptime(date, '%Y-%m-%d').strftime('%a'))
        
        # Find expense for this date
        amount = 0
        for item in summary['weekly_expenses']:
            if item['date'] == date:
                amount = item['total']
                break
        daily_amounts.append(amount)
    
    return jsonify({
        'pie_chart': {
            'labels': categories,
            'data': amounts
        },
        'bar_chart': {
            'labels': dates,
            'data': daily_amounts
        },
        'summary': {
            'total_income': summary['total_income'],
            'total_expenses': summary['total_expenses'],
            'balance': summary['balance'],
            'monthly_expenses': summary['monthly_expenses'],
            'monthly_salary': summary['monthly_salary'],
            'remaining_budget': summary['remaining_budget'],
            'daily_spending_limit': summary['daily_spending_limit']
        }
    })

@app.route('/api/ai_advice')
@login_required
def ai_advice_api():
    """API endpoint for AI advice"""
    user_id = session['user_id']
    advice = generate_ai_advice(user_id)
    return jsonify({'advice': advice})

@app.route('/savings_goals')
@login_required
def savings_goals():
    """Savings goals page"""
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM savings_goals WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    goals = cursor.fetchall()
    conn.close()
    
    return render_template('savings_goals.html', goals=goals)

@app.route('/add_savings_goal', methods=['POST'])
@login_required
def add_savings_goal():
    """Add new savings goal"""
    user_id = session['user_id']
    
    name = request.form.get('name', '').strip()
    target_amount = float(request.form.get('target_amount', 0))
    deadline = request.form.get('deadline', '')
    
    if not name or target_amount <= 0:
        flash('Please provide valid goal name and target amount', 'danger')
        return redirect(url_for('savings_goals'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO savings_goals (user_id, name, target_amount, deadline)
        VALUES (?, ?, ?, ?)
    ''', (user_id, name, target_amount, deadline if deadline else None))
    conn.commit()
    conn.close()
    
    flash('Savings goal added successfully!', 'success')
    return redirect(url_for('savings_goals'))

@app.route('/update_goal_progress/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    """Update savings goal progress"""
    user_id = session['user_id']
    amount = float(request.form.get('amount', 0))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE savings_goals 
        SET current_amount = current_amount + ?
        WHERE id = ? AND user_id = ?
    ''', (amount, goal_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Goal progress updated!', 'success')
    return redirect(url_for('savings_goals'))

@app.route('/delete_goal/<int:goal_id>')
@login_required
def delete_goal(goal_id):
    """Delete a savings goal"""
    user_id = session['user_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM savings_goals WHERE id = ? AND user_id = ?', (goal_id, user_id))
    conn.commit()
    conn.close()
    
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('savings_goals'))

@app.route('/export_pdf')
@login_required
def export_pdf():
    """Export monthly report as PDF"""
    user_id = session['user_id']
    user = get_user_data(user_id)
    summary = get_financial_summary(user_id)
    
    # Get current month transactions
    current_month = datetime.now().strftime('%Y-%m')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM transactions 
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        ORDER BY date DESC
    ''', (user_id, current_month))
    month_transactions = cursor.fetchall()
    conn.close()
    
    # Generate HTML for PDF
    html_content = render_template('pdf_report.html',
                                 user=user,
                                 summary=summary,
                                 transactions=month_transactions,
                                 month=datetime.now().strftime('%B %Y'))
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = f'attachment; filename=budget_report_{current_month}.html'
    
    return response

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    user_id = session['user_id']
    user = get_user_data(user_id)
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Update email
        if email != user['email']:
            try:
                cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
                conn.commit()
                flash('Email updated successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Email already in use', 'danger')
        
        # Update password
        if current_password and new_password:
            if check_password_hash(user['password'], current_password):
                hashed_password = generate_password_hash(new_password)
                cursor.execute('UPDATE users SET password = ? WHERE id = ?', 
                             (hashed_password, user_id))
                conn.commit()
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect', 'danger')
        
        conn.close()
        return redirect(url_for('profile'))
    
    return render_template('profile.html', user=user)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500

# Template filters
@app.template_filter('format_currency')
def format_currency(value):
    """Format number as currency"""
    if value is None:
        return '₹0.00'
    return f'₹{value:,.2f}'

@app.template_filter('format_date')
def format_date(value):
    """Format date string"""
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime('%b %d, %Y')
        except:
            return value
    return value

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
