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

- The biggest change was scope reduction from the full 8-class UML to a smaller, testable 4-class backend in [pawpal_system.py](pawpal_system.py): Owner, Pet, CareTask, and Scheduler. I made this change to deliver a working vertical slice faster, keep the API surface manageable, and avoid over-engineering before core scheduling behavior was validated.

- I also shifted explanatory output responsibilities into Scheduler for the first version (via an explain method) rather than maintaining a separate PlanExplainer class. This reduced cross-class coordination early on and made debugging easier while the scheduling rules were still evolving.

- Finally, I postponed dedicated DailyPlan, ScheduleItem, and DailyConstraint classes and represented those concerns more implicitly in method inputs/outputs. This tradeoff let me prioritize core scheduling logic first; those classes can be reintroduced once constraints and output formatting stabilize.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
