
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    sentry_sdk.init(
        dsn="https://YOUR_SENTRY_DSN@sentry.io/PROJECT_ID",
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
        environment="production",
        release="evento-system@3.0.0"
    )
    
    return sentry_sdk

# Adicionar ao main.py
from app.monitoring.sentry_config import init_sentry

# No startup do FastAPI
@app.on_event("startup")
async def startup_event():
    init_sentry()
    print("✅ Sentry monitoring initialized")
