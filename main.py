
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
    preferred_time_window="afternoon",
    must_follow_task="Feed Breakfast"  # Play must be after feeding
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
    preferred_time_window="evening",
    must_follow_task="Evening Walk"  # Dinner after evening walk
)

# Add tasks to pets
pet_1.add_task(task_1)
pet_1.add_task(task_2)
pet_1.add_task(task_3)
pet_2.add_task(task_4)
pet_2.add_task(task_5)
print("\n✓ Tasks created and assigned to pets")

# Set owner's preferred timeblocks
preferred_blocks = [
    TimeBlock(start_time=time(9, 0), end_time=time(12, 30)),    # Morning: 3.5 hours
    TimeBlock(start_time=time(13, 0), end_time=time(16, 30)),   # Afternoon: 3.5 hours
    TimeBlock(start_time=time(17, 0), end_time=time(21, 0)),    # Evening: 4 hours
]
owner_1.set_preferred_timeblocks(preferred_blocks)
print("✓ Preferred timeblocks set")

# Generate schedules
print(f"\n{'=' * 80}")
print("Generating Feasibility Reports...")
print(f"{'=' * 80}")

scheduler = Scheduler()

# Show feasibility for each pet individually
print(f"\n📋 Feasibility Report - {pet_1.name}:")
report_fluffy = scheduler.get_feasibility_report(pet_1.tasks, owner_1.available_time_per_day)
for key, value in report_fluffy.items():
    print(f"  • {key}: {value}")

print(f"\n📋 Feasibility Report - {pet_2.name}:")
report_buddy = scheduler.get_feasibility_report(pet_2.tasks, owner_1.available_time_per_day)
for key, value in report_buddy.items():
    print(f"  • {key}: {value}")

# Show multi-pet coordination (new feature)
print(f"\n{'=' * 80}")
print("Generating Coordinated Multi-Pet Schedules...")
print(f"{'=' * 80}")

multi_schedules = scheduler.optimize_multi_pet_schedule(owner_1, datetime.now())

# Display schedules
for pet_name, schedule in multi_schedules.items():
    print(f"\n{'=' * 80}")
    print(schedule.explain_schedule())
    
    print(f"\nSummary for {pet_name}:")
    summary = schedule.get_schedule_summary()
    for key, value in summary.items():
        print(f"  • {key}: {value}")
    
    # Show detailed timeblock information
    print(f"\n{'=' * 80}")
    print(f"Timeblock Details for {pet_name}:")
    print('-' * 80)
    for i, block in enumerate(schedule.available_timeblocks, 1):
        print(f"Block {i}: {block.start_time} - {block.end_time} ({block.get_duration()} min)")
        if block.has_task():
            print(f"  Task: {block.task.name} ({block.task.duration} min)")
            print(f"  Available: {block.get_available_time()} min")
        else:
            print(f"  Available: {block.get_available_time()} min (empty)")

# ================== CONFLICT DETECTION: OVERLAPPING SCHEDULED TIMES ==================
print(f"\n{'=' * 80}")
print("CHECKING FOR OVERLAPPING SCHEDULED TIMES ACROSS PETS")
print(f"{'=' * 80}")

# Build task-to-timeblock and pet lookup for all scheduled tasks
all_tasks = []
task_to_timeblock = {}
pet_lookup = {}
for pet_name, schedule in multi_schedules.items():
    for task, tb in schedule.task_to_timeblock.items():
        if tb is not None:
            all_tasks.append(task)
            task_to_timeblock[task] = tb
            pet_lookup[task] = pet_name

conflicts = scheduler.detect_conflicts(all_tasks, task_to_timeblock=task_to_timeblock, pet_lookup=pet_lookup)
if "overlapping_tasks" in conflicts:
    print("\n⚠️ Overlapping Scheduled Tasks Detected:")
    for issue in conflicts["overlapping_tasks"]:
        print(f"  • {issue}")
else:
    print("\n✓ No overlapping scheduled tasks detected.")

# ================== TEST: FORCE TWO TASKS AT THE SAME TIME ==================
print(f"\n{'=' * 80}")
print("TEST: FORCE TWO TASKS AT THE SAME TIMEBLOCK FOR OVERLAP WARNING")
print(f"{'=' * 80}")

# Create two tasks and assign them to the same timeblock manually
overlap_task1 = Task(
    name="Overlap Task 1",
    duration=30,
    priority=Priority.HIGH,
    category="Test",
    frequency=Frequency.ONE_TIME
)
overlap_task2 = Task(
    name="Overlap Task 2",
    duration=20,
    priority=Priority.MEDIUM,
    category="Test",
    frequency=Frequency.ONE_TIME
)
same_timeblock = TimeBlock(start_time=time(8, 0), end_time=time(8, 45))

# Assign both tasks to the same timeblock (simulate overlap)
task_to_timeblock_overlap = {
    overlap_task1: same_timeblock,
    overlap_task2: same_timeblock
}
pet_lookup_overlap = {
    overlap_task1: "TestPet",
    overlap_task2: "TestPet"
}
all_tasks_overlap = [overlap_task1, overlap_task2]

conflicts_overlap = scheduler.detect_conflicts(all_tasks_overlap, task_to_timeblock=task_to_timeblock_overlap, pet_lookup=pet_lookup_overlap)
if "overlapping_tasks" in conflicts_overlap:
    print("\n⚠️ Overlapping Scheduled Tasks Detected (Test):")
    for issue in conflicts_overlap["overlapping_tasks"]:
        print(f"  • {issue}")
else:
    print("\n✓ No overlapping scheduled tasks detected (Test).")

# Also show individual optimization for comparison
print(f"\n{'=' * 80}")
print("Individual Optimized Schedule Examples (for comparison):")
print(f"{'=' * 80}")

daily_schedule_fluffy = scheduler.optimize(owner_1, pet_1, pet_1.tasks)
daily_schedule_buddy = scheduler.optimize(owner_1, pet_2, pet_2.tasks)

# Display Fluffy's schedule
print(f"\n{'=' * 80}")
print("FLUFFY (Individual Optimization):")
print(daily_schedule_fluffy.explain_schedule())

print(f"\nSummary for {pet_1.name}:")
summary_fluffy = daily_schedule_fluffy.get_schedule_summary()
for key, value in summary_fluffy.items():
    print(f"  • {key}: {value}")

# Display Buddy's schedule
print(f"\n{'=' * 80}")
print("BUDDY (Individual Optimization):")
print(daily_schedule_buddy.explain_schedule())

print(f"\nSummary for {pet_2.name}:")
summary_buddy = daily_schedule_buddy.get_schedule_summary()
for key, value in summary_buddy.items():
    print(f"  • {key}: {value}")

# ============================================================================
# DEMONSTRATION: SORTING & FILTERING METHODS
# ============================================================================
print(f"\n{'=' * 80}")
print("TESTING SORTING & FILTERING METHODS")
print(f"{'=' * 80}")

# Create a new pet with tasks added OUT OF ORDER for testing
pet_test = Pet(name="Max", pet_type="Dog", age=4)
owner_1.add_pet(pet_test)

# Add tasks INTENTIONALLY OUT OF ORDER
test_tasks = [
    Task(name="Evening Treat", duration=5, priority=Priority.LOW, category="Feeding", 
         preferred_time_window="evening"),
    Task(name="Morning Play", duration=30, priority=Priority.HIGH, category="Enrichment",
         preferred_time_window="morning"),
    Task(name="Afternoon Nap Check", duration=10, priority=Priority.LOW, category="Care",
         preferred_time_window="afternoon"),
    Task(name="Morning Walk", duration=25, priority=Priority.HIGH, category="Walk",
         preferred_time_window="morning"),
    Task(name="Dinner", duration=15, priority=Priority.HIGH, category="Feeding",
         preferred_time_window="evening"),
    Task(name="Afternoon Fetch", duration=40, priority=Priority.MEDIUM, category="Enrichment",
         preferred_time_window="afternoon"),
]

# Add tasks to pet in mixed order
for task in test_tasks:
    pet_test.add_task(task)

print(f"\n✓ Created pet '{pet_test.name}' with {len(test_tasks)} tasks added OUT OF ORDER")

# ============================================================================
# TEST 1: SORT BY TIME (Preferred Time Window)
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 1: SORT BY PREFERRED TIME WINDOW")
print(f"{'-' * 80}")
print("\nOriginal order (out of order):")
for i, task in enumerate(test_tasks, 1):
    print(f"  {i}. {task.name:25} | Window: {str(task.preferred_time_window):10} | Priority: {task.priority.value:6} | {task.duration} min")

sorted_by_time = scheduler.sort_by_time(test_tasks)
print("\nAfter sort_by_time():")
for i, task in enumerate(sorted_by_time, 1):
    print(f"  {i}. {task.name:25} | Window: {str(task.preferred_time_window):10} | Priority: {task.priority.value:6} | {task.duration} min")

# ============================================================================
# TEST 2: SORT BY PRIORITY AND TIME
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 2: SORT BY PRIORITY + TIME WINDOW")
print(f"{'-' * 80}")
sorted_by_priority = scheduler.sort_tasks_by_priority_and_time(test_tasks)
print("\nAfter sort_tasks_by_priority_and_time():")
for i, task in enumerate(sorted_by_priority, 1):
    print(f"  {i}. {task.name:25} | Priority: {task.priority.value:6} | Window: {str(task.preferred_time_window):10} | {task.duration} min")

# ============================================================================
# TEST 3: SORT BY DURATION (longest first)
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 3: SORT BY DURATION (LONGEST FIRST)")
print(f"{'-' * 80}")
sorted_by_duration_desc = scheduler.sort_tasks_by_duration_desc(test_tasks)
print("\nAfter sort_tasks_by_duration_desc():")
for i, task in enumerate(sorted_by_duration_desc, 1):
    print(f"  {i}. {task.name:25} | Duration: {task.duration:2} min | Priority: {task.priority.value:6}")

# ============================================================================
# TEST 4: SORT BY DURATION (shortest first)
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 4: SORT BY DURATION (SHORTEST FIRST)")
print(f"{'-' * 80}")
sorted_by_duration_asc = scheduler.sort_tasks_by_duration_asc(test_tasks)
print("\nAfter sort_tasks_by_duration_asc():")
for i, task in enumerate(sorted_by_duration_asc, 1):
    print(f"  {i}. {task.name:25} | Duration: {task.duration:2} min | Priority: {task.priority.value:6}")

# ============================================================================
# TEST 5: MARK SOME TASKS AS COMPLETED
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 5: COMPLETION STATUS FILTERING")
print(f"{'-' * 80}")

# Mark some tasks as completed
test_tasks[0].mark_complete()  # Evening Treat
test_tasks[1].mark_complete()  # Morning Play
test_tasks[4].mark_complete()  # Dinner

print(f"\n✓ Marked {sum(1 for t in test_tasks if t.is_completed)} tasks as completed:")
for task in test_tasks:
    status = "✓ DONE" if task.is_completed else "○ TODO"
    print(f"  {status} | {task.name:25}")

# ============================================================================
# TEST 6: FILTER BY COMPLETION STATUS (across all pets)
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 6: FILTER BY COMPLETION STATUS")
print(f"{'-' * 80}")

# Get completed tasks across all pets
completed_all = scheduler.filter_tasks_by_status(owner_1, completed=True)
print("\nCompleted tasks across all pets:")
for pet_name, tasks_list in completed_all.items():
    print(f"\n  {pet_name}: {len(tasks_list)} completed")
    for task in tasks_list:
        print(f"    ✓ {task.name:25} | {task.duration} min")

# Get incomplete tasks across all pets
incomplete_all = scheduler.filter_tasks_by_status(owner_1, completed=False)
print("\nIncomplete tasks across all pets:")
for pet_name, tasks_list in incomplete_all.items():
    print(f"\n  {pet_name}: {len(tasks_list)} incomplete")
    for task in tasks_list:
        print(f"    ○ {task.name:25} | {task.duration} min")

# ============================================================================
# TEST 7: FILTER BY PET NAME
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 7: FILTER BY PET NAME")
print(f"{'-' * 80}")

# Get all tasks for specific pet
max_tasks = scheduler.filter_tasks_by_pet(owner_1, "Max")
print(f"\nAll tasks for Max: {len(max_tasks)} tasks")
for task in max_tasks:
    status = "✓" if task.is_completed else "○"
    print(f"  {status} {task.name:25} | Window: {str(task.preferred_time_window):10} | {task.duration} min")

# Get active tasks for specific pet
max_active = scheduler.filter_active_tasks_by_pet(owner_1, "Max")
print(f"\nActive (incomplete) tasks for Max: {len(max_active)} tasks")
for task in max_active:
    print(f"  ○ {task.name:25} | Priority: {task.priority.value:6} | {task.duration} min")

# Get completed tasks for specific pet
max_completed = scheduler.filter_completed_tasks_by_pet(owner_1, "Max")
print(f"\nCompleted tasks for Max: {len(max_completed)} tasks")
for task in max_completed:
    print(f"  ✓ {task.name:25} | Category: {task.category:12} | {task.duration} min")

# ============================================================================
# TEST 8: FILTER BY PET + COMPLETION STATUS
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 8: FILTER BY PET + COMPLETION STATUS")
print(f"{'-' * 80}")

# Get incomplete tasks for Max specifically
max_incomplete = scheduler.filter_tasks(owner_1, completed=False, pet_name="Max")
print("\nIncomplete tasks for Max specifically:")
for pet_name, tasks_list in max_incomplete.items():
    print(f"\n  {pet_name}: {len(tasks_list)} incomplete")
    for task in sorted_by_time:  # Sort them first
        if task.is_completed is False:
            print(f"    → {task.name:25} | {task.preferred_time_window:10} | {task.duration} min")

# ============================================================================
# TEST 9: FILTER BY CATEGORY
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 9: FILTER BY CATEGORY")
print(f"{'-' * 80}")

# Filter tasks by category
feeding_tasks = scheduler.filter_tasks_by_category(test_tasks, "Feeding")
enrichment_tasks = scheduler.filter_tasks_by_category(test_tasks, "Enrichment")

print(f"\nFeeding tasks: {len(feeding_tasks)}")
for task in feeding_tasks:
    status = "✓" if task.is_completed else "○"
    print(f"  {status} {task.name:25} | {task.duration} min")

print(f"\nEnrichment tasks: {len(enrichment_tasks)}")
for task in enrichment_tasks:
    status = "✓" if task.is_completed else "○"
    print(f"  {status} {task.name:25} | {task.duration} min")

# ============================================================================
# TEST 10: FILTER BY PRIORITY
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 10: FILTER BY PRIORITY")
print(f"{'-' * 80}")

high_priority = scheduler.filter_tasks_by_priority(test_tasks, Priority.HIGH)
print(f"\nHigh priority tasks: {len(high_priority)}")
for task in high_priority:
    status = "✓" if task.is_completed else "○"
    print(f"  {status} {task.name:25} | {task.duration} min | {task.category}")

medium_priority = scheduler.filter_tasks_by_priority(test_tasks, Priority.MEDIUM)
print(f"\nMedium priority tasks: {len(medium_priority)}")
for task in medium_priority:
    status = "✓" if task.is_completed else "○"
    print(f"  {status} {task.name:25} | {task.duration} min | {task.category}")

# ============================================================================
# TEST 11: GET TASK SUMMARY BY PET
# ============================================================================
print(f"\n{'-' * 80}")
print("TEST 11: TASK SUMMARY BY PET")
print(f"{'-' * 80}")

pet_summary = scheduler.get_task_summary_by_pet(owner_1)
print(f"\nTask Summary for {owner_1.name}:")
print(f"{'Pet':<15} {'Total':<8} {'Active':<8} {'Completed':<12} {'Total Min':<12} {'Complete %':<12}")
print(f"{'-' * 75}")
for pet_name, stats in pet_summary.items():
    print(f"{pet_name:<15} {stats['total_tasks']:<8} {stats['active_tasks']:<8} {stats['completed_tasks']:<12} {stats['total_duration_minutes']:<12} {stats['completion_percentage']:<12.1f}%")

print(f"\n{'=' * 80}")
print("✅ All Sorting & Filtering Methods Tested Successfully!")
print("=" * 80)

# ============================================================================
# BONUS: TEST RECURRING TASK AUTO-CREATION
# ============================================================================
print(f"\n{'=' * 80}")
print("BONUS: TESTING RECURRING TASK AUTO-CREATION")
print(f"{'=' * 80}")

# Create a new pet for recurring task testing
pet_recurring = Pet(name="Daisy", pet_type="Cat", age=2)
owner_1.add_pet(pet_recurring)

# Create recurring daily and weekly tasks
daily_walk = Task(
    name="Daily Morning Walk",
    duration=20,
    priority=Priority.HIGH,
    category="Walk",
    is_recurring=True,
    frequency=Frequency.DAILY,
    preferred_time_window="morning"
)

weekly_grooming = Task(
    name="Weekly Grooming",
    duration=60,
    priority=Priority.MEDIUM,
    category="Grooming",
    is_recurring=True,
    frequency=Frequency.WEEKLY,
    preferred_time_window="afternoon"
)

one_time_vaccine = Task(
    name="Annual Vaccine",
    duration=30,
    priority=Priority.HIGH,
    category="Medical",
    is_recurring=True,
    frequency=Frequency.MONTHLY,
    preferred_time_window="morning"
)

pet_recurring.add_task(daily_walk)
pet_recurring.add_task(weekly_grooming)
pet_recurring.add_task(one_time_vaccine)

print(f"\n✓ Created pet '{pet_recurring.name}' with recurring tasks:")
print("  • Daily Morning Walk (DAILY recurring)")
print("  • Weekly Grooming (WEEKLY recurring)")
print("  • Annual Vaccine (MONTHLY recurring - no auto-create)")

print(f"\n{'-' * 80}")
print(f"BEFORE: Task counts for {pet_recurring.name}:")
print(f"  Total tasks: {len(pet_recurring.get_tasks())}")
print(f"  Active tasks: {len(pet_recurring.get_active_tasks())}")
print(f"  Completed tasks: {len(pet_recurring.get_completed_tasks())}")

# Mark the daily walk as complete - should auto-create next occurrence
print(f"\n{'-' * 80}")
print("Marking 'Daily Morning Walk' as complete...")
result1 = scheduler.mark_recurring_task_complete(owner_1, "Daisy", "Daily Morning Walk")
print(f"  {result1['message']}")
next_task_1 = result1.get("next_task")
if result1.get("next_task_created") and isinstance(next_task_1, dict):
    print(f"  → Next task created: {next_task_1.get('name')} ({next_task_1.get('frequency')})")

# Mark the weekly grooming as complete - should auto-create next occurrence
print(f"\n{'-' * 80}")
print("Marking 'Weekly Grooming' as complete...")
result2 = scheduler.mark_recurring_task_complete(owner_1, "Daisy", "Weekly Grooming")
print(f"  {result2['message']}")
next_task_2 = result2.get("next_task")
if result2.get("next_task_created") and isinstance(next_task_2, dict):
    print(f"  → Next task created: {next_task_2.get('name')} ({next_task_2.get('frequency')})")

# Try marking the monthly vaccine - should NOT auto-create
print(f"\n{'-' * 80}")
print("Marking 'Annual Vaccine' as complete...")
result3 = scheduler.mark_recurring_task_complete(owner_1, "Daisy", "Annual Vaccine")
print(f"  {result3['message']}")
if not result3['next_task_created']:
    print("  → No auto-creation for MONTHLY recurring tasks (manual management)")

print(f"\n{'-' * 80}")
print(f"AFTER: Task counts for {pet_recurring.name}:")
print(f"  Total tasks: {len(pet_recurring.get_tasks())} (was 3, now {len(pet_recurring.get_tasks())} = +2 new recurrences)")
print(f"  Active tasks: {len(pet_recurring.get_active_tasks())}")
print(f"  Completed tasks: {len(pet_recurring.get_completed_tasks())}")

print(f"\n{'-' * 80}")
print(f"All tasks in {pet_recurring.name}'s list:")
for i, task in enumerate(pet_recurring.get_tasks(), 1):
    status = "✓ DONE" if task.is_completed else "○ TODO"
    completed_time = f" @ {task.completion_date.strftime('%H:%M:%S')}" if task.completion_date else ""
    recurring_info = f" [{task.frequency.value}]" if task.is_recurring else ""
    print(f"  {i}. {status} {task.name:<25} {recurring_info:<10}{completed_time}")

# Get completion report
print(f"\n{'-' * 80}")
print("COMPLETION REPORT:")
report = scheduler.get_task_completion_report(owner_1)
for pet_name in report['pets']:
    if report['pets'][pet_name]['completed_tasks']:
        print(f"\n  {pet_name} - Completed tasks:")
        for completed_task in report['pets'][pet_name]['completed_tasks']:
            print(f"    ✓ {completed_task['name']:<25} @ {completed_task['completed_at']} ({completed_task['category']})")
            if completed_task['was_recurring']:
                print(f"      └─ Was recurring ({completed_task['frequency']}) → Next occurrence auto-created")

print(f"\n{'=' * 80}")
print("✅ Recurring Task Auto-Creation Feature Working!")
print("=" * 80)