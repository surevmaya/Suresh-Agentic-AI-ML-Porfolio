# Flask Authentication App

A secure Flask web application with user authentication, session management, and a supply chain control tower dashboard.

## Quick Start

### 1. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
```

### 4. Run the app
```bash
flask run
```

The app will be available at `http://localhost:5000`

## Demo Credentials

- **Username:** admin
- **Password:** admin123

## Features

- **Secure Authentication:** Passwords hashed with werkzeug.security (scrypt)
- **Session Management:** User sessions stored securely
- **Protected Routes:** Dashboard requires login
- **Environment Configuration:** Secrets stored in .env (not in code)
- **Supply Chain Dashboard:** Interactive simulator for semiconductor inventory management

## Architecture

- `app.py` - Flask application with routes and authentication logic
- `templates/` - HTML templates (login, dashboard)
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (credentials, secrets) — not committed to git
- `.env.example` - Template for environment variables

## Security Notes

- Never commit `.env` to version control (already in .gitignore)
- Generate a new `SECRET_KEY` for production: `python -c "import secrets; print(secrets.token_hex(32))"`
- Change `DEMO_PASSWORD_HASH` in production with your own credentials
- Passwords are never stored in plaintext—always hashed with `generate_password_hash()`
