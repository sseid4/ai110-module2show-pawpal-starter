from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Tuple


@dataclass
class CareTask:
    task_id: str
    pet_id: str
    title: str
    category: str
    duration_minutes: int
    priority: int
    due_date: date
    preferred_window: str
    status: str = "pending"
    frequency: str = "daily"  # daily, weekly, as-needed
    completed_date: date | None = None
    notes: str = ""
    reminder_set: bool = False

    def mark_done(self) -> None:
        """Mark this task as done and store completion date."""
        self.status = "done"
        from datetime import date as date_class
        self.completed_date = date_class.today()

    def mark_complete(self) -> None:
        """Compatibility alias for marking a task complete."""
        self.mark_done()

    def mark_pending(self) -> None:
        """Mark task as pending again."""
        self.status = "pending"
        self.completed_date = None

    def reschedule(self, new_time: date) -> None:
        """Move the task to a new due date and mark it rescheduled."""
        self.due_date = new_time
        self.status = "rescheduled"

    def is_due_today(self, on_date: date) -> bool:
        """Return True when this task is due on the provided date."""
        return self.due_date == on_date and self.status != "done"

    def is_complete(self) -> bool:
        """Return True when this task has been completed."""
        return self.status == "done"

    def is_overdue(self, on_date: date) -> bool:
        """Check if task is overdue compared to given date."""
        return self.due_date < on_date and self.status != "done"

    def is_critical(self) -> bool:
        """Check if task is high priority or critical."""
        return self.priority <= 2

    def add_note(self, note: str) -> None:
        """Add or update notes for this task."""
        self.notes = note

    def set_reminder(self, enabled: bool = True) -> None:
        """Enable or disable reminder for this task."""
        self.reminder_set = enabled

    def time_until_due(self, today: date) -> int:
        """Return days until task is due. Negative means overdue."""
        from datetime import timedelta
        delta = self.due_date - today
        return delta.days

    def __str__(self) -> str:
        """Return a human-readable summary of the task."""
        return (
            f"[{self.status.upper()}] {self.title} "
            f"(due: {self.due_date}, priority: {self.priority}, "
            f"{self.duration_minutes} min, window: {self.preferred_window})"
        )


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    energy_level: str
    medical_notes: str
    care_tasks: List[CareTask] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    weight_kg: float = 0.0
    last_vet_visit: date | None = None

    def add_task(self, task: CareTask) -> None:
        """Add a care task for this pet."""
        if task.pet_id != self.pet_id:
            task.pet_id = self.pet_id
        self.care_tasks.append(task)

    def list_tasks(self) -> List[CareTask]:
        """Return all tasks for this pet."""
        return self.care_tasks

    def get_pending_tasks(self) -> List[CareTask]:
        """Return all incomplete tasks."""
        return [t for t in self.care_tasks if t.status != "done"]

    def get_tasks_due_today(self, on_date: date) -> List[CareTask]:
        """Return tasks due on a specific date."""
        return [t for t in self.care_tasks if t.is_due_today(on_date)]

    def get_overdue_tasks(self, on_date: date) -> List[CareTask]:
        """Return all overdue tasks."""
        return [t for t in self.care_tasks if t.is_overdue(on_date)]

    def get_tasks_by_category(self, category: str) -> List[CareTask]:
        """Return tasks filtered by category."""
        return [t for t in self.get_pending_tasks()
                if t.category.lower() == category.lower()]

    def get_critical_tasks(self) -> List[CareTask]:
        """Return all high-priority incomplete tasks."""
        return [t for t in self.get_pending_tasks() if t.is_critical()]

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID. Returns True if removed."""
        original_len = len(self.care_tasks)
        self.care_tasks = [t for t in self.care_tasks if t.task_id != task_id]
        return len(self.care_tasks) < original_len

    def update_pet_info(self, **kwargs) -> None:
        """Update pet attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def needs_medication(self) -> bool:
        """Check if pet has pending medication tasks."""
        return any(
            t.category.lower() == "medication" and t.status != "done"
            for t in self.care_tasks
        )

    def is_high_maintenance(self) -> bool:
        """Check if pet has many pending tasks."""
        return len(self.get_pending_tasks()) >= 5

    def get_task_completion_rate(self) -> float:
        """Calculate percentage of completed tasks (0-1)."""
        if not self.care_tasks:
            return 0.0
        completed = sum(1 for t in self.care_tasks if t.is_complete())
        return completed / len(self.care_tasks)

    def add_allergy(self, allergy: str) -> None:
        """Add an allergy to the pet's profile."""
        if allergy not in self.allergies:
            self.allergies.append(allergy)

    def remove_allergy(self, allergy: str) -> None:
        """Remove an allergy from the pet's profile."""
        self.allergies = [a for a in self.allergies if a != allergy]

    def set_last_vet_visit(self, visit_date: date) -> None:
        """Record last vet visit date."""
        self.last_vet_visit = visit_date

    def needs_vet_checkup(self, today: date, months_between_visits: int = 12) -> bool:
        """Check if pet needs a vet checkup based on last visit."""
        from datetime import timedelta
        if self.last_vet_visit is None:
            return True
        checkup_interval = timedelta(days=30 * months_between_visits)
        return (today - self.last_vet_visit) > checkup_interval

    def __str__(self) -> str:
        """Return a readable description of this pet and task status."""
        status = f"{len(self.get_pending_tasks())} pending" if self.get_pending_tasks() else "all done"
        return f"{self.name} ({self.species}, age {self.age}) — {status}"


@dataclass
class Owner:
    owner_id: str
    name: str
    available_minutes_per_day: int
    preferred_time_blocks: List[str] = field(default_factory=list)
    task_preferences: Dict[str, str] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)
    max_pets: int = 10
    email: str = ""
    phone: str = ""

    def add_pet(self, pet: Pet) -> bool:
        """Add a pet. Returns False if at max capacity."""
        if len(self.pets) >= self.max_pets:
            return False
        self.pets.append(pet)
        return True

    def remove_pet(self, pet_id: str) -> bool:
        """Remove a pet by ID. Returns True if removed."""
        original_len = len(self.pets)
        self.pets = [p for p in self.pets if p.pet_id != pet_id]
        return len(self.pets) < original_len

    def get_pet(self, pet_id: str) -> Pet | None:
        """Retrieve a specific pet by ID."""
        for pet in self.pets:
            if pet.pet_id == pet_id:
                return pet
        return None

    def get_pet_by_name(self, name: str) -> Pet | None:
        """Retrieve a pet by name."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self) -> List[CareTask]:
        """Retrieve all tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.care_tasks)
        return tasks

    def get_all_tasks_due_today(self, on_date: date) -> List[CareTask]:
        """Get all tasks for all pets due on a specific date."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks_due_today(on_date))
        return tasks

    def get_all_overdue_tasks(self, on_date: date) -> List[CareTask]:
        """Get all overdue tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_overdue_tasks(on_date))
        return tasks

    def get_all_critical_tasks(self) -> List[CareTask]:
        """Get all high-priority incomplete tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_critical_tasks())
        return tasks

    def get_pets_needing_medication(self) -> List[Pet]:
        """Get all pets with pending medication tasks."""
        return [p for p in self.pets if p.needs_medication()]

    def get_high_maintenance_pets(self) -> List[Pet]:
        """Get pets with many pending tasks."""
        return [p for p in self.pets if p.is_high_maintenance()]

    def get_total_pending_tasks(self) -> int:
        """Count total incomplete tasks across all pets."""
        return sum(len(p.get_pending_tasks()) for p in self.pets)

    def get_total_pet_care_time_today(self, on_date: date) -> int:
        """Calculate total minutes needed for all tasks due today."""
        tasks = self.get_all_tasks_due_today(on_date)
        return sum(t.duration_minutes for t in tasks)

    def can_fit_tasks_today(self, on_date: date) -> bool:
        """Check if all due tasks fit within available time."""
        return self.get_total_pet_care_time_today(on_date) <= self.available_minutes_per_day

    def update_profile(self, **kwargs) -> None:
        """Update owner attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_availability(self, minutes: int) -> None:
        """Update daily available minutes."""
        self.available_minutes_per_day = max(0, minutes)

    def set_preferences(self, preferences: Dict[str, str]) -> None:
        """Update task preferences."""
        self.task_preferences.update(preferences)

    def add_time_block_preference(self, time_block: str) -> None:
        """Add a preferred time block for scheduling."""
        if time_block not in self.preferred_time_blocks:
            self.preferred_time_blocks.append(time_block)

    def remove_time_block_preference(self, time_block: str) -> None:
        """Remove a preferred time block."""
        self.preferred_time_blocks = [
            t for t in self.preferred_time_blocks if t != time_block
        ]

    def get_workload_summary(self, on_date: date) -> Dict:
        """Get a summary of today's workload."""
        tasks_today = self.get_all_tasks_due_today(on_date)
        overdue = self.get_all_overdue_tasks(on_date)
        return {
            "total_pets": len(self.pets),
            "tasks_due_today": len(tasks_today),
            "total_minutes_needed": sum(t.duration_minutes for t in tasks_today),
            "available_minutes": self.available_minutes_per_day,
            "overdue_tasks": len(overdue),
            "critical_tasks": len(self.get_all_critical_tasks()),
        }

    def __str__(self) -> str:
        """Return a readable summary of the owner and current workload."""
        return (
            f"Owner: {self.name} | Pets: {len(self.pets)} | "
            f"Available: {self.available_minutes_per_day} min/day | "
            f"Pending: {self.get_total_pending_tasks()} tasks"
        )


@dataclass
class DailyPlan:
    date: date
    planned_items: List[CareTask] = field(default_factory=list)
    scheduled_items: List[Tuple[CareTask, str]] = field(default_factory=list)
    total_scheduled_minutes: int = 0
    unscheduled_tasks: List[CareTask] = field(default_factory=list)
    explanation_log: List[str] = field(default_factory=list)

    def add_plan_item(self, task: CareTask, time_slot: str) -> None:
        """Add a scheduled item to the plan."""
        self.scheduled_items.append((task, time_slot))
        self.planned_items.append(task)
        self.total_scheduled_minutes += task.duration_minutes

    def remove_plan_item(self, task_id: str) -> bool:
        """Remove a scheduled item by task ID."""
        original_len = len(self.scheduled_items)
        for task, slot in self.scheduled_items:
            if task.task_id == task_id:
                self.total_scheduled_minutes -= task.duration_minutes
        self.scheduled_items = [
            (t, s) for t, s in self.scheduled_items if t.task_id != task_id
        ]
        return len(self.scheduled_items) < original_len

    def add_unscheduled_task(self, task: CareTask) -> None:
        """Add a task that couldn't be scheduled."""
        self.unscheduled_tasks.append(task)

    def is_over_capacity(self, available_minutes: int) -> bool:
        """Check if scheduled tasks exceed available time."""
        return self.total_scheduled_minutes > available_minutes

    def get_utilization_rate(self, available_minutes: int) -> float:
        """Calculate utilization as percentage (0-1)."""
        if available_minutes <= 0:
            return 0.0
        return min(1.0, self.total_scheduled_minutes / available_minutes)

    def get_remaining_capacity(self, available_minutes: int) -> int:
        """Get remaining available minutes after scheduling."""
        return max(0, available_minutes - self.total_scheduled_minutes)

    def get_tasks_by_slot(self, time_slot: str) -> List[CareTask]:
        """Get all tasks scheduled in a specific time slot."""
        return [t for t, s in self.scheduled_items if s.lower() == time_slot.lower()]

    def add_log_entry(self, entry: str) -> None:
        """Add an entry to the explanation log."""
        self.explanation_log.append(entry)

    def summarize(self) -> str:
        """Generate a text summary of the plan."""
        lines = [f"Daily Plan for {self.date}"]
        lines.append(
            f"  Scheduled: {len(self.scheduled_items)} tasks "
            f"({self.total_scheduled_minutes} min)"
        )
        for task, slot in self.scheduled_items:
            lines.append(
                f"    {slot}: {task.title} ({task.duration_minutes} min)"
            )
        if self.unscheduled_tasks:
            lines.append(f"  Unscheduled ({len(self.unscheduled_tasks)}):")
            for task in self.unscheduled_tasks:
                lines.append(f"    - {task.title} (priority {task.priority})")
        return "\n".join(lines)

    def get_reasoning(self) -> List[str]:
        """Get the explanation log for scheduling decisions."""
        return self.explanation_log


@dataclass
class Scheduler:
    owner: Owner
    pets: List[Pet] = field(default_factory=list)

    _DEFAULT_BLOCKS: Tuple[str, ...] = ("morning", "afternoon", "evening")
    _RECURRING_INTERVAL_DAYS: Dict[str, int] = field(
        default_factory=lambda: {"daily": 1, "weekly": 7, "monthly": 30}
    )

    def sync_pets(self) -> None:
        """Synchronize pets from owner's pet list."""
        self.pets = self.owner.pets

    def generate_plan(self, plan_date: date) -> DailyPlan:
        """Generate a daily plan for all pets."""
        self.sync_pets()
        all_due = []

        # Collect all tasks due on this date
        for pet in self.pets:
            all_due.extend(pet.get_tasks_due_today(plan_date))

        # Check for overdue tasks and prioritize them
        overdue_tasks = []
        for pet in self.pets:
            overdue_tasks.extend(pet.get_overdue_tasks(plan_date))

        # Combine and de-duplicate task IDs that might appear in both lists.
        all_tasks = {}
        for task in overdue_tasks + all_due:
            all_tasks[task.task_id] = task

        prioritized = self.prioritize_tasks(list(all_tasks.values()), plan_date)

        return self.allocate_time_slots(prioritized, plan_date)

    def prioritize_tasks(self, tasks: List[CareTask], plan_date: date) -> List[CareTask]:
        """Sort tasks by overdue status, due date, window, priority, and duration."""
        preferred_blocks = self.owner.preferred_time_blocks or list(self._DEFAULT_BLOCKS)
        window_rank = {name.lower(): idx for idx, name in enumerate(preferred_blocks)}

        def sort_key(task):
            is_overdue = 0 if task.is_overdue(plan_date) else 1
            preferred = window_rank.get(task.preferred_window.lower(), len(window_rank))
            return (is_overdue, task.due_date, preferred, task.priority, task.duration_minutes)

        return sorted(tasks, key=sort_key)

    def get_filtered_tasks(
        self,
        pet_id: str | None = None,
        status: str | None = None,
        plan_date: date | None = None,
    ) -> List[CareTask]:
        """Filter tasks by pet, status, and due date."""
        self.sync_pets()
        tasks = self.owner.get_all_tasks()

        if pet_id is not None:
            tasks = [t for t in tasks if t.pet_id == pet_id]
        if status is not None:
            status_lower = status.lower()
            tasks = [t for t in tasks if t.status.lower() == status_lower]
        if plan_date is not None:
            tasks = [t for t in tasks if t.is_due_today(plan_date) or t.is_overdue(plan_date)]

        return tasks

    def filter_tasks(
        self,
        completion_status: str | None = None,
        pet_name: str | None = None,
    ) -> List[CareTask]:
        """Filter tasks by completion status and/or pet name."""
        self.sync_pets()
        tasks = self.owner.get_all_tasks()

        if completion_status is not None:
            status_lower = completion_status.lower()
            tasks = [t for t in tasks if t.status.lower() == status_lower]

        if pet_name is not None:
            pet_name_lower = pet_name.lower()
            pet_ids = {
                p.pet_id for p in self.owner.pets if p.name.lower() == pet_name_lower
            }
            tasks = [t for t in tasks if t.pet_id in pet_ids]

        return tasks

    def _get_time_block_capacities(self, preferred_blocks: List[str]) -> Dict[str, int]:
        """Split daily availability across preferred blocks for basic capacity checks."""
        block_count = len(preferred_blocks)
        if block_count == 0:
            return {}

        total = self.owner.available_minutes_per_day
        base = total // block_count
        remainder = total % block_count

        capacities: Dict[str, int] = {}
        for idx, block in enumerate(preferred_blocks):
            capacities[block] = base + (1 if idx < remainder else 0)

        return capacities

    def allocate_time_slots(self, tasks: List[CareTask], plan_date: date) -> DailyPlan:
        """Allocate tasks into preferred windows and fallback to available windows."""
        plan = DailyPlan(date=plan_date)
        budget = self.owner.available_minutes_per_day
        preferred_blocks = self.owner.preferred_time_blocks or list(self._DEFAULT_BLOCKS)
        block_remaining = self._get_time_block_capacities(preferred_blocks)

        for task in tasks:
            if task.duration_minutes > budget:
                plan.unscheduled_tasks.append(task)
                plan.explanation_log.append(
                    f"✗ Skipped '{task.title}' ({task.pet_id}) — "
                    f"needs {task.duration_minutes} min, only {budget} min left"
                )
                continue

            preferred_slot = task.preferred_window.lower()
            chosen_slot = None

            if preferred_slot in block_remaining and block_remaining[preferred_slot] >= task.duration_minutes:
                chosen_slot = preferred_slot
            else:
                for slot in preferred_blocks:
                    if block_remaining[slot] >= task.duration_minutes:
                        chosen_slot = slot
                        break

            if chosen_slot is None:
                plan.unscheduled_tasks.append(task)
                plan.explanation_log.append(
                    f"✗ Skipped '{task.title}' ({task.pet_id}) — no window has "
                    f"{task.duration_minutes} min remaining"
                )
                continue

            plan.add_plan_item(task, chosen_slot)
            budget -= task.duration_minutes
            block_remaining[chosen_slot] -= task.duration_minutes
            plan.explanation_log.append(
                f"✓ Scheduled '{task.title}' ({task.pet_id}) in {chosen_slot} "
                f"(priority {task.priority}, {task.duration_minutes} min, "
                f"remaining budget: {budget} min)"
            )

        return plan

    def explain_decisions(self, plan: DailyPlan) -> List[str]:
        """Get the decision log for a plan."""
        return plan.get_reasoning()

    def get_all_incomplete_tasks(self) -> List[CareTask]:
        """Get all incomplete tasks across all pets."""
        self.sync_pets()
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_pending_tasks())
        return tasks

    def get_tasks_by_category(self, category: str) -> List[CareTask]:
        """Filter incomplete tasks by category."""
        return [
            t for t in self.get_all_incomplete_tasks()
            if t.category.lower() == category.lower()
        ]

    def get_critical_path_tasks(self) -> List[CareTask]:
        """Get high-priority tasks that need immediate attention."""
        return [t for t in self.get_all_incomplete_tasks() if t.is_critical()]

    def get_medication_schedule(self) -> Dict[str, List[CareTask]]:
        """Get all medication tasks organized by pet."""
        med_tasks = self.get_tasks_by_category("medication")
        schedule = {}
        for task in med_tasks:
            if task.pet_id not in schedule:
                schedule[task.pet_id] = []
            schedule[task.pet_id].append(task)
        return schedule

    def get_conflict_analysis(self, plan_date: date) -> Dict:
        """Analyze scheduling conflicts and constraints."""
        tasks_due = self.owner.get_all_tasks_due_today(plan_date)
        total_minutes_needed = sum(t.duration_minutes for t in tasks_due)
        available = self.owner.available_minutes_per_day
        preferred_blocks = self.owner.preferred_time_blocks or list(self._DEFAULT_BLOCKS)
        window_capacity = self._get_time_block_capacities(preferred_blocks)
        window_load = {block: 0 for block in preferred_blocks}

        for task in tasks_due:
            slot = task.preferred_window.lower()
            if slot in window_load:
                window_load[slot] += task.duration_minutes

        window_conflicts = {
            block: window_load[block] - window_capacity[block]
            for block in preferred_blocks
            if window_load[block] > window_capacity[block]
        }
        total_overload = total_minutes_needed > available
        window_overload = bool(window_conflicts)

        return {
            "tasks_due": len(tasks_due),
            "total_minutes_needed": total_minutes_needed,
            "available_minutes": available,
            "has_conflict": total_overload or window_overload,
            "excess_minutes": max(0, total_minutes_needed - available),
            "utilization_rate": min(1.0, total_minutes_needed / available) if available > 0 else 0,
            "window_capacity": window_capacity,
            "window_load": window_load,
            "window_conflicts": window_conflicts,
            "has_window_conflict": window_overload,
        }

    def detect_task_conflicts(self, plan_date: date) -> List[str]:
        """Detect lightweight schedule conflicts and return warning messages.

        This method intentionally uses a simple strategy: tasks are considered
        conflicting when they share the same due date and preferred window
        label (for example, two "morning" tasks). It does not attempt to model
        exact start/end timestamps.

        Args:
            plan_date: The date for which task conflicts should be checked.

        Returns:
            A list of human-readable warning strings. The list is empty when
            no conflicts are detected.
        """
        tasks_due = [
            t for t in self.owner.get_all_tasks_due_today(plan_date)
            if t.status != "done"
        ]

        buckets: Dict[Tuple[date, str], List[CareTask]] = {}
        for task in tasks_due:
            key = (task.due_date, task.preferred_window.lower())
            buckets.setdefault(key, []).append(task)

        warnings: List[str] = []
        for (due, window), bucket in buckets.items():
            if len(bucket) < 2:
                continue

            pet_ids = {t.pet_id for t in bucket}
            pet_names = []
            for pet_id in sorted(pet_ids):
                pet = self.owner.get_pet(pet_id)
                pet_names.append(pet.name if pet else pet_id)

            task_titles = ", ".join(t.title for t in bucket)
            if len(pet_ids) == 1:
                warnings.append(
                    f"WARNING: Same-pet time conflict on {due} ({window}) for {pet_names[0]}: {task_titles}"
                )
            else:
                warnings.append(
                    "WARNING: Cross-pet time conflict on "
                    f"{due} ({window}) for pets {', '.join(pet_names)}: {task_titles}"
                )

        return warnings

    def _create_next_recurring_task(self, task: CareTask, completed_on: date) -> CareTask | None:
        """Create the next pending instance of a recurring task.

        The next due date is calculated from the completion date using
        ``timedelta(days=interval)``, where interval is based on the task
        frequency (daily/weekly/monthly). A unique task ID is generated to
        avoid collisions with existing tasks.

        Args:
            task: The completed recurring task.
            completed_on: The date the task was completed.

        Returns:
            A newly created ``CareTask`` for the next occurrence, or ``None``
            when the frequency is not recurring.
        """
        interval = self._RECURRING_INTERVAL_DAYS.get(task.frequency.lower())
        if interval is None:
            return None

        next_due_date = completed_on + timedelta(days=interval)
        existing_ids = {t.task_id for t in self.owner.get_all_tasks()}
        base_id = f"{task.task_id}_next_{next_due_date.isoformat()}"
        next_task_id = base_id
        suffix = 2
        while next_task_id in existing_ids:
            next_task_id = f"{base_id}_{suffix}"
            suffix += 1

        return CareTask(
            task_id=next_task_id,
            pet_id=task.pet_id,
            title=task.title,
            category=task.category,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            due_date=next_due_date,
            preferred_window=task.preferred_window,
            status="pending",
            frequency=task.frequency,
            notes=task.notes,
            reminder_set=task.reminder_set,
        )

    def _roll_task_to_next_occurrence(self, task: CareTask, completed_on: date) -> CareTask | None:
        """Compatibility wrapper that delegates recurring task creation."""
        return self._create_next_recurring_task(task, completed_on)

    def reschedule_task(self, task_id: str, new_date: date) -> bool:
        """Reschedule a task to a different date."""
        self.sync_pets()
        for pet in self.pets:
            for task in pet.care_tasks:
                if task.task_id == task_id:
                    task.reschedule(new_date)
                    return True
        return False

    def mark_task_complete(self, task_id: str) -> bool:
        """Mark a task as done and spawn the next recurring instance when needed.

        For non-recurring tasks, only the original task state is updated.
        For recurring tasks, the completed task remains ``done`` and a separate
        pending task is appended for the next occurrence.

        Args:
            task_id: Identifier of the task to mark complete.

        Returns:
            ``True`` when the task exists and is updated, otherwise ``False``.
        """
        self.sync_pets()
        completed_on = date.today()
        for pet in self.pets:
            for task in pet.care_tasks:
                if task.task_id == task_id:
                    task.mark_done()
                    next_task = self._roll_task_to_next_occurrence(task, completed_on)
                    if next_task is not None:
                        pet.add_task(next_task)
                    return True
        return False

    def get_workload_forecast(self, days_ahead: int = 7) -> Dict:
        """Forecast workload for the next N days."""
        from datetime import timedelta, date as date_class
        today = date_class.today()
        forecast = {}

        for day_offset in range(days_ahead):
            check_date = today + timedelta(days=day_offset)
            tasks = self.owner.get_all_tasks_due_today(check_date)
            total_minutes = sum(t.duration_minutes for t in tasks)
            forecast[str(check_date)] = {
                "tasks": len(tasks),
                "minutes": total_minutes,
                "feasible": total_minutes <= self.owner.available_minutes_per_day,
            }

        return forecast

    def get_schedule_summary(self, plan: DailyPlan) -> str:
        """Generate a human-readable summary of the plan."""
        lines = [
            f"\n{'='*60}",
            f"Daily Plan for {plan.date}",
            f"{'='*60}",
            f"\nSUMMARY:",
            f"  Owner: {self.owner.name}",
            f"  Available time: {self.owner.available_minutes_per_day} minutes",
            f"  Scheduled tasks: {len(plan.scheduled_items)}",
            f"  Total scheduled time: {plan.total_scheduled_minutes} minutes",
            f"  Unscheduled tasks: {len(plan.unscheduled_tasks)}",
        ]

        if plan.scheduled_items:
            lines.append(f"\nSCHEDULED TASKS:")
            for task, slot in plan.scheduled_items:
                pet = self.owner.get_pet(task.pet_id)
                pet_name = pet.name if pet else "Unknown"
                lines.append(
                    f"  [{slot}] {task.title} ({pet_name}) - "
                    f"{task.duration_minutes} min | Priority: {task.priority}"
                )

        if plan.unscheduled_tasks:
            lines.append(f"\nUNSCHEDULED TASKS:")
            for task in plan.unscheduled_tasks:
                pet = self.owner.get_pet(task.pet_id)
                pet_name = pet.name if pet else "Unknown"
                lines.append(
                    f"  ✗ {task.title} ({pet_name}) - "
                    f"{task.duration_minutes} min | Priority: {task.priority}"
                )

        lines.append(f"\n{'='*60}\n")
        return "\n".join(lines)
