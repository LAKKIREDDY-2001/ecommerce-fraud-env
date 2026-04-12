"""Typed models for the E-Commerce Fraud Investigation environment."""

from __future__ import annotations
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from openenv.core.env_server.types import Action, Observation, State

OperationType = Literal[
    "view_order",
    "view_user",
    "approve_order",
    "reject_order",
    "ban_user",
    "finalize",
    "noop",
]

class ProgressBreakdown(BaseModel):
    order_action_score: float = Field(default=0.01)
    user_action_score: float = Field(default=0.01)
    total_score: float = Field(default=0.01)
    notes: List[str] = Field(default_factory=list)

class OrderRecord(BaseModel):
    order_id: str
    user_id: str
    amount: float
    status: str = "pending"  # pending, approved, rejected
    user_banned: bool = False
    progress: ProgressBreakdown = Field(default_factory=ProgressBreakdown)

class OrderDetail(BaseModel):
    order_id: str
    user_id: str
    amount: float
    items: List[str]
    shipping_address: str
    billing_address: str
    payment_method: str
    ip_address: str
    device_id: str

class UserDetail(BaseModel):
    user_id: str
    account_age_days: int
    previous_orders_count: int
    total_spent: float
    is_banned: bool = False

class TaskCard(BaseModel):
    task_id: str
    title: str
    difficulty: Literal["easy", "medium", "hard"]
    objective: str
    success_criteria: List[str] = Field(default_factory=list)
    max_steps: int

class FraudAction(Action):
    operation: OperationType = Field(..., description="Operation to perform.")
    order_id: Optional[str] = Field(default=None, description="Target order ID.")
    user_id: Optional[str] = Field(default=None, description="Target user ID.")
    reason: Optional[str] = Field(default=None, description="Reason for rejection.")

class FraudObservation(Observation):
    task: TaskCard
    queue: List[OrderRecord] = Field(default_factory=list)
    current_order: Optional[OrderDetail] = None
    current_user: Optional[UserDetail] = None
    knowledge_base: List[str] = Field(default_factory=list)
    progress_score: float = Field(default=0.01)
    final_score: Optional[float] = None
    last_action: str = Field(default="")
    allowed_actions: List[str] = Field(default_factory=list)

class FraudState(State):
    task_id: Optional[str] = None
    current_order_id: Optional[str] = None
    current_user_id: Optional[str] = None
    queue: List[OrderRecord] = Field(default_factory=list)
    finalized: bool = False
    max_steps: int = 0
    progress_score: float = 0.01
    final_score: Optional[float] = None
    grading_breakdown: Dict[str, ProgressBreakdown] = Field(default_factory=dict)
