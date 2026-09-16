import os
def production_checks():
    env=os.getenv("APP_ENV","development")
    checks={
      "database_url":bool(os.getenv("DATABASE_URL")),
      "jwt_secret":bool(os.getenv("JWT_SECRET")) and os.getenv("JWT_SECRET") not in ("change-me","ci-only-secret-change-me"),
      "payment_webhook_secret":bool(os.getenv("PAYMENT_WEBHOOK_SECRET")) and os.getenv("PAYMENT_WEBHOOK_SECRET")!="change-me",
      "cors_origins":bool(os.getenv("CORS_ORIGINS")),
      "production_environment":env in ("staging","production"),
    }
    return checks,all(checks.values())
