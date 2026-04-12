"""Deterministic graders for Fraud environment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from models import ProgressBreakdown  # type: ignore
from tasks import TaskDefinition, OrderSpec  # type: ignore

EPSILON = 0.001
SCORE_FLOOR = EPSILON
SCORE_CEILING = 0.999

@dataclass
class OrderWorkspace:
    status: str = "pending"
    reason: str = ""
    user_banned: bool = False
    viewed_order: bool = False
    viewed_user: bool = False

def _normalize(text: str) -> str:
    return " ".join(text.lower().split())

def _clamp_task_score(score: float) -> float:
    clamped = max(SCORE_FLOOR, min(SCORE_CEILING, score))
    return EPSILON if clamped <= 0 else (1.0 - EPSILON if clamped >= 1.0 else clamped)

def grade_order(spec: OrderSpec, workspace: OrderWorkspace) -> ProgressBreakdown:
    order_score = SCORE_FLOOR
    if workspace.status != "pending":
        if workspace.status == spec.correct_order_action:
            order_score = SCORE_CEILING
            if spec.correct_order_action == "reject" and spec.required_reason_keywords:
                norm_reason = _normalize(workspace.reason)
                matched = any(k.lower() in norm_reason for k in spec.required_reason_keywords)
                if not matched:
                    order_score = 0.5  # Partial credit for correct reject action with weak reason.
        else:
            order_score = SCORE_FLOOR

    user_score = SCORE_FLOOR
    if spec.correct_user_action == "ban":
        user_score = SCORE_CEILING if workspace.user_banned else SCORE_FLOOR
    else:
        user_score = SCORE_CEILING if not workspace.user_banned else SCORE_FLOOR

    total = (0.6 * order_score) + (0.4 * user_score)
    return ProgressBreakdown(
        order_action_score=round(_clamp_task_score(order_score), 4),
        user_action_score=round(_clamp_task_score(user_score), 4),
        total_score=round(_clamp_task_score(total), 4),
    )

def grade_task(
    task: TaskDefinition,
    workspaces: Dict[str, OrderWorkspace],
    finalized: bool,
) -> tuple[float, Dict[str, ProgressBreakdown]]:
    breakdown: Dict[str, ProgressBreakdown] = {}
    if not task.orders:
        return round(SCORE_FLOOR, 4), breakdown

    scores: List[float] = []
    for spec in task.orders:
        workspace = workspaces.get(spec.order_id, OrderWorkspace())
        bk = grade_order(spec, workspace)
        breakdown[spec.order_id] = bk
        scores.append(bk.total_score)

    mean_score = sum(scores) / len(scores)
    finalization_bonus = 0.05 if finalized else SCORE_FLOOR
    final_score = _clamp_task_score((mean_score * 0.95) + finalization_bonus)
    clamped_final = max(EPSILON, min(0.999, final_score))
    return round(clamped_final, 4), breakdown
