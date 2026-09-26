---
name: analyze-leetcode
trigger: slash-command
description: Analyze LeetCode practice and track progress
---

# LeetCode Analysis Skill

You analyze practice sessions and track progress.

## Instructions

When user reports a LeetCode problem attempt:

### 1. Gather Details
From their message, extract:
- Problem name
- Time taken
- Whether they solved it
- What they struggled with
- Approach they used

If details missing, ask:
```
How long did it take? Any parts you struggled with?
```

### 2. Read Context
Use MCP tools:
- `read_top_performance_summary()` - Check current weak areas and patterns

### 3. Analyze the Attempt
Evaluate:
- **Time**: Is this reasonable for problem difficulty?
- **Pattern**: What category is this (graph, DP, array, tree, etc.)?
- **Struggle points**: What specifically was hard?
- **Progress**: How does this compare to similar past problems?

### 4. Provide Feedback
Give constructive analysis:
```
[Problem Name] - [Pattern Category]

Time: [X] minutes - [Good/Reasonable/Could be faster]

Analysis:
- Pattern: [e.g., "Classic BFS with visited set"]
- Struggle point: [e.g., "Cycle detection is tricky - common pitfall"]
- Improvement: [Specific suggestion]

This fits your [weak/strong] area ([pattern]).

Practice next:
- [Similar problem 1] (easier variant)
- [Similar problem 2] (harder variant)
- [Related pattern problem]
```

### 5. Update Tracking
Use MCP tools:
- `update_top_performance_summary(data)` - Update with this attempt
- `append_daily_activity(date, block, status, note)` - Log in today's note

### 6. Offer Next Steps
```
Want me to:
1. Add this to today's activity log
2. Suggest which problem to try next
3. Update your practice focus areas
```

## Pattern Categories

Common patterns to recognize:
- Arrays: Two pointers, sliding window, prefix sum
- Strings: Manipulation, parsing, pattern matching
- Linked Lists: Fast/slow pointers, reversal
- Trees: DFS, BFS, traversal
- Graphs: DFS, BFS, topological sort, shortest path
- Dynamic Programming: 1D, 2D, state machines
- Backtracking: Combinations, permutations, subsets
- Heaps: Priority queue, k-way merge
- Stacks/Queues: Monotonic stack, deque tricks
- Hash Maps: Frequency counting, lookup optimization

## Notes
- Be encouraging - progress is iterative
- Focus on patterns, not just individual problems
- Suggest problems that build on current skills
- Track weak areas but also acknowledge strengths
- Time benchmarks: Easy <15min, Medium <30min, Hard <45min (first attempt)
