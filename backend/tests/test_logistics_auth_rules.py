import uuid

import pytest
from fastapi import HTTPException

from app.database.models import TransportJob, User
from app.logistics import router as logistics_router


def _user(user_id: uuid.UUID) -> User:
    return User(
        id=user_id,
        phone=f"+225{str(user_id.int)[-10:]}",
        password_hash="test-only",
        preferred_language="fr",
        status="ACTIVE",
    )


def _job(transporter_user_id: uuid.UUID) -> TransportJob:
    return TransportJob(
        transport_ref="TRN-AUTH-TEST",
        order_id=uuid.uuid4(),
        transporter_user_id=transporter_user_id,
        origin="Village",
        destination="Abidjan",
        status="PLANNED",
    )


def test_assigned_transporter_has_job_access(monkeypatch):
    assigned_id = uuid.uuid4()
    user = _user(assigned_id)
    job = _job(assigned_id)
    monkeypatch.setattr(logistics_router, "_can_manage_all_logistics", lambda db, current_user: False)

    assert logistics_router._require_job_access(object(), user, job) is None


def test_other_transporter_is_denied_job_access(monkeypatch):
    assigned_id = uuid.uuid4()
    other = _user(uuid.uuid4())
    job = _job(assigned_id)
    monkeypatch.setattr(logistics_router, "_can_manage_all_logistics", lambda db, current_user: False)

    with pytest.raises(HTTPException) as exc:
        logistics_router._require_job_access(object(), other, job)

    assert exc.value.status_code == 403
    assert exc.value.detail == "TRANSPORT_JOB_NOT_ASSIGNED_TO_USER"


def test_operations_manager_override_is_allowed(monkeypatch):
    user = _user(uuid.uuid4())
    job = _job(uuid.uuid4())
    monkeypatch.setattr(logistics_router, "_can_manage_all_logistics", lambda db, current_user: True)

    assert logistics_router._require_job_access(object(), user, job) is None
