const pawpalClassDiagram = String.raw`classDiagram
    class Owner {
        +String owner_id
        +String name
        +int available_minutes_per_day
        +List~String~ preferred_time_blocks
        +Dict~String, String~ task_preferences
        +List~Pet~ pets
        +update_profile()
        +set_availability(minutes)
        +set_preferences(preferences)
    }

    class Pet {
        +String pet_id
        +String name
        +String species
        +int age
        +String energy_level
        +String medical_notes
        +List~CareTask~ care_tasks
        +update_pet_info()
        +needs_medication() bool
    }

    class CareTask {
        +String task_id
        +String pet_id
        +String title
        +String category
        +int duration_minutes
        +int priority
        +Date due_date
        +String preferred_window
        +String status
        +mark_done()
        +reschedule(new_time)
        +is_due_today(date) bool
    }

    class Scheduler {
        +Owner owner
        +List~Pet~ pets
        +generate_plan(date) DailyPlan
        +prioritize_tasks(tasks) List~CareTask~
        +allocate_time_slots(tasks, date) DailyPlan
        +explain_decisions(plan) List~String~
    }

    class DailyPlan {
        +Date date
        +List~CareTask~ planned_items
        +List~Tuple~CareTask, String~~ scheduled_items
        +int total_scheduled_minutes
        +List~CareTask~ unscheduled_tasks
        +List~String~ explanation_log
        +add_plan_item(task, time_slot)
        +summarize() String
        +get_reasoning() List~String~
    }

    Owner "1" --> "many" Pet : has
    Pet "1" --> "many" CareTask : has
    Scheduler --> Owner : reads preferences
    Scheduler --> Pet : reads needs
    Scheduler --> CareTask : prioritizes
    Scheduler --> DailyPlan : produces
    DailyPlan "1" --> "many" CareTask : schedules
`;

export default pawpalClassDiagram;
