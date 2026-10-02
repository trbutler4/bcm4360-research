# Contribution workflow

1. Read the current research report, applicable audit addenda, provenance rules, and hardware safety policy.
2. Select one bounded question or defect. Refresh upstream and record the exact starting commit.
3. Work in a separate checkout of the target project. Do not vendor the whole tree here.
4. Establish a failing witness using independently authored synthetic input when possible.
5. Verify the intended behavior and the correct contract boundary before changing code.
6. Make the smallest appropriate change. Cover success, failure, malformed/missing input, and likely integration boundaries.
7. Run the target project's real host-test entry points as well as the new regression. A blocked build is a blocked build, not a passing test.
8. Record commands, outputs or sanitized summaries, environment, provenance, and unresolved limitations in an experiment record.
9. Run this notebook's local checks and inspect the staged diff. Commit only reviewed, publishable contents.
10. Prepare an upstream patch or PR description with before/after evidence. Get approval before submission or publication.

Do not add a human's DCO sign-off on their behalf. Keep existing licensing notices intact and disclose AI assistance according to the target project's rules.

## Notebook checks

```sh
make check
make test
git diff --cached --check
git diff --cached --stat
git diff --cached
```

The checker is a limited guardrail. It does not prove there are no secrets or licensing problems and does not read Git history for past leaks. Ignored files can still be force-added, so a manual staged review is mandatory.
