---
title: E-Commerce Fraud Environment Server
emoji: 🛡️
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
app_port: 7860
base_path: /web
tags:
  - openenv
---

# E-Commerce Fraud Investigation Environment

[![Hugging Face Space](https://img.shields.io/badge/Hugging%20Face-Live%20Demo-f59e0b)](https://huggingface.co/spaces/Lakkireddy-2001/ecommerce-fraud-env)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-16a34a)](https://huggingface.co/spaces/Lakkireddy-2001/ecommerce-fraud-env)
[![Task Scores](https://img.shields.io/badge/Scoring-Strictly%20Within%20(0%2C1)-dc2626)](https://huggingface.co/spaces/Lakkireddy-2001/ecommerce-fraud-env)

`ecommerce_fraud_env` is a novel, real-world OpenEnv environment for Trust & Safety investigation. An AI agent must inspect a queue of flagged e-commerce orders, cross-reference users, devices, IPs, and historical order data, and decide whether to approve/reject the orders and ban malicious actors.

## Demo

- Live Space: https://huggingface.co/spaces/Lakkireddy-2001/ecommerce-fraud-env
- GitHub Repo: https://github.com/LAKKIREDDY-2001/ecommerce-fraud-env
- Environment Name: `ecommerce_fraud_env`

## Why This Submission Stands Out

- Realistic trust-and-safety workflow with linked entity investigation instead of one-step classification.
- Deterministic grading with partial credit, keyword-aware rejection logic, and strict OpenEnv-safe score bounds.
- Three difficulty tiers that test reasoning quality, not just memorization.
- Ready for both local validation and Hugging Face Space deployment.

## Why This Is Useful

E-commerce fraud detection is a multi-billion dollar real-world domain. Manual review teams process thousands of risky orders every day, correlating disparate data sources. This environment simulates:
- Proxy/VPN IP spoofing
- Stolen credit card detection
- Multi-accounting Bot Rings

It tests an agent's ability to plan, correlate cross-entity data, and execute deterministic policy actions safely without False Positives (wrongly banning legitimate travelers).

## Action Space

The environment accepts a typed `FraudAction`:

- `view_order(order_id)`: Load order context.
- `view_user(user_id)`: Load user context.
- `approve_order(order_id)`: Marks an order safe.
- `reject_order(order_id, reason)`: Marks an order fraudulent along with a specific required reason keywords.
- `ban_user(user_id)`: Bans the user account permanently.
- `finalize()`
- `noop()`

## Observation Space

Each `FraudObservation` includes:

- `task`: Card with objective, difficulty, and max steps
- `queue`: Summary of pending orders
- `current_order`: Fully hydrated order detail (only populated after `view_order`)
- `current_user`: Fully hydrated user detail (only populated after `view_user`)
- `knowledge_base`: Precise rule snippets defining the investigation strict criteria.

## Tasks & Reward Design

### 1. Easy: Obvious Proxy Fraud
A single high-value order with a mismatched IP (VPN) and billing address. The agent must reject the order (citing `proxy` or `ip`) and ban the user.

### 2. Medium: Distinguish Good vs Bad
Two orders in the queue. The agent must realize one is a legitimate traveling user (mismatched IP but old trusted account history) and approve it, while rejecting and banning the other user using a stolen card on a brand-new account.

### 3. Hard: Dismantle a Bot Ring
Three identical low-value orders from brand new accounts using the exact same Device ID but different IPs. The agent must correlate the `device_id`, reject all three citing `bot` or `device match`, and ban all three users.

Rewards are deterministic partial-progress signals that always stay strictly inside `(0, 1)` to satisfy OpenEnv submission validation. Wrong or incomplete actions receive low-but-valid partial values, while correct investigation and finalization move the score near the upper bound without ever returning exactly `1.0`.

## Setup

```bash
uv sync
openenv validate
uv run server
```

Then open:
- `http://localhost:7860/web`
- `http://localhost:7860/docs`

## Docker

```bash
docker build -t ecommerce-fraud-env .
docker run -p 7860:7860 ecommerce-fraud-env
```

## Baseline Inference

Required environment variables:
- `API_BASE_URL`
- `MODEL_NAME`
- `API_KEY`

Run the baseline:
```bash
python inference.py
```
The baseline uses the injected LiteLLM proxy via the `OpenAI` client when both `API_BASE_URL` and `API_KEY` are present, and gracefully falls back to a deterministic high-scoring policy otherwise.
