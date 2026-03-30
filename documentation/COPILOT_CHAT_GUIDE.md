# Using Copilot Chat for Testing

## Starting a Chat Session

In VS Code, press `Cmd+Shift+I` to open Copilot Chat. Reference `#codebase` so the suggestions stay grounded in this project.

## Useful Prompts

Here is a prompt you can copy and paste to ask Copilot about edge cases:

```
I'm building PawPal+, a pet care scheduling system in Python with:
- Task recurring logic (daily/weekly/biweekly/monthly/once frequencies)
- Time-budget scheduling algorithm (greedy packing)
- 6 algorithmic methods: sort_by_duration, sort_by_priority, sort_by_pet_name, 
  filter_by_pet, filter_by_priority, filter_by_completion_status
- Conflict detection (pet overwhelm, energy missequencing, back-to-back high-energy)

#codebase

What are the most important EDGE CASES I should test for? 
Please prioritize by:
1. Likelihood of real-world occurrence
2. Potential for data loss or crashes
3. Surprise bugs (counterintuitive behavior)

Focus on edge cases, not happy paths (I already test those).
```

---

## Key Topics to Explore with Copilot

### Topic 1: Date Boundary Edge Cases
"For recurring task date calculations, should I test:
- Tasks due on Feb 28 / Feb 29 (leap year)?
- Tasks spanning month boundaries (Mar 31 → Apr 30)?
- Tasks with last_completed_on=None?
- Past dates (task completed in 2025, checking if due in 2026)?"

### Topic 2: Time Budget Edge Cases
"My time-budget algorithm does:
```python
for pet, task in organize_tasks(owner):
    if minutes_used + task.time_minutes > available_minutes:
        continue
    plan.append((pet, task))
    minutes_used += task.time_minutes
```

What could break? Should I test:
- negative available_minutes?
- tasks with time_minutes=0?
- integer overflow (very large available_minutes)?
- floating-point rounding issues?"

### Topic 3: Empty/Null Input Handling
"Should the system gracefully handle:
- Owner with no pets?
- Pet with no tasks?
- Empty task list passed to sort/filter methods?
- None values in task properties?"

### Topic 4: Sorting Stability & Chaining
"For sorting and filtering:
- Should I test stable ordering (ties broken by secondary criteria)?
- Should I test chaining: sort → filter → sort?
- What happens if I filter first then sort vs sort first then filter?"

### Topic 5: Conflict Detection Heuristics
"My conflict detector looks for:
- 3+ high-priority tasks for one pet
- High-energy task (walk/playtime) → grooming
- Back-to-back high-energy (>60 min total)
- Total time >180 min

Are these heuristics correct? Any false positives or false negatives 
I should test for? Any missing cases?"

---

## Test Plan Summary (3-5 Core Behaviors)

1. **Recurring Task Logic** - Different frequencies calculate next dates correctly
2. **Time-Budget Scheduling** - Greedy algorithm fits high-priority tasks first
3. **Sorting Methods** - 3 methods (duration, priority, pet name) produce correct order
4. **Filtering Methods** - 3 methods (by pet, by priority, by status) return matching tasks
5. **Conflict Detection** - Warns about overwhelm, energy issues, time overruns without blocking

---

## After Copilot Suggests Edge Cases

1. Copy Copilot's suggestions into this document
2. Create new test methods in `tests/test_pawpal.py`
3. Run tests: `pytest tests/test_pawpal.py -v`
4. Fix any failures by updating `pawpal_system.py` or tests
5. Commit: `git add . && git commit -m "test: add edge case testing for [topic]"`

---

## Expected Outcome

After this testing phase:
- Existing tests should still pass
- Additional edge-case tests should be added
- Behavior on boundaries should be clearer and easier to trust
- Confidence in scheduler reliability should increase
