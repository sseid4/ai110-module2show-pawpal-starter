"""
PawPal System - Today's Schedule Generator
Demonstrates creating an owner with pets and tasks, then generating today's schedule
"""

from datetime import date
from pawpal_system import CareTask, Pet, Owner, Scheduler


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def main():
    """Main script: Create owner and pets, add tasks, print today's schedule."""

    # Step 1: Create an Owner
    print_section("CREATING OWNER")
    owner = Owner(
        owner_id="owner_001",
        name="John Smith",
        available_minutes_per_day=240,
        preferred_time_blocks=["morning", "afternoon", "evening"],
        email="john.smith@example.com",
        phone="555-0123",
    )
    print(f"\n✓ Owner created: {owner.name}")
    print(f"  - Available time per day: {owner.available_minutes_per_day} minutes")
    print(f"  - Email: {owner.email}")
    print(f"  - Preferred time blocks: {', '.join(owner.preferred_time_blocks)}")

    # Step 2: Create at least two Pets
    print_section("CREATING PETS")

    pet1 = Pet(
        pet_id="pet_001",
        name="Buddy",
        species="Golden Retriever",
        age=4,
        energy_level="high",
        medical_notes="Needs regular walks due to high energy",
    )

    pet2 = Pet(
        pet_id="pet_002",
        name="Luna",
        species="Cat",
        age=2,
        energy_level="medium",
        medical_notes="Takes medication for thyroid",
    )

    pet3 = Pet(
        pet_id="pet_003",
        name="Charlie",
        species="Hamster",
        age=1,
        energy_level="high",
        medical_notes="Nocturnal, prefers evening handling",
    )

    owner.add_pet(pet1)
    owner.add_pet(pet2)
    owner.add_pet(pet3)

    print(f"\n✓ Pets created and added to owner:")
    for pet in owner.pets:
        print(f"  - {pet.name} ({pet.species}), age {pet.age}, energy: {pet.energy_level}")

    # Step 3: Add at least three Tasks with different times to pets
    print_section("ADDING TASKS")

    today = date.today()

    # Buddy's tasks
    task1 = CareTask(
        task_id="task_001",
        pet_id="pet_001",
        title="Morning walk",
        category="exercise",
        duration_minutes=45,
        priority=1,
        due_date=today,
        preferred_window="morning",
        frequency="daily",
    )
    pet1.add_task(task1)

    task2 = CareTask(
        task_id="task_002",
        pet_id="pet_001",
        title="Feed Buddy",
        category="feeding",
        duration_minutes=15,
        priority=1,
        due_date=today,
        preferred_window="afternoon",
        frequency="daily",
    )
    pet1.add_task(task2)

    # Luna's tasks
    task3 = CareTask(
        task_id="task_003",
        pet_id="pet_002",
        title="Medication - Morning",
        category="medication",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
        frequency="daily",
    )
    pet2.add_task(task3)

    task4 = CareTask(
        task_id="task_004",
        pet_id="pet_002",
        title="Feed Luna",
        category="feeding",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="evening",
        frequency="daily",
    )
    pet2.add_task(task4)

    task5 = CareTask(
        task_id="task_005",
        pet_id="pet_002",
        title="Clean litter box",
        category="hygiene",
        duration_minutes=20,
        priority=2,
        due_date=today,
        preferred_window="afternoon",
        frequency="daily",
    )
    pet2.add_task(task5)

    # Charlie's tasks
    task6 = CareTask(
        task_id="task_006",
        pet_id="pet_003",
        title="Clean cage",
        category="hygiene",
        duration_minutes=30,
        priority=2,
        due_date=today,
        preferred_window="morning",
        frequency="weekly",
    )
    pet3.add_task(task6)

    task7 = CareTask(
        task_id="task_007",
        pet_id="pet_003",
        title="Feed Charlie",
        category="feeding",
        duration_minutes=5,
        priority=1,
        due_date=today,
        preferred_window="evening",
        frequency="daily",
    )
    pet3.add_task(task7)

    print(f"\n✓ Tasks created and added:")
    print(f"\n  {pet1.name}'s tasks:")
    for task in pet1.list_tasks():
        print(f"    - {task.title} ({task.category}) - {task.duration_minutes}min | {task.preferred_window}")

    print(f"\n  {pet2.name}'s tasks:")
    for task in pet2.list_tasks():
        print(f"    - {task.title} ({task.category}) - {task.duration_minutes}min | {task.preferred_window}")

    print(f"\n  {pet3.name}'s tasks:")
    for task in pet3.list_tasks():
        print(f"    - {task.title} ({task.category}) - {task.duration_minutes}min | {task.preferred_window}")

    # Step 4: Create Scheduler and generate Today's Schedule
    print_section("TODAY'S SCHEDULE")

    scheduler = Scheduler(owner=owner)
    scheduler.sync_pets()

    # Generate the daily plan
    daily_plan = scheduler.generate_plan(today)

    # Print today's schedule
    print(scheduler.get_schedule_summary(daily_plan))

    # Print additional analysis
    print_section("SCHEDULE ANALYSIS")

    conflict_analysis = scheduler.get_conflict_analysis(today)
    print(f"\n✓ Schedule Feasibility Analysis:")
    print(f"  - Total tasks today: {conflict_analysis['tasks_due']}")
    print(f"  - Total time needed: {conflict_analysis['total_minutes_needed']} minutes")
    print(f"  - Available time: {conflict_analysis['available_minutes']} minutes")
    print(f"  - Time utilization: {conflict_analysis['utilization_rate']:.1%}")
    print(f"  - Schedule is feasible: {'✓ YES' if not conflict_analysis['has_conflict'] else '✗ NO'}")

    if conflict_analysis['has_conflict']:
        print(f"  - WARNING: Need {conflict_analysis['excess_minutes']} more minutes!")

    # Print task breakdown by pet
    print(f"\n✓ Tasks by Pet:")
    for pet in owner.pets:
        pending = pet.get_pending_tasks()
        print(f"  - {pet.name}: {len(pending)} tasks pending")

    # Print critical tasks
    critical_tasks = scheduler.get_critical_path_tasks()
    print(f"\n✓ High-Priority Tasks (P1):")
    for task in critical_tasks:
        pet = owner.get_pet(task.pet_id)
        pet_name = pet.name if pet else "Unknown"
        print(f"  - {task.title} ({pet_name}) - {task.duration_minutes}min")

    print_section("SCHEDULE GENERATION COMPLETE")


if __name__ == "__main__":
    main()
