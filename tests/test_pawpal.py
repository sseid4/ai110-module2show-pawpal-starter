from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import CareTask, Owner, Pet, Scheduler


def test_task_completion_changes_status() -> None:
    task = CareTask(
        task_id="task_001",
        pet_id="pet_001",
        title="Give medication",
        category="medication",
        duration_minutes=10,
        priority=1,
        due_date=date.today(),
        preferred_window="morning",
    )

    assert task.status == "pending"

    task.mark_complete()

    assert task.status == "done"


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(
        pet_id="pet_001",
        name="Buddy",
        species="Dog",
        age=3,
        energy_level="high",
        medical_notes="",
    )

    initial_count = len(pet.list_tasks())

    task = CareTask(
        task_id="task_002",
        pet_id="pet_001",
        title="Morning walk",
        category="exercise",
        duration_minutes=20,
        priority=2,
        due_date=date.today(),
        preferred_window="morning",
    )
    pet.add_task(task)

    assert len(pet.list_tasks()) == initial_count + 1


def test_scheduler_generates_plan_with_due_tasks() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_001",
        name="Casey",
        available_minutes_per_day=60,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_001",
        name="Luna",
        species="Cat",
        age=2,
        energy_level="medium",
        medical_notes="",
    )

    due_today = CareTask(
        task_id="task_101",
        pet_id=pet.pet_id,
        title="Feed",
        category="feeding",
        duration_minutes=15,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    not_due = CareTask(
        task_id="task_102",
        pet_id=pet.pet_id,
        title="Nail trim",
        category="hygiene",
        duration_minutes=10,
        priority=2,
        due_date=today + timedelta(days=1),
        preferred_window="evening",
    )

    pet.add_task(due_today)
    pet.add_task(not_due)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan(today)

    assert len(plan.scheduled_items) == 1
    assert plan.scheduled_items[0][0].task_id == "task_101"
    assert plan.total_scheduled_minutes == 15
    assert len(plan.unscheduled_tasks) == 0


def test_scheduler_prioritizes_overdue_then_priority_then_duration() -> None:
    today = date.today()
    yesterday = today - timedelta(days=1)

    owner = Owner(
        owner_id="owner_002",
        name="Jordan",
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon"],
    )
    pet = Pet(
        pet_id="pet_002",
        name="Buddy",
        species="Dog",
        age=4,
        energy_level="high",
        medical_notes="",
    )

    overdue = CareTask(
        task_id="task_201",
        pet_id=pet.pet_id,
        title="Overdue walk",
        category="exercise",
        duration_minutes=20,
        priority=3,
        due_date=yesterday,
        preferred_window="morning",
    )
    due_short = CareTask(
        task_id="task_202",
        pet_id=pet.pet_id,
        title="Medication",
        category="medication",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    due_long = CareTask(
        task_id="task_203",
        pet_id=pet.pet_id,
        title="Feeding prep",
        category="feeding",
        duration_minutes=15,
        priority=1,
        due_date=today,
        preferred_window="afternoon",
    )

    pet.add_task(overdue)
    pet.add_task(due_long)
    pet.add_task(due_short)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan(today)
    ordered_ids = [task.task_id for task, _slot in plan.scheduled_items]

    assert ordered_ids == ["task_201", "task_202", "task_203"]


def test_scheduler_marks_unscheduled_when_over_capacity() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_003",
        name="Riley",
        available_minutes_per_day=25,
        preferred_time_blocks=["morning", "evening"],
    )
    pet = Pet(
        pet_id="pet_003",
        name="Charlie",
        species="Hamster",
        age=1,
        energy_level="medium",
        medical_notes="",
    )

    task_a = CareTask(
        task_id="task_301",
        pet_id=pet.pet_id,
        title="Feed",
        category="feeding",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    task_b = CareTask(
        task_id="task_302",
        pet_id=pet.pet_id,
        title="Clean habitat",
        category="hygiene",
        duration_minutes=20,
        priority=2,
        due_date=today,
        preferred_window="evening",
    )

    pet.add_task(task_a)
    pet.add_task(task_b)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan(today)

    scheduled_ids = [task.task_id for task, _slot in plan.scheduled_items]
    unscheduled_ids = [task.task_id for task in plan.unscheduled_tasks]

    assert scheduled_ids == ["task_301"]
    assert unscheduled_ids == ["task_302"]
    assert plan.total_scheduled_minutes == 10

    analysis = scheduler.get_conflict_analysis(today)
    assert analysis["has_conflict"] is True
    assert analysis["excess_minutes"] == 5
