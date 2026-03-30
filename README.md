# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling Features

Beyond basic task management, PawPal+ includes several algorithmic improvements to help owners plan better:

### Sorting Methods
- **`sort_by_duration()`**: Order tasks from quick (e.g., 5 min feeding) to long (e.g., 30 min walk), or vice versa. Useful for fitting quick wins into tight schedules.
- **`sort_by_priority()`**: Rank tasks by importance (high → medium → low). Essential care comes first; optional enrichment comes later.
- **`sort_by_pet_name()`**: Group tasks by pet for easier review of individual pet schedules.

### Filtering Methods
- **`filter_by_pet()`**: View only tasks for a specific pet (e.g., "Show me everything for Buddy").
- **`filter_by_priority()`**: Find all high-priority tasks to ensure critical care isn't skipped.
- **`filter_by_completion_status()`**: See pending vs. completed tasks to track progress and plan ahead.

### Recurring Task Automation
Tasks can be set to repeat on a schedule:
- **Daily**: Morning walk auto-generates every day (1-day interval).
- **Weekly**: Grooming auto-generates every 7 days.
- **Biweekly/Monthly**: Longer intervals for less frequent tasks.
- **Once**: One-time tasks don't repeat.

When a recurring task is marked complete, the system automatically creates the next occurrence with the same properties, eliminating manual rescheduling.

### Conflict Detection
Before presenting a plan, the scheduler scans for potential issues:
- **Pet overwhelm**: Warns if one pet has 3+ high-priority tasks in a single day.
- **Energy missequencing**: Alerts when a high-energy task (walk, playtime) is immediately followed by grooming—the pet may be too energetic for grooming.
- **Back-to-back high-energy**: Flags two high-energy tasks totaling >60 minutes consecutively.
- **Time overrun**: Informs when total scheduled time exceeds 180 minutes (3+ hours).

Warnings are non-blocking; the plan is still presented to the user with warnings displayed prominently.

## Testing PawPal+

### Running Tests

Run the test suite to verify all system behaviors:

```bash
python -m pytest tests/test_pawpal.py -v
```

### Test Coverage

The test suite has 35 tests across 8 test classes:

- Task Lifecycle (2 tests): Task completion, incompletion, and status tracking
- Task Management (2 tests): Adding/removing tasks from pets
- Owner Management (2 tests): Pet addition and multi-pet task aggregation
- Recurring Tasks (7 tests): Daily/weekly/biweekly scheduling, auto-generation, one-time behavior
- Sorting Methods (5 tests): Duration, priority, pet name, and case-insensitive matching
- Filtering Methods (7 tests): Filtering by pet, priority, completion status, and chaining
- Conflict Detection (8 tests): Pet overwhelm, energy missequencing, back-to-back high-energy, time overrun
- Scheduler Core (2 tests): Time-budget planning and plan summary generation

All 35 tests pass consistently with zero failures.

### Confidence Level

Five stars. The system is thoroughly tested with comprehensive coverage across all core algorithms and edge cases. All sorting, filtering, and conflict detection methods are verified. Recurring task automation works across all frequencies. Time budget scheduling handles realistic constraints properly. No known bugs or regressions.

The PawPal+ system is ready for production use as a pet care scheduler.
