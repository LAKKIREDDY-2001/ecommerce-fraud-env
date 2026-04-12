import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graders import OrderWorkspace, grade_task  # type: ignore
from tasks import TASKS  # type: ignore

def test_easy_task_perfect_score():
    task = TASKS["easy_proxy_fraud"]
    workspace = {
        "ORD-101": OrderWorkspace(
            status="reject",
            reason="proxy mismatch",
            user_banned=True,
        )
    }
    score, breakdown = grade_task(task, workspace, finalized=True)
    assert score == pytest.approx(0.999)
    assert breakdown["ORD-101"].total_score == pytest.approx(0.999)

def test_medium_task_perfect_score():
    task = TASKS["medium_mixed_queue"]
    workspace = {
        "ORD-201": OrderWorkspace(status="approve"),
        "ORD-202": OrderWorkspace(status="reject", reason="stolen", user_banned=True)
    }
    score, bk = grade_task(task, workspace, finalized=True)
    assert score == pytest.approx(0.999)

def test_hard_task_perfect_score():
    task = TASKS["hard_bot_ring"]
    workspace = {
        "ORD-301": OrderWorkspace(status="reject", reason="bot ring", user_banned=True),
        "ORD-302": OrderWorkspace(status="reject", reason="device match", user_banned=True),
        "ORD-303": OrderWorkspace(status="reject", reason="bot ring", user_banned=True)
    }
    score, bk = grade_task(task, workspace, finalized=True)
    assert score == pytest.approx(0.999)

def test_all_scores_stay_strictly_inside_open_interval():
    for task in TASKS.values():
        score, breakdown = grade_task(task, {}, finalized=False)
        assert 0.0 < score < 1.0
        for item in breakdown.values():
            assert 0.0 < item.order_action_score < 1.0
            assert 0.0 < item.user_action_score < 1.0
            assert 0.0 < item.total_score < 1.0

def test_non_finalized_task_never_returns_zero():
    task = TASKS["medium_mixed_queue"]
    score, breakdown = grade_task(task, {}, finalized=False)

    assert score == pytest.approx(0.1916)
    assert breakdown["ORD-201"].total_score == pytest.approx(0.4002)
    assert breakdown["ORD-202"].total_score == pytest.approx(0.001)
