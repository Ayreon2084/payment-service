# Payment Service API

Asynchronous REST API application for payment processing system.

## Tech Stack

- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy (async)
- **Web Framework**: FastAPI
- **Infrastructure**: Docker Compose
- **Package Manager**: Poetry
- **Tests**: Pytest

## Features

### Entities
- **User** - Regular application user
- **Admin** - Administrator with extended privileges
- **Account** - User account with balance, linked to user
- **Payment** - Payment transaction with unique identifier and amount

### User Capabilities
- Authenticate by email/password
- Get own data (id, email, full_name)
- Get list of own accounts with balances
- Get list of own payments

### Administrator Capabilities
- Authenticate by email/password
- Get own data (id, email, full_name)
- Create/Update/Delete users
- Get list of all users with their accounts and balances

### Webhook Payment Processing
A webhook endpoint emulates processing of payment notifications from external payment system.

**Webhook JSON structure:**
- `transaction_id` - unique transaction identifier in external system
- `account_id` - unique account identifier
- `user_id` - unique user identifier
- `amount` - payment amount (in minor currency units)
- `signature` - SHA256 hash signature

**Signature calculation:**
SHA256 hash of concatenated values in alphabetical order of keys + secret key:
`{account_id}{amount}{transaction_id}{user_id}{secret_key}`

**Example** (for secret_key `gfdmhghif38yrf9ew0jkf32`):
```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

**Webhook processing steps:**
1. Verify signature
2. Check if account exists for user - create if not
3. Save transaction to database
4. Add amount to user account balance

**Important**: Transactions are unique - payment with the same `transaction_id` can be processed only once.

### Test Data
Migration creates test data:
- Test user
- Test user account
- Test administrator

## Installation and Running

### Prerequisites
- Python 3.13+
- PostgreSQL 15+
- Poetry (for dependency management)
- Docker and Docker Compose (optional)

### Option 1: Running with Docker Compose

1. Create `.env` file in the project root (you can copy from `.env.example`):
```env
DB_HOST=db
DB_PORT=5432
DB_NAME=payment_service_db
DB_USERNAME=test_user
DB_PASSWORD=postgres2084

SEED_ADMIN_EMAIL=admin@admin.com
SEED_ADMIN_PASSWORD=@lmightYAdmin42
SEED_USER_EMAIL=user@user.com
SEED_USER_PASSWORD=Not@lam1ghtyAtAll

PAYMENT_SECRET_KEY=ZvpFvcFcRfy0Vw4tHOBk7rHk_3Fk-mO6da5siB7ek_8
JWT_SECRET_KEY=sCc0fTCzUPv8X8m2eO8qbjKcLTwq43VW0kNtyMU9PYs
DEBUG=False
```

2. Run the application:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:8000`

### Option 2: Running without Docker

1. Install dependencies:
```bash
poetry install
```

2. Create PostgreSQL database:
```sql
CREATE DATABASE payment_service_db;
CREATE USER test_user WITH PASSWORD 'postgres2084';
GRANT ALL PRIVILEGES ON DATABASE payment_service_db TO test_user;
```

3. Create `.env` file (copy from `.env.example` and adjust for local development):
   - Set `DB_HOST=localhost`
   - Set `DB_PORT=5435`
   - Keep other values as in `.env.example` or customize as needed

4. Run migrations:
```bash
poetry run alembic upgrade head
```

5. Start the application:

**Option A - Using uvicorn directly:**
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Option B - Using Python module (with auto-reload):**
```bash
poetry run python -m app.main
```

**Option C - Using Python directly:**
```bash
poetry run python app/main.py
```

### Default Test Credentials

After running migrations, the following test users are created (values from `.env` file):

**Administrator:**
- Email: `admin@admin.com` (configured via `SEED_ADMIN_EMAIL` in `.env`)
- Password: `@lmightYAdmin42` (configured via `SEED_ADMIN_PASSWORD` in `.env`)

**User:**
- Email: `user@user.com` (configured via `SEED_USER_EMAIL` in `.env`)
- Password: `Not@lam1ghtyAtAll` (configured via `SEED_USER_PASSWORD` in `.env`)
- Initial balance: 1000.00 USD (100000 cents)

**Note:** These credentials are set in the `.env` file and can be customized before running migrations.

### API Endpoints

**Authentication** (`/auth`):
- `POST /auth/register` - Register new user
- `POST /auth/login` - Authenticate and get JWT token
- `POST /auth/logout` - Logout (client should delete token)

**User** (`/users`):
- `GET /users/me` - Get current user information
- `GET /users/me/accounts` - Get current user's accounts
- `GET /users/me/payments` - Get current user's payments

**Accounts** (`/accounts`):
- `POST /accounts` - Create new account (authenticated users)
- `GET /accounts/{account_id}` - Get account by ID (owner or admin)

**Payments** (`/payments`):
- `POST /payments/webhook` - Process payment webhook from external system

**Admin** (`/admin`):
- `GET /admin/users` - List all users with accounts (admin only)
- `GET /admin/users/{user_id}` - Get user details with accounts (admin only)
- `POST /admin/users` - Create user (admin only)
- `PATCH /admin/users/{user_id}` - Update user (admin only)
- `DELETE /admin/users/{user_id}` - Delete user (admin only)

### API Documentation

After starting the application, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example Webhook Request

```bash
curl -X POST http://localhost:8000/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
  }'
```

**Note:** The signature is calculated as SHA256 hash of the string: `{account_id}{amount}{transaction_id}{user_id}{secret_key}`

For testing, you can use the debug endpoint (available only if `DEBUG=True`):
```bash
POST /payments/generate-test-signature
```

## Running Tests

### Prerequisites
Install test dependencies:
```bash
poetry install --with dev
```

### Run all tests
```bash
poetry run pytest
```

### Run specific test file
```bash
poetry run pytest tests/test_auth.py
```

### Test Structure
- `tests/test_auth.py` - Authentication endpoints tests
- `tests/test_users.py` - User endpoints tests
- `tests/test_accounts.py` - Account endpoints tests
- `tests/test_payments.py` - Payment webhook tests
- `tests/test_admin.py` - Admin endpoints tests
- `tests/test_services.py` - Service layer tests
- `tests/conftest.py` - Pytest fixtures and configuration

Tests use an in-memory SQLite database and don't require a running PostgreSQL instance.
