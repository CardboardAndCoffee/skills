# Equivalence Contract: <target name>

> The per-target definition of "same behavior". This is **data a human ratifies**
> before the optimization loop may run. If any required section can't be filled in
> soundly, the target does not run — fail closed.

## Target

- **Location:** `<file>:<symbol>` (function / method / query)
- **Frozen Original captured at:** `<commit sha / date>`
- **Signature:** `<inputs -> output>`

## Input domain

- **Valid inputs:** <describe the domain precisely — types, ranges, shapes,
  invariants the caller guarantees>
- **Excluded inputs:** <values the original is not contracted to handle; the
  oracle must not generate these>
- **Generator:** <how inputs are sampled — distribution, edge cases to force:
  empty, zero, max, negative, duplicates, unicode, etc.>
- **Volume:** <how many inputs per oracle run; large enough to find edge bugs>

## Equality relation

Pick exactly one and specify it. (Don't auto-detect.)

- [ ] **Exact** — `original(x) == candidate(x)` (pure, comparable values)
- [ ] **Tolerance** — floating-point; `abs/rel` tolerance = `<value>`; NaN/inf
      handling = `<rule>`
- [ ] **Effect-trace** — compare a captured trace of declared effects (below) in
      addition to / instead of the return value
- [ ] **Custom** — `<define the relation precisely>`

## Determinism injection

How nondeterminism is pinned so both versions are comparable. If the target has
nondeterminism that cannot be injected, **do not run.**

- **Clock:** <frozen / injected / n/a>
- **RNG:** <seeded / injected / n/a>
- **Iteration order:** <forced deterministic / n/a>
- **I/O & external state:** <stubbed / captured / n/a>

## Declared effects

- **Side effects the original performs:** <writes, mutations, I/O, logging — or
  "none (pure)">
- **How each is captured & compared:** <mechanism, or "n/a (pure)">
- **Effects that are NOT captured:** <if any exist, the contract is incomplete →
  fail closed>

## Attestations

- [ ] No concurrency / shared-mutable-state races in the target.
- [ ] All side effects are declared and captured above (or the target is pure).
- [ ] The equality relation fully characterizes "correct" for this target.
- [ ] The input generator covers the documented domain and its edge cases.

## Ratification

- **Author:** <who drafted this>
- **Ratified by (human):** <name> — **date:** <date>
