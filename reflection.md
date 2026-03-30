# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- My initial UML design used a small set of core classes in addition to one orchestration class:

    1. Owner: stored owner info and scheduling preferences (available minutes, preferred time windows, task preferences).
    2. Pet: stored pet profile data (name, species, age/needs) and linked to the owner.
    3. CareTask: represented one task with attributes like title, duration, priority, optional preferred time, and category (walk, feeding, meds, etc.).
    4. DailyConstraint: grouped day-specific limits such as total available time and blocked/unavailable periods.
    5. Scheduler: main decision engine; selected tasks that fit constraints, ranked them by priority and urgency, and ordered them into a daily plan.
    6. ScheduleItem: represented one scheduled entry (task + start/end time + reason).
    7. DailyPlan: held the final list of schedule items, total planned time, skipped tasks, and summary metadata.
    8. PlanExplainer: generated human-readable reasoning for why tasks were chosen, deferred, or skipped.

    This split helped separate data objects (Owner, Pet, CareTask) from decision logic (Scheduler) and output/explanation (DailyPlan, PlanExplainer).

    I also defined key relationships in the UML so implementation boundaries were clear: one Owner can manage one or more Pets, each Pet can have many CareTasks, the Scheduler consumes CareTasks plus DailyConstraint and outputs one DailyPlan, and each DailyPlan contains many ScheduleItems. I treated ScheduleItem as a scheduled instance of a CareTask so each planned block stays traceable to the original task definition.

    I identified two likely bottlenecks early: the Scheduler could become a "god class" if ranking, constraint checks, ordering, and explanation data stayed tightly coupled; and PlanExplainer could produce weak reasoning if it only saw final outputs without decision metadata from the Scheduler.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Yes, my design changed during implementation.

- The biggest change was scope reduction from the full 8-class UML to a smaller, testable 4-class backend in [pawpal_system.py](pawpal_system.py): Owner, Pet, Task, and Scheduler. I made this change to deliver a working vertical slice faster, keep the API surface manageable, and avoid over-engineering before core scheduling behavior was validated.

- I also shifted explanatory output responsibilities into Scheduler for the first version (via an explain method) rather than maintaining a separate PlanExplainer class. This reduced cross-class coordination early on and made debugging easier while the scheduling rules were still evolving.

- Finally, I postponed dedicated DailyPlan, ScheduleItem, and DailyConstraint classes and represented those concerns more implicitly in method inputs/outputs. This tradeoff let me prioritize core scheduling logic first; those classes can be reintroduced once constraints and output formatting stabilize.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three primary constraints:

1. **Time budget**: Total available minutes is the hard constraint. The `build_daily_plan()` method uses a greedy algorithm to pack tasks until no more fit in the remaining time window. This is the most important constraint because pet owners have fixed daily schedules.

2. **Task priority** (high/medium/low): Tasks are weighted and sorted by priority first. High-priority tasks (e.g., feeding, medications) are scheduled before medium/low tasks (e.g., grooming, entertainment). This respects that some pet care is essential (health/safety) while other tasks are discretionary.

3. **Task frequency** (daily/weekly/biweekly/monthly/once): Recurring tasks are prioritized by how often they need to occur. Daily tasks weight higher than weekly tasks, ensuring essential routines aren't skipped. This reflects the reality that frequent tasks are more time-critical and harder to reschedule.

I decided constraints mattered in this order because:
- **Time is non-negotiable**: An owner's schedule can't bend; we must work within their available minutes.
- **Priority is user-driven**: Each task's importance is assigned by the owner based on their specific pet's needs.
- **Frequency compounds**: Daily tasks accumulate faster than weekly ones, making them more pressing to include in the plan.

I deprioritized other potential constraints (time-of-day preferences, pet energy levels, pet compatibility) in the MVP because they would have tripled implementation complexity. These are now tracked in [IMPROVEMENTS.md](documentation/IMPROVEMENTS.md) for future phases.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The core tradeoff is **transparent ranking simplicity vs. configurable weights at runtime**.

The `organize_tasks()` method ranks tasks using a fixed tuple-based sort key with static dictionaries (`priority_weight`, `frequency_weight`):

```python
key=lambda pair: (
    -self.priority_weight.get(pair[1].priority, 2),
    -self.frequency_weight.get(pair[1].frequency, 0),
    pair[1].time_minutes,
    pair[0].name.lower(),
    pair[1].description.lower(),
)
```

This approach **prioritizes readability and transparency**:
- Sorting logic is visible in one place
- Weights are explicit and understood at a glance  
- Ranking criteria are predictable (priority → frequency → duration → pet name → task name)
- No indirection through separate scoring methods

The tradeoff is that **weights cannot be adjusted without code changes**. In a more flexible design, I could extract weights to configuration files or method parameters, but that would add layers of indirection and make the ranking logic less obvious to someone reading the code. For this project (a learning exercise, small dataset of 5-30 tasks per day), **transparency and simplicity of logic outweigh runtime configurability**. If the app grows to support hundreds of tasks or user-specific weight preferences, extracting configurable scoring functions would become worthwhile.

Another minor tradeoff: **exact time matching vs. conflict detection**. The scheduler checks if tasks fit within total available minutes (greedy bin-packing approach) but doesn't model time-of-day constraints or task sequencing conflicts. It detects pet overwhelm warnings but assumes sequential execution. For future versions, assigning specific time slots (e.g., "Morning walk at 8:00 AM, Feeding at 6:00 PM") would require tracking blocked periods and preventing overlaps, adding complexity. For the current version, a single-pass scheduling algorithm with post-hoc conflict warnings strikes a reasonable balance between user control and implementation simplicity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI mostly to move faster on implementation and test design:

1. **Design clarification**: I asked AI to review my first UML draft and point out missing relationships or likely bottlenecks. That helped me tighten my design discussion early.

2. **Test case generation**: I used AI to suggest test scenarios for recurring tasks, filtering, and sorting. It helped me catch edge cases I probably would have missed on the first pass.

3. **Refactoring suggestions**: During Phase 4, I asked for cleaner ways to structure sorting, filtering, and conflict detection. I ended up adopting the lambda-based sorting approach and the `(Pet, Task)` tuple pattern.

4. **Documentation**: I used AI for docstring cleanup and for brainstorming which tradeoffs were worth calling out in this reflection.

The most helpful prompts were specific and code-based. For example, asking "Here is my sorting lambda, how can I make it more readable?" worked much better than broad prompts like "How do I sort tasks?".

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I reviewed `organize_tasks()`, AI suggested extracting the sort key into a helper method. I decided not to do that and kept the inline lambda.

My reasoning:
1. **Readability**: In this project, seeing the sort order directly in one place is easier to understand.
2. **Scope**: The method is already short, so extracting a helper would add indirection without much benefit.
3. **Project stage**: For an MVP, I preferred fewer abstractions. I would refactor if the sorting rules become larger or user-configurable.

**Verification**: I compared both versions and asked which one would be easier for a new teammate to read quickly. The inline version won for this codebase. I also checked whether extraction would improve test coverage, and it would not.

This reinforced a practical lesson: good suggestions still need to match the stage of the project. I used AI guidance, but I still made the final call based on readability and scope.

**c. Copilot strategy reflection**

- Which Copilot features were most effective for building your scheduler?
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
- How did using separate chat sessions for different phases help you stay organized?
- What did you learn about being the lead architect when working with powerful AI tools?

The most useful Copilot features in VS Code were:

1. **`#file:pawpal_system.py` grounding**: This kept suggestions tied to the real backend API and reduced generic advice.
2. **`#codebase` context**: This helped Copilot reason across `app.py`, tests, and docs when I needed consistent updates.
3. **Inline Chat for local fixes**: It was fast for debugging one failing test or improving one method without leaving the file.
4. **Chat mode for planning**: For broader work (test planning, architecture cleanup), the chat thread was better than inline edits.

One suggestion I explicitly rejected was extracting the `organize_tasks()` sort key into a helper too early. I kept the inline lambda because it made ranking logic obvious in one place during MVP development. I only want extra abstraction when complexity actually justifies it.

Using separate chat sessions by phase helped a lot with organization:

1. **Design session**: UML and class boundaries only.
2. **Implementation session**: method behavior and algorithm choices.
3. **Testing session**: edge cases, assertions, and failure triage.
4. **Documentation session**: README and reflection polish.

That separation reduced context mixing, made prompts more focused, and made it easier to track decisions.

My biggest takeaway about being the lead architect is that AI is powerful, but it is still a collaborator, not the decision-maker. My role was to define scope, enforce naming/model consistency, reject unnecessary complexity, and verify behavior with tests. In other words, Copilot sped up execution, but system quality still depended on my architectural judgment.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I initially wrote 15 unit tests across five critical areas:

1. **Task completion lifecycle** (2 tests): Verify that marking a task complete sets `completed=True` and `last_completed_on=date`, and that marking incomplete resets the flag. Essential because the UI relies on accurate task state.

2. **Task addition/removal** (2 tests): Verify that tasks can be added to a pet and removed correctly. Important because the data model must maintain accurate task counts.

3. **Owner management** (2 tests): Verify that pets can be added to owners and that `get_all_tasks()` correctly aggregates tasks across all pets. Critical because the scheduler operates on the Owner's full task set.

4. **Recurring task automation** (7 tests): Test the core of Phase 4—verifying that `get_next_occurrence_date()` calculates correct dates (daily=+1, weekly=+7), that `create_next_occurrence()` clones task properties correctly, that one-time tasks don't auto-generate, and that marking a daily task complete triggers the next occurrence. This is the most important behavior because it automates the app's key value proposition.

5. **Scheduling algorithm** (2 tests): Verify that `build_daily_plan()` respects time limits and that `plan_summary()` generates readable output. Important for the core MVP feature.

At first, I focused more on core behavior than rare edge cases, since the app runs on small daily task sets and in-memory state.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

At that stage, my confidence was **8/10**. All 15 tests passed, the demo worked, and the Streamlit integration was stable. I felt strongest in:
- Task creation, completion, and recurring automation
- Sorting and filtering (tested with real data in main.py)
- Time budget planning (greedy algorithm is simple and predictable)
- Conflict detection (warnings are heuristic-based and safe to show)

I was less confident about:
- Behavior when a pet has 100+ tasks (not tested; may have performance issues)
- Handling of tasks added with `time_minutes=0` (untested edge case)
- Behavior when `available_minutes=0` (should return empty plan, assumed correct but not tested)
- Recurring tasks that span month boundaries (e.g., Feb 28 → Mar 28; date math is correct but not explicitly tested)

**Edge cases to test next:**
1. Empty owner with no pets → should not crash when building a plan
2. Large time gaps (e.g., `available_minutes=1000`) → ensure greedy algorithm doesn't degrade
3. All tasks have the same priority/frequency → verify stable sort order (name-based)
4. Completing tasks with 0 minutes duration → verify time budget calculation doesn't assume all tasks have > 0 minutes
5. Recurring task due date boundary (daily task due at 11:59 PM on March 30, check if it's due on March 31)
6. Conflict detection on empty plan → should return no warnings, not crash

Those edge cases were my next priority for raising confidence.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is the recurring task automation (Phase 3). The combination of:
- Frequency-to-days mapping constant (FREQUENCY_TO_DAYS)
- `Task.get_next_occurrence_date()` using timedelta for clean date arithmetic
- `Scheduler.mark_task_complete()` auto-generating the next occurrence
...creates a feature that is actually useful in practice. After setup, recurring tasks keep moving forward automatically. The implementation is compact, testable, and removes manual work for the user.

I am also happy with the design-to-implementation path. I started with a broader UML and then reduced scope to 4 core classes so I could ship a working version quickly. That decision made it possible to finish the sorting, filtering, and conflict-detection improvements on time.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Top improvements for the next phase (also documented in [IMPROVEMENTS.md](documentation/IMPROVEMENTS.md)):

1. **Decision reasoning**: Add a `build_daily_plan_with_reasoning()` method that returns not just the plan but a dict of `{task: reason_for_inclusion_or_exclusion}`. Users should understand why their dog's morning walk was skipped (time budget exceeded) vs. why playtime was removed (lower priority than feeding).

2. **Time-of-day assignment**: Upgrade from a greedy "fit tasks in any order" algorithm to one that assigns specific time slots (e.g., 8:00 AM walk, 6:00 PM feeding). This requires modeling blocked periods, preferred time windows, and task sequencing.

3. **Pet energy/temperament awareness**: Some pets shouldn't have back-to-back high-energy tasks without a cool-down period. The current conflict detection only warns; the next version should auto-reorder or suggest skips.

4. **Persistent storage**: Migrate from Streamlit session state (in-memory, lost on page reload) to SQLite or PostgreSQL. Right now, users lose their pet data if they close the browser.

5. **UI polish**: Add pet photos and one-click "mark complete" toggles in the schedule display. The current text-only layout works, but it still feels basic.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

**Do not over-engineer early; prioritize clarity and iteration speed.**

My initial UML made sense conceptually but was too large for an MVP. Features like PlanExplainer and DailyConstraint were valid ideas, but not necessary in the first implementation. By cutting them, I:
- Went from design to working code in one afternoon instead of a week
- Could test hypotheses (Does a greedy algorithm work? Can users understand tuple-based sorting?)
- Unblocked the algorithmic improvements (filtering, sorting, recurring tasks, conflicts) that made the system genuinely useful

The same applies to AI collaboration: specific prompts with concrete code produce better results than broad prompts. Also, AI suggestions about architecture are useful, but they still need to fit the maturity of the project.

Finally, tests did more than catch bugs; they clarified expected behavior. Writing recurrence tests forced me to define exact rules for dates and edge cases. The test suite ended up acting like a specification for the scheduling logic.
