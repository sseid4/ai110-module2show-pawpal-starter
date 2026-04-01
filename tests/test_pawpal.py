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


def test_prioritize_tasks_returns_chronological_order_for_non_overdue_tasks() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_012",
        name="Sky",
        available_minutes_per_day=180,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_014",
        name="Olive",
        species="Dog",
        age=5,
        energy_level="medium",
        medical_notes="",
    )

    due_in_three_days = CareTask(
        task_id="task_1201",
        pet_id=pet.pet_id,
        title="Nail trim",
        category="hygiene",
        duration_minutes=10,
        priority=2,
        due_date=today + timedelta(days=3),
        preferred_window="morning",
    )
    due_tomorrow = CareTask(
        task_id="task_1202",
        pet_id=pet.pet_id,
        title="Brush coat",
        category="hygiene",
        duration_minutes=10,
        priority=2,
        due_date=today + timedelta(days=1),
        preferred_window="morning",
    )
    due_in_two_days = CareTask(
        task_id="task_1203",
        pet_id=pet.pet_id,
        title="Ear cleaning",
        category="hygiene",
        duration_minutes=10,
        priority=2,
        due_date=today + timedelta(days=2),
        preferred_window="morning",
    )

    pet.add_task(due_in_three_days)
    pet.add_task(due_tomorrow)
    pet.add_task(due_in_two_days)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    ordered = scheduler.prioritize_tasks(
        [due_in_three_days, due_tomorrow, due_in_two_days],
        plan_date=today,
    )

    assert [task.task_id for task in ordered] == ["task_1202", "task_1203", "task_1201"]


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


def test_scheduler_deduplicates_task_list_when_overdue_and_due_today_overlap() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_004",
        name="Alex",
        available_minutes_per_day=60,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_004",
        name="Milo",
        species="Dog",
        age=5,
        energy_level="high",
        medical_notes="",
    )

    task = CareTask(
        task_id="task_401",
        pet_id=pet.pet_id,
        title="Walk",
        category="exercise",
        duration_minutes=20,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )

    pet.add_task(task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan(today)

    assert len(plan.scheduled_items) == 1
    assert plan.total_scheduled_minutes == 20


def test_scheduler_respects_preferred_window_when_capacity_allows() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_005",
        name="Sam",
        available_minutes_per_day=90,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_005",
        name="Nova",
        species="Cat",
        age=3,
        energy_level="medium",
        medical_notes="",
    )

    morning_task = CareTask(
        task_id="task_501",
        pet_id=pet.pet_id,
        title="Medication",
        category="medication",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    evening_task = CareTask(
        task_id="task_502",
        pet_id=pet.pet_id,
        title="Play time",
        category="exercise",
        duration_minutes=10,
        priority=2,
        due_date=today,
        preferred_window="evening",
    )

    pet.add_task(morning_task)
    pet.add_task(evening_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan(today)

    slot_by_task_id = {task.task_id: slot for task, slot in plan.scheduled_items}
    assert slot_by_task_id["task_501"] == "morning"
    assert slot_by_task_id["task_502"] == "evening"


def test_scheduler_can_filter_tasks_by_pet_status_and_date() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_006",
        name="Taylor",
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet_a = Pet(
        pet_id="pet_006",
        name="Ruby",
        species="Dog",
        age=2,
        energy_level="high",
        medical_notes="",
    )
    pet_b = Pet(
        pet_id="pet_007",
        name="Pip",
        species="Cat",
        age=4,
        energy_level="low",
        medical_notes="",
    )

    a_task = CareTask(
        task_id="task_601",
        pet_id=pet_a.pet_id,
        title="Feed Ruby",
        category="feeding",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    b_task = CareTask(
        task_id="task_602",
        pet_id=pet_b.pet_id,
        title="Feed Pip",
        category="feeding",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="evening",
        status="done",
    )

    pet_a.add_task(a_task)
    pet_b.add_task(b_task)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    scheduler = Scheduler(owner=owner)
    filtered = scheduler.get_filtered_tasks(
        pet_id=pet_a.pet_id,
        status="pending",
        plan_date=today,
    )

    assert [task.task_id for task in filtered] == ["task_601"]


def test_marking_recurring_task_complete_rolls_due_date_forward() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_007",
        name="Morgan",
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_008",
        name="Bean",
        species="Dog",
        age=1,
        energy_level="high",
        medical_notes="",
    )

    recurring_task = CareTask(
        task_id="task_701",
        pet_id=pet.pet_id,
        title="Daily walk",
        category="exercise",
        duration_minutes=20,
        priority=1,
        due_date=today,
        preferred_window="morning",
        frequency="daily",
    )

    pet.add_task(recurring_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    success = scheduler.mark_task_complete("task_701")

    assert success is True
    assert recurring_task.status == "done"
    assert recurring_task.completed_date == today

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 2

    next_task = [t for t in all_tasks if t.task_id != "task_701"][0]
    assert next_task.status == "pending"
    assert next_task.frequency == "daily"
    assert next_task.due_date == today + timedelta(days=1)


def test_marking_weekly_recurring_task_creates_next_week_instance() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_009",
        name="Avery",
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_010",
        name="Mochi",
        species="Rabbit",
        age=2,
        energy_level="medium",
        medical_notes="",
    )

    recurring_task = CareTask(
        task_id="task_901",
        pet_id=pet.pet_id,
        title="Cage deep clean",
        category="hygiene",
        duration_minutes=25,
        priority=2,
        due_date=today,
        preferred_window="afternoon",
        frequency="weekly",
    )

    pet.add_task(recurring_task)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    success = scheduler.mark_task_complete("task_901")

    assert success is True
    assert recurring_task.status == "done"
    assert recurring_task.completed_date == today

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 2

    next_task = [t for t in all_tasks if t.task_id != "task_901"][0]
    assert next_task.status == "pending"
    assert next_task.frequency == "weekly"
    assert next_task.due_date == today + timedelta(days=7)


def test_conflict_analysis_reports_window_overload() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_008",
        name="Jamie",
        available_minutes_per_day=90,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_009",
        name="Skye",
        species="Cat",
        age=6,
        energy_level="medium",
        medical_notes="",
    )

    # Total daily minutes fit, but morning load should exceed the morning block.
    morning_a = CareTask(
        task_id="task_801",
        pet_id=pet.pet_id,
        title="Morning feed",
        category="feeding",
        duration_minutes=20,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    morning_b = CareTask(
        task_id="task_802",
        pet_id=pet.pet_id,
        title="Morning meds",
        category="medication",
        duration_minutes=15,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    evening = CareTask(
        task_id="task_803",
        pet_id=pet.pet_id,
        title="Evening play",
        category="exercise",
        duration_minutes=5,
        priority=2,
        due_date=today,
        preferred_window="evening",
    )

    pet.add_task(morning_a)
    pet.add_task(morning_b)
    pet.add_task(evening)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    analysis = scheduler.get_conflict_analysis(today)

    assert analysis["has_window_conflict"] is True
    assert analysis["has_conflict"] is True
    assert analysis["window_conflicts"]["morning"] == 5


def test_detect_task_conflicts_returns_same_pet_warning() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_010",
        name="Parker",
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet = Pet(
        pet_id="pet_011",
        name="Finn",
        species="Dog",
        age=3,
        energy_level="high",
        medical_notes="",
    )

    task_a = CareTask(
        task_id="task_1001",
        pet_id=pet.pet_id,
        title="Morning walk",
        category="exercise",
        duration_minutes=20,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    task_b = CareTask(
        task_id="task_1002",
        pet_id=pet.pet_id,
        title="Medication",
        category="medication",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )

    pet.add_task(task_a)
    pet.add_task(task_b)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.detect_task_conflicts(today)

    assert len(warnings) == 1
    assert "Same-pet time conflict" in warnings[0]
    assert "Finn" in warnings[0]


def test_detect_task_conflicts_returns_cross_pet_warning() -> None:
    today = date.today()

    owner = Owner(
        owner_id="owner_011",
        name="Quinn",
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
    pet_a = Pet(
        pet_id="pet_012",
        name="Archie",
        species="Dog",
        age=4,
        energy_level="high",
        medical_notes="",
    )
    pet_b = Pet(
        pet_id="pet_013",
        name="Nori",
        species="Cat",
        age=2,
        energy_level="medium",
        medical_notes="",
    )

    task_a = CareTask(
        task_id="task_1101",
        pet_id=pet_a.pet_id,
        title="Feed Archie",
        category="feeding",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )
    task_b = CareTask(
        task_id="task_1102",
        pet_id=pet_b.pet_id,
        title="Feed Nori",
        category="feeding",
        duration_minutes=10,
        priority=1,
        due_date=today,
        preferred_window="morning",
    )

    pet_a.add_task(task_a)
    pet_b.add_task(task_b)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.detect_task_conflicts(today)

    assert len(warnings) == 1
    assert "Cross-pet time conflict" in warnings[0]
    assert "Archie" in warnings[0]
    assert "Nori" in warnings[0]
