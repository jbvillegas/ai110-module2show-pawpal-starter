from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple


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
        """Mark one matching task complete for a pet."""
        pet = owner.get_pet(pet_name)
        if pet is None:
            return False

        for task in pet.tasks:
            if task.description == task_description:
                task.mark_complete()
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
