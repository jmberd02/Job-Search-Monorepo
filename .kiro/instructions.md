# Superpowers Agent

You are an AI coding agent using the Superpowers development workflow.

Skill definitions are located in:

.kiro/skills/

Each skill folder contains instructions that define how to perform a task.

When a task matches a skill:
1. Load the corresponding skill definition
2. Follow the workflow defined in that skill
3. Execute the steps exactly as described

A skill index exists at:

.kiro/skills/INDEX.md

When solving problems:

1. Review the skill index
2. Select relevant skills
3. Load the skill instructions
4. Follow the workflow defined in the skill

---

# Development Process

Before implementing a feature you should normally:

1. brainstorming
2. writing-plans
3. executing-plans
4. verification-before-completion
5. finishing-a-development-branch

---

# Debugging

When encountering bugs or failures use:

systematic-debugging

---

# Quality Control

Use these skills when appropriate:

test-driven-development  
requesting-code-review  
receiving-code-review

---

# Advanced workflows

These skills may be used when beneficial:

dispatching-parallel-agents  
subagent-driven-development  
using-git-worktrees

---

# Task Memory

A persistent task file exists at:

TASK.md

Always read TASK.md before starting work.

When working on a feature:

1. Store the goal in TASK.md
2. Write the implementation plan in TASK.md
3. Break the plan into tasks
4. Mark tasks complete as they are finished
5. Continue working from the current task on the next prompt

When using Superpowers skills:

writing-plans → write the plan to TASK.md  
executing-plans → update the task checklist  
verification-before-completion → confirm all tasks are done