from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional, Sequence, Tuple


FREQUENCY_TO_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30,
    "once": None,
}


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time_minutes: int
    frequency: str
    completed: bool = False
    priority: str = "medium"
    last_completed_on: Optional[date] = None

    def mark_complete(self, completed_on: Optional[date] = None) -> None:
        """Mark the task complete for the current cycle."""
        self.completed = True
        self.last_completed_on = completed_on or date.today()

    def mark_incomplete(self) -> None:
        """Reset completion state so the task can be scheduled again."""
        self.completed = False

    def get_next_occurrence_date(self) -> Optional[date]:
        """Calculate the due date for the next occurrence of this recurring task."""
        if self.frequency not in FREQUENCY_TO_DAYS:
            return None

        interval = FREQUENCY_TO_DAYS[self.frequency]
        if interval is None:  # "once" tasks don't recur
            return None

        if self.last_completed_on is None:
            return date.today()

        return self.last_completed_on + timedelta(days=interval)

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create a new task instance for the next occurrence of this recurring task."""
        if self.frequency == "once":
            return None  # Non-recurring tasks don't have next occurrences

        next_date = self.get_next_occurrence_date()
        if next_date is None:
            return None

        # Create a new task with the same properties but reset completion status
        new_task = Task(
            description=self.description,
            time_minutes=self.time_minutes,
            frequency=self.frequency,
            completed=False,
            priority=self.priority,
            last_completed_on=None  # New instance hasn't been completed yet
        )
        return new_task

    def is_due(self, on_date: Optional[date] = None) -> bool:
        """Return True if the task should be performed on the given date."""
        check_date = on_date or date.today()

        if self.frequency not in FREQUENCY_TO_DAYS:
            return not self.completed

        interval = FREQUENCY_TO_DAYS[self.frequency]
        if interval is None:
            return not self.completed

        if self.last_completed_on is None:
            return True

        return check_date >= (self.last_completed_on + timedelta(days=interval))


@dataclass
class Pet:
    """Stores pet profile details and that pet's tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """Remove first matching task by description. Returns success."""
        for index, task in enumerate(self.tasks):
            if task.description == description:
                del self.tasks[index]
                return True
        return False

    def get_tasks(self, include_completed: bool = True) -> List[Task]:
        """Return this pet's tasks, optionally filtering completed tasks."""
        if include_completed:
            return list(self.tasks)
        return [task for task in self.tasks if not task.completed]

    def get_due_tasks(self, on_date: Optional[date] = None) -> List[Task]:
        """Return only tasks currently due for this pet."""
        return [task for task in self.tasks if task.is_due(on_date)]


@dataclass
class Owner:
    """Manages multiple pets and aggregates their tasks."""

    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove first matching pet by name. Returns success."""
        for index, pet in enumerate(self.pets):
            if pet.name == pet_name:
                del self.pets[index]
                return True
        return False

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Get a pet by name, or None if no match exists."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self, include_completed: bool = True) -> List[Tuple[Pet, Task]]:
        """Return all tasks from every pet as (pet, task) tuples."""
        all_tasks: List[Tuple[Pet, Task]] = []
        for pet in self.pets:
            for task in pet.get_tasks(include_completed=include_completed):
                all_tasks.append((pet, task))
        return all_tasks


@dataclass
class Scheduler:
    """Retrieves, organizes, and manages tasks across all pets."""

    frequency_weight: Dict[str, int] = field(
        default_factory=lambda: {
            "daily": 4,
            "weekly": 3,
            "biweekly": 2,
            "monthly": 1,
            "once": 5,
        }
    )
    priority_weight: Dict[str, int] = field(
        default_factory=lambda: {
            "high": 3,
            "medium": 2,
            "low": 1,
        }
    )

    def retrieve_all_tasks(self, owner: Owner, include_completed: bool = False) -> List[Tuple[Pet, Task]]:
        """Fetch all tasks from owner pets."""
        return owner.get_all_tasks(include_completed=include_completed)

    def organize_tasks(self, owner: Owner, on_date: Optional[date] = None) -> List[Tuple[Pet, Task]]:
        """Return due tasks sorted by urgency and time required."""
        due_pairs = [
            (pet, task)
            for pet, task in self.retrieve_all_tasks(owner, include_completed=False)
            if task.is_due(on_date)
        ]

        return sorted(
            due_pairs,
            key=lambda pair: (
                -self.priority_weight.get(pair[1].priority, 2),
                -self.frequency_weight.get(pair[1].frequency, 0),
                pair[1].time_minutes,
                pair[0].name.lower(),
                pair[1].description.lower(),
            ),
        )

    def build_daily_plan(
        self,
        owner: Owner,
        available_minutes: int,
        on_date: Optional[date] = None,
    ) -> List[Tuple[Pet, Task]]:
        """Build a plan that fits into the owner's available time."""
        plan: List[Tuple[Pet, Task]] = []
        minutes_used = 0

        for pet, task in self.organize_tasks(owner, on_date=on_date):
            if minutes_used + task.time_minutes > available_minutes:
                continue
            plan.append((pet, task))
            minutes_used += task.time_minutes

        return plan

    def mark_task_complete(self, owner: Owner, pet_name: str, task_description: str) -> bool:
        """Mark one matching task complete for a pet and create next occurrence if recurring."""
        pet = owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.tasks:
            if task.description == task_description:
                task.mark_complete()

                # If task is recurring, create next occurrence automatically
                if task.frequency != "once":
                    next_task = task.create_next_occurrence()
                    if next_task:
                        pet.add_task(next_task)

                return True

        return False

    def plan_summary(self, plan: List[Tuple[Pet, Task]]) -> str:
        """Create a readable summary of a generated plan."""
        if not plan:
            return "No tasks fit the available time window."

        lines = ["Daily plan:"]
        total = 0
        for pet, task in plan:
            total += task.time_minutes
            lines.append(
                f"- {pet.name}: {task.description} ({task.time_minutes} min, {task.frequency}, {task.priority} priority)"
            )
        lines.append(f"Total scheduled time: {total} minutes")
        return "\n".join(lines)

    def sort_by_duration(self, tasks: Sequence[Tuple[Pet, Task]], ascending: bool = True) -> List[Tuple[Pet, Task]]:
        """
        Sort tasks by duration (time_minutes) in ascending or descending order.
        
        Args:
            tasks: Sequence of (Pet, Task) tuples to be sorted.
            ascending: If True, shortest tasks first (default). If False, longest tasks first.
        
        Returns:
            Sorted list of (Pet, Task) tuples ordered by task duration.
        """
        reverse = not ascending
        return sorted(tasks, key=lambda pair: pair[1].time_minutes, reverse=reverse)

    def sort_by_priority(self, tasks: Sequence[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
        """
        Sort tasks by priority level, with high priority tasks first.
        
        Priority order: high (3) > medium (2) > low (1).
        
        Args:
            tasks: Sequence of (Pet, Task) tuples to be sorted.
        
        Returns:
            Sorted list of (Pet, Task) tuples ordered by priority level (descending).
        """
        priority_order = {"high": 3, "medium": 2, "low": 1}
        return sorted(
            tasks,
            key=lambda pair: priority_order.get(pair[1].priority, 0),
            reverse=True
        )

    def sort_by_pet_name(self, tasks: Sequence[Tuple[Pet, Task]]) -> List[Tuple[Pet, Task]]:
        """
        Sort tasks by pet name in alphabetical order (case-insensitive).
        
        Args:
            tasks: Sequence of (Pet, Task) tuples to be sorted.
        
        Returns:
            Sorted list of (Pet, Task) tuples ordered alphabetically by pet name.
        """
        return sorted(tasks, key=lambda pair: pair[0].name.lower())

    def filter_by_pet(self, tasks: Sequence[Tuple[Pet, Task]], pet_name: str) -> List[Tuple[Pet, Task]]:
        """
        Filter tasks to include only those belonging to a specific pet.
        
        Args:
            tasks: Sequence of (Pet, Task) tuples to filter.
            pet_name: The name of the pet (case-insensitive) to filter by.
        
        Returns:
            List of (Pet, Task) tuples where the pet name matches (case-insensitive).
        """
        return [pair for pair in tasks if pair[0].name.lower() == pet_name.lower()]

    def filter_by_completion_status(self, tasks: Sequence[Tuple[Pet, Task]], completed: bool = False) -> List[Tuple[Pet, Task]]:
        """
        Filter tasks by completion status.
        
        Args:
            tasks: Sequence of (Pet, Task) tuples to filter.
            completed: If True, return only completed tasks. If False (default), return only pending tasks.
        
        Returns:
            List of (Pet, Task) tuples matching the completion status.
        """
        return [pair for pair in tasks if pair[1].completed == completed]

    def filter_by_priority(self, tasks: Sequence[Tuple[Pet, Task]], min_priority: str = "low") -> List[Tuple[Pet, Task]]:
        """
        Filter tasks to include only those at or above a minimum priority level.
        
        Priority levels: low (1) < medium (2) < high (3).
        
        Args:
            tasks: Sequence of (Pet, Task) tuples to filter.
            min_priority: Minimum priority level to include ("low", "medium", or "high"). Default: "low".
        
        Returns:
            List of (Pet, Task) tuples with priority >= min_priority.
        """
        priority_order = {"high": 3, "medium": 2, "low": 1}
        min_level = priority_order.get(min_priority, 0)
        return [
            pair for pair in tasks
            if priority_order.get(pair[1].priority, 0) >= min_level
        ]

    def detect_conflicts(self, plan: List[Tuple[Pet, Task]]) -> List[str]:
        """
        Detect potential scheduling conflicts and return warning messages.
        
        Checks for:
        - Pet overwhelm: A single pet with 3+ high-priority tasks in one day.
        - Energy missequencing: High-energy task (walk/play/fetch/run) followed by grooming.
        - Back-to-back high-energy: Two high-energy tasks totaling >60 minutes consecutively.
        - Time overrun: Total schedule >180 minutes (3+ hours).
        
        Args:
            plan: List of (Pet, Task) tuples representing the scheduled plan.
        
        Returns:
            List of warning messages (strings). Empty list if no conflicts detected.
            Messages use ⚠️ for warnings and ℹ️ for informational alerts.
        """
        warnings = []

        # Check for same-pet task conflicts (too many tasks back-to-back)
        pet_task_count: Dict[str, int] = {}
        for pet, task in plan:
            pet_name = pet.name
            pet_task_count[pet_name] = pet_task_count.get(pet_name, 0) + 1

        # Warn if a single pet has too many high-intensity tasks
        for pet, task in plan:
            if task.priority == "high" and pet_task_count[pet.name] >= 3:
                warnings.append(
                    f"⚠️  WARNING: {pet.name} has {pet_task_count[pet.name]} high-priority tasks. "
                    f"Consider spacing them out to avoid overwhelming the pet."
                )
                break  # Only warn once per pet

        # Check for problematic task sequences (same pet)
        for i, (pet1, task1) in enumerate(plan):
            if i + 1 < len(plan):
                pet2, task2 = plan[i + 1]
                if pet1.name == pet2.name:
                    # Check if high-energy task followed by grooming
                    is_task1_high_energy = task1.description.lower() in ["walk", "playtime", "fetch", "run"]
                    is_task2_grooming = task2.description.lower() in ["grooming", "bath", "nail trim"]

                    if is_task1_high_energy and is_task2_grooming:
                        warnings.append(
                            f"⚠️  WARNING: {pet1.name} has a high-energy task ('{task1.description}') "
                            f"followed immediately by grooming ('{task2.description}'). "
                            f"Pet may be too energetic. Consider adding a cool-down period."
                        )

                    # Check if two high-energy tasks back-to-back
                    is_task2_high_energy = task2.description.lower() in ["walk", "playtime", "fetch", "run"]
                    if is_task1_high_energy and is_task2_high_energy and task1.time_minutes + task2.time_minutes > 60:
                        warnings.append(
                            f"⚠️  WARNING: {pet1.name} has two high-energy tasks back-to-back "
                            f"('{task1.description}' + '{task2.description}'). "
                            f"Total {task1.time_minutes + task2.time_minutes} minutes may be too much."
                        )

        # Check for time budget overrun
        total_time = sum(task.time_minutes for _, task in plan)
        # This is informational, not a conflict per se
        if total_time > 180:  # More than 3 hours
            warnings.append(
                f"ℹ️  INFO: Total scheduled time is {total_time} minutes. "
                f"Owner may find this schedule exhausting."
            )

        return warnings

    def validate_plan(self, plan: List[Tuple[Pet, Task]], available_minutes: int) -> tuple[List[Tuple[Pet, Task]], List[str]]:
        """
        Validate a plan and return it with any conflict warnings.
        
        This method runs conflict detection on a plan and returns both the plan
        and any warnings as a tuple. Useful for checking scheduling issues before
        presenting the plan to the user.
        
        Args:
            plan: List of (Pet, Task) tuples representing the scheduled plan.
            available_minutes: The time budget used to create the plan (for context).
        
        Returns:
            Tuple of (plan, warnings) where:
            - plan: The original (Pet, Task) list unchanged.
            - warnings: List of warning message strings from detect_conflicts().
        """
        warnings = self.detect_conflicts(plan)
        return plan, warnings
