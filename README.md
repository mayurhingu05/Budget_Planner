# Smart Budget Planner & AI Financial Advisor

A comprehensive web-based financial management application built with Flask, featuring expense tracking, budget planning, data visualization, and AI-powered financial insights.

![Smart Budget Planner](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Core Features
- **User Authentication**: Secure registration and login with password hashing
- **Dashboard**: Overview of income, expenses, balance, and daily spending limit
- **Transaction Management**: Add, view, and delete income/expense transactions
- **Smart Budget Planner**: Calculate daily spending limits based on monthly salary
- **Data Visualization**: Interactive charts using Chart.js (pie and bar charts)

### AI Financial Advisor
- Rule-based financial analysis
- Spending pattern insights
- Budget warnings and recommendations
- Personalized savings tips

### Extra Features
- **Dark Mode Toggle**: Switch between light and dark themes
- **PDF Export**: Generate monthly financial reports
- **Date Filtering**: Filter transactions by date range
- **Search Functionality**: Search transactions by description or category
- **Category Icons**: Visual category representation
- **Notification Alerts**: Budget exceeded warnings
- **Savings Goals Tracker**: Set and track savings goals

## Tech Stack

- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Inter)

## Project Structure

```
budget_project/
│
├── app.py                 # Main Flask application
├── database.db            # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Main dashboard
│   ├── transactions.html # Transaction history
│   ├── savings_goals.html # Savings goals page
│   ├── profile.html      # User profile
│   ├── pdf_report.html   # PDF report template
│   └── error.html        # Error pages
│
└── static/               # Static assets
    ├── style.css         # Main stylesheet
    └── script.js         # JavaScript functionality
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd budget_project
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install flask werkzeug
```

Or use the requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

### Step 5: Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

## Default Login Credentials

After registration, you can use your own credentials. For testing:

1. Register a new account at `/register`
2. Login with your credentials at `/login`

## Usage Guide

### 1. Registration & Login
- Create a new account with username, email (optional), and password
- Login with your credentials
- Passwords are securely hashed using Werkzeug

### 2. Dashboard
- View financial summary cards (Income, Expenses, Balance, Daily Limit)
- See monthly budget progress
- View expense breakdown charts
- Get AI financial advice
- See recent transactions

### 3. Adding Transactions
- Click "Add Transaction" button
- Select type (Income/Expense)
- Choose category
- Enter amount and date
- Add optional description
- Submit

### 4. Setting Monthly Salary
- Click "Update Salary" on dashboard
- Enter your monthly salary
- System calculates daily spending limit automatically

### 5. Viewing Transactions
- Navigate to "Transactions" page
- Use filters (date range, category, search)
- Sort by clicking column headers
- Delete transactions if needed

### 6. Savings Goals
- Go to "Goals" page
- Click "New Goal"
- Set target amount and deadline
- Track progress
- Add contributions to goals

### 7. Exporting Reports
- Click "Export Report" on dashboard
- Download HTML report with all transactions
- Print or save as PDF from browser

### 8. Dark Mode
- Click moon/sun icon in navigation
- Preference is saved automatically

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE,
    monthly_salary REAL DEFAULT 0,
    savings_goal REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

### Savings Goals Table
```sql
CREATE TABLE savings_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    target_amount REAL NOT NULL,
    current_amount REAL DEFAULT 0,
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

## API Endpoints

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Main Pages
- `GET /dashboard` - Main dashboard
- `GET /transactions` - Transaction history with filters
- `GET /savings_goals` - Savings goals page
- `GET/POST /profile` - User profile settings

### Actions
- `POST /add_transaction` - Add new transaction
- `GET /delete_transaction/<id>` - Delete transaction
- `POST /update_salary` - Update monthly salary
- `POST /add_savings_goal` - Add savings goal
- `POST /update_goal_progress/<id>` - Update goal progress
- `GET /delete_goal/<id>` - Delete savings goal

### API
- `GET /api/chart_data` - Get data for charts
- `GET /api/ai_advice` - Get AI financial advice
- `GET /export_pdf` - Export monthly report

## Sample Data for Testing

You can add these sample transactions after logging in:

### Income Transactions
1. Salary - $5000 - Category: Salary - Date: Current month 1st
2. Freelance - $800 - Category: Freelance - Date: Current month 15th

### Expense Transactions
1. Rent - $1200 - Category: Bills - Date: Current month 1st
2. Groceries - $350 - Category: Food - Date: Current month 5th
3. Gas - $60 - Category: Travel - Date: Current month 7th
4. Internet - $80 - Category: Bills - Date: Current month 10th
5. Restaurant - $120 - Category: Food - Date: Current month 12th
6. Shopping - $200 - Category: Shopping - Date: Current month 14th
7. Gym - $50 - Category: Health - Date: Current month 1st
8. Uber - $45 - Category: Travel - Date: Current month 18th

## Customization

### Changing Colors
Edit CSS variables in `static/style.css`:

```css
:root {
    --primary-color: #6366f1;  /* Change this */
    --secondary-color: #8b5cf6; /* Change this */
    /* ... */
}
```

### Adding New Categories
Edit the category lists in:
1. `templates/dashboard.html` - In the `updateCategories()` function
2. `templates/transactions.html` - In the `updateCategories()` function

### Modifying AI Advice Rules
Edit the `generate_ai_advice()` function in `app.py` to customize financial advice logic.

## Security Features

- Password hashing with Werkzeug
- Session management
- CSRF protection ready
- SQL injection prevention via parameterized queries
- XSS protection via template escaping

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Keyboard Shortcuts

- `Ctrl/Cmd + K` - Focus search
- `Ctrl/Cmd + D` - Toggle dark mode
- `Escape` - Close modals

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete the database file and restart
rm database.db
python app.py
```

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
```

### Static Files Not Loading
Clear browser cache or hard refresh:
- Windows: `Ctrl + F5`
- macOS: `Cmd + Shift + R`

## Future Enhancements

- [ ] OpenAI API integration for advanced AI advice
- [ ] Recurring transactions
- [ ] Bill reminders
- [ ] Multi-currency support
- [ ] Bank account integration
- [ ] Mobile app (React Native/Flutter)
- [ ] Data export to Excel/CSV
- [ ] Budget categories with limits
- [ ] Investment tracking
- [ ] Net worth calculator

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework by Pallets Projects
- Chart.js for beautiful charts
- Font Awesome for icons
- Google Fonts for typography

## Contact

For questions or support, please open an issue on GitHub.

---

**Happy Budgeting!** 💰📊
