"""FastAPI application for the Fraud environment."""
import os
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["ENABLE_WEB_INTERFACE"] = "true"

from openenv.core.env_server.http_server import create_app
from fastapi.responses import RedirectResponse

try:
    from ..models import FraudAction, FraudObservation
    from .fraud_environment import EcommerceFraudEnvironment
except ImportError:
    from models import FraudAction, FraudObservation
    from server.fraud_environment import EcommerceFraudEnvironment

app = create_app(
    EcommerceFraudEnvironment,
    FraudAction,
    FraudObservation,
    env_name="ecommerce_fraud_env",
    max_concurrent_envs=4,
)

@app.get("/")
async def root():
    return RedirectResponse(url="/web")

def main(host: str = "0.0.0.0", port: int = int(os.getenv("PORT", "7860"))) -> None:
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
