from pathlib import Path
def test_runtime_dependency_manifest_contains_commercial_stack():
    text=(Path(__file__).parents[1]/"requirements.txt").read_text().lower()
    for dep in ["fastapi","sqlalchemy","psycopg","alembic","pwdlib","redis","pytest","httpx"]:
        assert dep in text
def test_ci_avoids_isolated_editable_bootstrap():
    text=(Path(__file__).parents[2]/".github/workflows/backend-ci.yml").read_text()
    assert "--no-build-isolation" in text
    assert "-r requirements.txt" in text
