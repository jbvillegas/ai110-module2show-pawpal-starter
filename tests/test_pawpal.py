"""Test suite for PawPal+ logic layer."""

import pytest
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


class TestTaskCompletion:
    """Test Task completion functionality."""

    def test_mark_complete_changes_status(self):
        """Verify that mark_complete() changes the task's completed status."""
        task = Task(description="Morning walk", time_minutes=30, frequency="daily", priority="high")
        
        # Initially, task should not be completed
        assert task.completed is False
        assert task.last_completed_on is None
        
        # Mark as complete
        task.mark_complete()
        
        # Verify status changed
        assert task.completed is True
        assert task.last_completed_on is not None
        assert task.last_completed_on == date.today()

    def test_mark_incomplete_resets_status(self):
        """Verify that mark_incomplete() resets the task's completed status."""
        task = Task(description="Feeding", time_minutes=10, frequency="daily")
        
        # Mark complete first
        task.mark_complete()
        assert task.completed is True
        
        # Mark incomplete
        task.mark_incomplete()
        
        # Verify status reset
        assert task.completed is False


class TestTaskAddition:
    """Test Pet task management."""

    def test_add_task_increases_count(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        pet = Pet(name="Buddy", species="dog", age=3)
        
        # Initially, pet should have no tasks
        assert len(pet.tasks) == 0
        
        # Add first task
        task1 = Task(description="Morning walk", time_minutes=30, frequency="daily", priority="high")
        pet.add_task(task1)
        
        # Verify count increased
        assert len(pet.tasks) == 1
        assert pet.tasks[0] == task1
        
        # Add second task
        task2 = Task(description="Feeding", time_minutes=10, frequency="daily")
        pet.add_task(task2)
        
        # Verify count increased again
        assert len(pet.tasks) == 2
        assert pet.tasks[1] == task2

    def test_remove_task_decreases_count(self):
        """Verify that removing a task from a Pet decreases that pet's task count."""
        pet = Pet(name="Whiskers", species="cat", age=5)
        
        # Add two tasks
        task1 = Task(description="Feeding", time_minutes=5, frequency="daily")
        task2 = Task(description="Grooming", time_minutes=15, frequency="weekly")
        pet.add_task(task1)
        pet.add_task(task2)
        
        assert len(pet.tasks) == 2
        
        # Remove one task
        success = pet.remove_task("Feeding")
        
        # Verify removal was successful and count decreased
        assert success is True
        assert len(pet.tasks) == 1
        assert pet.tasks[0] == task2


class TestOwnerManagement:
    """Test Owner pet management."""

    def test_add_pet_to_owner(self):
        """Verify that adding a pet to an Owner increases pet count."""
        owner = Owner(name="Alice")
        
        # Initially, owner should have no pets
        assert len(owner.pets) == 0
        
        # Add first pet
        dog = Pet(name="Buddy", species="dog", age=3)
        owner.add_pet(dog)
        
        # Verify count increased
        assert len(owner.pets) == 1
        assert owner.pets[0] == dog

    def test_get_all_tasks_aggregates(self):
        """Verify that Owner.get_all_tasks() aggregates tasks across all pets."""
        owner = Owner(name="Alice")
        
        # Create pets with tasks
        dog = Pet(name="Buddy", species="dog", age=3)
        dog.add_task(Task(description="Walk", time_minutes=30, frequency="daily"))
        dog.add_task(Task(description="Feeding", time_minutes=10, frequency="daily"))
        
        cat = Pet(name="Whiskers", species="cat", age=5)
        cat.add_task(Task(description="Litter box", time_minutes=10, frequency="daily"))
        
        owner.add_pet(dog)
        owner.add_pet(cat)
        
        # Get all tasks
        all_tasks = owner.get_all_tasks(include_completed=True)
        
        # Verify aggregation
        assert len(all_tasks) == 3
        # Check that tasks are returned as (pet, task) tuples
        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in all_tasks)


class TestRecurringTasks:
    """Test recurring task logic and next occurrence generation."""

    def test_get_next_occurrence_date_daily(self):
        """Verify that get_next_occurrence_date() calculates correct date for daily tasks."""
        task = Task(description="Feeding", time_minutes=10, frequency="daily", priority="high")
        task.mark_complete(completed_on=date(2026, 3, 30))

        next_date = task.get_next_occurrence_date()

        assert next_date == date(2026, 3, 31)

    def test_get_next_occurrence_date_weekly(self):
        """Verify that get_next_occurrence_date() calculates correct date for weekly tasks."""
        task = Task(description="Grooming", time_minutes=30, frequency="weekly", priority="medium")
        task.mark_complete(completed_on=date(2026, 3, 30))

        next_date = task.get_next_occurrence_date()

        assert next_date == date(2026, 4, 6)

    def test_create_next_occurrence_daily(self):
        """Verify that create_next_occurrence() creates a new task for daily recurrence."""
        original = Task(description="Walk", time_minutes=30, frequency="daily", priority="high")
        original.mark_complete(completed_on=date(2026, 3, 30))

        next_task = original.create_next_occurrence()

        assert next_task is not None
        assert next_task.description == "Walk"
        assert next_task.time_minutes == 30
        assert next_task.frequency == "daily"
        assert next_task.priority == "high"
        assert next_task.completed is False
        assert next_task.last_completed_on is None

    def test_create_next_occurrence_none_for_once_tasks(self):
        """Verify that create_next_occurrence() returns None for non-recurring tasks."""
        task = Task(description="Vaccination", time_minutes=15, frequency="once", priority="high")
        task.mark_complete()

        next_task = task.create_next_occurrence()

        assert next_task is None

    def test_automatic_task_generation_on_complete(self):
        """Verify that marking a recurring task complete automatically creates next occurrence."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        owner.add_pet(dog)

        # Add a daily task
        daily_task = Task(description="Morning walk", time_minutes=30, frequency="daily", priority="high")
        dog.add_task(daily_task)

        assert len(dog.tasks) == 1

        # Create scheduler and mark task complete
        scheduler = Scheduler()
        success = scheduler.mark_task_complete(owner, "Buddy", "Morning walk")

        # Verify completion and auto-generation
        assert success is True
        assert len(dog.tasks) == 2  # Original + new occurrence
        assert dog.tasks[0].completed is True  # Original is completed
        assert dog.tasks[1].completed is False  # New occurrence not yet completed
        assert dog.tasks[1].description == "Morning walk"  # Same description
        assert dog.tasks[1].frequency == "daily"  # Same frequency

    def test_no_auto_generation_for_once_tasks(self):
        """Verify that non-recurring tasks don't create next occurrences."""
        owner = Owner(name="Alice")
        cat = Pet(name="Whiskers", species="cat", age=5)
        owner.add_pet(cat)

        # Add a one-time task
        once_task = Task(description="Annual checkup", time_minutes=45, frequency="once", priority="high")
        cat.add_task(once_task)

        assert len(cat.tasks) == 1

        # Mark complete
        scheduler = Scheduler()
        scheduler.mark_task_complete(owner, "Whiskers", "Annual checkup")

        # Verify no new task is created
        assert len(cat.tasks) == 1  # Still only the original
        assert cat.tasks[0].completed is True

    def test_weekly_task_generates_with_correct_interval(self):
        """Verify weekly tasks generate next occurrence 7 days later."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        owner.add_pet(dog)

        # Add a weekly task completed on March 30
        weekly_task = Task(description="Grooming", time_minutes=60, frequency="weekly", priority="medium")
        weekly_task.last_completed_on = date(2026, 3, 23)  # Set previous completion
        dog.add_task(weekly_task)

        # Verify next occurrence is 7 days later
        next_date = weekly_task.get_next_occurrence_date()
        assert next_date == date(2026, 3, 30)


class TestSortingMethods:
    """Test Scheduler sorting algorithms."""

    def test_sort_by_duration_ascending(self):
        """Verify that sort_by_duration() orders tasks from shortest to longest."""
        scheduler = Scheduler()
        
        # Create tasks with different durations
        tasks = [
            (Pet(name="Buddy", species="dog", age=3), Task(description="Walk", time_minutes=30, frequency="daily")),
            (Pet(name="Buddy", species="dog", age=3), Task(description="Feeding", time_minutes=10, frequency="daily")),
            (Pet(name="Buddy", species="dog", age=3), Task(description="Play", time_minutes=40, frequency="daily")),
        ]
        
        # Sort ascending (shortest first)
        sorted_tasks = scheduler.sort_by_duration(tasks, ascending=True)
        
        # Verify order: 10, 30, 40
        assert sorted_tasks[0][1].time_minutes == 10
        assert sorted_tasks[1][1].time_minutes == 30
        assert sorted_tasks[2][1].time_minutes == 40

    def test_sort_by_duration_descending(self):
        """Verify that sort_by_duration(ascending=False) orders longest to shortest."""
        scheduler = Scheduler()
        
        tasks = [
            (Pet(name="Buddy", species="dog", age=3), Task(description="Walk", time_minutes=30, frequency="daily")),
            (Pet(name="Buddy", species="dog", age=3), Task(description="Feeding", time_minutes=10, frequency="daily")),
            (Pet(name="Buddy", species="dog", age=3), Task(description="Play", time_minutes=40, frequency="daily")),
        ]
        
        # Sort descending (longest first)
        sorted_tasks = scheduler.sort_by_duration(tasks, ascending=False)
        
        # Verify order: 40, 30, 10
        assert sorted_tasks[0][1].time_minutes == 40
        assert sorted_tasks[1][1].time_minutes == 30
        assert sorted_tasks[2][1].time_minutes == 10

    def test_sort_by_priority_high_first(self):
        """Verify that sort_by_priority() orders high-priority tasks first."""
        scheduler = Scheduler()
        
        tasks = [
            (Pet(name="Buddy", species="dog", age=3), Task(description="Play", time_minutes=20, frequency="daily", priority="low")),
            (Pet(name="Buddy", species="dog", age=3), Task(description="Walk", time_minutes=30, frequency="daily", priority="high")),
            (Pet(name="Buddy", species="dog", age=3), Task(description="Grooming", time_minutes=45, frequency="weekly", priority="medium")),
        ]
        
        sorted_tasks = scheduler.sort_by_priority(tasks)
        
        # Verify order: high, medium, low
        assert sorted_tasks[0][1].priority == "high"
        assert sorted_tasks[1][1].priority == "medium"
        assert sorted_tasks[2][1].priority == "low"

    def test_sort_by_pet_name_alphabetically(self):
        """Verify that sort_by_pet_name() orders tasks alphabetically by pet name."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        whiskers = Pet(name="Whiskers", species="cat", age=5)
        max_pet = Pet(name="Max", species="dog", age=2)
        
        tasks = [
            (whiskers, Task(description="Feeding", time_minutes=5, frequency="daily")),
            (buddy, Task(description="Walk", time_minutes=30, frequency="daily")),
            (max_pet, Task(description="Play", time_minutes=20, frequency="daily")),
        ]
        
        sorted_tasks = scheduler.sort_by_pet_name(tasks)
        
        # Verify order: Buddy, Max, Whiskers (alphabetical)
        assert sorted_tasks[0][0].name == "Buddy"
        assert sorted_tasks[1][0].name == "Max"
        assert sorted_tasks[2][0].name == "Whiskers"

    def test_sort_by_priority_case_insensitive(self):
        """Verify that sorting works with case-insensitive pet names."""
        scheduler = Scheduler()
        
        buddy_lower = Pet(name="buddy", species="dog", age=3)
        buddy_upper = Pet(name="BUDDY", species="dog", age=3)
        
        tasks = [
            (buddy_upper, Task(description="Walk", time_minutes=30, frequency="daily")),
            (buddy_lower, Task(description="Feeding", time_minutes=10, frequency="daily")),
        ]
        
        sorted_tasks = scheduler.sort_by_pet_name(tasks)
        
        # Both should be grouped together (both "buddy" when lowercased)
        assert len(sorted_tasks) == 2


class TestFilteringMethods:
    """Test Scheduler filtering algorithms."""

    def test_filter_by_pet_single_pet(self):
        """Verify that filter_by_pet() returns only tasks for the specified pet."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        whiskers = Pet(name="Whiskers", species="cat", age=5)
        
        tasks = [
            (buddy, Task(description="Walk", time_minutes=30, frequency="daily")),
            (whiskers, Task(description="Feeding", time_minutes=5, frequency="daily")),
            (buddy, Task(description="Play", time_minutes=20, frequency="daily")),
        ]
        
        # Filter for Buddy's tasks
        buddy_tasks = scheduler.filter_by_pet(tasks, "Buddy")
        
        # Verify only Buddy's tasks returned
        assert len(buddy_tasks) == 2
        assert all(pet.name == "Buddy" for pet, _ in buddy_tasks)
        descriptions = {task.description for _, task in buddy_tasks}
        assert descriptions == {"Walk", "Play"}

    def test_filter_by_pet_case_insensitive(self):
        """Verify that filter_by_pet() is case-insensitive."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        tasks = [(buddy, Task(description="Walk", time_minutes=30, frequency="daily"))]
        
        # Filter with different cases
        result_lower = scheduler.filter_by_pet(tasks, "buddy")
        result_upper = scheduler.filter_by_pet(tasks, "BUDDY")
        
        # Verify both return the same tasks
        assert len(result_lower) == 1
        assert len(result_upper) == 1

    def test_filter_by_priority_high_tasks(self):
        """Verify that filter_by_priority() returns tasks at or above threshold."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        tasks = [
            (buddy, Task(description="Walk", time_minutes=30, frequency="daily", priority="high")),
            (buddy, Task(description="Grooming", time_minutes=45, frequency="weekly", priority="medium")),
            (buddy, Task(description="Play", time_minutes=20, frequency="daily", priority="low")),
        ]
        
        # Filter for high-priority only
        high_priority = scheduler.filter_by_priority(tasks, min_priority="high")
        
        # Verify only high-priority tasks returned
        assert len(high_priority) == 1
        assert high_priority[0][1].priority == "high"

    def test_filter_by_priority_medium_and_high(self):
        """Verify that filter_by_priority(medium) returns medium and high tasks."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        tasks = [
            (buddy, Task(description="Walk", time_minutes=30, frequency="daily", priority="high")),
            (buddy, Task(description="Grooming", time_minutes=45, frequency="weekly", priority="medium")),
            (buddy, Task(description="Play", time_minutes=20, frequency="daily", priority="low")),
        ]
        
        # Filter for medium-priority and above
        medium_and_above = scheduler.filter_by_priority(tasks, min_priority="medium")
        
        # Verify medium and high returned, low excluded
        assert len(medium_and_above) == 2
        priorities = {task.priority for _, task in medium_and_above}
        assert priorities == {"high", "medium"}

    def test_filter_by_completion_status_pending(self):
        """Verify that filter_by_completion_status() returns pending tasks when completed=False."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        task1 = Task(description="Walk", time_minutes=30, frequency="daily")
        task2 = Task(description="Feeding", time_minutes=10, frequency="daily")
        task2.mark_complete()
        
        tasks = [
            (buddy, task1),
            (buddy, task2),
        ]
        
        # Filter for pending tasks
        pending = scheduler.filter_by_completion_status(tasks, completed=False)
        
        # Verify only pending tasks returned
        assert len(pending) == 1
        assert pending[0][1].description == "Walk"

    def test_filter_by_completion_status_completed(self):
        """Verify that filter_by_completion_status() returns completed tasks when completed=True."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        task1 = Task(description="Walk", time_minutes=30, frequency="daily")
        task2 = Task(description="Feeding", time_minutes=10, frequency="daily")
        task2.mark_complete()
        
        tasks = [
            (buddy, task1),
            (buddy, task2),
        ]
        
        # Filter for completed tasks
        completed = scheduler.filter_by_completion_status(tasks, completed=True)
        
        # Verify only completed tasks returned
        assert len(completed) == 1
        assert completed[0][1].description == "Feeding"

    def test_chaining_filters_pet_then_priority(self):
        """Verify that filters can be chained effectively."""
        scheduler = Scheduler()
        
        buddy = Pet(name="Buddy", species="dog", age=3)
        whiskers = Pet(name="Whiskers", species="cat", age=5)
        
        tasks = [
            (buddy, Task(description="Walk", time_minutes=30, frequency="daily", priority="high")),
            (whiskers, Task(description="Feeding", time_minutes=5, frequency="daily", priority="high")),
            (buddy, Task(description="Play", time_minutes=20, frequency="daily", priority="low")),
        ]
        
        # Chain filters: get Buddy's high-priority tasks
        buddy_tasks = scheduler.filter_by_pet(tasks, "Buddy")
        buddy_high = scheduler.filter_by_priority(buddy_tasks, min_priority="high")
        
        # Verify result
        assert len(buddy_high) == 1
        assert buddy_high[0][0].name == "Buddy"
        assert buddy_high[0][1].priority == "high"


class TestConflictDetection:
    """Test Scheduler conflict detection."""

    def test_detect_pet_overwhelm_three_high_priority(self):
        """Verify that detect_conflicts() warns when a pet has 3+ high-priority tasks."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        
        dog.add_task(Task(description="Walk 1", time_minutes=30, frequency="daily", priority="high"))
        dog.add_task(Task(description="Walk 2", time_minutes=30, frequency="daily", priority="high"))
        dog.add_task(Task(description="Feeding", time_minutes=10, frequency="daily", priority="high"))
        
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=180)
        warnings = scheduler.detect_conflicts(plan)
        
        # Verify overwhelm warning is generated
        assert len(warnings) > 0
        assert any("overwhelm" in w.lower() for w in warnings)

    def test_detect_no_overwhelm_two_tasks_total(self):
        """Verify that no overwhelm warning when pet has only 2 total tasks."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        
        dog.add_task(Task(description="Walk", time_minutes=30, frequency="daily", priority="high"))
        dog.add_task(Task(description="Feeding", time_minutes=10, frequency="daily", priority="high"))
        
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=180)
        warnings = scheduler.detect_conflicts(plan)
        
        # Verify no overwhelm warning (only 2 tasks total)
        assert not any("overwhelm" in w.lower() for w in warnings)

    def test_detect_energy_missequencing(self):
        """Verify that detect_conflicts() warns about high-energy followed by grooming."""
        owner = Owner(name="Alice")
        dog = Pet(name="Max", species="dog", age=5)
        
        dog.add_task(Task(description="Playtime", time_minutes=40, frequency="daily", priority="high"))
        dog.add_task(Task(description="Grooming", time_minutes=45, frequency="daily", priority="high"))
        
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=150)
        warnings = scheduler.detect_conflicts(plan)
        
        # Verify energy missequencing warning
        assert len(warnings) > 0
        assert any("energetic" in w.lower() for w in warnings)

    def test_detect_back_to_back_high_energy_over_60_min(self):
        """Verify that detect_conflicts() warns about back-to-back high-energy tasks >60 min."""
        owner = Owner(name="Alice")
        dog = Pet(name="Max", species="dog", age=5)
        
        dog.add_task(Task(description="Walk", time_minutes=35, frequency="daily", priority="high"))
        dog.add_task(Task(description="Playtime", time_minutes=35, frequency="daily", priority="high"))
        
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=180)
        warnings = scheduler.detect_conflicts(plan)
        
        # Verify back-to-back high-energy warning
        assert len(warnings) > 0
        assert any("back-to-back" in w.lower() for w in warnings)

    def test_no_warning_for_back_to_back_under_60_min(self):
        """Verify no warning when back-to-back high-energy tasks total less than 60 min."""
        owner = Owner(name="Alice")
        dog = Pet(name="Max", species="dog", age=5)
        
        dog.add_task(Task(description="Walk", time_minutes=25, frequency="daily", priority="high"))
        dog.add_task(Task(description="Playtime", time_minutes=30, frequency="daily", priority="high"))
        
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=180)
        warnings = scheduler.detect_conflicts(plan)
        
        # Verify no back-to-back warning (55 min total < 60)
        assert not any("back-to-back" in w.lower() for w in warnings)

    def test_detect_time_overrun_over_180_minutes(self):
        """Verify that detect_conflicts() warns when total time exceeds 180 minutes."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        
        dog.add_task(Task(description="Walk 1", time_minutes=60, frequency="daily", priority="high"))
        dog.add_task(Task(description="Walk 2", time_minutes=60, frequency="daily", priority="high"))
        dog.add_task(Task(description="Play", time_minutes=61, frequency="daily", priority="medium"))
        
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=500)
        warnings = scheduler.detect_conflicts(plan)
        
        # Verify time overrun warning
        assert len(warnings) > 0
        assert any("exhausting" in w.lower() or "info" in w.lower() for w in warnings)

    def test_no_warning_for_empty_plan(self):
        """Verify that detect_conflicts() handles empty plans without crashing."""
        scheduler = Scheduler()
        warnings = scheduler.detect_conflicts([])
        
        # Should return empty list without errors
        assert warnings == []

    def test_validate_plan_returns_plan_and_warnings(self):
        """Verify that validate_plan() returns both plan and warnings."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        dog.add_task(Task(description="Walk", time_minutes=30, frequency="daily", priority="high"))
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=60)
        validated_plan, warnings = scheduler.validate_plan(plan, available_minutes=60)
        
        # Verify return structure
        assert isinstance(validated_plan, list)
        assert isinstance(warnings, list)
        assert validated_plan == plan  # Plan should be unchanged


class TestScheduler:
    """Test Scheduler functionality."""

    def test_build_daily_plan_respects_time_limit(self):
        """Verify that build_daily_plan respects available_minutes constraint."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        
        # Add tasks totaling more than available time
        dog.add_task(Task(description="Walk", time_minutes=30, frequency="daily", priority="high"))
        dog.add_task(Task(description="Feeding", time_minutes=20, frequency="daily", priority="high"))
        dog.add_task(Task(description="Play", time_minutes=25, frequency="daily", priority="medium"))
        
        owner.add_pet(dog)
        
        # Build plan with only 50 minutes available
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=50)
        
        # Verify plan respects time limit
        total_time = sum(task.time_minutes for _, task in plan)
        assert total_time <= 50
        
        # Verify high-priority tasks are included
        plan_descriptions = {task.description for _, task in plan}
        assert "Walk" in plan_descriptions
        assert "Feeding" in plan_descriptions

    def test_plan_summary_generates_readable_output(self):
        """Verify that plan_summary() generates readable output."""
        owner = Owner(name="Alice")
        dog = Pet(name="Buddy", species="dog", age=3)
        dog.add_task(Task(description="Walk", time_minutes=30, frequency="daily", priority="high"))
        owner.add_pet(dog)
        
        scheduler = Scheduler()
        plan = scheduler.build_daily_plan(owner, available_minutes=60)
        summary = scheduler.plan_summary(plan)
        
        # Verify summary contains expected content
        assert "Daily plan:" in summary
        assert "Buddy" in summary
        assert "Walk" in summary
        assert "Total scheduled time:" in summary
