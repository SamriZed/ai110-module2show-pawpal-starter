"""
PawPal+ System - Pet Care Scheduling Application
Core classes for managing owners, pets, tasks, and daily schedules.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime, time
from enum import Enum


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
    
    def is_high_priority(self) -> bool:
        """Check if task is high priority"""
        return self.priority == Priority.HIGH
    
    def can_fit_in_timeblock(self, timeblock: 'TimeBlock') -> bool:
        """Check if task can fit in given timeblock"""
        return self.duration <= timeblock.get_duration()
    
    def mark_complete(self) -> None:
        """Mark this task as completed"""
        self.is_completed = True


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


class Owner:
    """Represents a pet owner"""
    
    def __init__(self, name: str, available_time_per_day: float):
        """Initialize an owner with name and available daily time."""
        self.name: str = name
        self.available_time_per_day: float = available_time_per_day  # in minutes
        self.preferred_timeblocks: List[TimeBlock] = []
        self.preferences: Dict[str, any] = {
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
        schedule = DailySchedule(owner, pet, date=datetime.now())
        schedule.generate_schedule()
        return schedule
    
    def prioritize_tasks(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks by priority and constraints"""
        # Sort by priority first (HIGH > MEDIUM > LOW), then by duration (longer first)
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: (priority_order[t.priority], -t.duration))
    
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
