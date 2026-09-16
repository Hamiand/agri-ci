def test_fastapi_app_imports_and_has_title():
    from app.main import app
    assert app.title
    assert any(r.path=="/health" for r in app.routes)
