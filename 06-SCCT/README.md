# Supply Chain Control Tower — Flask Auth Demo

A production-oriented authentication demo for a semiconductor supply chain management system. Built to showcase secure credential handling, environment-based configuration, and Flask session management.

## What This Demo Shows

- **Environment-based Configuration** — Sensitive values (secret keys, password hashes) loaded via `python-dotenv` from `.env`, not hardcoded.
- **Hashed Credentials** — Werkzeug `scrypt` key derivation for password hashing (`generate_password_hash` / `check_password_hash`).
- **Flask Session Auth** — Decorator-based route protection (`@login_required`), session-based login state, and secure logout.
- **Responsive Login UI** — Dark-themed login form with real-time validation, error handling, and loading states.
- **Protected Routes** — Dashboard and API endpoints blocked until authenticated.

## Quick Start

1. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   ```

4. **Run the app:**
   ```bash
   python app.py
   ```
   Open http://localhost:5000 in your browser.

5. **Demo login:**
   - **Username:** `admin`
   - **Password:** `admin123`

## Tech Stack

- **Framework:** Flask 3.0.0
- **Security:** Werkzeug 3.0.1 (scrypt hashing)
- **Config:** python-dotenv 1.0.0
- **Runtime:** Python 3.9+
