---
name: verification-before-completion
description: "Use when reporting software changes or test/build results, especially before committing: match claims to fresh, relevant evidence and clearly state which checks were not run."
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO PASSING CLAIMS WITHOUT RELEVANT VERIFICATION EVIDENCE
```

Do not claim a test, build, or fix passes without relevant, fresh evidence. If no check was run, say so plainly.

## The Gate Function

Before reporting a technical result:

1. Identify the claim and the smallest relevant check that supports it.
2. Run the check when verification is requested or warranted by the task.
3. Read its output and exit status.
4. Report what was checked; distinguish unrun checks from passing checks.

Do not run a broad suite when a focused check is sufficient or when the user has not asked for tests.

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | A partial check presented as evidence for the full suite |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Describing an unverified test/build/fix as passing
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying a check passed without running that check**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run relevant test command] [See: exit 0] "The focused test passes"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ When a red-green regression cycle is useful, confirm the test fails before the fix and passes after it.
❌ Claiming a regression test proves the fix without running it.
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## When To Apply

**Use before:**
- Claiming a test, build, or bug fix passed
- Committing or handing off implementation work
- Reporting whether requested acceptance criteria are met

**Rule applies to:**
- Exact and paraphrased claims about checks or implementation results
- Implications that a check passed when it was not run
