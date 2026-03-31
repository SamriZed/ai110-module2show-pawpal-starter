"""
Unit tests for PawPal+ pet care scheduling system
Tests for Task completion and Pet task management
"""
import pytest
from datetime import time
from pawpal_system import Owner, Pet, Task, TimeBlock, Priority, Scheduler, Frequency


class TestTaskCompletion:
    """Test suite for Task completion functionality"""
    
    def test_mark_complete_changes_status(self):
        """Verify that calling mark_complete() changes the task's status"""
        # Arrange
        task = Task(
            name="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            category="exercise"
        )
        
        # Assert initial state
        assert task.is_completed == False, "Task should not be completed initially"
        
        # Act
        task.mark_complete()
        
        # Assert final state
        assert task.is_completed == True, "Task should be marked as completed"
    
    def test_mark_complete_multiple_calls(self):
        """Verify that mark_complete() can be called multiple times without error"""
        # Arrange
        task = Task(
            name="Feed Dog",
            duration=15,
            priority=Priority.MEDIUM,
            category="feeding"
        )
        
        # Act & Assert - multiple calls should work
        task.mark_complete()
        assert task.is_completed == True
        
        task.mark_complete()
        assert task.is_completed == True, "Marking complete multiple times should remain True"
    
    def test_different_tasks_independent_status(self):
        """Verify that completion status is independent for different task instances"""
        # Arrange
        task1 = Task(
            name="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            category="exercise"
        )
        task2 = Task(
            name="Evening Walk",
            duration=40,
            priority=Priority.HIGH,
            category="exercise"
        )
        
        # Act
        task1.mark_complete()
        
        # Assert
        assert task1.is_completed == True, "Task1 should be completed"
        assert task2.is_completed == False, "Task2 should still be incomplete"


class TestTaskAddition:
    """Test suite for Pet task addition functionality"""
    
    def test_add_task_increases_count(self):
        """Verify that adding a task to a Pet increases that pet's task count"""
        # Arrange
        pet = Pet(name="Max", pet_type="dog", age=3)
        task = Task(
            name="Walk",
            duration=30,
            priority=Priority.HIGH,
            category="exercise"
        )
        
        # Assert initial state
        initial_count = len(pet.get_tasks())
        assert initial_count == 0, "Pet should start with no tasks"
        
        # Act
        pet.add_task(task)
        
        # Assert final state
        final_count = len(pet.get_tasks())
        assert final_count == 1, "Pet should have 1 task after adding"
        assert final_count == initial_count + 1, "Task count should increase by 1"
    
    def test_add_multiple_tasks(self):
        """Verify that adding multiple tasks correctly increments the count"""
        # Arrange
        pet = Pet(name="Bella", pet_type="cat", age=5)
        task1 = Task(
            name="Feeding",
            duration=15,
            priority=Priority.HIGH,
            category="feeding"
        )
        task2 = Task(
            name="Play Time",
            duration=45,
            priority=Priority.MEDIUM,
            category="enrichment"
        )
        task3 = Task(
            name="Grooming",
            duration=60,
            priority=Priority.LOW,
            category="grooming"
        )
        
        # Act
        pet.add_task(task1)
        assert len(pet.get_tasks()) == 1
        
        pet.add_task(task2)
        assert len(pet.get_tasks()) == 2
        
        pet.add_task(task3)
        assert len(pet.get_tasks()) == 3
    
    def test_added_task_is_in_pet_tasks(self):
        """Verify that the added task actually appears in the pet's task list"""
        # Arrange
        pet = Pet(name="Buddy", pet_type="dog", age=7)
        task = Task(
            name="Medication",
            duration=10,
            priority=Priority.HIGH,
            category="health"
        )
        
        # Act
        pet.add_task(task)
        
        # Assert
        tasks = pet.get_tasks()
        assert task in tasks, "Added task should be in pet's task list"
        assert tasks[0].name == "Medication", "Task name should match"
    
    def test_add_same_task_multiple_times(self):
        """Verify that the same task can be added multiple times (duplicate entries)"""
        # Arrange
        pet = Pet(name="Max", pet_type="dog", age=3)
        task = Task(
            name="Walk",
            duration=30,
            priority=Priority.HIGH,
            category="exercise"
        )
        
        # Act
        pet.add_task(task)
        pet.add_task(task)
        
        # Assert
        assert len(pet.get_tasks()) == 2, "Same task can be added multiple times"


class TestTaskRemoval:
    """Test suite for Pet task removal functionality"""
    
    def test_remove_task_decreases_count(self):
        """Verify that removing a task from a Pet decreases the task count"""
        # Arrange
        pet = Pet(name="Fluffy", pet_type="cat", age=2)
        task1 = Task(
            name="Feeding",
            duration=15,
            priority=Priority.HIGH,
            category="feeding"
        )
        task2 = Task(
            name="Play Time",
            duration=30,
            priority=Priority.MEDIUM,
            category="enrichment"
        )
        
        pet.add_task(task1)
        pet.add_task(task2)
        assert len(pet.get_tasks()) == 2
        
        # Act
        pet.remove_task("Feeding")
        
        # Assert
        assert len(pet.get_tasks()) == 1, "Task count should decrease after removal"
        remaining_tasks = pet.get_tasks()
        assert remaining_tasks[0].name == "Play Time", "Correct task should remain"
    
    def test_remove_nonexistent_task(self):
        """Verify that removing a non-existent task doesn't cause errors"""
        # Arrange
        pet = Pet(name="Buddy", pet_type="dog", age=4)
        task = Task(
            name="Walk",
            duration=30,
            priority=Priority.HIGH,
            category="exercise"
        )
        pet.add_task(task)
        
        # Act & Assert - should not raise an error
        initial_count = len(pet.get_tasks())
        pet.remove_task("NonexistentTask")
        assert len(pet.get_tasks()) == initial_count, "Count unchanged when removing non-existent task"


class TestPetManagement:
    """Test suite for Owner pet management"""
    
    def test_add_pet_to_owner(self):
        """Verify that adding a pet to an owner increases the pet count"""
        # Arrange
        owner = Owner(name="Alice", available_time_per_day=480)
        pet = Pet(name="Max", pet_type="dog", age=3)
        
        # Act
        owner.add_pet(pet)
        
        # Assert
        assert len(owner.pets) == 1, "Owner should have 1 pet after adding"
        assert owner.pets[0].name == "Max", "Added pet should be in owner's pet list"
    
    def test_owner_add_task_via_owner_interface(self):
        """Verify that tasks can be added to pets through the Owner interface"""
        # Arrange
        owner = Owner(name="Bob", available_time_per_day=360)
        pet = Pet(name="Buddy", pet_type="dog", age=5)
        owner.add_pet(pet)
        
        task = Task(
            name="Walk",
            duration=30,
            priority=Priority.HIGH,
            category="exercise"
        )
        
        # Act
        owner.add_task("Buddy", task)
        
        # Assert
        assert len(pet.get_tasks()) == 1, "Task should be added to pet"
        assert pet.get_tasks()[0].name == "Walk", "Correct task should be added"


class TestTimeBlock:
    """Test suite for TimeBlock functionality"""
    
    def test_timeblock_duration_calculation(self):
        """Verify that timeblock duration is calculated correctly"""
        # Arrange
        block = TimeBlock(start_time=time(9, 0), end_time=time(12, 0))
        
        # Act
        duration = block.get_duration()
        
        # Assert
        assert duration == 180, "Duration should be 180 minutes (3 hours)"
    
    def test_task_fits_in_timeblock(self):
        """Verify that task.can_fit_in_timeblock works correctly"""
        # Arrange
        block = TimeBlock(start_time=time(9, 0), end_time=time(10, 0))  # 60 minutes
        task_fit = Task(
            name="Short Task",
            duration=45,
            priority=Priority.MEDIUM,
            category="test"
        )
        task_no_fit = Task(
            name="Long Task",
            duration=90,
            priority=Priority.MEDIUM,
            category="test"
        )
        
        # Assert
        assert task_fit.can_fit_in_timeblock(block) == True, "45min task should fit in 60min block"
        assert task_no_fit.can_fit_in_timeblock(block) == False, "90min task should not fit in 60min block"


class TestHighPriority:
    """Test suite for task priority checking"""
    
    def test_is_high_priority(self):
        """Verify that is_high_priority() correctly identifies high priority tasks"""
        # Arrange
        high_priority_task = Task(
            name="Medication",
            duration=10,
            priority=Priority.HIGH,
            category="health"
        )
        medium_priority_task = Task(
            name="Play",
            duration=30,
            priority=Priority.MEDIUM,
            category="enrichment"
        )
        low_priority_task = Task(
            name="Grooming",
            duration=60,
            priority=Priority.LOW,
            category="grooming"
        )
        
        # Assert
        assert high_priority_task.is_high_priority() == True
        assert medium_priority_task.is_high_priority() == False
        assert low_priority_task.is_high_priority() == False



# --- EDGE CASE TESTS: Sorting, Recurrence, Conflict Detection ---
def test_sort_tasks_by_time_chronological():
    """Tasks should be sorted by scheduled start time (chronological order)"""
    # Create tasks with different preferred time windows
    t1 = Task(name="Morning Feed", duration=15, priority=Priority.HIGH, category="feeding", preferred_time_window="morning")
    t2 = Task(name="Afternoon Walk", duration=30, priority=Priority.MEDIUM, category="exercise", preferred_time_window="afternoon")
    t3 = Task(name="Evening Play", duration=20, priority=Priority.LOW, category="enrichment", preferred_time_window="evening")
    tasks = [t2, t3, t1]  # Out of order
    scheduler = Scheduler()
    sorted_tasks = scheduler.sort_tasks_by_time(tasks)
    sorted_names = [t.name for t in sorted_tasks]
    assert sorted_names == ["Morning Feed", "Afternoon Walk", "Evening Play"], "Tasks should be sorted by time window"

def test_daily_task_completion_creates_next_occurrence():
    """Completing a daily recurring task should create a new task for the next day"""
    pet = Pet(name="Max", pet_type="dog", age=2)
    task = Task(
        name="Daily Walk",
        duration=30,
        priority=Priority.HIGH,
        category="exercise",
        is_recurring=True,
        frequency=Frequency.DAILY
    )
    pet.add_task(task)
    next_task = pet.mark_task_complete_with_recurrence("Daily Walk")
    assert next_task is not None, "Next occurrence should be created for recurring task"
    assert next_task.name == "Daily Walk"
    assert next_task.due_date is not None, "Next occurrence should have a due date"
    assert next_task.is_completed is False, "New task should not be completed"

def test_scheduler_detects_duplicate_times():
    """Scheduler should flag overlapping/duplicate time assignments as conflicts"""
    t1 = Task(name="Feed", duration=30, priority=Priority.HIGH, category="feeding")
    t2 = Task(name="Walk", duration=30, priority=Priority.HIGH, category="exercise")
    tb1 = TimeBlock(start_time=time(9, 0), end_time=time(9, 30), task=t1)
    tb2 = TimeBlock(start_time=time(9, 0), end_time=time(9, 30), task=t2)  # Overlaps with tb1
    scheduler = Scheduler()
    tasks = [t1, t2]
    task_to_timeblock = {t1: tb1, t2: tb2}
    pet_lookup = {t1: "TestPet", t2: "TestPet"}
    conflicts = scheduler.detect_conflicts(tasks, task_to_timeblock=task_to_timeblock, pet_lookup=pet_lookup)
    assert "overlapping_tasks" in conflicts, "Should detect overlapping tasks"
    assert any("overlaps" in msg for msg in conflicts["overlapping_tasks"]), "Conflict message should mention overlap"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
