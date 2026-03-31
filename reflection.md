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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
