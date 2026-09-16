# Actual HTTP Contract Inspection — v0.30

## Router declarations
- `GET /aggregations/{aggregation_id}` — `aggregation/router.py`
- `POST /demands/{demand_id}/aggregate` — `aggregation/router.py`
- `POST /login` — `auth/router.py`
- `POST /refresh` — `auth/router.py`
- `POST /register` — `auth/router.py`
- `GET /my-allocations` — `collection/router.py`
- `GET /operations` — `collection/router.py`
- `POST /{collection_id}/quality` — `collection/router.py`
- `POST /{commitment_id}/accept` — `commitments/router.py`
- `POST /{commitment_id}/decline` — `commitments/router.py`
- `GET /mine` — `demands/router.py`
- `GET /lots` — `logistics/router.py`
- `GET /transport-jobs` — `logistics/router.py`
- `POST /lots` — `logistics/router.py`
- `POST /transport-jobs` — `logistics/router.py`
- `POST /transport-jobs/{job_id}/depart` — `logistics/router.py`
- `POST /{demand_id}/match` — `matching/router.py`
- `GET /{order_id}` — `orders/router.py`
- `GET /{order_id}/operations` — `orders/router.py`
- `POST /from-aggregation/{aggregation_id}` — `orders/router.py`
- `GET /farmer/me` — `payments/router.py`
- `GET /{payment_id}/ledger` — `payments/router.py`
- `POST /orders/{order_id}/prepare` — `payments/router.py`
- `POST /{payment_id}/provider-success` — `payments/router.py`

## Request/response schema fields
- `auth/schemas.py::RegisterRequest` — phone, password, preferred_language, role
- `auth/schemas.py::LoginRequest` — phone, password
- `auth/schemas.py::UserResponse` — id, phone, preferred_language, status, roles
- `auth/schemas.py::TokenResponse` — access_token, token_type, user