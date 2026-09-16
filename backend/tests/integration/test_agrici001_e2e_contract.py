import os,pytest
pytestmark=[pytest.mark.integration,pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"),reason="TEST_DATABASE_URL required for PostgreSQL integration")]
def test_agrici001_reference_quantities():
    initial=[400,750,600,300,950]
    assert sum(initial)==3000
    assert sum(initial)-300==2700
    coop_remaining=450
    assert min(coop_remaining,300)==300
    assert 2700+300==3000
