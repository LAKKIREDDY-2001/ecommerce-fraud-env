"""OpenEnv client for the Fraud environment."""

from __future__ import annotations
from typing import Dict
from openenv.core import EnvClient
from openenv.core.client_types import StepResult

try:
    from .models import FraudAction, FraudObservation, FraudState
except ImportError:
    from models import FraudAction, FraudObservation, FraudState  # type: ignore

class FraudEnv(
    EnvClient[FraudAction, FraudObservation, FraudState]
):
    """Client for a running fraud environment."""

    def _step_payload(self, action: FraudAction) -> Dict:
        return action.model_dump(exclude_none=True)

    def _parse_result(self, payload: Dict) -> StepResult[FraudObservation]:
        obs = FraudObservation.model_validate(payload["observation"])
        return StepResult(
            observation=obs,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> FraudState:
        return FraudState.model_validate(payload)
