from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass
class Owner:
	"""Represents the pet owner and planning preferences."""

	name: str
	daily_time_available_minutes: int
	preferred_time_windows: List[str] = field(default_factory=list)
	task_preferences: Dict[str, str] = field(default_factory=dict)

	def update_preferences(self, new_preferences: Dict[str, str]) -> None:
		"""Update owner task preference mappings."""
		pass

	def is_time_window_preferred(self, window: str) -> bool:
		"""Return whether a given time window is preferred by the owner."""
		pass

	def available_time_remaining(self, plan_minutes_used: int) -> int:
		"""Compute remaining available minutes after a plan is built."""
		pass


@dataclass
class Pet:
	"""Represents a pet and its care profile."""

	name: str
	species: str
	age: int
	energy_level: str
	special_needs: List[str] = field(default_factory=list)

	def requires_task_type(self, task_type: str) -> bool:
		"""Return whether this pet needs a given task type."""
		pass

	def get_care_profile(self) -> str:
		"""Summarize core care profile information for scheduling."""
		pass

	def validate_task_for_pet(self, task: CareTask) -> bool:
		"""Return whether a task is valid for this pet's profile."""
		pass


@dataclass
class CareTask:
	"""Represents one pet care task candidate."""

	title: str
	category: str
	duration_minutes: int
	priority: str
	preferred_window: str
	recurrence: str
	required: bool = False

	def is_due_today(self, date: str) -> bool:
		"""Return whether this task is due on the provided date."""
		pass

	def priority_score(self) -> int:
		"""Convert priority to a numeric score for ranking."""
		pass

	def fits_time_budget(self, remaining_minutes: int) -> bool:
		"""Return whether this task fits the remaining time budget."""
		pass


@dataclass
class Scheduler:
	"""Coordinates task ranking and daily plan construction."""

	total_minutes_available: int
	scoring_weights: Dict[str, float] = field(default_factory=dict)

	def rank_tasks(
		self,
		tasks: Sequence[CareTask],
		owner: Owner,
		pet: Pet,
	) -> List[CareTask]:
		"""Rank tasks using priority, preferences, and pet context."""
		pass

	def select_tasks(
		self,
		tasks: Sequence[CareTask],
		available_minutes: int,
	) -> List[CareTask]:
		"""Choose tasks that should be included in the daily plan."""
		pass

	def assign_time_slots(self, tasks: Sequence[CareTask]) -> List[CareTask]:
		"""Order selected tasks into a practical execution sequence."""
		pass

	def build_plan(
		self,
		tasks: Sequence[CareTask],
		owner: Owner,
		pet: Pet,
	) -> List[CareTask]:
		"""Build a complete daily task plan for the given owner and pet."""
		pass

	def explain_choices(
		self,
		included: Sequence[CareTask],
		skipped: Sequence[CareTask],
	) -> str:
		"""Explain why tasks were included or skipped."""
		pass
