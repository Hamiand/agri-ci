from pathlib import Path


def test_unhandled_errors_are_traceable_without_logging_request_secrets():
    main = Path("app/main.py").read_text()
    logging_module = Path("app/core/logging.py").read_text()

    assert '"api.unhandled_exception"' in main
    assert "trace_id=trace_id" in main
    assert "method=request.method" in main
    assert "path=request.url.path" in main
    assert "exception_type=type(exc).__name__" in main

    # The generic failure path must not serialise bodies, headers, tokens or
    # the exception message, which may contain user/provider secrets.
    handler = main.split("async def unhandled_exception", 1)[1].split("@app.get", 1)[0]
    assert "request.body" not in handler
    assert "request.headers" not in handler
    assert "str(exc)" not in handler
    assert "repr(exc)" not in handler

    assert "json.dumps" in logging_module
    assert 'logging.getLogger("agrici")' in logging_module
