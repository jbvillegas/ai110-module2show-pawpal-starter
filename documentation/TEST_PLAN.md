# PawPal+ Testing Plan

## 1. Core Behaviors to Verify

Based on `pawpal_system.py`, these 5 behaviors are critical:

### 1a. **Task Recurring Logic** (Task class)
- `get_next_occurrence_date()` calculates correct next due dates
- `create_next_occurrence()` clones task properties correctly
- `is_due()` returns True when task should be scheduled, False when completed or not yet due
- One-time tasks (`frequency="once"`) never recur after completion

**Happy Path:**
- Daily task completed today → next occurrence due tomorrow
- Weekly task completed March 30 → next occurrence due April 6
- One-time task → no next occurrence

**Edge Cases:**
- Task completed on month boundary (Feb 28 → Mar 28)
- Task with last_completed_on=None → treated as always due
- Invalid frequency string → handled gracefully

### 1b. **Scheduling Algorithm** (Scheduler.organize_tasks, build_daily_plan)
- `organize_tasks()` returns due tasks sorted by priority, frequency, and duration
- `build_daily_plan()` greedily packs tasks until time budget is exhausted
- Time budget constraint is respected (no task overflows available_minutes)
- Within the time limit, high-priority and frequent tasks scheduled first

**Happy Path:**
- Owner with 6 tasks, 90 min available → schedule highest-priority tasks that fit
- All tasks fit → full plan returned
- No tasks fit (all too long or low priority) → empty plan

**Edge Cases:**
- Empty owner (no pets) → empty plan, no crash
- Owner with pets but no tasks → empty plan
- available_minutes=0 → no tasks scheduled
- All tasks marked complete → no tasks in plan
- Task with time_minutes=0 → should be schedulable (edge case in time calculation)
- available_minutes very large (1000+) → verify algorithm doesn't degrade

### 1c. **Sorting Methods** (sort_by_duration, sort_by_priority, sort_by_pet_name)
- Each method returns correctly ordered list
- Sorting is stable (when priorities tie, secondary criteria matter)
- Case-insensitive pet name sorting

**Happy Path:**
- 5 tasks with mixed durations → sorted ascending/descending correctly
- 5 tasks with mixed priorities (high/medium/low) → sorted high→low
- 3 pets with names (Buddy, Whiskers, Max) → sorted alphabetically

**Edge Cases:**
- Single task → returns containing only that task
- All tasks have same duration/priority/pet → stable order maintained
- Mixed case pet names (BUDDY, buddy, Buddy) → all treated as same

### 1d. **Filtering Methods** (filter_by_pet, filter_by_priority, filter_by_completion_status)
- Each method returns only matching tasks
- Filtering is case-insensitive (for pet names)
- Chaining filters produces correct intersection

**Happy Path:**
- Filter Buddy's tasks from 6-task list → 3 Buddy tasks returned
- Filter high-priority from 6-task list → 2 high-priority tasks
- Filter pending tasks (completed=False) → 4 pending, 2 completed

**Edge Cases:**
- Filter non-existent pet ("Fluffy" when only Buddy exists) → empty list, no crash
- Filter all tasks for priority → correct subset
- Filter completed when none completed → empty list
- Chain filters: filter_by_pet → filter_by_priority → filter_by_duration

### 1e. **Conflict Detection** (detect_conflicts, validate_plan)
- Detects pet overwhelm (3+ high-priority tasks)
- Detects energy missequencing (high-energy → grooming)
- Detects back-to-back high-energy tasks (>60 min total)
- Warns when total time >180 minutes
- Returns non-blocking warnings (doesn't crash, doesn't change plan)

**Happy Path:**
- Well-balanced plan (2 high-priority per pet, varied task types) → no warnings
- Plan with informational alerts (>180 min) → shows info without blocking

**Edge Cases:**
- Empty plan → no crashes, empty warnings list
- One high-priority task (not 3) → no overwhelm warning
- High-energy → feeding (opposite of grooming) → no warning
- Two high-energy tasks totaling 55 min (under threshold) → no warning
- Plan with exact time boundary (180 min) → no info warning

---

## 2. Testing Strategy

### Phase 1: Happy Path Tests (Baseline)
- All core behaviors work when used correctly
- Valid inputs produce expected outputs
- No crashes with typical data

### Phase 2: Edge Case Tests (Robustness)
- Empty/null inputs handled gracefully
- Boundary conditions (0 minutes, 1 task, exact thresholds)
- Chaining operations (sort then filter, filter then sort)
- Month/year boundaries for date calculations

### Phase 3: Integration Tests (Full Workflows)
- Mark task complete → next occurrence generated
- Filter tasks → sort filtered list → verify correct order
- Build plan → detect conflicts → present warnings

---

## 3. Questions for Copilot (#codebase)

Topics to discuss with Copilot Chat:
1. What edge cases for recurring task date calculations would you prioritize? (Feb 29, month boundaries, leap years?)
2. For the time-budget scheduling algorithm, what are the most likely failure modes? (negative available_minutes, tasks with 0 duration?)
3. Should we test sorting/filtering stability (when two tasks tie on primary criterion)? Why or why not?
4. Are there any edge cases in conflict detection heuristics that might produce misleading warnings?
5. Should we add tests for method chaining (sort → filter → sort)?

---

## 4. Test Coverage Goals

- **Task recurring logic**: 8 tests (daily/weekly/biweekly/monthly/once, boundaries)
- **Scheduling algorithm**: 6 tests (normal, empty, time constraints, edge times)
- **Sorting methods**: 6 tests (each of 3 methods, plus stability)
- **Filtering methods**: 6 tests (each of 3 methods, empty results, chaining)
- **Conflict detection**: 5 tests (overwhelm, energy, back-to-back, time overrun)

**Total: ~31 new tests** to complement the existing 15 tests.

---

## 5. Running Tests

```bash
pytest tests/test_pawpal.py -v  # Run all tests
pytest tests/test_pawpal.py::TestRecurringTasks -v  # Run specific test class
pytest tests/test_pawpal.py -k "edge" -v  # Run tests with "edge" in name
```

---

## Ready for Next Steps?

The test plan above identifies critical behaviors and edge cases. Next:
1. Start a new Copilot Chat session
2. Reference this TEST_PLAN.md with #codebase
3. Ask for specific edge case recommendations
4. Implement new tests based on Copilot suggestions
