# Step 1: Plan What to Test - COMPLETE ✅

## Summary of Testing Plan

I've prepared a comprehensive testing strategy for PawPal+ focusing on core behaviors and edge cases.

---

## Core Behaviors Identified (5 Critical Areas)

### 1️⃣ **Task Recurring Logic** 
**What to test:** Different frequencies (daily/weekly/biweekly/monthly/once) calculating correct next occurrence dates.

- ✅ `get_next_occurrence_date()` - calculates next due date based on frequency
- ✅ `create_next_occurrence()` - clones task with correct properties
- ✅ `is_due(on_date)` - returns True when task should be scheduled
- ✅ One-time tasks don't recur after completion

**Happy Path Examples:**
- Daily task completed today → due tomorrow
- Weekly task completed Mar 30 → due Apr 6
- One-time task completed → stays completed

**Edge Cases to Test:**
- Month boundary (Feb 28 → Mar 28)
- Null `last_completed_on` → treated as always due
- Invalid frequency string → graceful handling

---

### 2️⃣ **Scheduling Algorithm**
**What to test:** Time-budget greedy packing respects constraints and prioritizes correctly.

- ✅ `organize_tasks()` - returns due tasks sorted by priority, frequency, duration
- ✅ `build_daily_plan()` - packs tasks greedily until time budget exhausted
- ✅ Respects time constraints (no overflow)
- ✅ High-priority and frequent tasks scheduled first

**Happy Path Examples:**
- 6 tasks, 90 min available → schedule highest-priority subset that fits
- All tasks fit → full plan returned
- No tasks fit → empty plan, no crash

**Edge Cases to Test:**
- `available_minutes=0` → no tasks scheduled
- `available_minutes` very large (1000+) → algorithm doesn't degrade
- All tasks marked complete → no tasks in plan
- Task with `time_minutes=0` → should be schedulable
- Owner with no pets → empty plan, no crash

---

### 3️⃣ **Sorting Methods** (3 methods)
**What to test:** Correct ordering by duration, priority, and pet name.

- ✅ `sort_by_duration()` - ascending/descending by time_minutes
- ✅ `sort_by_priority()` - high > medium > low
- ✅ `sort_by_pet_name()` - alphabetical (case-insensitive)

**Happy Path Examples:**
- 5 tasks mixed durations → sorted ascending/descending correctly
- 5 tasks mixed priorities → sorted high→low
- 3 pets (Buddy, Whiskers, Max) → alphabetical order

**Edge Cases to Test:**
- Single task → returns list containing only that task
- All tasks same duration/priority/pet → stable order maintained
- Mixed case pet names (BUDDY, buddy, Buddy) → all treated same

---

### 4️⃣ **Filtering Methods** (3 methods)
**What to test:** Each filter returns only matching tasks; chaining filters works.

- ✅ `filter_by_pet(pet_name)` - only tasks for specific pet
- ✅ `filter_by_priority(min_priority)` - threshold-based (≥ level)
- ✅ `filter_by_completion_status(completed)` - pending vs completed

**Happy Path Examples:**
- Filter Buddy's tasks from 6-task list → 3 Buddy tasks
- Filter high-priority → 2 high-priority tasks
- Filter pending → 4 pending, 2 completed

**Edge Cases to Test:**
- Non-existent pet ("Fluffy") → empty list, no crash
- No tasks match filter → empty list
- Chain filters: `filter_by_pet()` → `filter_by_priority()` → correct intersection
- Case-insensitive pet name matching (buddy vs BUDDY)

---

### 5️⃣ **Conflict Detection**
**What to test:** Warnings are accurate, non-blocking, and catch real issues.

- ✅ `detect_conflicts(plan)` - scans for 4 types of conflicts
- ✅ `validate_plan(plan, available_minutes)` - returns (plan, warnings)
- ✅ Warnings are non-blocking; plan still presented to user

**Conflict Types:**
1. Pet overwhelm: 3+ high-priority tasks → warning
2. Energy missequencing: high-energy (walk/playtime) → grooming → warning
3. Back-to-back high-energy: 2 high-energy tasks >60 min → warning
4. Time overrun: total time >180 minutes → info alert

**Happy Path Examples:**
- Well-balanced plan (2 high-priority per pet) → no warnings
- Plan >180 min → shows info without blocking

**Edge Cases to Test:**
- Empty plan → no crashes, empty warnings list
- One high-priority (not 3) → no overwhelm warning
- High-energy → feeding (not grooming) → no warning
- Two high-energy totaling 55 min (under 60) → no warning
- Plan with exactly 180 min → no info warning

---

## Testing Documents Created

### 📄 `TEST_PLAN.md`
Comprehensive testing roadmap covering:
- All 5 core behaviors with happy paths and edge cases
- Testing strategy (Phase 1: happy paths → Phase 2: edge cases → Phase 3: integration)
- Test coverage goals (31 new tests)
- Questions for Copilot about edge case prioritization

### 📄 `COPILOT_CHAT_GUIDE.md` 
Guide for starting a focused Copilot Chat session:
- Ready-to-copy prompt for asking about edge cases
- 5 key topics to explore (date boundaries, time budget, empty inputs, sorting stability, conflict heuristics)
- Next steps after Copilot suggests improvements

---

## Next Steps: Start Copilot Chat Session

### How to Invoke Copilot
1. Press `Cmd+Shift+I` in VS Code (or click Copilot Chat in sidebar)
2. Open a **new chat session** (dedicated to testing)
3. Copy-paste the prompt from `COPILOT_CHAT_GUIDE.md`
4. Reference `#codebase` in your prompt

### Example Prompt
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

## Questions to Explore with Copilot

1. **Date Boundaries**: Should I prioritize leap year handling, month boundaries, or null dates?
2. **Time Budget Algorithm**: What could break with negative minutes, zero minutes, or very large values?
3. **Empty Inputs**: How should the system behave with empty owners, empty pets, or empty task lists?
4. **Sorting Stability**: Do I need tests for stable ordering when tasks tie on primary criterion?
5. **Conflict Detection**: Are the 4 heuristics (overwhelm, energy, back-to-back, time overrun) complete?

---

## Current Test Status

- ✅ 15 existing tests: all passing
- ✅ Core behaviors identified: 5 critical areas
- ✅ Happy paths documented: basic functionality
- ⏳ Edge cases planned: 31+ new tests recommended
- ⏳ Copilot review pending: awaiting edge case prioritization

---

## Ready for Copilot Chat?

Yes! The testing plan is complete. You can now:

1. Open a new Copilot Chat session
2. Reference `#codebase` and ask for edge case recommendations
3. Implement suggested tests in `tests/test_pawpal.py`
4. Run `pytest tests/test_pawpal.py -v` to verify
5. Commit edge case tests with `git add . && git commit -m "test: add edge case coverage"`

**Estimated time for Copilot Chat review: 10-15 minutes**
**Estimated time to implement suggested tests: 1-2 hours**
