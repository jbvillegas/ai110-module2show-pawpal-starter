import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize application state
# st.session_state acts as a dictionary that persists across page reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Pet Owner")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+** — your pet care planning assistant.

Create pets, add care tasks, and generate daily schedules automatically!
"""
)

st.divider()

# ============================================================================
# SECTION 1: MANAGE OWNER & PETS
# ============================================================================
st.header("1️⃣ Owner & Pets")

col1, col2 = st.columns(2)
with col1:
    new_owner_name = st.text_input("Your name", value=st.session_state.owner.name)
    if new_owner_name != st.session_state.owner.name:
        st.session_state.owner.name = new_owner_name

with col2:
    st.metric("Pets", len(st.session_state.owner.pets))

st.subheader("Add a New Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Buddy")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "hamster", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=50, value=3)

if st.button("➕ Add Pet"):
    # Check if pet already exists
    if st.session_state.owner.get_pet(pet_name) is None:
        new_pet = Pet(name=pet_name, species=species, age=age)
        st.session_state.owner.add_pet(new_pet)
        st.success(f"✅ {pet_name} added!")
        st.rerun()
    else:
        st.error(f"❌ A pet named '{pet_name}' already exists.")

# Display current pets
if st.session_state.owner.pets:
    st.subheader("Your Pets")
    for pet in st.session_state.owner.pets:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{pet.name}** ({pet.species}, {pet.age}y)")
        with col2:
            st.metric("Tasks", len(pet.tasks))
        with col3:
            if st.button("❌ Remove", key=f"remove_{pet.name}"):
                st.session_state.owner.remove_pet(pet.name)
                st.success(f"Removed {pet.name}")
                st.rerun()
else:
    st.info("No pets yet. Add one above!")

st.divider()

# ============================================================================
# SECTION 2: MANAGE TASKS
# ============================================================================
st.header("2️⃣ Tasks & Schedule")

if st.session_state.owner.pets:
    selected_pet_name = st.selectbox(
        "Select a pet to add tasks",
        options=[pet.name for pet in st.session_state.owner.pets]
    )
    selected_pet = st.session_state.owner.get_pet(selected_pet_name)

    st.subheader(f"Add Task for {selected_pet_name}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        task_desc = st.text_input("Task description", value="Morning walk")
    with col2:
        task_time = st.number_input("Time (minutes)", min_value=1, max_value=240, value=30)
    with col3:
        task_freq = st.selectbox("Frequency", ["daily", "weekly", "biweekly", "monthly", "once"])
    with col4:
        task_priority = st.selectbox("Priority", ["low", "medium", "high"])

    if st.button("➕ Add Task"):
        task = Task(
            description=task_desc,
            time_minutes=task_time,
            frequency=task_freq,
            priority=task_priority
        )
        selected_pet.add_task(task)
        st.success(f"✅ Task '{task_desc}' added to {selected_pet_name}!")
        st.rerun()

    # Display tasks for selected pet
    if selected_pet.tasks:
        st.subheader(f"{selected_pet_name}'s Tasks")
        for task in selected_pet.tasks:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.write(f"**{task.description}**")
            with col2:
                st.caption(f"{task.time_minutes}m")
            with col3:
                st.caption(task.frequency)
            with col4:
                st.caption(f"🔴 {task.priority}" if task.priority == "high" else f"🟡 {task.priority}" if task.priority == "medium" else f"🟢 {task.priority}")
            with col5:
                if st.button("❌", key=f"task_remove_{selected_pet_name}_{task.description}"):
                    selected_pet.remove_task(task.description)
                    st.rerun()
    else:
        st.info(f"No tasks yet. Add one above!")

else:
    st.warning("⚠️ Add a pet first!")

st.divider()

# ============================================================================
# SECTION 3: GENERATE SCHEDULE
# ============================================================================
st.header("3️⃣ Generate Daily Schedule")

available_minutes = st.number_input(
    "Available time today (minutes)",
    min_value=5,
    max_value=1440,
    value=120
)

if st.button("🎯 Generate Schedule"):
    if not st.session_state.owner.pets:
        st.error("❌ Add at least one pet first!")
    elif not any(pet.tasks for pet in st.session_state.owner.pets):
        st.error("❌ Add at least one task first!")
    else:
        # Build the daily plan
        plan = st.session_state.scheduler.build_daily_plan(
            st.session_state.owner,
            available_minutes=available_minutes
        )

        # Display the plan
        st.subheader("📋 Today's Schedule")
        st.markdown(st.session_state.scheduler.plan_summary(plan))

        # Show breakdown
        if plan:
            st.subheader("Task Breakdown")
            for i, (pet, task) in enumerate(plan, 1):
                with st.expander(f"{i}. [{pet.name}] {task.description}", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Time", f"{task.time_minutes} min")
                    with col2:
                        st.metric("Priority", task.priority)
                    with col3:
                        st.metric("Frequency", task.frequency)
                    with col4:
                        if st.button("✓ Mark Done", key=f"mark_done_{pet.name}_{task.description}"):
                            st.session_state.scheduler.mark_task_complete(
                                st.session_state.owner,
                                pet.name,
                                task.description
                            )
                            st.success(f"✅ Marked '{task.description}' as complete!")
                            st.rerun()
        else:
            st.warning("⚠️ No tasks fit in the available time. Increase available time or reduce task count.")
