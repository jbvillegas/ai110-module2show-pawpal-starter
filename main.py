"""Demo script to test PawPal+ logic layer with sorting and filtering."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    """Create sample data and demonstrate sorting, filtering, and conflict detection."""
    # Create owner
    owner = Owner(name="Alice")

    # Create pets
    dog = Pet(name="Buddy", species="dog", age=3)
    cat = Pet(name="Whiskers", species="cat", age=5)

    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Add tasks OUT OF ORDER to demonstrate sorting
    print("\n" + "="*60)
    print("Adding tasks OUT OF ORDER to test sorting...")
    print("="*60 + "\n")

    # Dog tasks (intentionally added in mixed order)
    dog.add_task(Task(description="Playtime", time_minutes=20, frequency="daily", priority="medium"))
    dog.add_task(Task(description="Morning walk", time_minutes=30, frequency="daily", priority="high"))
    dog.add_task(Task(description="Feeding", time_minutes=10, frequency="daily", priority="high"))

    # Cat tasks (mixed order)
    cat.add_task(Task(description="Grooming", time_minutes=15, frequency="weekly", priority="low"))
    cat.add_task(Task(description="Feeding", time_minutes=5, frequency="daily", priority="high"))
    cat.add_task(Task(description="Litter box cleaning", time_minutes=10, frequency="daily", priority="high"))

    # Create scheduler
    scheduler = Scheduler()

    # Get all tasks
    all_tasks = owner.get_all_tasks(include_completed=False)

    print("📋 ALL TASKS (as added - unsorted):")
    print("-" * 60)
    for i, (pet, task) in enumerate(all_tasks, 1):
        status = "✓" if task.completed else "○"
        print(f"{i}. {status} [{pet.name}] {task.description} ({task.time_minutes}m, {task.priority} priority)")
    
    # SORTING DEMONSTRATIONS
    print("\n" + "="*60)
    print("SORTING DEMONSTRATIONS")
    print("="*60)

    # 1. Sort by duration (ascending)
    print("\n⏱️  SORTED BY DURATION (shortest first):")
    print("-" * 60)
    sorted_by_duration = scheduler.sort_by_duration(all_tasks, ascending=True)
    for i, (pet, task) in enumerate(sorted_by_duration, 1):
        print(f"{i}. [{pet.name}] {task.description} ({task.time_minutes}m)")

    # 2. Sort by priority (high first)
    print("\n🔴 SORTED BY PRIORITY (high → low):")
    print("-" * 60)
    sorted_by_priority = scheduler.sort_by_priority(all_tasks)
    for i, (pet, task) in enumerate(sorted_by_priority, 1):
        priority_emoji = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
        print(f"{i}. [{pet.name}] {task.description} ({task.priority} priority)")

    # 3. Sort by pet name
    print("\n🐾 SORTED BY PET NAME:")
    print("-" * 60)
    sorted_by_pet = scheduler.sort_by_pet_name(all_tasks)
    for i, (pet, task) in enumerate(sorted_by_pet, 1):
        print(f"{i}. [{pet.name}] {task.description}")

    # FILTERING DEMONSTRATIONS
    print("\n" + "="*60)
    print("FILTERING DEMONSTRATIONS")
    print("="*60)

    # 1. Filter by pet name
    print("\n🐕 TASKS FOR 'Buddy' ONLY:")
    print("-" * 60)
    buddy_tasks = scheduler.filter_by_pet(all_tasks, "Buddy")
    if buddy_tasks:
        for i, (pet, task) in enumerate(buddy_tasks, 1):
            print(f"{i}. {task.description} ({task.time_minutes}m, {task.priority} priority)")
    else:
        print("No tasks found for Buddy")

    # 2. Filter by priority (high only)
    print("\n🔴 HIGH PRIORITY TASKS ONLY:")
    print("-" * 60)
    high_priority_tasks = scheduler.filter_by_priority(all_tasks, min_priority="high")
    for i, (pet, task) in enumerate(high_priority_tasks, 1):
        print(f"{i}. [{pet.name}] {task.description} ({task.time_minutes}m)")

    # 3. Mark a task complete and filter by status
    print("\n✓ MARKING 'Morning walk' AS COMPLETE:")
    print("-" * 60)
    buddy = owner.get_pet("Buddy")
    for task in buddy.tasks:
        if task.description == "Morning walk":
            task.mark_complete()
            print(f"✓ Marked '{task.description}' as complete")
            break

    # Filter pending tasks
    print("\n⏳ PENDING TASKS (not yet completed):")
    print("-" * 60)
    pending_tasks = scheduler.filter_by_completion_status(all_tasks, completed=False)
    for i, (pet, task) in enumerate(pending_tasks, 1):
        print(f"{i}. [{pet.name}] {task.description}")

    # Filter completed tasks
    print("\n✓ COMPLETED TASKS:")
    print("-" * 60)
    completed_tasks = scheduler.filter_by_completion_status(all_tasks, completed=True)
    if completed_tasks:
        for i, (pet, task) in enumerate(completed_tasks, 1):
            print(f"{i}. [{pet.name}] {task.description} (completed on {task.last_completed_on})")
    else:
        print("No completed tasks yet")

    # CHAINING FILTERS & SORTS
    print("\n" + "="*60)
    print("CHAINING FILTERS & SORTS")
    print("="*60)

    print("\n🐕 HIGH PRIORITY BUDDY TASKS (sorted by duration):")
    print("-" * 60)
    buddy_high_priority = scheduler.filter_by_pet(all_tasks, "Buddy")
    buddy_high_priority = scheduler.filter_by_priority(buddy_high_priority, "high")
    buddy_high_priority = scheduler.sort_by_duration(buddy_high_priority, ascending=False)
    for i, (pet, task) in enumerate(buddy_high_priority, 1):
        print(f"{i}. {task.description} ({task.time_minutes}m)")

    # BUILD SCHEDULE WITH NEW TOOLS
    print("\n" + "="*60)
    print("DAILY SCHEDULE (using all 90 minutes)")
    print("="*60 + "\n")

    available_time = 90
    plan = scheduler.build_daily_plan(owner, available_minutes=available_time)
    print(scheduler.plan_summary(plan))

    # CONFLICT DETECTION DEMONSTRATION
    print("\n" + "="*60)
    print("CONFLICT DETECTION")
    print("="*60)

    # Check for conflicts in the current plan
    warnings = scheduler.detect_conflicts(plan)
    if warnings:
        print("\n⚠️  SCHEDULING WARNINGS DETECTED:")
        print("-" * 60)
        for warning in warnings:
            print(warning)
    else:
        print("\n✓ No scheduling conflicts detected!")

    # Create a problematic schedule to demonstrate conflict detection
    print("\n" + "="*60)
    print("PROBLEMATIC SCHEDULE EXAMPLE")
    print("="*60)

    print("\n🔨 Creating a schedule with intentional conflicts...")
    print("-" * 60)

    # Create a new owner with a dog that has conflicting tasks
    owner2 = Owner(name="Bob")
    dog2 = Pet(name="Max", species="dog", age=5)
    owner2.add_pet(dog2)

    # Add tasks that will create conflicts
    dog2.add_task(Task(description="Morning walk", time_minutes=30, frequency="daily", priority="high"))
    dog2.add_task(Task(description="Playtime", time_minutes=40, frequency="daily", priority="high"))
    dog2.add_task(Task(description="Grooming", time_minutes=45, frequency="daily", priority="high"))

    # Build and validate plan
    conflict_plan = scheduler.build_daily_plan(owner2, available_minutes=150)
    print("\n📋 Problematic Plan for Max:")
    print("-" * 60)
    print(scheduler.plan_summary(conflict_plan))

    # Check for conflicts
    conflict_warnings = scheduler.detect_conflicts(conflict_plan)
    if conflict_warnings:
        print("\n⚠️  SCHEDULING CONFLICTS DETECTED:")
        print("-" * 60)
        for warning in conflict_warnings:
            print(warning)
    else:
        print("\n✓ No scheduling conflicts detected!")

    # RECURRING TASK DEMONSTRATION
    print("\n" + "="*60)
    print("RECURRING TASK AUTOMATION")
    print("="*60)

    print(f"\n📋 BUDDY'S TASKS BEFORE MARKING 'Morning walk' COMPLETE:")
    print("-" * 60)
    buddy = owner.get_pet("Buddy")
    for i, task in enumerate(buddy.tasks, 1):
        status = "✓" if task.completed else "○"
        freq = f" (next due: {task.get_next_occurrence_date()})" if task.completed and task.frequency != "once" else ""
        print(f"{i}. {status} {task.description}{freq}")

    print(f"\nTotal tasks for Buddy: {len(buddy.tasks)}")

    print(f"\n✓ MARKING A NEW DAILY TASK AS COMPLETE:")
    print("-" * 60)
    scheduler.mark_task_complete(owner, "Buddy", "Feeding")
    print(f"✓ Marked 'Feeding' as complete and generated next occurrence!")

    print(f"\n📋 BUDDY'S TASKS AFTER MARKING 'Feeding' COMPLETE:")
    print("-" * 60)
    for i, task in enumerate(buddy.tasks, 1):
        status = "✓" if task.completed else "○"
        next_info = f" → repeats on {task.get_next_occurrence_date()}" if task.frequency != "once" else ""
        print(f"{i}. {status} {task.description}{next_info}")

    print(f"\nTotal tasks for Buddy: {len(buddy.tasks)}")

    print("\n💡 RECURRING TASK BEHAVIOR:")
    print("-" * 60)
    print("✓ Daily tasks: Auto-generate next occurrence 1 day after completion")
    print("✓ Weekly tasks: Auto-generate next occurrence 7 days after completion")
    print("✓ One-time tasks: Do NOT generate next occurrence (stay completed)")
    print("✓ All recurring properties (time, priority, category) copied to new instance")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
