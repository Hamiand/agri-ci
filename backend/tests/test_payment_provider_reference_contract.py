from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.payments.service import mark_provider_success


def test_success_replay_requires_same_provider_reference():
    payment=SimpleNamespace(status="SUCCESS",provider_reference="PROVIDER-REF-001")
    assert mark_provider_success(None,payment,"PROVIDER-REF-001") is payment

    with pytest.raises(HTTPException) as exc:
        mark_provider_success(None,payment,"PROVIDER-REF-OTHER")

    assert exc.value.status_code==409
    assert exc.value.detail=="PAYMENT_PROVIDER_REFERENCE_CONFLICT"
    assert payment.provider_reference=="PROVIDER-REF-001"
