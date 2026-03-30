
from pawpal_system import Owner, Pet, Task, TimeBlock, Scheduler, Priority, Frequency
from datetime import datetime, time

print("=" * 80)
print("          PawPal+ - Pet Care Scheduling System Demo")
print("=" * 80)

# Create owner with available time
owner_1 = Owner(name="Alice", available_time_per_day=480)  # 480 min = 8 hours
print(f"\n✓ Owner: {owner_1.name} with {owner_1.available_time_per_day} minutes available")

# Create pets
pet_1 = Pet(name="Fluffy", pet_type="Cat", age=3)
pet_2 = Pet(name="Buddy", pet_type="Dog", age=5)
owner_1.add_pet(pet_1)
owner_1.add_pet(pet_2)
print(f"✓ Pets: {pet_1.name} (Cat, age {pet_1.age}) and {pet_2.name} (Dog, age {pet_2.age})")

# Create tasks
task_1 = Task(
    name="Morning Walk",
    duration=30,
    priority=Priority.HIGH,
    category="Walk",
    frequency=Frequency.DAILY,
    preferred_time_window="morning"
)
task_2 = Task(
    name="Feed Breakfast",
    duration=15,
    priority=Priority.HIGH,
    category="Feeding",
    frequency=Frequency.DAILY,
    preferred_time_window="morning"
)
task_3 = Task(
    name="Play Session",
    duration=45,
    priority=Priority.MEDIUM,
    category="Enrichment",
    frequency=Frequency.DAILY,
    preferred_time_window="afternoon"
)
task_4 = Task(
    name="Evening Walk",
    duration=40,
    priority=Priority.HIGH,
    category="Walk",
    frequency=Frequency.DAILY,
    preferred_time_window="evening"
)
task_5 = Task(
    name="Dinner",
    duration=20,
    priority=Priority.MEDIUM,
    category="Feeding",
    frequency=Frequency.DAILY,
    preferred_time_window="evening"
)

# Add tasks to pets
pet_1.add_task(task_1)
pet_1.add_task(task_2)
pet_1.add_task(task_3)
pet_2.add_task(task_4)
pet_2.add_task(task_5)
print(f"\n✓ Tasks created and assigned to pets")

# Set owner's preferred timeblocks
preferred_blocks = [
    TimeBlock(start_time=time(9, 0), end_time=time(12, 30)),    # Morning: 3.5 hours
    TimeBlock(start_time=time(13, 0), end_time=time(16, 30)),   # Afternoon: 3.5 hours
    TimeBlock(start_time=time(17, 0), end_time=time(21, 0)),    # Evening: 4 hours
]
owner_1.set_preferred_timeblocks(preferred_blocks)
print(f"✓ Preferred timeblocks set")

# Generate schedules
print(f"\n{'=' * 80}")
print(f"Generating schedules...")
scheduler = Scheduler()

daily_schedule_fluffy = scheduler.optimize(owner_1, pet_1, pet_1.tasks)
daily_schedule_buddy = scheduler.optimize(owner_1, pet_2, pet_2.tasks)

# Display Fluffy's schedule
print(f"\n{'=' * 80}")
print(daily_schedule_fluffy.explain_schedule())

print(f"\nSummary for {pet_1.name}:")
summary_fluffy = daily_schedule_fluffy.get_schedule_summary()
for key, value in summary_fluffy.items():
    print(f"  • {key}: {value}")

# Display Buddy's schedule
print(f"\n{'=' * 80}")
print(daily_schedule_buddy.explain_schedule())

print(f"\nSummary for {pet_2.name}:")
summary_buddy = daily_schedule_buddy.get_schedule_summary()
for key, value in summary_buddy.items():
    print(f"  • {key}: {value}")

# Show detailed timeblock information
print(f"\n{'=' * 80}")
print(f"Timeblock Details for {pet_1.name}:")
print('-' * 80)
for i, block in enumerate(daily_schedule_fluffy.available_timeblocks, 1):
    print(f"Block {i}: {block.start_time} - {block.end_time} ({block.get_duration()} min)")
    if block.has_task():
        print(f"  Task: {block.task.name} ({block.task.duration} min)")
        print(f"  Available: {block.get_available_time()} min")
    else:
        print(f"  Available: {block.get_available_time()} min (empty)")

print(f"\n{'=' * 80}")
print("✅ Demo Completed Successfully!")
print("=" * 80)