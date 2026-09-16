# AGRI-CI Staging Deployment — v0.28

## Required environment
`APP_ENV=staging`
`DATABASE_URL=postgresql+psycopg://...`
`TEST_DATABASE_URL=postgresql+psycopg://...`
`JWT_SECRET=<strong random secret>`
`PAYMENT_WEBHOOK_SECRET=<provider/staging secret>`
`CORS_ORIGINS=https://<staging-web-origin>`

## Proof sequence
```bash
cd backend
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
python scripts/dependency_doctor.py
python scripts/preflight.py
alembic upgrade head
python -c "from app.main import app; print(app.title, len(app.routes))"
pytest -q
```

Do not promote to RC1 if any command fails.

## Production note
The included in-process rate limiter is suitable only for a small single-backend pilot.
Before horizontally scaling AGRI-CI, move rate-limit state to Redis or the ingress/API gateway.
