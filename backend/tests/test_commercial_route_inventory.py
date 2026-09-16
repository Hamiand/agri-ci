from app.main import app
def test_commercial_routes_are_mounted():
    paths={r.path for r in app.routes}
    required={
      "/health","/auth/register","/auth/login","/farmers","/farms","/plots","/harvests",
      "/offers","/buyers","/demands","/collection","/lots","/transport-jobs",
      "/deliveries","/payments/farmer/me","/payment-webhooks/provider"
    }
    missing=required-paths
    assert not missing,f"Missing commercial routes: {sorted(missing)}"
