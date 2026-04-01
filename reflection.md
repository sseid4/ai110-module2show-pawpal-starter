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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One tradeoff in my scheduler is that conflict detection is intentionally lightweight: it treats tasks as conflicting only when they share the same due date and preferred window label (for example, two "morning" tasks), rather than computing real start/end time overlaps.

This is reasonable for this project because tasks currently do not store exact clock times or durations on a timeline. The lightweight approach gives useful warning messages early, keeps the algorithm simple to understand, and avoids adding complexity that would require a full time-grid model and richer user inputs.

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
