from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pawpal_system import CareTask, Pet


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
