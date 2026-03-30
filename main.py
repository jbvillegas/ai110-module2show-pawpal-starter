"""Demo script to test PawPal+ logic layer."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    """Create sample data and generate a daily schedule."""
    # Create owner
    owner = Owner(name="Alice")

    # Create pets
    dog = Pet(name="Buddy", species="dog", age=3)
    cat = Pet(name="Whiskers", species="cat", age=5)

    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Add tasks to dog
    dog.add_task(Task(description="Morning walk", time_minutes=30, frequency="daily", priority="high"))
    dog.add_task(Task(description="Feeding", time_minutes=10, frequency="daily", priority="high"))
    dog.add_task(Task(description="Playtime", time_minutes=20, frequency="daily", priority="medium"))

    # Add tasks to cat
    cat.add_task(Task(description="Feeding", time_minutes=5, frequency="daily", priority="high"))
    cat.add_task(Task(description="Litter box cleaning", time_minutes=10, frequency="daily", priority="high"))
    cat.add_task(Task(description="Grooming", time_minutes=15, frequency="weekly", priority="low"))

    # Create scheduler
    scheduler = Scheduler()

    # Build a daily plan with 90 minutes available
    available_time = 90
    plan = scheduler.build_daily_plan(owner, available_minutes=available_time)

    # Print the schedule
    print(f"\n{'='*60}")
    print(f"Today's Schedule for {owner.name}")
    print(f"Available time: {available_time} minutes")
    print(f"{'='*60}\n")

    if plan:
        print(scheduler.plan_summary(plan))
        
        # Additional breakdown
        print(f"\n{'Tasks in this plan:':^60}")
        print("-" * 60)
        for i, (pet, task) in enumerate(plan, 1):
            print(f"{i}. [{pet.name}] {task.description}")
            print(f"   Time: {task.time_minutes} min | Priority: {task.priority} | Frequency: {task.frequency}")
    else:
        print("No tasks could fit in the available time.")

    # Check if any tasks were skipped
    included_descriptions = {task.description for _, task in plan}
    skipped = [
        (pet, task)
        for pet, task in owner.get_all_tasks(include_completed=False)
        if task.is_due() and task.description not in included_descriptions
    ]

    if skipped:
        print(f"\n{'Skipped tasks (no time remaining):':^60}")
        print("-" * 60)
        for pet, task in skipped:
            print(f"• [{pet.name}] {task.description} ({task.time_minutes} min, {task.priority} priority)")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
