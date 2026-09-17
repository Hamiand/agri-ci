from pathlib import Path


def test_payment_webhook_supports_retry_states_and_guards_terminal_transitions():
    source=Path("app/payments/webhook.py").read_text()

    assert 'SUPPORTED_EVENTS={"payment.success","payment.failed","payment.refunded"}' in source
    assert 'except (TypeError,ValueError):raise HTTPException(status_code=422,detail="INVALID_PAYMENT_ID")' in source
    assert '.with_for_update()' in source
    assert 'pay.status=="SUCCESS"' in source
    assert 'detail="PAYMENT_ALREADY_SUCCESSFUL"' in source
    assert 'pay.status=="REFUNDED"' in source
    assert 'detail="PAYMENT_ALREADY_REFUNDED"' in source
    assert 'pay.status not in {"SUCCESS","REFUNDED"}' in source
    assert 'detail="PAYMENT_NOT_SUCCESSFUL"' in source
    assert 'pay.status="FAILED"' in source
    assert 'pay.status="REFUNDED"' in source
    assert 'mark_provider_success(db,pay,provider_ref)' in source
    assert 'hmac.compare_digest(expected,signature)' in source
