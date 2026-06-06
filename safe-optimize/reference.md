# Safe Optimize — reference

Detailed vocabulary and rationale, loaded when you need it. Distilled from the
Whetstone design (CONTEXT.md, the ADRs, and the README).

## Vocabulary

**Target** — a single unit of code enrolled for optimization: a method,
function, or query. (Avoid calling it "candidate" — that's the proposed rewrite.)

**Frozen Original** — the target's implementation *at enrollment time*, treated as
the definition of correct behavior. Candidates are judged against it, never
against the existing test suite. (Don't call it "baseline" — that's reserved for
the performance reference point.)

**Equivalence Contract** — the per-target spec of what "same behavior" means:
equality relation, valid input domain, effect capture, determinism injection,
and attestations. **Data, ratified by a human** before the loop runs. The
template is `templates/equivalence-contract.md`.

**Correctness Oracle** — the mechanism that decides a candidate is behaviorally
indistinguishable from the Frozen Original: differential testing under the
contract over a large volume of generated inputs. Not "a test", not "a checker".

**Candidate** — a proposed rewrite of the target's body. Admissible only if it
passes the oracle.

**Incumbent** — the current best candidate; what new candidates are measured
against. (Not "champion" / "winner".)

**Promotion** — accepting a candidate as the new incumbent: it passed the oracle
*and* beat the incumbent on the held-out set by more than noise and more than the
effect-size threshold.

**Lineage** — a chain of candidates descending from one starting point through
successive mutations.

**Restart** — beginning a fresh lineage from the Frozen Original with an
instruction to take a structurally different approach. The cheap escape from a
local optimum.

**Stall** — a lineage producing no promotion over K iterations; triggers a
restart. When all lineages stall together (global stall), the run ends.

**Quarantine** — removing a target because its correctness can no longer be
verified (e.g. a hidden effect surfaces mid-run). Always flagged and logged,
never a silent skip; the gate is never relaxed to keep going.

**Fitness** — the measured performance of a candidate: a deterministic proxy plus
wall-clock, judged only on the held-out set. Keep time and memory as **separate
axes**.

**Deterministic Proxy** — a noise-free cost measure (instruction count,
allocations) used as the primary gate signal, with wall-clock as real-world
confirmation.

**Held-out Set** — benchmark inputs the optimizer never sees during the search.
The honest fitness signal, and — compared against the visible training inputs —
the overfitting detector. (Not "test set" — that collides with the test suite.)

**Benchmark Adapter** — the per-runtime measurement plug-in (JMH for the JVM,
criterion for Rust, pytest-benchmark for Python) that returns a
`(mean, confidence interval)`.

**Engine** — the generic, reusable core: mutate → gate → benchmark → keep best →
log. Identical across every target and runtime.

**Evidence Bundle** — the artifacts attached to a result: oracle record,
performance deltas with intervals, the ratified contract, the full attempt log,
and the best-so-far graph.

## Why these rules (rationale)

### The Frozen Original is the oracle, not the test suite
Even at 100% line coverage, the suite proves every line *ran*, not that every
behavioral contract is *asserted*. A performance optimizer is an adversary that
will find and exploit the edges the suite never pinned down — overflow, empty
input, precision, ordering, locale. Defining "correct" as "indistinguishable from
the code that works today, but faster" is the exact contract we want, and it
sidesteps the unanswerable "is the suite behaviorally complete?" The suite is a
fast pre-filter; the differential oracle is the gate.

### Generic engine, per-target oracle, per-runtime adapter
"Generic + handles both pure and impure code + autonomous + safe" cannot all hold
at once. The oracle is *fundamentally different* per case: exact equality (pure),
tolerance (floating-point), effect-trace comparison (effectful), or
nonexistent (nondeterministic). A single auto-detecting oracle looks generic in a
demo and silently ships the case it guessed wrong. So genericity lives in the
**engine**, never in the oracle. A target whose contract is missing or unverified
does not run.

### Greedy hill-climb with restarts, not a population
The mutation operator is an LLM that can make a coordinated algorithmic leap in
one shot — it doesn't need a population to cross a valley that blind mutation
could only cross by keeping worse candidates alive. A population would also cost
K× the expensive, noisy benchmark runs and reintroduce soft judgment (something
must decide which "currently worse but promising" candidates to keep) — exactly
the taste call we pushed out of the loop. The one failure mode of greedy-from-best
is the model getting in a rut; random restarts from the original are the cheap
mitigation, and the natural home for the opt-in algorithm-change tier.

### Differential equality has limits
It only holds for deterministic, comparable behavior. Floating-point, side
effects, and nondeterminism each need extra contract machinery (tolerance, effect
capture, determinism injection); where that machinery is absent, the target does
not run. This is why concurrency is excluded — a passing differential run cannot
prove the absence of a race.

## Resolved ambiguities

- **"Improvement" = faster only.** Better-designed has no deterministic oracle and
  is out of scope for autonomous operation.
- **No single "performance index".** Fitness keeps separate axes (time, memory); a
  composite hides a time-for-memory regression.
- **"Handles both" is the engine, not the oracle.** One engine; per-target oracle.
- **"Test" is overloaded.** The existing suite is a pre-filter; the oracle is
  differential testing against the Frozen Original.
