"""Tasks for E-Commerce Fraud Investigation."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Literal

Difficulty = Literal["easy", "medium", "hard"]

@dataclass(frozen=True)
class UserSpec:
    user_id: str
    account_age_days: int
    previous_orders_count: int
    total_spent: float

@dataclass(frozen=True)
class OrderSpec:
    order_id: str
    user: UserSpec
    amount: float
    items: List[str]
    shipping_address: str
    billing_address: str
    payment_method: str
    ip_address: str
    device_id: str
    correct_order_action: Literal["approve", "reject"]
    correct_user_action: Literal["ban", "ignore"]
    required_reason_keywords: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class TaskDefinition:
    task_id: str
    title: str
    difficulty: Difficulty
    objective: str
    success_criteria: List[str]
    knowledge_base: List[str]
    max_steps: int
    orders: List[OrderSpec]

TASKS: Dict[str, TaskDefinition] = {
    "easy_proxy_fraud": TaskDefinition(
        task_id="easy_proxy_fraud",
        title="Handle Obvious Proxy Fraud",
        difficulty="easy",
        objective="Review a high-value order with suspicious mismatch.",
        success_criteria=[
            "Reject the order with reason mentioning 'proxy' or 'ip mismatch'.",
            "Ban the user account.",
        ],
        knowledge_base=[
            "If an order's shipping country does not match the billing country AND the IP address indicates a VPN/Proxy, reject the order.",
            "Always ban users who attempt IP mismatch proxy fraud.",
        ],
        max_steps=8,
        orders=[
            OrderSpec(
                order_id="ORD-101",
                user=UserSpec(user_id="USR-99", account_age_days=1, previous_orders_count=0, total_spent=0.0),
                amount=2499.00,
                items=["MacBook Pro 16"],
                shipping_address="123 Proxy Ln, London, UK",
                billing_address="456 Real St, New York, US",
                payment_method="Credit Card ending in 1234",
                ip_address="104.16.89.20 (Known VPN)",
                device_id="DEV-1A2B",
                correct_order_action="reject",
                correct_user_action="ban",
                required_reason_keywords=["proxy", "ip"],
            )
        ],
    ),
    "medium_mixed_queue": TaskDefinition(
        task_id="medium_mixed_queue",
        title="Distinguish Good vs Bad Users",
        difficulty="medium",
        objective="Review two orders. Approve the traveler, reject the fraudster.",
        success_criteria=[
            "Approve the legitimate traveler's order.",
            "Reject the stolen card order and ban the fraudster.",
        ],
        knowledge_base=[
            "If billing and shipping countries mismatch but the user account is > 300 days old with > 5 orders, they are traveling. Approve the order (no ban).",
            "If multiple orders use the exact same Device ID but different users, it is multi-accounting fraud. Reject and ban both.",
        ],
        max_steps=12,
        orders=[
            OrderSpec(
                order_id="ORD-201",
                user=UserSpec(user_id="USR-10", account_age_days=400, previous_orders_count=12, total_spent=4500.0),
                amount=150.00,
                items=["Travel Adapter"],
                shipping_address="Hotel Paris, Paris, FR",
                billing_address="123 Main St, NY, US",
                payment_method="Credit Card 9999",
                ip_address="192.168.1.1 (Paris)",
                device_id="DEV-TRAVEL",
                correct_order_action="approve",
                correct_user_action="ignore",
            ),
            OrderSpec(
                order_id="ORD-202",
                user=UserSpec(user_id="USR-88", account_age_days=2, previous_orders_count=0, total_spent=0.0),
                amount=900.00,
                items=["Gift Cards"],
                shipping_address="PO Box 1, NY, US",
                billing_address="123 Main St, NY, US",
                payment_method="Stolen Card",
                ip_address="10.0.0.1",
                device_id="DEV-FRAUD",
                correct_order_action="reject",
                correct_user_action="ban",
            ),
        ],
    ),
    "hard_bot_ring": TaskDefinition(
        task_id="hard_bot_ring",
        title="Dismantle a Bot Ring",
        difficulty="hard",
        objective="Identify linked devices and ban all coordinating accounts.",
        success_criteria=[
            "Cross-reference the Device ID to find the bot ring.",
            "Reject all orders associated with the bot ring.",
            "Ban all users in the ring.",
        ],
        knowledge_base=[
            "A Bot Ring occurs when 3 or more users share the exact same Device ID.",
            "All orders from a Bot Ring must be rejected.",
            "All users in a Bot Ring must be banned.",
            "When rejecting bot ring orders, the reason MUST mention 'bot ring' or 'device match'.",
        ],
        max_steps=18,
        orders=[
            OrderSpec("ORD-301", UserSpec("USR-A", 1, 0, 0), 50.0, ["Credit"], "A", "A", "CC1", "IP1", "DEV-RING", "reject", "ban", ["bot", "device"]),
            OrderSpec("ORD-302", UserSpec("USR-B", 1, 0, 0), 50.0, ["Credit"], "B", "B", "CC2", "IP2", "DEV-RING", "reject", "ban", ["bot", "device"]),
            OrderSpec("ORD-303", UserSpec("USR-C", 1, 0, 0), 50.0, ["Credit"], "C", "C", "CC3", "IP3", "DEV-RING", "reject", "ban", ["bot", "device"]),
        ],
    ),
}
