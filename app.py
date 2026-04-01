import streamlit as st

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

st.markdown("### Tasks")
st.caption("Add care tasks for your pet. Tasks feed directly into the scheduler.")

from datetime import date

# Priority mapping: string to numeric (1=high, 2=medium, 3=low)
priority_map = {"high": 1, "medium": 2, "low": 3}

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)

if st.button("Add task"):
    # Create a CareTask object and add it to the pet
    task = CareTask(
        task_id=f"{st.session_state.pet.pet_id}_task_{len(st.session_state.pet.care_tasks) + 1}",
        pet_id=st.session_state.pet.pet_id,
        title=task_title,
        category="general",
        duration_minutes=int(duration),
        priority=priority_map.get(priority, 2),
        due_date=date.today(),
        preferred_window="morning",
    )
    st.session_state.pet.add_task(task)
    st.success(f"✓ Task '{task_title}' added to {st.session_state.pet.name}!")

# Display current tasks from the pet object
current_tasks = st.session_state.pet.list_tasks()
if current_tasks:
    st.write(f"**Tasks for {st.session_state.pet.name}:**")
    task_display = [
        {
            "Title": t.title,
            "Duration (min)": t.duration_minutes,
            "Priority": "H" if t.priority == 1 else ("M" if t.priority == 2 else "L"),
            "Status": t.status,
        }
        for t in current_tasks
    ]
    st.table(task_display)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("📅 Build Schedule")
st.caption("Generate today's optimized pet care schedule.")

if st.button("Generate schedule"):
    # Create scheduler and generate plan for today
    scheduler = Scheduler(owner=st.session_state.owner)
    plan = scheduler.generate_plan(date.today())

    # Display schedule summary
    st.write(scheduler.get_schedule_summary(plan))

    # Show conflict analysis
    conflict = scheduler.get_conflict_analysis(date.today())
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

    # Show scheduling decisions log if available
    if plan.explanation_log:
        with st.expander("📋 Scheduling Decisions", expanded=False):
            for entry in plan.explanation_log:
                st.write(entry)
