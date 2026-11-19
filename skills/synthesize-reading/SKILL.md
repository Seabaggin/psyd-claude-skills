---
name: synthesize-reading
description: Turn the user's own highlights and margin notes on a reading (from Zotero, a PDF reader, Readwise, or pasted in) into a short, retrieval-first study note, after they've read and annotated it. Use when the user asks to synthesize, write up, or "turn my highlights into a note" for an article, chapter, or book — e.g. "synthesize my Smith 2024 highlights", "I annotated the Sue chapter, make the note" — even if they don't say "synthesize." Produces a TL;DR card, sortable design/population/measures fields, and expanded key points (articles), or one block per chapter (books and textbooks). Works only from what the user highlighted. NOT a substitute for reading, NOT for graded reading responses or discussion posts, and NOT for pre-read or post-read coaching (that's reading-coach).
---

# Turn your highlights into a short study note

**Design goal: utility at scale.** A grad student collects hundreds of sources across
coursework, practicum and a dissertation. A study note exists to help the user
**find** a source later and **judge** it when citing, not to re-teach it. The PDF
is one click away; don't reproduce it. Short beats thorough.

## Guardrails
- **The user's highlights are the input.** If they haven't read and annotated the
  source, stop and say so; offer the `reading-coach` pre-read instead. Never build a
  note from the PDF alone.
- **Study notes only.** If the note is going into a graded assignment (a reading
  response, a discussion post, an annotated bibliography entry), stop: that writing
  is theirs. Offer to check it instead.
- **Never invent.** Every claim, number and page number comes from the source or
  the highlights. If a page number is unknown, leave `(p. ?)` rather than guess.
- **Their margin notes are theirs.** Quote them verbatim; never paraphrase or drop them.
- **Never move, rename or modify the PDF or the reference-manager library.** Read only.

## Where the note goes
Ask once where the note should live and in what format, unless it's obvious from
the conversation (an existing note to fill in, a folder of source notes).
- **Obsidian or another Markdown app:** write the callout form shown below
  (`> [!abstract]+ TL;DR`). Other apps render callouts as plain blockquotes, which is fine.
- **Word, Google Docs, Notion:** use the same sections as plain headings.
- **If the note was made by an import plugin** (e.g. Zotero Integration with
  `{% persist %}` blocks or `%% begin … %%` markers): edit only inside the regions the
  template keeps across re-imports. Anything outside them is regenerated on the next
  import and your work would be lost. If unsure which regions persist, ask.

## Two anatomies

**Journal articles** are read once, so the synthesis can *replace* the raw
highlights. The finished note is:

```
--- frontmatter (optional) ---  design / population / measures
> [!abstract]+ TL;DR
> [!keypoints]+ Key points       (expanded)
> [!figure]- Figures             ONLY if the highlights held images
```

Nothing from the highlights may be lost silently: every highlight is either
folded into the synthesis or deliberately judged not worth keeping, and every
margin note goes into **My notes**. If the user prefers to keep the raw highlights
under the synthesis, keep them.

**Figures:** image highlights are never deleted. Any image not already embedded
in the synthesis moves, in page order, into one collapsed callout at the end of
the note. Omit it when there are no leftover images.

**Textbooks and books** are read across weeks, chapter by chapter. Keep the raw
highlights, and add to the note one chapter at a time:

```
> [!abstract]+ About this book
> [!chapter]- Ch. N — Title      one collapsed block per chapter read
(raw highlights, untouched)
```

## Step 1 — Gather

1. Read all the highlights; they are the priority signal. For each one, **infer
   why the user marked it** (a definition to cite, a surprising finding, a clinical
   takeaway, a critique, a named concept). The synthesis must carry that reason, not
   just the text.
2. If the user shares the PDF, read it (`pdftotext -layout`, or directly) for design,
   sample, measures, page numbers and printed learning objectives.
3. Ask which course it's for, only if the user wants that recorded.

## Step 1a — Weigh the source by consequence

Size the note by **how much the source will matter to the user's work**, not by
paper length. Ask: what does it feed, and will they act on it in practice?

- **Core** — feeds work they will *do*: assessment instruments, diagnosis,
  intervention evidence, ethics standards, practicum skills. Keep the numbers,
  caveats and specifics a clinician or citation needs. Up to ~350 words.
- **Discussion** — interesting, good for class talk, but not consequential
  (professional-development pieces, opinion or educator-experience studies). Keep
  the claim, the quotable definitions, and the one or two vivid findings worth
  bringing up in discussion. ≤ ~200 words.

Cut by usefulness, not by count: drop anything they would never pull up again
(per-discipline breakdowns, workload anecdotes, method minutiae), but keep the
single best discussion example even in a short note. When unsure which tier, say
which you chose in one line of the final reply.

## Step 1b — Confirm "simple" before writing

If the paper looks **simple** (see "Simple papers" under Step 3), stop before writing
and ask in one line, e.g.: "This reads as a simple paper (position piece, one claim,
~3 ideas) — use the short format?" Proceed only after they answer. If it isn't
simple, don't ask; use the standard format.

## Step 1c — Ask when a highlight's significance is unclear

If you can't tell why a highlight mattered (a stray sentence, a fragment, an aside
that fits no theme), list those highlights with page numbers and ask what drew them
to each, in one message, before writing. Fold the answers in. If every highlight's
purpose is clear, don't ask. Combine this with the Step 1b question when both apply.

## Step 2 — Fields + TL;DR

### Fields (optional, for sorting a library of notes)

If the user keeps source notes in a database (Obsidian Bases or Dataview, Notion),
add `design`, `population` and `measures` as properties. Otherwise put them in the
TL;DR's Evidence line and skip this.

- **design** — exactly one value from this list:
  `meta-analysis` · `systematic review` · `RCT` · `quasi-experimental` ·
  `longitudinal` · `cross-sectional` · `psychometric` · `qualitative` ·
  `mixed methods` · `case study` · `narrative review` · `theoretical` ·
  `textbook` · `book`
  (`narrative review` = scoping or non-systematic reviews; `theoretical` = position,
  conceptual, teaching or framework papers; `psychometric` = test construction,
  validation, norming; `book` = an author's own voice rather than a survey text.)
- **population** — short free text: who was studied, with the detail that decides
  generalizability (n, setting, notable skew). Omit for theoretical papers, reviews
  and books.
- **measures** — instruments actually administered, `;`-separated, standard
  abbreviations (PANAS; SWLS). Omit when none.

### TL;DR

```markdown
> [!abstract]+ TL;DR
> **Claim** — <one sentence: the finding or argument>
>
> **Use it for** — <when you'd pull this up later: 1–3 retrieval cues, semicolon-separated>
>
> **Evidence** — <design · who · headline result, one line; for theory papers, what the argument rests on>
>
> **Frame** — <theoretical lens, only if the paper names one>
>
> **Limits** — <one line>
>
> **Follow up** — <1–3 references worth chasing, only if any stand out>
>
> **My notes**
> - <(p. N) *the user's margin note or take, verbatim*>
>
> **Links** — <related concepts or sources, each with ≤4 words of why>
```

About 100 words. **My notes** holds the user's own margin notes and takes, quoted
verbatim; omit the field when there are none. `Frame`, `Follow up` and `Links` are
optional; omit the whole line when empty. Statistics only if one number *is* the finding.

## Step 3 — Synthesis

### Journal articles: one expanded key-points block

```markdown
> [!keypoints]+ Key points
> - **Bold lead-in** — one idea per bullet, ≤ ~30 words
```

- **3–7 bullets.** Whole-note length follows the Step 1a tier (discussion ≤ ~200,
  core up to ~350); count before finishing. Lead with what the user highlighted.
- Keep: quotable definitions **with page numbers** (APA needs them: `(p. 2)`), the
  core findings, the clinical takeaway, a key caveat.
- Cut: sample cleaning, statistical procedure, per-section structure, self-tests,
  "in plain terms" restatements.
- **Numbers must be readable.** For empirical papers, report the key results *with
  their numbers* and say what the numbers mean:
  1. A **"Reading the numbers"** bullet whenever the paper uses a metric a reader
     can't interpret cold (D scores, ω, AUC, $r$, OR, Cohen's *d*, $g$, $\alpha$,
     percentiles, index scores): the metric, its scale or range, which direction is
     "more," and the conventional size benchmarks.
  2. **Results bullets** carry the actual values with a plain-language gloss
     ("$r = -.25$, a small negative correlation"; "$d = .62$, medium").
  3. Don't dump every number: the headline results and the ones a citation would need.
  Theoretical papers with no data skip this.
- At most **one** table or figure, only when it beats bullets.
- A short "vs." bullet only when two terms are genuinely confusable.

### Simple papers: go shorter

A paper is **simple** when it checks most of these: no study of its own (position,
theory, teaching or commentary); the claim fits in one sentence and the rest
elaborates it; only ~3–4 retrievable ideas (a definition, a named concept, a
framework); its best content is mostly "as cited" from others. Judge the paper, not
its length or the highlight count. Empirical studies are never simple (sample,
measures and limits matter when citing). Always confirm with the user first (Step 1b).

For a simple paper:
- **TL;DR** keeps only Claim, Use it for, Evidence, Links. Drop Frame, Limits and
  Follow up unless one truly stands out.
- **Key points**: 2–4 bullets, one per retrievable idea.
- **Every named concept gets its own bullet**; never fold it into another bullet's tail.

### Books and textbooks: overview card + one collapsed block per chapter

```markdown
> [!abstract]+ About this book
> **Purpose** — <what the book is for, and its stance>
>
> **Used in** — <course · chapters assigned, if the user wants this>
>
> **How it's organized** — <one line>
>
> **Links** — <concepts it feeds most>
```

**`book` vs. `textbook`:** a `book` is an author's own voice (a clinician's memoir,
nonfiction for clinicians). It never has learning objectives or per-chapter blocks.
Its card is:

```markdown
> [!abstract]+ About this book
> **What's the point** — <what the book is and its core conviction>
>
> **Why it's worth reading** — <its value to a trainee; when you'd reread it>
>
> **Links** — <concepts>
```

and its synthesis is one collapsed `> [!keypoints]- Chapter notes` holding, per
chapter read, a bold `**Ch. N — Title**` line and 1–3 bullets (or a sentence or two)
of anything of note. Only textbooks get the structure below.

**Chapter length:** about **150–350 words per chapter** (objectives excluded), a
guide, not a quota. If the summary already captures what's worth retrieving, stop;
never pad. A dense chapter can run to the top of the range.

**Short-chapter books** (a few pages per chapter, no printed objectives): skip
per-chapter blocks; use one collapsed `[!keypoints]-` with one bullet per chapter,
the chapter number in the lead-in. Otherwise, one block per chapter read, in
chapter order, all collapsed:

```markdown
> [!chapter]- Ch. 19 — <Chapter title>
> **Learning objectives**
> 1. <printed LOs, verbatim; if none, omit the Learning objectives label entirely>
>
> - **Bold lead-in** — concise bullets, as many as the chapter earns
>
> **Feeds** — <concepts>
```

## Step 3b — Enumerations are lists, never run-on lines

Whenever a bullet names **three or more parallel items** (types, models, steps,
stages, criteria, components, strategies), keep the bullet's bold lead-in and put
the items on their own lines as a nested numbered list, each with its own short
gloss if it had one:

```markdown
> - **Three models of disability** — the author argues for the affirmative (p. 2).
>     1. **Medical** — impairment as a health problem in the person.
>     2. **Social** — disability is the barriers society builds around impairment.
>     3. **Affirmative** — disabled and nondisabled lives valued equally.
```

Never chain items with `;`, `·` or commas inside one bullet. Exceptions: the
**Links** / **Feeds** / **Use it for** lines, and number ranges or statistics.

## Step 4 — Finish

1. Every margin note from the annotations appears in **My notes**, verbatim.
2. Every image highlight is either in the synthesis or in **Figures**.
3. **Articles:** the word count fits the tier. **Books:** the raw highlights are
   byte-identical to before.
4. If the note came from an import plugin, confirm your edits sit only inside the
   regions that survive re-import.
5. Tell the user which tier you chose and anything you judged not worth keeping.
