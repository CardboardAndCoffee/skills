#!/usr/bin/env python3
"""Differential-testing + benchmark harness for the pure, comparable case.

This is the concrete, runnable core of the `sharpen` loop for Python
targets whose equality relation is exact `==`:

  1. Oracle  — run a large volume of generated inputs through the Frozen Original
               and a candidate; any mismatch rejects the candidate.
  2. Fitness — only if the oracle passes, benchmark both on a HELD-OUT set of
               inputs (distinct from the ones used while iterating) and report
               mean wall-clock with a 95% confidence interval, plus the speedup.

It deliberately keeps time as its own axis and reports confidence intervals so a
real win can be told apart from jitter. For floating-point, effectful, or
nondeterministic targets you need a different equality relation / effect capture
(see ../reference.md) — this harness only covers exact equality.

Run it directly for a worked demo:

    python diff_harness.py
"""

from __future__ import annotations

import math
import random
import statistics
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence


# --------------------------------------------------------------------------- #
# Oracle
# --------------------------------------------------------------------------- #
@dataclass
class CounterExample:
    arg: object
    original: object
    candidate: object


def differential_test(
    original: Callable,
    candidate: Callable,
    inputs: Iterable,
    equals: Callable[[object, object], bool] | None = None,
) -> CounterExample | None:
    """Return the first input where candidate disagrees with original, else None.

    `equals` defaults to exact `==`. Exceptions are part of behavior: if the
    original raises, the candidate must raise the same exception type.
    """
    eq = equals or (lambda a, b: a == b)
    for arg in inputs:
        try:
            expected = original(arg)
            orig_exc = None
        except Exception as exc:  # noqa: BLE001 - exception identity is behavior
            expected = None
            orig_exc = type(exc)

        try:
            got = candidate(arg)
            cand_exc = None
        except Exception as exc:  # noqa: BLE001
            got = None
            cand_exc = type(exc)

        if orig_exc is not None or cand_exc is not None:
            if orig_exc is not cand_exc:
                return CounterExample(arg, orig_exc, cand_exc)
            continue

        if not eq(expected, got):
            return CounterExample(arg, expected, got)
    return None


# --------------------------------------------------------------------------- #
# Fitness (benchmark)
# --------------------------------------------------------------------------- #
@dataclass
class Stat:
    mean_s: float
    ci95_s: float  # half-width of the 95% confidence interval

    def __str__(self) -> str:
        return f"{self.mean_s * 1e6:8.2f} us  +/- {self.ci95_s * 1e6:6.2f}"


def benchmark(fn: Callable, inputs: Sequence, repeats: int = 30) -> Stat:
    """Time one pass over `inputs`, repeated `repeats` times; mean + 95% CI."""
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        for arg in inputs:
            fn(arg)
        samples.append(time.perf_counter() - start)

    mean = statistics.mean(samples)
    if len(samples) > 1:
        stdev = statistics.stdev(samples)
        ci95 = 1.96 * stdev / math.sqrt(len(samples))
    else:
        ci95 = 0.0
    return Stat(mean, ci95)


@dataclass
class Verdict:
    counterexample: CounterExample | None
    original: Stat | None
    candidate: Stat | None
    speedup: float | None

    @property
    def promotable(self) -> bool:
        """Correct, and faster beyond the noise floor (CIs don't overlap)."""
        if self.counterexample is not None:
            return False
        assert self.original and self.candidate
        gap = self.original.mean_s - self.candidate.mean_s
        noise = self.original.ci95_s + self.candidate.ci95_s
        return gap > noise


def evaluate(
    original: Callable,
    candidate: Callable,
    oracle_inputs: Iterable,
    heldout_inputs: Sequence,
    equals: Callable[[object, object], bool] | None = None,
    repeats: int = 30,
) -> Verdict:
    """Gate on the oracle, then measure fitness on the held-out set."""
    ce = differential_test(original, candidate, oracle_inputs, equals)
    if ce is not None:
        return Verdict(ce, None, None, None)

    base = benchmark(original, heldout_inputs, repeats)
    cand = benchmark(candidate, heldout_inputs, repeats)
    speedup = base.mean_s / cand.mean_s if cand.mean_s else float("inf")
    return Verdict(None, base, cand, speedup)


# --------------------------------------------------------------------------- #
# Worked demo: optimize "sum of squares 0..n-1" from a loop to a closed form.
# --------------------------------------------------------------------------- #
def _demo() -> None:
    # Frozen Original: the obvious loop.
    def frozen_original(n: int) -> int:
        total = 0
        for i in range(n):
            total += i * i
        return total

    # Candidate: closed form  (n-1)n(2n-1)/6 .
    def candidate(n: int) -> int:
        m = n - 1
        return m * (m + 1) * (2 * m + 1) // 6

    rng = random.Random(0)
    # Oracle inputs include forced edge cases (0, 1) plus random volume.
    oracle_inputs = [0, 1, 2] + [rng.randint(0, 500) for _ in range(50_000)]
    # Held-out set: inputs we did NOT iterate against, sampled separately.
    heldout_inputs = [random.Random(99).randint(200, 400) for _ in range(200)]

    verdict = evaluate(frozen_original, candidate, oracle_inputs, heldout_inputs)

    print("sharpen differential harness — demo")
    print("-" * 48)
    if verdict.counterexample is not None:
        ce = verdict.counterexample
        print(f"REJECTED — counterexample at {ce.arg!r}: "
              f"original={ce.original!r} candidate={ce.candidate!r}")
        return

    print(f"Oracle: PASS ({len(oracle_inputs):,} inputs, exact equality)")
    print(f"  original  (held-out): {verdict.original}")
    print(f"  candidate (held-out): {verdict.candidate}")
    print(f"  speedup: {verdict.speedup:.1f}x")
    print(f"  promotable: {verdict.promotable} "
          f"(correct AND faster beyond the noise floor)")


if __name__ == "__main__":
    _demo()
