import streamlit as st
from datetime import date

from pawpal_system import CareTask, Owner, Pet, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Session "vault" guard: create objects once, then reuse on reruns.
if "owner" not in st.session_state or not isinstance(st.session_state.owner, Owner):
    st.session_state.owner = Owner(
        owner_id="owner_streamlit",
        name=owner_name,
        available_minutes_per_day=120,
        preferred_time_blocks=["morning", "afternoon", "evening"],
    )
else:
    st.session_state.owner.name = owner_name

if "pet" not in st.session_state or not isinstance(st.session_state.pet, Pet):
    st.session_state.pet = Pet(
        pet_id="pet_streamlit",
        name=pet_name,
        species=species,
        age=1,
        energy_level="medium",
        medical_notes="",
    )
    if st.session_state.owner.get_pet(st.session_state.pet.pet_id) is None:
        st.session_state.owner.add_pet(st.session_state.pet)
else:
    st.session_state.pet.name = pet_name
    st.session_state.pet.species = species

st.caption(
    f"Session owner loaded: {st.session_state.owner.name} | "
    f"pet: {st.session_state.pet.name}"
)

scheduler = Scheduler(owner=st.session_state.owner)

st.markdown("### Tasks")
st.caption("Add care tasks for your pet. Tasks feed directly into the scheduler.")

# Priority mapping: string to numeric (1=high, 2=medium, 3=low)
priority_map = {"high": 1, "medium": 2, "low": 3}

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
with col4:
    category = st.selectbox("Category", ["general", "feeding", "medication", "exercise", "hygiene"])
with col5:
    preferred_window = st.selectbox("Preferred window", ["morning", "afternoon", "evening"])

task_due_date = st.date_input("Due date", value=date.today())

if st.button("Add task"):
    # Create a CareTask object and add it to the pet
    task = CareTask(
        task_id=f"{st.session_state.pet.pet_id}_task_{len(st.session_state.pet.care_tasks) + 1}",
        pet_id=st.session_state.pet.pet_id,
        title=task_title,
        category=category,
        duration_minutes=int(duration),
        priority=priority_map.get(priority, 2),
        due_date=task_due_date,
        preferred_window=preferred_window,
    )
    st.session_state.pet.add_task(task)
    st.success(f"✓ Task '{task_title}' added to {st.session_state.pet.name}!")

# Display current tasks using scheduler filters and sorting.
st.markdown("#### Task List")
list_col1, list_col2 = st.columns(2)
with list_col1:
    completion_filter = st.selectbox("Filter by status", ["all", "pending", "done", "rescheduled"])
with list_col2:
    show_today_only = st.toggle("Only due/overdue today", value=False)

status_arg = None if completion_filter == "all" else completion_filter
plan_date_arg = date.today() if show_today_only else None
filtered_tasks = scheduler.get_filtered_tasks(
    pet_id=st.session_state.pet.pet_id,
    status=status_arg,
    plan_date=plan_date_arg,
)
sorted_tasks = scheduler.prioritize_tasks(filtered_tasks, date.today())

if sorted_tasks:
    task_display = []
    for t in sorted_tasks:
        task_display.append(
            {
                "Due": str(t.due_date),
                "Title": t.title,
                "Category": t.category,
                "Window": t.preferred_window,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Status": t.status,
            }
        )
    st.table(task_display)
else:
    st.info("No tasks match the selected filter.")

st.divider()

st.subheader("📅 Build Schedule")
st.caption("Generate today's optimized pet care schedule.")

if st.button("Generate schedule"):
    # Create scheduler and generate plan for today
    plan = scheduler.generate_plan(date.today())

    if plan.scheduled_items:
        st.success("Schedule generated successfully.")
    else:
        st.warning("No tasks were scheduled. Add due tasks or adjust constraints.")

    scheduled_table = [
        {
            "Window": slot,
            "Task": task.title,
            "Pet": st.session_state.owner.get_pet(task.pet_id).name
            if st.session_state.owner.get_pet(task.pet_id)
            else task.pet_id,
            "Duration (min)": task.duration_minutes,
            "Priority": task.priority,
        }
        for task, slot in plan.scheduled_items
    ]
    if scheduled_table:
        st.markdown("#### Today's Scheduled Tasks")
        st.table(scheduled_table)

    if plan.unscheduled_tasks:
        st.markdown("#### Unscheduled Tasks")
        st.table(
            [
                {
                    "Task": task.title,
                    "Pet": st.session_state.owner.get_pet(task.pet_id).name
                    if st.session_state.owner.get_pet(task.pet_id)
                    else task.pet_id,
                    "Needed (min)": task.duration_minutes,
                    "Preferred Window": task.preferred_window,
                }
                for task in plan.unscheduled_tasks
            ]
        )

    # Show conflict analysis
    conflict = scheduler.get_conflict_analysis(date.today())
    conflict_warnings = scheduler.detect_task_conflicts(date.today())
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tasks Today", conflict["tasks_due"])
    with col2:
        st.metric("Time Needed", f"{conflict['total_minutes_needed']}m")
    with col3:
        st.metric("Available", f"{conflict['available_minutes']}m")
    with col4:
        status = "✓ Feasible" if not conflict["has_conflict"] else "✗ Overload"
        st.metric("Status", status)

    if conflict_warnings:
        st.warning(
            "Some tasks share the same time window. Consider moving one task to reduce stress and avoid missed care."
        )
        with st.expander("See conflict details", expanded=True):
            for warning in conflict_warnings:
                st.write(f"- {warning}")
    elif conflict["has_conflict"]:
        st.warning(
            "Today's workload exceeds available time or window capacity. Check unscheduled tasks and rebalance priorities."
        )
    else:
        st.success("No scheduling conflicts detected for today.")

    # Show scheduling decisions log if available
    if plan.explanation_log:
        with st.expander("📋 Scheduling Decisions", expanded=False):
            for entry in plan.explanation_log:
                st.write(entry)
