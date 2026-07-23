# Door Code API

A REST API for issuing single-use, time-limited door access codes.

The intended setup: a customer pays for access, the system issues them a code, and a
keypad wired to a Raspberry Pi verifies that code against this API before unlocking.
Codes expire after a configurable window and are consumed on first successful use.

Built with FastAPI, SQLAlchemy and PostgreSQL.

## Features

- Cryptographically secure code generation
- Configurable expiry window per code
- One-time use — a code is consumed the first time it successfully opens the door
- JWT-protected code generation, with an open verification endpoint for the door hardware
- Automated test suite running against a dedicated PostgreSQL test database

## Design decisions

**`secrets` rather than `random` for code generation.** `random` is seeded
pseudo-randomness and is predictable given enough output — unacceptable for anything
guarding a physical door. `secrets.token_hex()` is cryptographically secure.

**All timestamps stored in UTC, with timezone-aware columns.** Storing local time
invites daylight-saving and multi-timezone bugs. Columns are declared
`DateTime(timezone=True)` so PostgreSQL returns timezone-aware values and expiry
comparisons are unambiguous.

**Verification consumes the code.** `verify_code` sets `used = True` on a successful
check, so a code opens the door exactly once. The alternative — a code valid for
unlimited entries within its window, like a hotel key card — is a reasonable model for
a different product, but single-use fits a pay-per-entry system.

**Split public and protected endpoints by trust level.** Generating a code is a
privileged action tied to payment, so it sits behind JWT auth. Verification is left
open because the door hardware must be able to check codes without holding
credentials. Locking both down would either break the door or require storing a token
on the device.

**Tests run against PostgreSQL, not in-memory SQLite.** SQLite was the initial choice
for speed, but it does not preserve timezone-aware datetimes, so tests passed or
failed for reasons that had nothing to do with the application logic. Testing against
the same engine used in production removed a source of false confidence.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Create a user |
| `POST` | `/auth/login` | — | Exchange credentials for a JWT |
| `POST` | `/codes/` | JWT | Issue a new door code |
| `POST` | `/codes/verify/{code}` | — | Verify and consume a code |

`POST /codes/` accepts an optional `valid_minutes` parameter (default 60).

Verification returns `200` with `{"access": "granted"}` on success, and `403` if the
code is unknown, already used, or expired.

Interactive documentation is available at `/docs` when the server is running.

## Setup

Requires Python 3.11+ and PostgreSQL.

```bash
git clone https://github.com/shadeisroot/doorcodeapi.git
cd doorcodeapi

python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create the databases:

```sql
CREATE DATABASE doorcodes;
CREATE DATABASE doorcodes_test;
```

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/doorcodes
TEST_DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/doorcodes_test
SECRET_KEY=
```

Generate a key for `SECRET_KEY` with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Create the tables and start the server:

```bash
python create_tables.py
uvicorn main:app --reload
```

## Tests

```bash
pytest
```

Each test runs against `doorcodes_test` with tables created and dropped around it, so
runs are isolated and repeatable. The suite covers authentication on the generation
endpoint, rejection of unknown codes, and the full lifecycle — register, log in,
issue a code, verify it, and confirm a second verification of the same code is
refused.

## Project structure

```
doorcodeapi/
├── main.py                 FastAPI app, router registration
├── create_tables.py        One-time table creation
├── app/
│   ├── config.py           Settings loaded from .env
│   ├── database.py         Engine, session factory, get_db dependency
│   ├── auth.py             Password hashing, JWT creation and verification
│   ├── models/             SQLAlchemy models — database tables
│   ├── schemas/            Pydantic models — request and response shapes
│   ├── crud/               Database queries, kept out of the route handlers
│   └── routers/            Route handlers
└── tests/
    ├── conftest.py         Test database and dependency override
    └── test_doorcodes.py
```

Database models and API schemas are kept separate on purpose: one describes what is
stored, the other describes what crosses the wire. They overlap heavily here, but the
distinction matters as soon as a field should be persisted without being exposed —
`hashed_password` being the obvious case.

## Not implemented

Deliberately out of scope for this version:

- **Payment integration.** Code generation stands in for the payment webhook that
  would trigger it in production.
- **Customer records.** Codes are not linked to a named customer, so there is no way
  to look someone up if they miss their window and call to ask for help. This would
  mean storing personal data and taking GDPR obligations seriously.
- **Schema migrations.** Tables are created directly rather than through Alembic,
  which is fine while the schema is disposable and not fine once there is real data.
- **Hardware.** The Raspberry Pi client that would read a keypad and call
  `/codes/verify/{code}` is not part of this repository.