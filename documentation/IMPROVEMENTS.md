# PawPal+ Scheduling Logic Improvements

## Current Status

### What Works
- Basic task creation and completion tracking
- Frequency-aware due date logic (daily, weekly, etc.)
- Priority-weighted task ranking via weighted tuple sort
- Greedy time-budget planning (fits as many tasks as possible)
- Multi-pet aggregation and management

### What Could Be Better
1. **Task Sorting**: Hard-coded weighted tuple in `organize_tasks()` - tough to adjust weights or add new criteria
2. **Time Management**: Greedy packing with no time-of-day awareness (morning, afternoon, evening)
3. **Scheduling Strategy**: Linear selection with no conflict detection or time-slot assignment
4. **Filtering**: No explicit filter methods (by pet, by status, by priority level)
5. **Recurring Tasks**: `is_due()` handles frequency but no special multi-occurrence handling
6. **Explainability**: No clear explanation of why task X was skipped

---

## Potential Improvements

Here are some ideas to build on the current system. I grouped them by difficulty.

### 1. Filtering Helpers
**Goal**: Add explicit methods to filter tasks by different criteria

```python
# In Scheduler class or as standalone methods
def filter_tasks_by_pet(tasks, pet_name) -> List[Tuple[Pet, Task]]
def filter_tasks_by_priority(tasks, min_priority) -> List[Tuple[Pet, Task]]
def filter_tasks_by_status(tasks, completed=False) -> List[Tuple[Pet, Task]]
def filter_tasks_by_time_window(tasks, window="morning") -> List[Tuple[Pet, Task]]
```

**Benefit**: Make filtering composable and testable. Cleaner than nested comprehensions.

---

### 2. Time-of-Day Scheduling
**Goal**: Assign tasks to logical time slots (morning, afternoon, evening)

```python
# Add to Task class
preferred_time_window: str = "flexible"  # "morning", "afternoon", "evening", "flexible"

# In Scheduler
def assign_time_slots(self, plan: List[Tuple[Pet, Task]]) -> List[TimedTask]:
    """Assign each task a start/end time within the day."""
    # Return list of (pet, task, start_hour, end_hour) tuples
```

**Benefit**: Schedule walks in morning (pet energy), grooming in afternoon, feeding at specific times.

---

### 3. Recurring Task Expansion
**Goal**: Handle multi-occurrence tasks (e.g., "Feeding" happens 2x daily)

```python
# Add to Task class
occurrences_per_day: int = 1  # How many times daily/weekly/etc

# In Scheduler
def expand_recurring_tasks(self, tasks) -> List[Tuple[Pet, Task, int]]:
    """Expand recurring tasks into separate schedule entries."""
    # E.g., "Feeding" (daily, 2x) becomes 2 entries in the plan
```

**Benefit**: Better reflect real pet care (feeding multiple times, multiple walks).

---

### 4. Conflict Detection
**Goal**: Detect and flag scheduling conflicts

```python
# In Scheduler
def has_conflicts(self, plan: List[Tuple[Pet, Task]]) -> List[str]:
    """Return list of conflict messages."""
    # Example conflicts:
    # - Two high-energy dogs scheduled back-to-back (recovery time needed)
    # - Grooming after play (pet too energetic)
    # - Feeding + walk in wrong order
```

**Benefit**: Catch scheduling issues before presenting plan to user.

---

### 5. Dynamic Sorting Strategy
**Goal**: Replace hard-coded tuple sort with configurable scoring function

```python
# In Scheduler
def calculate_task_score(self, task, context) -> float:
    """
    Compute urgency score using:
    - Priority weight
    - Days overdue (if recurring)
    - Pet energy level
    - Time window preference
    """
    
def rank_tasks_by_score(self, tasks) -> List[Tuple[Pet, Task]]:
    """Sort by dynamic scores instead of tuple weights."""
```

**Benefit**: Easy to adjust algorithm; more flexible than tuple sorting.

---

### 6️⃣ **Skipped Task Analysis** (EASY)
**Goal**: Explain why tasks were skipped with decision metadata

```python
# In Scheduler
def build_daily_plan_with_reasoning(self, owner, available_minutes):
    """Return plan + dict of {task: reason_skipped}."""
    # Reasons:
    # - "Time budget exceeded"
    # - "Lower priority than other tasks"
    # - "Not due today"
    # - "Conflict with scheduled task"
```

**Benefit**: Transparency for users; helps debug scheduling decisions.

---

### 7️⃣ **Pet Energy/Type Awareness** (MEDIUM)
**Goal**: Factor pet type and energy into task ordering

```python
# Add to Pet class
energy_level: str = "medium"  # "low", "medium", "high"
task_preferences: Dict[str, int] = {}  # "walk": 2x, "play": 1x, etc.

# In Scheduler
def rank_tasks_by_pet_context(tasks, pet) -> List[Tuple[Pet, Task]]:
    """Prioritize tasks that match pet's energy and preferences."""
```

**Benefit**: High-energy dogs get walks first; calm cats get grooming later in day.

---

## Implementation Priority (Recommended Order)

| # | Feature | Effort | Impact | Dependencies |
|---|---------|--------|--------|---|
| 1️⃣ | Filtering Helpers | 30 min | Medium | None |
| 2️⃣ | Skipped Task Reasoning | 30 min | High | None |
| 3️⃣ | Dynamic Sorting | 45 min | High | None |
| 4️⃣ | Time-of-Day Scheduling | 60 min | High | Filtering |
| 5️⃣ | Pet Energy Awareness | 45 min | Medium | Dynamic Sorting |
| 6️⃣ | Recurring Task Expansion | 60 min | Medium | Time-of-Day |
| 7️⃣ | Conflict Detection | 60 min | Medium | Recurring Tasks |

---

## Quick Wins (Do First)
- ✅ Add filter methods → improves testability and reusability
- ✅ Add reasoning to `build_daily_plan()` → improves transparency
- ✅ Replace tuple sort with scoring function → improves maintainability

## Phase 3 Stretch Goals
- Add time-aware scheduling (start/end times for each task)
- Detect conflicting task pairs
- Expand recurring tasks into multiple schedule entries
