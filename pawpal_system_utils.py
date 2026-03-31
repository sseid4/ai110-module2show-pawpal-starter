"""Utility functions and classes for PawPal System."""

from datetime import date, timedelta
from typing import List, Dict, Tuple
from pawpal_system import CareTask, Pet, Owner, Scheduler, DailyPlan


class PawPalUtils:
    """Helper utilities for PawPal task management."""

    @staticmethod
    def create_task(
        task_id: str,
        pet_id: str,
        title: str,
        category: str,
        duration_minutes: int,
        priority: int,
        due_date: date,
        preferred_window: str = "morning",
        frequency: str = "daily",
    ) -> CareTask:
        """Factory method to create a CareTask with validation."""
        return CareTask(
            task_id=task_id,
            pet_id=pet_id,
            title=title,
            category=category,
            duration_minutes=max(1, duration_minutes),
            priority=max(1, priority),
            due_date=due_date,
            preferred_window=preferred_window,
            frequency=frequency,
        )

    @staticmethod
    def create_recurring_tasks(
        pet_id: str,
        base_title: str,
        category: str,
        duration_minutes: int,
        priority: int,
        frequency: str,
        start_date: date,
        num_occurrences: int,
    ) -> List[CareTask]:
        """Create recurring tasks (e.g., daily, weekly)."""
        tasks = []
        interval_days = {"daily": 1, "weekly": 7, "monthly": 30}.get(frequency, 1)

        for i in range(num_occurrences):
            task_date = start_date + timedelta(days=i * interval_days)
            task_id = f"{pet_id}_{category}_{i}"
            task = PawPalUtils.create_task(
                task_id=task_id,
                pet_id=pet_id,
                title=f"{base_title} ({task_date.strftime('%a')})",
                category=category,
                duration_minutes=duration_minutes,
                priority=priority,
                due_date=task_date,
                frequency=frequency,
            )
            tasks.append(task)

        return tasks

    @staticmethod
    def get_pet_health_summary(pet: Pet) -> Dict:
        """Generate a health/care summary for a pet."""
        pending = pet.get_pending_tasks()
        completed = [t for t in pet.care_tasks if t.is_complete()]

        return {
            "pet_name": pet.name,
            "species": pet.species,
            "age": pet.age,
            "energy_level": pet.energy_level,
            "total_tasks": len(pet.care_tasks),
            "pending_tasks": len(pending),
            "completed_tasks": len(completed),
            "completion_rate": pet.get_task_completion_rate(),
            "needs_medication": pet.needs_medication(),
            "allergies": pet.allergies,
            "last_vet_visit": pet.last_vet_visit,
            "medical_notes": pet.medical_notes,
        }

    @staticmethod
    def get_owner_workload_assessment(owner: Owner, date_range: int = 7) -> Dict:
        """Assess owner's workload over a period of days."""
        today = date.today()
        total_tasks = 0
        total_minutes = 0
        critical_count = 0

        for day_offset in range(date_range):
            check_date = today + timedelta(days=day_offset)
            tasks = owner.get_all_tasks_due_today(check_date)
            total_tasks += len(tasks)
            total_minutes += sum(t.duration_minutes for t in tasks)
            critical_count += sum(1 for t in tasks if t.is_critical())

        avg_daily_tasks = total_tasks / date_range if date_range > 0 else 0
        avg_daily_minutes = total_minutes / date_range if date_range > 0 else 0

        workload_level = "Low"
        if avg_daily_minutes > owner.available_minutes_per_day:
            workload_level = "Critical"
        elif avg_daily_minutes > owner.available_minutes_per_day * 0.8:
            workload_level = "High"
        elif avg_daily_minutes > owner.available_minutes_per_day * 0.5:
            workload_level = "Moderate"

        return {
            "period_days": date_range,
            "total_tasks": total_tasks,
            "total_minutes": total_minutes,
            "critical_tasks": critical_count,
            "avg_daily_tasks": avg_daily_tasks,
            "avg_daily_minutes": avg_daily_minutes,
            "available_per_day": owner.available_minutes_per_day,
            "workload_level": workload_level,
            "is_sustainable": avg_daily_minutes <= owner.available_minutes_per_day,
        }

    @staticmethod
    def export_plan_to_text(plan: DailyPlan) -> str:
        """Export a daily plan as formatted text."""
        lines = [
            f"\n{'#'*70}",
            f"# PAWPAL DAILY SCHEDULE - {plan.date.strftime('%A, %B %d, %Y')}",
            f"{'#'*70}\n",
        ]

        if plan.scheduled_items:
            lines.append("SCHEDULED ACTIVITIES:")
            lines.append("-" * 70)
            for task, slot in plan.scheduled_items:
                lines.append(
                    f"  [{slot.upper():10}] {task.title:30} | "
                    f"{task.duration_minutes:3}min | P{task.priority}"
                )
        else:
            lines.append("No scheduled activities.")

        if plan.unscheduled_tasks:
            lines.append("\n⚠️  COULD NOT FIT (Low Priority/No Time):")
            lines.append("-" * 70)
            for task in plan.unscheduled_tasks:
                lines.append(
                    f"  {task.title:30} | {task.duration_minutes:3}min | P{task.priority}"
                )

        lines.append(f"\nTOTAL SCHEDULED: {plan.total_scheduled_minutes} minutes")
        lines.append(f"{'#'*70}\n")

        return "\n".join(lines)

    @staticmethod
    def identify_scheduling_issues(scheduler: Scheduler, plan_date: date) -> List[str]:
        """Identify potential scheduling problems."""
        issues = []
        analysis = scheduler.get_conflict_analysis(plan_date)

        if analysis["has_conflict"]:
            excess = analysis["excess_minutes"]
            issues.append(
                f"⚠️  OVERLOAD: Tasks exceed available time by {excess} minutes"
            )

        overdue = scheduler.owner.get_all_overdue_tasks(plan_date)
        if overdue:
            issues.append(
                f"⚠️  OVERDUE: {len(overdue)} tasks are overdue"
            )

        critical = scheduler.get_critical_path_tasks()
        if critical:
            issues.append(
                f"⚠️  CRITICAL: {len(critical)} high-priority tasks pending"
            )

        high_maintenance_pets = scheduler.owner.get_high_maintenance_pets()
        if high_maintenance_pets:
            pet_names = ", ".join(p.name for p in high_maintenance_pets)
            issues.append(
                f"ℹ️   HIGH LOAD: {pet_names} have many pending tasks"
            )

        med_tasks = scheduler.get_medication_schedule()
        if med_tasks:
            issues.append(
                f"φ  MEDICATION: {len(med_tasks)} pet(s) have medication tasks"
            )

        return issues if issues else ["✓ No scheduling issues detected"]
