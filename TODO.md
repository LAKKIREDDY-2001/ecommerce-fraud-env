# Validator Fix: Strict (0,1) Scores - Progress 7/9

**Current Issue:** HF/GitHub validator sees boundary scores in support_triage (hf-space/hf-space/graders.py).

**Approved Fix Steps:**
### 1. [x] Local fraud env: 0.98 aggregate ✓
### 2. [x] pytest fraud tests: 5/5 pass ✓
### 3. [ ] Edit hf-space/hf-space/graders.py: add SCORE_FLOOR/CEILING, clamp raw 0.99
### 4. [ ] Edit inference.py: EPS=0.01
### 5. [ ] pytest hf-space/hf-space/tests/
### 6. [ ] Rerun assessment for triage
### 7. [x] git pull synced
### 8. [ ] New branch blackboxai/fix-boundaries, commit/push
### 9. [ ] HF rebuild

Next: Implement Step 3.
