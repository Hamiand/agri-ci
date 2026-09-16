from app.main import app
def test_agrici001_public_http_route_contract():
    mounted={(m,r.path) for r in app.routes for m in (getattr(r,"methods",None) or set())}
    required=[
      ("POST","/auth/register"),("POST","/farmers"),("POST","/farms"),("POST","/plots"),
      ("POST","/harvests"),("POST","/offers"),("POST","/buyers"),("POST","/demands"),
      ("POST","/demands/{demand_id}/match"),("POST","/demands/{demand_id}/aggregate"),
      ("POST","/commitments/{commitment_id}/accept"),("POST","/commitments/{commitment_id}/decline"),
      ("POST","/orders/from-aggregation/{aggregation_id}"),("POST","/collection"),
      ("POST","/collection/{collection_id}/quality"),("POST","/lots"),
      ("POST","/transport-jobs"),("POST","/transport-jobs/{job_id}/depart"),
      ("POST","/deliveries"),("POST","/payments/orders/{order_id}/prepare"),
      ("POST","/payment-webhooks/provider")]
    missing=[x for x in required if x not in mounted]
    assert not missing,f"AGRI-CI-001 missing HTTP routes: {missing}"
