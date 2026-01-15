# Aureon

A double-entry accounting and loan management system built with FastAPI and SQLModel.

## Features

- 🧾 Double-entry ledger system (Journals, Postings, Accounts)
- 💰 Loan management with amortization schedules
- 👥 Multi-tenant architecture with company isolation
- 🔐 Security and user management
- 💱 Multi-currency support with exchange rates
- 🔄 Payment provider integration
- 📊 Audit logging and reconciliation

## Tech Stack

- **Backend**: FastAPI + SQLModel
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Language**: Python 3.12

## Setup
```bash
# Clone the repository
git clone git@github.com:Skenwise/Aureon.git
cd Aureon

# Create virtual environment
python -m venv AureonVenv
source AureonVenv/bin/activate  # On Windows: AureonVenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic -c database/alembic.ini upgrade head
```

## Project Status

🚧 **In Development** - Initial database schema completed
