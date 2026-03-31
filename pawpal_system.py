"""
PawPal+ System - Pet Care Scheduling Application
Core classes for managing owners, pets, tasks, and daily schedules.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, time, timedelta
from enum import Enum
from collections import defaultdict
from itertools import combinations



class Priority(Enum):
    """Task priority levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Frequency(Enum):
    """Task recurrence frequency"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    BIWEEKLY = "BIWEEKLY"
    MONTHLY = "MONTHLY"
    ONE_TIME = "ONE_TIME"


@dataclass(unsafe_hash=True)
class Task:
    """Represents a pet care task"""
    name: str
    duration: int  # in minutes
    priority: Priority
    category: str
    is_recurring: bool = False
    frequency: Optional[Frequency] = None
    preferred_time_window: Optional[str] = None  # "morning", "afternoon", "evening"
    must_follow_task: Optional[str] = None  # name of task that must complete first
    min_interval_after: int = 0  # minimum minutes between this task and next
    is_completed: bool = False  # tracks if task has been completed
    completion_date: Optional[datetime] = None  # tracks when task was completed
    due_date: Optional[datetime] = None  # tracks when task is due (for recurring tasks)
    
    def is_high_priority(self) -> bool:
        """Check if task is high priority"""
        return self.priority == Priority.HIGH
    
    def can_fit_in_timeblock(self, timeblock: 'TimeBlock') -> bool:
        """Check if task can fit in given timeblock"""
        return self.duration <= timeblock.get_duration()
    
    def mark_complete(self) -> None:
        """Mark this task as completed with timestamp"""
        self.is_completed = True
        self.completion_date = datetime.now()
    
    def create_duplicate(self) -> 'Task':
        """Create a new instance of this task (for recurring task next occurrence)"""
        next_due_date = None
        
        # Calculate next due date based on frequency using timedelta
        if self.is_recurring and self.frequency:
            # Use current due date or today as base
            if self.due_date:
                base_date = self.due_date
            else:
                base_date = datetime.now()
            
            # Map frequency to days using timedelta
            frequency_days = {
                Frequency.DAILY: 1,
                Frequency.WEEKLY: 7,
                Frequency.BIWEEKLY: 14,
                Frequency.MONTHLY: 30,
                Frequency.ONE_TIME: None
            }
            
            days_to_add = frequency_days.get(self.frequency)
            if days_to_add is not None:
                next_due_date = base_date + timedelta(days=days_to_add)
        
        return Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            category=self.category,
            is_recurring=self.is_recurring,
            frequency=self.frequency,
            preferred_time_window=self.preferred_time_window,
            must_follow_task=self.must_follow_task,
            min_interval_after=self.min_interval_after,
            is_completed=False,
            completion_date=None,
            due_date=next_due_date
        )


@dataclass
class TimeBlock:
    """Represents a time slot in the daily schedule"""
    start_time: time
    end_time: time
    task: Optional[Task] = None
    
    def get_duration(self) -> int:
        """Get duration of timeblock in minutes"""
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        return end_minutes - start_minutes
    
    def has_task(self) -> bool:
        """Check if timeblock has an assigned task"""
        return self.task is not None
    
    def get_available_time(self) -> int:
        """Get available time in timeblock (accounting for assigned task if any)"""
        total_duration = self.get_duration()
        if self.has_task():
            return total_duration - self.task.duration
        return total_duration
    
    def assign_task(self, task: Task) -> bool:
        """Assign a task to this timeblock"""
        if task.can_fit_in_timeblock(self):
            self.task = task
            return True
        return False


@dataclass
class Pet:
    """Represents a pet"""
    name: str
    pet_type: str  # dog, cat, bird, etc.
    age: int  # in years
    tasks: List[Task] = field(default_factory=list)
    
    def add_task(self, task: Task) -> None:
        """Add a task for this pet"""
        self.tasks.append(task)
    
    def remove_task(self, task_name: str) -> None:
        """Remove a task by name"""
        self.tasks = [t for t in self.tasks if t.name != task_name]
    
    def get_tasks(self) -> List[Task]:
        """Get all tasks for this pet"""
        return self.tasks
    
    def get_tasks_by_status(self, completed: bool = False) -> List[Task]:
        """Filter tasks by completion status"""
        return [t for t in self.tasks if t.is_completed == completed]
    
    def get_active_tasks(self) -> List[Task]:
        """Get only incomplete tasks"""
        return self.get_tasks_by_status(completed=False)
    
    def get_completed_tasks(self) -> List[Task]:
        """Get only completed tasks"""
        return self.get_tasks_by_status(completed=True)
    
    def mark_task_complete_with_recurrence(self, task_name: str) -> Optional[Task]:
        """
        Mark a task as complete and create the next occurrence if it's recurring.
        
        Args:
            task_name: Name of the task to mark complete
        
        Returns:
            The newly created task for next occurrence (if recurring), else None
        """
        # Find the task
        task = next((t for t in self.tasks if t.name == task_name), None)
        if not task:
            return None
        
        # Mark as complete
        task.mark_complete()
        
        # If recurring, create next occurrence
        if task.is_recurring and task.frequency in [Frequency.DAILY, Frequency.WEEKLY]:
            next_task = task.create_duplicate()
            self.add_task(next_task)
            return next_task
        
        return None


class Owner:
    """Represents a pet owner"""
    
    def __init__(self, name: str, available_time_per_day: float):
        """Initialize an owner with name and available daily time."""
        self.name: str = name
        self.available_time_per_day: float = available_time_per_day  # in minutes
        self.preferred_timeblocks: List[TimeBlock] = []
        self.preferences: Dict[str, Any] = {
            "compact_schedule": True,          # cluster tasks vs spread them
            "prefer_morning": False,           # prefer morning tasks
            "rest_between_minutes": 30,        # minimum rest between tasks
        }
        self.pets: List[Pet] = []
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to owner's list"""
        self.pets.append(pet)
    
    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name"""
        self.pets = [p for p in self.pets if p.name != pet_name]
    
    def add_task(self, pet_name: str, task: Task) -> None:
        """Add a task for a specific pet"""
        for pet in self.pets:
            if pet.name == pet_name:
                pet.add_task(task)
                return
    
    def remove_task(self, pet_name: str, task_name: str) -> None:
        """Remove a task for a specific pet"""
        for pet in self.pets:
            if pet.name == pet_name:
                pet.remove_task(task_name)
                return
    
    def get_available_time(self) -> float:
        """Get total available time for pet care"""
        return self.available_time_per_day
    
    def set_preferred_timeblocks(self, timeblocks: List[TimeBlock]) -> None:
        """Set owner's preferred time slots"""
        self.preferred_timeblocks = timeblocks
    
    def get_all_tasks_by_status(self, completed: bool = False) -> Dict[str, List[Task]]:
        """Get all tasks across all pets, grouped by status"""
        result = {}
        for pet in self.pets:
            result[pet.name] = pet.get_tasks_by_status(completed=completed)
        return result
    
    def get_all_active_tasks(self) -> Dict[str, List[Task]]:
        """Get all incomplete tasks across all pets"""
        return self.get_all_tasks_by_status(completed=False)
    
    def get_all_completed_tasks(self) -> Dict[str, List[Task]]:
        """Get all completed tasks across all pets"""
        return self.get_all_tasks_by_status(completed=True)


class DailySchedule:

    """Represents a single day's schedule"""
    
    def __init__(self, owner: Owner, pet: Pet, date: datetime):
        """Initialize a daily schedule for a pet and owner on a specific date."""
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.date: datetime = date
        self.scheduled_tasks: List[Task] = []
        self.available_timeblocks: List[TimeBlock] = []
        self.task_to_timeblock: Dict[Task, TimeBlock] = {}  # explicit task-to-timeblock mapping
        self.unscheduled_tasks: List[Task] = []  # tasks that couldn't fit in schedule
    
    def generate_schedule(self) -> None:
        """Generate the daily schedule based on tasks and constraints"""
        scheduler = Scheduler()
        self.available_timeblocks = scheduler.generate_daily_timeblocks(self.owner, self.date)
        tasks = self.pet.get_tasks()
        
        if tasks:
            prioritized = scheduler.prioritize_tasks(tasks)
            task_assignments = scheduler.fit_tasks_in_timeblocks(prioritized, self.available_timeblocks)
            
            for task, timeblock in task_assignments.items():
                if timeblock:
                    self.add_scheduled_task(task, timeblock)
                else:
                    self.unscheduled_tasks.append(task)
    
    def add_scheduled_task(self, task: Task, timeblock: TimeBlock) -> None:
        """Add a task to the schedule at a specific timeblock"""
        if timeblock.assign_task(task):
            self.scheduled_tasks.append(task)
            self.task_to_timeblock[task] = timeblock
    
    def explain_schedule(self) -> str:
        """Generate human-readable explanation of why tasks were scheduled as they are"""
        explanation = f"Daily Schedule for {self.pet.name} on {self.date.strftime('%Y-%m-%d')}\n"
        explanation += f"Owner: {self.owner.name} | Available Time: {self.owner.available_time_per_day} minutes\n\n"
        explanation += f"Scheduled Tasks ({len(self.scheduled_tasks)}):\n"
        
        for task in self.scheduled_tasks:
            if task in self.task_to_timeblock:
                tb = self.task_to_timeblock[task]
                explanation += f"  - {task.name}: {tb.start_time}-{tb.end_time} ({task.duration} min) [Priority: {task.priority.value}]\n"
        
        if self.unscheduled_tasks:
            explanation += f"\nUnscheduled Tasks ({len(self.unscheduled_tasks)}) - Could not fit:\n"
            for task in self.unscheduled_tasks:
                explanation += f"  - {task.name} ({task.duration} min)\n"
        
        return explanation
    
    def get_schedule_summary(self) -> Dict:
        """Get a summary of the full day's schedule"""
        total_scheduled_time = sum(t.duration for t in self.scheduled_tasks)
        return {
            "date": self.date.isoformat(),
            "pet_name": self.pet.name,
            "owner_name": self.owner.name,
            "total_available_minutes": self.owner.available_time_per_day,
            "scheduled_tasks_count": len(self.scheduled_tasks),
            "unscheduled_tasks_count": len(self.unscheduled_tasks),
            "total_scheduled_minutes": total_scheduled_time,
            "utilization_percentage": round((total_scheduled_time / self.owner.available_time_per_day) * 100, 1)
        }


class Scheduler:
    """Handles scheduling logic and optimization"""
    
    def generate_daily_timeblocks(self, owner: Owner, date: datetime) -> List[TimeBlock]:
        """Convert owner's preferred timeblocks into actual day's timeblocks"""
        if owner.preferred_timeblocks:
            # Create fresh copies of preferred timeblocks for this schedule
            return [TimeBlock(start_time=tb.start_time, end_time=tb.end_time) for tb in owner.preferred_timeblocks]
        else:
            # Default: 9 AM to 9 PM in 4-hour blocks
            return [
                TimeBlock(start_time=time(9, 0), end_time=time(13, 0)),
                TimeBlock(start_time=time(13, 0), end_time=time(17, 0)),
                TimeBlock(start_time=time(17, 0), end_time=time(21, 0)),
            ]
    
    def optimize(self, owner: Owner, pet: Pet, tasks: List[Task]) -> DailySchedule:
        """Create an optimized daily schedule"""
        # Validate feasibility before attempting to schedule
        if not self._validate_schedule_feasibility(tasks, owner.available_time_per_day):
            print(f"⚠️ WARNING: Total task duration ({sum(t.duration for t in tasks)} min) exceeds available time ({owner.available_time_per_day} min)")
        
        schedule = DailySchedule(owner, pet, date=datetime.now())
        schedule.generate_schedule()
        return schedule
    
    def optimize_multi_pet_schedule(self, owner: Owner, date: datetime) -> Dict[str, DailySchedule]:
        """Create coordinated schedules for all pets, fairly allocating owner's available time"""
        schedules = {}  # Key: pet name, Value: DailySchedule
        total_time_used = 0
        
        if not owner.pets:
            print("⚠️ No pets to schedule")
            return schedules
        
        # Calculate total required time across all pets
        total_required_time = sum(sum(task.duration for task in pet.tasks) for pet in owner.pets)
        available_time = owner.available_time_per_day
        
        # Check if globally feasible
        if total_required_time > available_time:
            print(f"⚠️ CONFLICT: Pets require {total_required_time} min but owner has only {available_time} min available")
            print(f"   Allocation per pet: {available_time / len(owner.pets):.0f} min each")
        
        # Generate schedule for each pet
        for pet in owner.pets:
            schedule = self.optimize(owner, pet, pet.tasks)
            schedules[pet.name] = schedule  # Use pet name as key
            total_time_used += sum(t.duration for t in schedule.scheduled_tasks)
        
        # Summary
        print(f"\n📊 Multi-Pet Schedule Summary for {owner.name}:")
        print(f"   Total pets: {len(owner.pets)}")
        print(f"   Owner available time: {available_time} min")
        print(f"   Total time scheduled: {total_time_used} min")
        print(f"   Utilization: {(total_time_used / available_time * 100):.1f}%")
        
        return schedules
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority and constraints, respecting task dependencies"""
        # First, sort by priority (HIGH > MEDIUM > LOW) and duration (longer first)
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        base_sorted = sorted(tasks, key=lambda t: (priority_order[t.priority], -t.duration))
        
        # Enforce task dependencies: tasks with must_follow_task go  after their dependencies
        ordered_tasks = []
        remaining = list(base_sorted)
        
        while remaining:
            for task in remaining:
                # If task has no dependency, or dependency is already scheduled, add it
                if not task.must_follow_task:
                    ordered_tasks.append(task)
                    remaining.remove(task)
                    break
                else:
                    # Check if dependency is already scheduled
                    dependency_scheduled = any(t.name == task.must_follow_task for t in ordered_tasks)
                    if dependency_scheduled:
                        ordered_tasks.append(task)
                        remaining.remove(task)
                        break
            else:
                # If we get here, there might be circular dependencies or missing dependencies
                # Just add remaining tasks in order (fallback)
                if remaining:
                    ordered_tasks.extend(remaining)
                    break
        
        return ordered_tasks
    
    def fit_tasks_in_timeblocks(
        self, tasks: List[Task], timeblocks: List[TimeBlock]
    ) -> Dict[Task, Optional[TimeBlock]]:
        """Assign tasks to timeblocks based on availability"""
        assignments = {}
        available_blocks = [tb for tb in timeblocks]  # copy list
        
        for task in tasks:
            best_block = self._find_best_timeblock(task, available_blocks)
            if best_block:
                assignments[task] = best_block
                best_block.task = task  # assign task to block
                available_blocks.remove(best_block)  # remove from available
            else:
                assignments[task] = None
        
        return assignments
    
    def _validate_schedule_feasibility(self, tasks: List[Task], available_minutes: float) -> bool:
        """Check if total task duration fits in available time"""
        total_duration = sum(task.duration for task in tasks)
        return total_duration <= available_minutes
    
    def get_feasibility_report(self, tasks: List[Task], available_minutes: float) -> Dict:
        """Generate detailed feasibility report for scheduling"""
        total_duration = sum(task.duration for task in tasks)
        high_priority_tasks = [t for t in tasks if t.priority == Priority.HIGH]
        medium_priority_tasks = [t for t in tasks if t.priority == Priority.MEDIUM]
        low_priority_tasks = [t for t in tasks if t.priority == Priority.LOW]
        
        high_priority_duration = sum(t.duration for t in high_priority_tasks)
        
        report = {
            "total_tasks": len(tasks),
            "total_duration": total_duration,
            "available_minutes": available_minutes,
            "feasible": total_duration <= available_minutes,
            "utilization_percentage": round((total_duration / available_minutes * 100), 1) if available_minutes > 0 else 0,
            "high_priority_count": len(high_priority_tasks),
            "high_priority_duration": high_priority_duration,
            "medium_priority_count": len(medium_priority_tasks),
            "low_priority_count": len(low_priority_tasks),
            "tasks_with_dependencies": len([t for t in tasks if t.must_follow_task]),
            "recurring_tasks": len([t for t in tasks if t.is_recurring]),
        }
        
        return report
    
    def _calculate_task_score(self, task: Task) -> float:
        """Calculate a score for task prioritization"""
        priority_score = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        return priority_score[task.priority]
    
    def _find_best_timeblock(self, task: Task, timeblocks: List[TimeBlock]) -> Optional[TimeBlock]:
        """Find the best timeblock for a given task"""
        for block in timeblocks:
            if task.can_fit_in_timeblock(block) and not block.has_task():
                # Prefer timeblock matching task's preferred window if specified
                if task.preferred_time_window:
                    hour = block.start_time.hour
                    if (task.preferred_time_window == "morning" and 6 <= hour < 12) or \
                       (task.preferred_time_window == "afternoon" and 12 <= hour < 17) or \
                       (task.preferred_time_window == "evening" and 17 <= hour < 21):
                        return block
                else:
                    return block
        
        # If no preferred time match, return any available block
        for block in timeblocks:
            if task.can_fit_in_timeblock(block) and not block.has_task():
                return block
        
        return None
    
    def sort_tasks_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by preferred time window (morning, afternoon, evening)"""
        time_window_order = {"morning": 0, "afternoon": 1, "evening": 2, None: 3}
        return sorted(tasks, key=lambda t: time_window_order.get(t.preferred_time_window, 3))
    
    def sort_by_time(self, tasks: List[Task], task_to_timeblock: Optional[Dict[Task, TimeBlock]] = None) -> List[Task]:
        """
        Sort Task objects by their time attribute.
        
        If task_to_timeblock mapping is provided, sorts by actual scheduled start time.
        Otherwise, sorts by preferred time window, with fallback to alphabetical order.
        
        Args:
            tasks: List of tasks to sort
            task_to_timeblock: Optional mapping of tasks to their assigned timeblocks
        
        Returns:
            Sorted list of tasks by time
        """
        if task_to_timeblock:
            # Sort by actual scheduled start time
            return sorted(
                tasks,
                key=lambda t: (
                    task_to_timeblock[t].start_time if t in task_to_timeblock and task_to_timeblock[t] else time(23, 59),
                    t.name  # Secondary sort by name for tasks without timeblocks
                )
            )
        else:
            # Sort by preferred time window order, then by duration (longer first), then by name
            time_window_order = {"morning": 0, "afternoon": 1, "evening": 2, None: 3}
            return sorted(
                tasks,
                key=lambda t: (
                    time_window_order.get(t.preferred_time_window, 3),
                    -t.duration,  # Longer tasks first
                    t.name  # Alphabetical fallback
                )
            )
    
    def sort_by_start_time(self, timeblocks: List[TimeBlock]) -> List[TimeBlock]:
        """Sort timeblocks by their start time"""
        return sorted(timeblocks, key=lambda tb: tb.start_time)
    
    def sort_tasks_by_duration_desc(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by duration in descending order (longest first) - helps with packing"""
        return sorted(tasks, key=lambda t: -t.duration)
    
    def sort_tasks_by_duration_asc(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by duration in ascending order (shortest first)"""
        return sorted(tasks, key=lambda t: t.duration)
    
    def sort_tasks_by_priority_and_time(self, tasks: List[Task]) -> List[Task]:
        """
        Sort tasks by priority first, then by preferred time window.
        Ensures high-priority tasks are scheduled in preferred time slots first.
        """
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        time_window_order = {"morning": 0, "afternoon": 1, "evening": 2, None: 3}
        
        return sorted(
            tasks,
            key=lambda t: (
                priority_order[t.priority],
                time_window_order.get(t.preferred_time_window, 3),
                -t.duration  # Longer tasks first within same priority/window
            )
        )
    
    def expand_recurring_tasks(self, tasks: List[Task], days: int = 7) -> Dict[int, List[Task]]:
        """Expand recurring tasks across multiple days"""
        expanded = {}
        
        for day in range(days):
            expanded[day] = []
            for task in tasks:
                if not task.is_recurring:
                    # Non-recurring tasks only on day 0
                    if day == 0:
                        expanded[day].append(task)
                else:
                    # Recurring logic based on frequency
                    should_include = False
                    if task.frequency == Frequency.DAILY:
                        should_include = True
                    elif task.frequency == Frequency.WEEKLY:
                        should_include = (day % 7 == 0)
                    elif task.frequency == Frequency.BIWEEKLY:
                        should_include = (day % 14 == 0)
                    elif task.frequency == Frequency.MONTHLY:
                        should_include = (day % 30 == 0)
                    elif task.frequency == Frequency.ONE_TIME:
                        should_include = (day == 0)
                    
                    if should_include:
                        expanded[day].append(task)
        
        return expanded
    def detect_conflicts(
        self,
        tasks: List[Task],
        task_to_timeblock: Optional[Dict[Task, 'TimeBlock']] = None,
        pet_lookup: Optional[Dict[Task, str]] = None
    ) -> Dict[str, List[str]]:
        """Lightweight conflict detection: returns warnings, never crashes."""
        try:
            from collections import defaultdict
            from itertools import combinations
            conflicts = defaultdict(list)

            # Precompute lookups
            task_by_name = {t.name: t for t in tasks}
            task_names = set(task_by_name.keys())

            # --- 1. Missing dependencies ---
            for task in tasks:
                dep = task.must_follow_task
                if dep and dep not in task_names:
                    conflicts["missing_dependencies"].append(
                        f"Task '{task.name}' depends on '{dep}' which doesn't exist"
                    )

            # --- 2. Circular dependencies ---
            for task in tasks:
                visited = set()
                current = task.name

                while current:
                    if current in visited:
                        conflicts["circular_dependencies"].append(
                            f"Circular dependency detected involving '{current}'"
                        )
                        break

                    visited.add(current)
                    current_task = task_by_name.get(current)
                    current = current_task.must_follow_task if current_task else None

            # --- 3. Unschedulable high-priority tasks ---
            high_priority_duration = sum(t.duration for t in tasks if t.is_high_priority())
            if high_priority_duration > 200:
                conflicts["unschedulable_tasks"].append(
                    f"High-priority tasks total {high_priority_duration} min - may be unschedulable"
                )

            # --- 4. Time window overload ---
            time_windows = defaultdict(list)
            for t in tasks:
                if t.preferred_time_window:
                    time_windows[t.preferred_time_window].append(t)

            for window, window_tasks in time_windows.items():
                total = sum(t.duration for t in window_tasks)
                if total > 240:
                    conflicts["time_conflicts"].append(
                        f"Too many tasks preferred for {window} ({total} min total)"
                    )

            # --- 5. Overlapping scheduled tasks ---
            if task_to_timeblock:
                scheduled = [
                    (task, pet_lookup.get(task, "?"), tb.start_time, tb.end_time)
                    for task, tb in task_to_timeblock.items()
                    if tb is not None
                ]

                for (t1, pet1, s1, e1), (t2, pet2, s2, e2) in combinations(scheduled, 2):
                    if s1 < e2 and s2 < e1:
                        conflicts["overlapping_tasks"].append(
                            f"Task '{t1.name}' (pet: {pet1}, {s1}-{e1}) overlaps with "
                            f"'{t2.name}' (pet: {pet2}, {s2}-{e2})"
                        )

            # Return only non-empty categories
            return {k: v for k, v in conflicts.items() if v}

        except Exception as e:
            return {"warning": [f"Conflict detection failed: {str(e)}"]}
    
    def get_conflict_summary(self, tasks: List[Task]) -> str:
        """Get human-readable conflict summary"""
        conflicts = self.detect_conflicts(tasks)
        if not conflicts:
            return "✓ No conflicts detected"
        
        summary = "⚠️ Scheduling Conflicts Detected:\n"
        for conflict_type, issues in conflicts.items():
            summary += f"\n{conflict_type.replace('_', ' ').title()}:\n"
            for issue in issues:
                summary += f"  • {issue}\n"
        return summary
    
    def filter_tasks(self, owner: Owner, completed: Optional[bool] = None, pet_name: Optional[str] = None) -> Dict[str, List[Task]]:
        """
        Filter tasks by completion status and/or pet name.
        
        Args:
            owner: The pet owner whose tasks to filter
            completed: Filter by completion status (True=completed, False=incomplete, None=all)
            pet_name: Filter by specific pet name (None=all pets)
        
        Returns:
            Dictionary with pet names as keys and filtered task lists as values
        """
        result = {}
        
        # Determine which pets to include
        pets_to_check = []
        if pet_name:
            # Filter to specific pet
            matching_pets = [p for p in owner.pets if p.name == pet_name]
            if not matching_pets:
                return result  # Pet not found
            pets_to_check = matching_pets
        else:
            # All pets
            pets_to_check = owner.pets
        
        # Filter tasks for each pet
        for pet in pets_to_check:
            if completed is None:
                # Return all tasks
                filtered = pet.get_tasks()
            else:
                # Return tasks by completion status
                filtered = pet.get_tasks_by_status(completed=completed)
            
            if filtered:  # Only add pets with matching tasks
                result[pet.name] = filtered
        
        return result
    
    def filter_tasks_by_status(self, owner: Owner, completed: bool) -> Dict[str, List[Task]]:
        """
        Filter all tasks across all pets by completion status.
        
        Args:
            owner: The pet owner
            completed: True for completed tasks, False for incomplete
        
        Returns:
            Dictionary with pet names as keys and filtered task lists as values
        """
        return self.filter_tasks(owner, completed=completed, pet_name=None)
    
    def filter_tasks_by_pet(self, owner: Owner, pet_name: str) -> List[Task]:
        """
        Get all tasks for a specific pet (both completed and incomplete).
        
        Args:
            owner: The pet owner
            pet_name: Name of the pet
        
        Returns:
            List of all tasks for that pet, or empty list if pet not found
        """
        filtered = self.filter_tasks(owner, completed=None, pet_name=pet_name)
        return filtered.get(pet_name, [])
    
    def filter_completed_tasks_by_pet(self, owner: Owner, pet_name: str) -> List[Task]:
        """
        Get completed tasks for a specific pet.
        
        Args:
            owner: The pet owner
            pet_name: Name of the pet
        
        Returns:
            List of completed tasks for that pet
        """
        filtered = self.filter_tasks(owner, completed=True, pet_name=pet_name)
        return filtered.get(pet_name, [])
    
    def filter_active_tasks_by_pet(self, owner: Owner, pet_name: str) -> List[Task]:
        """
        Get incomplete (active) tasks for a specific pet.
        
        Args:
            owner: The pet owner
            pet_name: Name of the pet
        
        Returns:
            List of incomplete tasks for that pet
        """
        filtered = self.filter_tasks(owner, completed=False, pet_name=pet_name)
        return filtered.get(pet_name, [])
    
    def filter_tasks_by_category(self, tasks: List[Task], category: str) -> List[Task]:
        """
        Filter tasks by category.
        
        Args:
            tasks: List of tasks to filter
            category: Category name to filter by
        
        Returns:
            List of tasks matching the category
        """
        return [t for t in tasks if t.category.lower() == category.lower()]
    
    def filter_tasks_by_priority(self, tasks: List[Task], priority: Priority) -> List[Task]:
        """
        Filter tasks by priority level.
        
        Args:
            tasks: List of tasks to filter
            priority: Priority level to filter by
        
        Returns:
            List of tasks with specified priority
        """
        return [t for t in tasks if t.priority == priority]
    
    def filter_recurring_tasks(self, tasks: List[Task]) -> List[Task]:
        """
        Get only recurring tasks from a task list.
        
        Args:
            tasks: List of tasks to filter
        
        Returns:
            List of recurring tasks only
        """
        return [t for t in tasks if t.is_recurring]
    
    def get_task_summary_by_pet(self, owner: Owner) -> Dict[str, Dict]:
        """
        Get a summary of task counts for each pet.
        
        Args:
            owner: The pet owner
        
        Returns:
            Dictionary with pet names as keys and task summary stats as values
        """
        summary = {}
        for pet in owner.pets:
            all_tasks = pet.get_tasks()
            active = pet.get_active_tasks()
            completed = pet.get_completed_tasks()
            
            summary[pet.name] = {
                "total_tasks": len(all_tasks),
                "active_tasks": len(active),
                "completed_tasks": len(completed),
                "total_duration_minutes": sum(t.duration for t in all_tasks),
                "active_duration_minutes": sum(t.duration for t in active),
                "completion_percentage": round((len(completed) / len(all_tasks) * 100), 1) if all_tasks else 0
            }
        
        return summary
    
    def create_next_recurring_task(self, task: Task) -> Optional[Task]:
        """
        Create the next occurrence of a recurring task.
        Automatically adds it to the pet's task list if task is daily or weekly.
        
        Args:
            task: The completed recurring task
        
        Returns:
            The newly created task instance, or None if not recurring
        """
        if not task.is_recurring:
            return None
        
        # Only auto-create for DAILY and WEEKLY (others can be managed differently)
        if task.frequency not in [Frequency.DAILY, Frequency.WEEKLY]:
            return None
        
        # Create duplicate
        next_task = task.create_duplicate()
        return next_task
    
    def mark_recurring_task_complete(self, owner: Owner, pet_name: str, task_name: str) -> Dict[str, Any]:
        """
        High-level method to mark a recurring task complete and auto-create next occurrence.
        
        Args:
            owner: The pet owner
            pet_name: Name of the pet
            task_name: Name of the task to complete
        
        Returns:
            Dictionary with completion info and next task details (if created)
        """
        result = {
            "success": False,
            "pet_name": pet_name,
            "task_name": task_name,
            "task_marked_complete": False,
            "next_task_created": False,
            "next_task": None,
            "message": ""
        }
        
        # Find the pet
        pet = next((p for p in owner.pets if p.name == pet_name), None)
        if not pet:
            result["message"] = f"Pet '{pet_name}' not found"
            return result
        
        # Find the task
        task = next((t for t in pet.tasks if t.name == task_name), None)
        if not task:
            result["message"] = f"Task '{task_name}' not found for {pet_name}"
            return result
        
        # Mark task complete
        task.mark_complete()
        result["task_marked_complete"] = True
        result["message"] = f"✓ Task '{task_name}' marked complete at {task.completion_date.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Handle recurring tasks
        if task.is_recurring:
            frequency = task.frequency.value if task.frequency else "unknown"
            if task.frequency in [Frequency.DAILY, Frequency.WEEKLY]:
                next_task = self.create_next_recurring_task(task)
                if next_task:
                    pet.add_task(next_task)
                    result["next_task_created"] = True
                    next_due_str = next_task.due_date.strftime('%Y-%m-%d') if next_task.due_date else "N/A"
                    result["next_task"] = {
                        "name": next_task.name,
                        "frequency": frequency,
                        "duration": next_task.duration,
                        "priority": next_task.priority.value,
                        "due_date": next_due_str
                    }
                    result["message"] += f" | Next {frequency.lower()} occurrence auto-created (Due: {next_due_str})"
            else:
                result["message"] += f" | Recurring task ({frequency}) - no auto-creation for this frequency"
        
        result["success"] = True
        return result
    
    def get_task_completion_report(self, owner: Owner) -> Dict[str, Any]:
        """
        Get a comprehensive report of completed tasks and auto-created recurrences.
        
        Args:
            owner: The pet owner
        
        Returns:
            Dictionary with completion statistics
        """
        report = {
            "owner_name": owner.name,
            "pets": {}
        }
        
        for pet in owner.pets:
            completed = pet.get_completed_tasks()
            active = pet.get_active_tasks()
            report["pets"][pet.name] = {
                "total_completed": len(completed),
                "completed_tasks": [],
                "active_tasks": [],
                "recurring_auto_created": 0
            }
            
            for task in completed:
                task_info = {
                    "name": task.name,
                    "category": task.category,
                    "completed_at": task.completion_date.strftime('%Y-%m-%d %H:%M:%S') if task.completion_date else "unknown",
                    "was_recurring": task.is_recurring,
                    "frequency": task.frequency.value if task.frequency else None
                }
                report["pets"][pet.name]["completed_tasks"].append(task_info)
            
            for task in active:
                due_date_str = task.due_date.strftime('%Y-%m-%d') if task.due_date else "N/A"
                task_info = {
                    "name": task.name,
                    "category": task.category,
                    "due_date": due_date_str,
                    "is_recurring": task.is_recurring,
                    "frequency": task.frequency.value if task.frequency else None,
                    "duration": task.duration
                }
                report["pets"][pet.name]["active_tasks"].append(task_info)
        
        return report
