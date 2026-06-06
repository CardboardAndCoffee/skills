# Tutorial structure & voice

This is the house style, distilled from a tutorial that took a reader from *no project* to
a *working build*. Match it. The reader is a competent engineer who may be **new to this
specific vertical** (the tool/tech/domain the guide teaches); your job is to remove every
"wait, how?" *about the vertical* before they hit it — never to explain general engineering.

How much you explain is set by the **level** (next section). The structure below is the
beginner shape; **Levels** says which parts shrink or drop as the reader's vertical
experience rises.

## Levels — calibrate to the reader's experience in the vertical

The level is **beginner / intermediate / expert**, and it tracks one thing only: how much the
reader already knows about **this specific vertical**. It is *not* engineering seniority — a
staff engineer who has never used the vertical wants beginner.

**The invariant.** General engineering competence is **constant and high** at all three levels.
Even beginner never explains shells, env vars, config files, or version control. What scales is
**vertical-specific** scaffolding: the tech's concepts, vocabulary, and click-by-click steps.
And the dial governs *only the named vertical* — a second tool the slice happens to require gets
a one-line pointer at every level, never a full teach.

**Pick one coherent preset** — don't mix dimensions. Each level is a fixed bundle:

| Dimension | Beginner (*new to it*) | Intermediate (*used it a bit*) | Expert (*fluent*) |
| --- | --- | --- | --- |
| Mental model | full, read-first | brief recap | **omitted** |
| Vocabulary | full glossary | slice-specific terms only | **omitted** |
| Prerequisites | spelled out | lighter | version/project-specific only |
| Step granularity | every menu/field/command named | commands + key fields | terse; decisive commands only |
| "Why" callouts | at every fork | at non-obvious forks | counterintuitive gotchas only |
| Troubleshooting | common newcomer errors | mix | subtle/non-obvious failures only |
| Verify checklist | maps 1:1 to acceptance criteria — **identical at every level** | ← | ← |

**Fixed floor — never drops, any level:** Title + promise, the level subtitle, the
not-yet-verified banner, numbered Steps, Troubleshooting, and Verify. At expert the result
reads like an *annotated runbook*: decisive
steps + gotchas + a done-check, with the concept-teaching stripped out — but the safety net
(Troubleshooting) and the definition of done (Verify) are always there.

**State the level in the doc.** Put a one-line subtitle directly under the `# H1`, phrased by
*vertical experience*, not by the bare level word:

> *For readers **new to ClickHouse** — assumes you've used a SQL database before but not this one.*
> *Intermediate: you've run ClickHouse queries; this covers the ingestion slice.*
> *Expert reference: you run ClickHouse daily; this is the project-specific ingestion runbook.*

This tells the reader what they're holding and makes "regenerate at another level" an obvious option.

## The required spine

Write these sections in this order (subject to the level's shape above). Headings use `##` for
Parts and `###` for Steps so the HTML builder can build a two-level TOC.

### 1. Title — `# H1`
Name the concrete thing being built and promise the end state in one or two sentences.

> `# OTW-5 — Unity greybox tracer: a step-by-step walkthrough`
>
> *This guide takes you from **no Unity project** to a **playable first-person greybox**: walk
> from the cabin to the Fork, commit, advance, reset, and break out at Depth 10.*

Immediately under the H1, add the **level subtitle** (see Levels) stating the assumed *vertical*
experience, and point at Troubleshooting up front so a stuck reader knows where to jump.

Then add the **not-yet-verified banner** — a warning callout, right after the subtitle, telling
the reader these steps weren't dry-run end-to-end so a command, path, or version may need
adjusting. It's mandatory at every level (the skill doesn't execute the steps it writes).

> **⚠️ Not yet verified.** These steps were written from the plan but haven't been run
> end-to-end, so a command, path, or version may need adjusting as you go. If a step doesn't
> behave as written, check **Troubleshooting** and adjust — then tell us what tripped, so the
> guide can be corrected.

### 2. "What you're building" — the mental model
One section, read **before touching anything**, that gives the reader the map the rest of the
guide hangs on. For HITL work this is where you draw the **seam**: what already exists (code,
tested modules, infra) vs. what the reader is about to build by hand, and the one rule that
keeps them on the right side of it. Make it the most important section and say so.

*By level:* full at beginner, a brief recap at intermediate, **omitted at expert** (a fluent
reader already holds the map). The HITL seam, if there is one, survives at every level it applies to.

### 3. Vocabulary
A short glossary so the guide, the tool's UI, and any code all use the same words. Define
the nouns the reader will see in menus and the nouns the code uses, and bridge them.

*By level:* full glossary at beginner, slice-specific terms only at intermediate, **omitted at expert**.

### 4. Prerequisites
Exact, checkable: tool versions, installs, accounts, OS notes. No "latest version" — name it.

*By level:* spelled out at beginner; at expert, only version- or project-specific setup a fluent
reader couldn't already assume.

### 5. Parts and Steps
`## Part N — <goal>` groups; `### Step N.M — <action>` within. **Granularity scales by level** —
name every menu/button/field at beginner, commands + key fields at intermediate, terse decisive
commands at expert (but never drop a step; an expert runbook is still complete, just unembellished). Rules:

- **Name every UI element**: the exact menu path, button label, field name, and the value to
  type. "Set **Project Settings → Player → Active Input Handling** to **Both**", not "configure input".
- **One action per step.** If a step has a sub-list, each item is still one concrete action.
- **No forward references** the reader can't act on. If something is wired later, say when and
  back-link to it from there.
- **Show the result**: "you should now see…", so the reader can self-check before moving on.
- **Code/config blocks** get fenced with a language tag (the HTML builder renders a copy button).
- Put repo-hygiene / setup that must happen *before* the tool opens in a **Part 0**.

### 6. Troubleshooting
A dedicated Part near the end: the errors they're most likely to hit, each with the symptom
and the **exact** fix. This is what makes a tutorial survive contact with a real reader.

### 7. Verify
A checklist that maps **one-to-one** to the acceptance criteria or definition of done, so the
reader knows they're finished and (for HITL) the work satisfies the brief. Use task-list
syntax (`- [ ]`) — the HTML builder turns these into progress-tracked checkboxes.

A short **"What's next (not this slice)"** is welcome to set the boundary, but keep it out of scope.

## Voice

- Second person, present tense, imperative: "Open the **Hierarchy**. Right-click → **Create Empty**."
- Confident and concrete. Prefer the exact value over a vague description.
- Explain **why** whenever a step is non-obvious or has a tempting wrong path — in a callout, so
  the why never clutters the do.
- Calm about footguns: name the trap plainly and give the fix, don't dramatize.

## Callouts (blockquotes)

Use `>` blockquotes for asides that aren't part of the linear do-this-now flow:

- **Why / context**: explain a decision, a trade-off, the reason a step exists.
- **Warning / footgun**: the HTML builder styles a callout as a warning when it leads with a
  warning marker. Start the blockquote with **⚠️**, or a bolded lead like **Heads-up**,
  **Gotcha**, **Warning**, **Caution**, **The #1 mistake**, **Don't**, or **Decision point** —
  these render amber.

```
> **⚠️ Heads-up — the part everyone trips on.** Unity won't compile the modules until you add
> the compat shim in Step 2.2. If you see `CS0246` now, that's expected; it clears in 2.2.
```

Callouts may contain lists and tables; keep them short — a paragraph or two.

## Length & splitting

A beginner walkthrough runs long (a thousand lines is normal) — that's fine; completeness beats
brevity there. **Length follows the level**: an expert runbook covering the same slice may be a
fraction of that. Either way the Markdown stays one file so the reader can search and the HTML
builds one page. Don't split a single walkthrough across files.

## After the draft — review checklist

- [ ] The level subtitle is present and phrased by **vertical experience**, not seniority.
- [ ] A reader **at the chosen level** could follow it top-to-bottom without outside *vertical*
      knowledge — and without being taught any general engineering.
- [ ] The shape matches the level: mental-model/vocabulary present-or-dropped per the table;
      no general-engineering explanation crept in at beginner.
- [ ] Step granularity matches the level (every field named at beginner → terse at expert), with
      no "configure the settings" hand-waving at any level, and **no step dropped**.
- [ ] Why-callouts match the level's density (every fork at beginner → counterintuitive gotchas at expert).
- [ ] No forward reference is left dangling.
- [ ] Troubleshooting and Verify are present (the floor holds at every level); Verify maps to the acceptance criteria 1:1.
- [ ] (If HTML) built from the Markdown, not hand-edited; both paths reported.
