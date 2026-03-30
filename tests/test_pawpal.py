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
