# PawPal+ Project Reflection

## 1. System Design

**Core user actions for PawPal+**

- A user should be able to enter and update basic owner and pet information so the planner can personalize care decisions.
- A user should be able to add and edit pet care tasks (such as walks, feeding, medication, enrichment, and grooming) with key details like duration and priority.
- A user should be able to generate and view a daily care plan that fits time and preference constraints, with a clear explanation of why tasks were scheduled in that order.

**a. Initial design**

My initial UML design split the system into small classes so each part had one clear job. I included `Owner`, `Pet`, `CareTask`, `Scheduler`, and `DailyPlan`.

- `Owner` stores the owner's profile and preferences (like available time and preferred care windows).
- `Pet` stores pet-specific information (species, age, energy level, medical notes) so planning can be personalized.
- `CareTask` represents one care activity and holds scheduling details such as duration, priority, due date, and status.
- `Scheduler` contains the planning logic: it prioritizes tasks, assigns tasks to time slots, and produces a daily plan.
- `DailyPlan` is the output model that stores scheduled tasks, unscheduled tasks, and explanation notes for why decisions were made.

**b. Design changes**

Yes. During implementation, I made a few relationship-focused design changes to reduce ambiguity and future bugs.

- I changed `Scheduler` from handling a single pet to supporting a list of pets. This better matches the real model where one owner can have multiple pets.
- I added `pet_id` to `CareTask` so each task is explicitly linked to the correct pet when tasks are combined into one daily plan.
- I added an explicit scheduled structure in `DailyPlan` (`scheduled_items`) to pair each task with its assigned time slot, because taking a `time_slot` argument without storing it would lose scheduling detail.

I made these changes to keep relationships consistent, improve traceability in the schedule output, and prevent logic bottlenecks when scaling from one pet to multi-pet planning.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- My scheduler considers total daily time availability, preferred time windows, task due date, overdue status, task priority, and task duration.
- I prioritized constraints in this order: overdue status first (urgent care should not be delayed), then due date, then preferred window, then priority and duration to make plans feasible and predictable.
- I also used conflict analysis as a second-pass safety check so the UI can warn users when a plan is technically possible overall but overloaded in a specific window like morning.

**b. Tradeoffs**

One tradeoff in my scheduler is that conflict detection is intentionally lightweight: it treats tasks as conflicting only when they share the same due date and preferred window label (for example, two "morning" tasks), rather than computing real start/end time overlaps.

This is reasonable for this project because tasks currently do not store exact clock times or durations on a timeline. The lightweight approach gives useful warning messages early, keeps the algorithm simple to understand, and avoids adding complexity that would require a full time-grid model and richer user inputs.

---

## 3. AI Collaboration

**a. How you used AI**

- I used VS Code Copilot in several modes: code generation for repetitive test setup, Ask mode to explain methods and suggest edge cases, and inline edits to quickly improve UI and documentation.
- The most effective Copilot features for building my scheduler were test drafting, rapid refactoring suggestions, and contextual code explanations tied to specific files.
- The prompts that helped most were specific and constraint-based, for example: "What edge cases should I test for recurring tasks and conflict detection?" and "How can I display conflict warnings clearly for non-technical users?"

**b. Judgment and verification**

- One suggestion I rejected was introducing full timestamp-based overlap logic immediately. I kept the lightweight window-based conflict model because my data model only had preferred windows (morning/afternoon/evening), not exact start/end times.
- I modified AI-generated ideas to fit my architecture boundaries instead of expanding scope too early.
- I verified suggestions by running `python -m pytest`, checking whether behavior stayed aligned with my scheduler design, and confirming UI outputs still matched backend rules.

---

## 4. Testing and Verification

**a. What you tested**

- I tested task completion state changes, plan generation for due tasks, prioritization order, capacity overflow handling, preferred-window scheduling, filtering by pet/status/date, recurring task roll-forward, de-duplication of tasks, and conflict warnings.
- These tests were important because they cover both happy paths (normal scheduling) and edge cases (overload, duplicate windows, recurrence), which are the highest-risk parts of a planner.

**b. Confidence**

- My confidence is high because the full automated suite passes and verifies the core intelligence behaviors.
- If I had more time, I would test: zero-minute availability days, unknown preferred window values, large multi-pet workloads, and recurring ID generation under repeated completions.

---

## 5. Reflection

**a. What went well**

- I am most satisfied with keeping a clean separation between domain models (`Owner`, `Pet`, `CareTask`), planning logic (`Scheduler`), and output representation (`DailyPlan`) while still delivering useful UI feedback.

**b. What you would improve**

- In another iteration, I would add exact task start/end times and a timeline-based allocator, then evolve conflict detection from window collisions to real overlap calculations.
- I would also add persistence (save/load tasks) and more owner-facing controls for recurring rules.

**c. Key takeaway**

- The biggest takeaway is that I must act as the lead architect when using AI: Copilot can accelerate coding, but I need to define scope, enforce design boundaries, and decide what not to implement yet.
- Using separate Copilot chat sessions for each phase helped me stay organized by reducing context drift: one session for planning/UML, one for implementation, one for testing, and one for polish/documentation.
- This structure made it easier to verify outputs, keep prompts focused, and maintain human oversight over quality and tradeoffs.

---

## Checkpoint Summary

I finalized PawPal+ as a polished project artifact by aligning UI behavior with scheduling logic, updating UML to match implementation, building and validating an automated test suite, and documenting architecture decisions and AI collaboration strategy. I can now clearly explain both the technical design and my role as the human decision-maker in an AI-assisted engineering workflow.
