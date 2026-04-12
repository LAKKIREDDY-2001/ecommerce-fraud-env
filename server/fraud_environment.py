"""Fraud investigation environment implementation."""

from __future__ import annotations
from typing import Any, Dict, Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import EnvironmentMetadata, State

try:
    from ..graders import OrderWorkspace, grade_task
    from ..models import (
        ProgressBreakdown, FraudAction, FraudObservation, FraudState,
        TaskCard, OrderDetail, OrderRecord, UserDetail
    )
    from ..tasks import TASKS, TaskDefinition
except ImportError:
    from graders import OrderWorkspace, grade_task
    from models import (
        ProgressBreakdown, FraudAction, FraudObservation, FraudState,
        TaskCard, OrderDetail, OrderRecord, UserDetail
    )
    from tasks import TASKS, TaskDefinition

class EcommerceFraudEnvironment(
    Environment[FraudAction, FraudObservation, FraudState]
):
    SUPPORTS_CONCURRENT_SESSIONS = True

    def __init__(self) -> None:
        super().__init__()
        self._task: TaskDefinition = TASKS["easy_proxy_fraud"]
        self._workspaces: Dict[str, OrderWorkspace] = {}
        self._state = FraudState(episode_id=str(uuid4()), task_id=self._task.task_id, max_steps=self._task.max_steps)
        self._current_order_id: Optional[str] = None
        self._current_user_id: Optional[str] = None
        self._last_action = "Initialize."
        self._reset_task("easy_proxy_fraud")

    def _reset_task(self, task_id: str, episode_id: Optional[str] = None) -> None:
        if task_id not in TASKS:
            raise ValueError(f"Invalid task_id: {task_id}")
        self._task = TASKS[task_id]
        self._workspaces = {spec.order_id: OrderWorkspace() for spec in self._task.orders}
        self._current_order_id = None
        self._current_user_id = None
        self._last_action = "Queue loaded."
        self._state = FraudState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_id=self._task.task_id,
            current_order_id=None,
            current_user_id=None,
            queue=self._build_queue_records(),
            finalized=False,
            max_steps=self._task.max_steps,
            progress_score=0.01,
            final_score=None,
            grading_breakdown={},
        )

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="ecommerce_fraud_env",
            description="Triage e-commerce fraud investigations by checking IPs, Device IDs, and cross-referencing user history.",
            version="1.0.0",
            author="OpenEnv",
        )

    def reset(self, seed: Optional[int] = None, episode_id: Optional[str] = None, **kwargs: Any) -> FraudObservation:
        del seed
        task_id = kwargs.get("task_id", "easy_proxy_fraud")
        self._reset_task(task_id, episode_id=episode_id)
        return self._build_observation(reward=0.0, done=False)

    def step(self, action: FraudAction, timeout_s: Optional[float] = None, **kwargs: Any) -> FraudObservation:
        del timeout_s, kwargs
        if self._state.finalized:
            return self._build_observation(reward=-0.1, done=True, override_last_action="Already finalized.")

        prev_progress, _ = grade_task(self._task, self._workspaces, finalized=False)
        self._state.step_count += 1
        done = False
        penalty = 0.01

        try:
            self._apply_action(action)
        except ValueError as exc:
            self._last_action = f"Invalid: {exc}"
            penalty += 0.1

        curr_progress, breakdown = grade_task(self._task, self._workspaces, finalized=False)
        reward = round(curr_progress - prev_progress - penalty, 4)

        if action.operation == "finalize":
            self._state.finalized = True
            done = True
            fs, fb = grade_task(self._task, self._workspaces, finalized=True)
            reward = round(fs - prev_progress - penalty, 4)
            breakdown = fb
            self._state.final_score = fs
            self._state.progress_score = fs
        elif self._state.step_count >= self._task.max_steps:
            done = True
            self._state.finalized = True
            fs, fb = grade_task(self._task, self._workspaces, finalized=False)
            self._state.final_score = fs
            self._state.progress_score = fs
            breakdown = fb
            self._last_action += " Max steps reached."
        else:
            self._state.progress_score = curr_progress

        self._state.current_order_id = self._current_order_id
        self._state.current_user_id = self._current_user_id
        self._state.queue = self._build_queue_records(breakdown)
        self._state.grading_breakdown = breakdown

        return self._build_observation(reward=reward, done=done, breakdown=breakdown)

    def _apply_action(self, action: FraudAction) -> None:
        if action.operation == "noop":
            self._last_action = "No-op."
            return
        if action.operation == "finalize":
            self._last_action = "Finalized."
            return

        if action.operation == "view_order":
            if not action.order_id or action.order_id not in self._workspaces:
                raise ValueError("Valid order_id required.")
            self._workspaces[action.order_id].viewed_order = True
            self._current_order_id = action.order_id
            self._last_action = f"Viewed order {action.order_id}."
            return

        if action.operation == "view_user":
            if not action.user_id:
                raise ValueError("Valid user_id required.")
            found = False
            for spec in self._task.orders:
                if spec.user.user_id == action.user_id:
                    self._workspaces[spec.order_id].viewed_user = True
                    found = True
            if not found:
                raise ValueError("User not found.")
            self._current_user_id = action.user_id
            self._last_action = f"Viewed user {action.user_id}."
            return

        if action.operation in ["approve_order", "reject_order"]:
            if not action.order_id or action.order_id not in self._workspaces:
                raise ValueError("Valid order_id required.")
            workspace = self._workspaces[action.order_id]
            if action.operation == "reject_order":
                if not action.reason:
                    raise ValueError("reject_order requires a reason.")
                workspace.status = "reject"
                workspace.reason = action.reason.strip()
            else:
                workspace.status = "approve"
                workspace.reason = ""
            self._current_order_id = action.order_id
            self._last_action = f"Order {action.order_id} set to {workspace.status}."
            return

        if action.operation == "ban_user":
            if not action.user_id:
                raise ValueError("Valid user_id required.")
            for spec in self._task.orders:
                if spec.user.user_id == action.user_id:
                    self._workspaces[spec.order_id].user_banned = True
            self._current_user_id = action.user_id
            self._last_action = f"Banned user {action.user_id}."
            return

        raise ValueError("Unsupported operation.")

    def _build_queue_records(self, bk: Optional[Dict] = None) -> list[OrderRecord]:
        bk = bk or {}
        recs = []
        for spec in self._task.orders:
            w = self._workspaces.get(spec.order_id, OrderWorkspace())
            recs.append(OrderRecord(
                order_id=spec.order_id,
                user_id=spec.user.user_id,
                amount=spec.amount,
                status=w.status,
                user_banned=w.user_banned,
                progress=bk.get(spec.order_id, ProgressBreakdown())
            ))
        return recs

    def _cur_order(self) -> Optional[OrderDetail]:
        if not self._current_order_id:
            return None
        spec = next((o for o in self._task.orders if o.order_id == self._current_order_id), None)
        return OrderDetail(
            order_id=spec.order_id, user_id=spec.user.user_id, amount=spec.amount,
            items=spec.items, shipping_address=spec.shipping_address,
            billing_address=spec.billing_address, payment_method=spec.payment_method,
            ip_address=spec.ip_address, device_id=spec.device_id
        ) if spec else None

    def _cur_user(self) -> Optional[UserDetail]:
        if not self._current_user_id:
            return None
        spec = next((o.user for o in self._task.orders if o.user.user_id == self._current_user_id), None)
        return UserDetail(
            user_id=spec.user_id, account_age_days=spec.account_age_days,
            previous_orders_count=spec.previous_orders_count, total_spent=spec.total_spent
        ) if spec else None

    def _build_observation(self, reward: float, done: bool, breakdown: Optional[Dict] = None, override_last_action: Optional[str] = None) -> FraudObservation:
        ps, fb = grade_task(self._task, self._workspaces, finalized=self._state.finalized)
        eb = breakdown or fb
        if done and self._state.final_score is None:
            self._state.final_score = ps
        curr = self._state.final_score if done else ps
        return FraudObservation(
            task=TaskCard(task_id=self._task.task_id, title=self._task.title, difficulty=self._task.difficulty, objective=self._task.objective, success_criteria=self._task.success_criteria, max_steps=self._task.max_steps),
            queue=self._build_queue_records(eb),
            current_order=self._cur_order(),
            current_user=self._cur_user(),
            knowledge_base=self._task.knowledge_base,
            progress_score=curr,
            final_score=self._state.final_score if done else None,
            last_action=override_last_action or self._last_action,
            allowed_actions=["view_order(order_id)", "view_user(user_id)", "approve_order(order_id)", "reject_order(order_id, reason)", "ban_user(user_id)", "finalize()", "noop()"],
            done=done, reward=reward,
            metadata={"step_count": self._state.step_count, "grading_breakdown": {tid: d.model_dump() for tid, d in eb.items()}}
        )

    @property
    def state(self) -> State:
        return self._state
