import streamlit as st
from pawpal_system import Owner, Pet, Task, TimeBlock, Scheduler, Priority, Frequency
from datetime import time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time_per_day=480)

if "pet" not in st.session_state:
    st.session_state.pet = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []

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

# Owner section
owner_name = st.text_input("Owner name", value=st.session_state.owner.name, key="owner_name_input")
if owner_name != st.session_state.owner.name:
    st.session_state.owner.name = owner_name

# Available time input
available_time = st.number_input(
    "Available time per day (minutes)", 
    value=int(st.session_state.owner.available_time_per_day),
    min_value=30,
    max_value=1440,
    key="available_time_input"
)
if available_time != st.session_state.owner.available_time_per_day:
    st.session_state.owner.available_time_per_day = available_time

# Pet section
st.subheader("Pet Information")
col_pet1, col_pet2 = st.columns(2)
with col_pet1:
    pet_name = st.text_input("Pet name", value=st.session_state.pet.name if st.session_state.pet else "Mochi", key="pet_name_input")
with col_pet2:
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species_input")

if st.button("Create/Update Pet"):
    # UI collects data → Create Pet object
    new_pet = Pet(name=pet_name, pet_type=species, age=0)
    
    # Call Owner.add_pet() - THE KEY METHOD HANDLING PET DATA
    st.session_state.owner.add_pet(new_pet)
    st.session_state.pet = new_pet
    
    st.success(f"✨ Pet '{pet_name}' added to {st.session_state.owner.name}'s care!")

if st.session_state.pet:
    st.info(f"📍 Current pet: **{st.session_state.pet.name}** ({st.session_state.pet.pet_type})")

st.markdown("### Tasks")
st.caption("Add tasks for your pet. These will be scheduled based on priority and duration.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="duration_input")
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="priority_input")

if st.button("Add task"):
    if not st.session_state.pet:
        st.error("❌ Please create a pet first!")
    else:
        # UI collects data → Create Task object
        priority_enum = Priority.HIGH if priority == "high" else Priority.MEDIUM if priority == "medium" else Priority.LOW
        new_task = Task(
            name=task_title,
            duration=int(duration),
            priority=priority_enum,
            category="general"
        )
        
        # Call Pet.add_task() - THE KEY METHOD HANDLING TASK DATA
        st.session_state.pet.add_task(new_task)
        
        # Store in UI state for display
        st.session_state.tasks.append({
            "title": task_title,
            "duration_minutes": int(duration),
            "priority": priority
        })
        st.success(f"✅ Task '{task_title}' added to {st.session_state.pet.name}!")

if st.session_state.tasks:
    st.write(f"**Current tasks ({len(st.session_state.tasks)}):**")
    task_display = [
        {
            "Task": task["title"],
            "Duration (min)": task["duration_minutes"],
            "Priority": task["priority"].upper()
        }
        for task in st.session_state.tasks
    ]
    st.table(task_display)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button will generate a schedule based on your tasks and constraints.")

if st.button("Generate schedule"):
    if not st.session_state.pet:
        st.error("❌ Please create a pet first!")
    elif not st.session_state.tasks:
        st.warning("⚠️ Please add at least one task!")
    else:
        # Create scheduler and generate schedule
        scheduler = Scheduler()
        schedule = scheduler.optimize(st.session_state.owner, st.session_state.pet, st.session_state.pet.get_tasks())
        
        st.success("✅ Schedule generated!")
        
        # Display schedule summary
        summary = schedule.get_schedule_summary()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Available Time", f"{int(summary['total_available_minutes'])} min")
        with col2:
            st.metric("Scheduled Time", f"{int(summary['total_scheduled_minutes'])} min")
        with col3:
            st.metric("Utilization", f"{summary['utilization_percentage']}%")
        with col4:
            st.metric("Tasks Scheduled", f"{summary['scheduled_tasks_count']}/{summary['scheduled_tasks_count'] + summary['unscheduled_tasks_count']}")
        
        # Display detailed explanation
        st.subheader("Schedule Details")
        st.text(schedule.explain_schedule())
