---
name: safe-optimize
description: Make a hot function, method, or query faster while proving it still behaves identically to the original — via differential testing against a frozen copy under an explicit equivalence contract, gated on a deterministic proxy and confirmed on a held-out benchmark. Use when the user asks to speed up / micro-optimize / make code faster without changing its behavior. Fails closed on code it cannot verify (concurrency, nondeterminism, unpinned side effects).
---

# Safe Optimize

Optimize code for **speed only**, autonomously, but only where you can *prove*
the faster version is behaviorally indistinguishable from the original. The
discipline (codename "Whetstone"): a performance task has a deterministic oracle
a prose task never had — "did it get faster" reduces to a benchmark, and "did it
stay correct" reduces to "is it indistinguishable from the code that worked
before." Both are machine-checkable, so the loop can grind and the human only
reads the result.

Two acts stay with the human: **defining what "correct" means** (ratifying the
contract) and **merging what ships**. Everything between is automatable.

## When to use

- "Make this function faster", "optimize this hot path", "speed this up without
  changing behavior", "micro-optimize this loop/query".
- The target is a single unit of code (a function, method, or query) whose
  behavior can be pinned down with inputs and an equality relation.

## When to refuse (fail closed)

Do **not** run the loop — say why and stop — when correctness can't be verified:

- **Concurrency / race-prone code** — a passing differential run cannot prove the
  absence of a race.
- **Nondeterminism** with no determinism injection (clocks, RNG, ordering, I/O
  iteration) — there is no differential oracle.
- **Side effects** that aren't captured by the contract — a hidden effect means
  "same return value" isn't "same behavior".
- **Design quality / readability** — no deterministic oracle; that's a human's
  call, not this skill's.

Fail closed: when in doubt, don't optimize and don't guess the contract.

## The loop

1. **Freeze the original.** Copy the target's current implementation verbatim as
   the *Frozen Original* — this, not the existing test suite, is the definition
   of correct. (See `reference.md` for why the suite is only a pre-filter.)
2. **Write the Equivalence Contract.** Fill in
   [`templates/equivalence-contract.md`](templates/equivalence-contract.md):
   input domain + generator, equality relation (exact / tolerance / effect-trace),
   determinism injection, and declared effects. **Get the human to ratify it
   before running.** If you can't write a sound contract, refuse (see above).
3. **Build the oracle.** Generate a large volume of inputs from the domain and
   check each candidate against the Frozen Original under the contract's equality
   relation. Use `scripts/diff_harness.py` for the pure/comparable case. Any
   counterexample → reject the candidate.
4. **Propose a candidate.** Rewrite the target body for speed. Start with local,
   structural wins; reserve algorithm changes for restarts (below).
5. **Gate, then confirm.** A candidate is only measured if it passes the oracle.
   Then check fitness on the **held-out set** (inputs you didn't optimize
   against): it must beat the incumbent on the deterministic proxy *and* on
   wall-clock, by more than noise and more than the effect-size threshold.
6. **Promote or discard.** If it wins on held-out by both signals → it becomes
   the new incumbent. Otherwise discard and try again from the incumbent.
7. **Restart on stall.** No promotion for several iterations → start a fresh
   lineage from the Frozen Original with an instruction to take a *structurally
   different* approach. Keep the global best across lineages. When every lineage
   stalls, stop.

## Rules that keep it honest

- **Judge on the held-out set, never on inputs you optimized against.** A win you
  could see coming is a win you tuned for. Compare held-out vs. train as your
  overfitting detector.
- **Proxy and wall-clock must agree.** The deterministic proxy (instruction count,
  allocations) is the primary gate; wall-clock is real-world confirmation. If they
  disagree, don't promote.
- **Keep time and memory as separate axes.** Never collapse them into one index —
  that hides a time-for-memory regression.
- **Never relax the gate to keep going.** If a hidden effect surfaces mid-run and
  correctness can no longer be verified, *quarantine* the target: flag it, log it,
  stop — never silently skip.
- **Greedy, not a population.** One incumbent, hill-climb, promote only verified
  held-out improvements; restarts are the escape from a rut. (Rationale in
  `reference.md`.)

## Output

Every promoted result ships as an **Evidence Bundle**, not a silent edit: the
oracle record (inputs run, equality relation), performance deltas with confidence
intervals (proxy + wall-clock, time and memory separately), the ratified
contract, and the attempt log. Present it as a PR / diff for a **human to merge** —
this skill never ships code on its own.

## Start small

For a first run, target a single **pure, equality-comparable** function (a sort,
a parser, integer math). Wire the real pieces end to end with
`scripts/diff_harness.py` and look at the graph: the question isn't "did it get
faster", it's "are the confidence intervals tight enough to tell a real win from
jitter, and does held-out track train?" If those hold, the result is trustworthy.

See [`reference.md`](reference.md) for the full vocabulary and the rationale
behind each rule.
