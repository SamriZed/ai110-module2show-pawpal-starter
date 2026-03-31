# PawPal+ Project Reflection

## 1. System Design

- Add and manage pet profiles and their needs
- Input constraints and preferences
- Generate and review a daily care plan with explanations

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Classes I included are: Scheduler, DailySchedule, Owner, Pet, Task, TimeBlock. 

-> Task represents a pet care task and check if it is a high priority and if it can fit in the time block.
-> TimeBlock represents a time slot in the daile schedule and check if it is available for a task, get duration, and assign a task to it.
-> Pet represents a pet and its care needs and preferences.
-> Owner represents the pet owner and can add/ remove pets and tasks, get available time, and set prefered time slots.
-> Daily schedule represents a single day's schedule and can generate schedule, add scheduled task, explain schedule, and get schedule summary.
-> Scheduler handles scheduling logic and optimization. It priortize tasks and fit tasks in time blocks.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, I made several adjustments during implementation. Based on Copilot’s suggestions, I added three new attributes to the Task class: preferred_time_window, must_follow_task, and min_interval_after. These should address the previously missing task constraints.

In the Owner class, I changed available_time_per_day to be measured in minutes to avoid unit mismatches, since Task.duration is also in minutes. I also expanded the fields under owner.preferences, which were previously too vague.

Additionally, I introduced a task_to_timeblock mapping for explicit scheduling, as well as an unscheduled_tasks list to track tasks that could not be accommodated. These changes also made explain_schedule() much easier to implement.

Finally, I updated the Scheduler by adding a generate_daily_timeblocks() method to create time blocks based on owner preferences, and a _validate_schedule() method to ensure that tasks fit within the available time.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The constrains my scheduler cosiders are: Time,Priority, Preferences, Dependencies, and Recurrence.
The most critical constraints are those that would make a schedule infeasible or illogical: time (fit and overlap), priority (urgent tasks first), and dependencies (task order).
Preferences (like time windows) are considered next, as they improve user satisfaction but are flexible.
Recurrence is handled to ensure ongoing care, but does not override time or priority constraints.
The scheduler issues warnings (not errors) for soft constraint violations.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is that it assigns each task to a single available timeblock that can fit the task’s duration, but it does not check for partial overlaps or attempt to split tasks across multiple timeblocks. If a task cannot fit entirely within one available block, it is left unscheduled.

This tradeoff is reasonable for this scenario because Pet care tasks (like feeding, walking, or grooming) need to be completed in one continuous session, not split across multiple periods. And This approach keeps the scheduling logic straightforward and efficient, avoiding the complexity of handling overlapping or fragmented time slots.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I first came up with four classes but then copilot suggested adding TimeBlock and DailySchedule, which made the design more modular and easier to implement. I also used copilot to generate method stubs and logic for scheduling, task fitting, and conflict detection.
The most helpful prompts were the ones codepath provided, I started following the patterns of those prompts to ask copilot. And using separate chat sessions for different phases helped me stay organized and focused on specific tasks (design, implementation, testing).

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

In the detect_conflicts method, I didn't accept the initial suggestion.

I used my understanding and different sources to make the code more readable, clean, and efficient.


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested core behaviors in the scheduling system at both unit-test and demo levels:

Task completion behavior: calling mark_complete() updates a task from incomplete to completed.
Task list management: adding a task to a pet increases task count, and removing a task decreases it.
Owner to pet delegation: adding a task through the owner correctly adds it to the selected pet.
Timeblock logic: duration calculation is correct, and task fit checks correctly allow or reject tasks by available minutes.
Priority logic: high-priority detection works as expected.
Scheduling utilities: task sorting by priority, time window, and duration behaves consistently.
Recurrence behavior: recurring tasks can generate next occurrences (daily/weekly flow).
Conflict and filtering utilities: conflict warnings and task filters (by status, pet, category, priority) return expected results.
These tests were important because they validate the most failure-prone parts of the system: task state changes, scheduling constraints, and time-based decisions. If these behaviors are wrong, the generated plan becomes misleading or unusable. Testing these paths gave me confidence that the scheduler is logically correct for normal use and common edge cases.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am very confident that the core scheduling logic works correctly for typical scenarios, as the tests cover a wide range of behaviors and all pass successfully. The system handles task completion, time fitting, priority detection, and recurrence as expected.

The preferred time is supported in the scheduling logic, but the Streamlit UI is not collecting that value when a task is added. If I had more time, I would work on connecting the preferred time window input in the UI to the Task creation logic, and then add tests to verify that tasks with different preferred time windows are scheduled accordingly. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Almost everything went well, but I am satisfied with the overall design and implementation of the scheduling logic. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The timeBlock is the one I would improve. So even if a task is 30 minutes and the block is 4 hours, the model treats that block as “used". I would redesign the time block to track remaining minutes and allow multiple tasks to be scheduled within the same block until it is fully utilized. This would make the scheduling more efficient and realistic, as many pet care tasks are short and can fit within larger time windows without needing to reserve the entire block for one task.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

If I were to do this project alone, it would have taken me much longer to design and implement the scheduling logic, especially with the added constraints and features. The AI collaboration allowed me to quickly iterate on the design, get suggestions for method implementations, and refine the logic in ways I might not have thought of on my own. It also helped me identify edge cases and testing scenarios that I might have missed. 
