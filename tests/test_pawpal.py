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
