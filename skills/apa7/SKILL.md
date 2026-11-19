---
name: apa7
description: >-
  Audit a paper for APA 7th edition compliance in two passes. Formatting: title page, headings,
  in-text citations, quotations, number/mechanics style, tables/figures, the
  reference list, and document layout (margins, font, spacing, page numbers,
  hanging indents). Writing style (Publication Manual Ch. 1, 4, 5, 8): tone,
  conciseness, precision, verb tense, voice, pronouns, modifiers, bias-free
  language, paraphrasing and plagiarism. Use this whenever the user asks to check, proofread, review,
  or "APA-ify" a paper, essay, manuscript, assignment, or article, or mentions
  APA, APA 7, APA style, citations, references, works-cited, headings, title page,
  running head, hanging indents, bias-free language, "scholarly voice," wordiness,
  tense, or passive voice — even if they don't say the word "format."
  Also use when they hand over a .docx, PDF, or draft and ask "is this formatted
  right?" or "did I cite this correctly?" Report-only by default: it produces a
  categorized audit with fixes and does not change files unless asked.
---

# APA 7 Format and Style Check

Audit a paper against APA 7th edition (student-paper) rules and return a
categorized, actionable report. **Default behavior is report-only** — find and
explain every issue with its location, the rule, and the fix; change nothing
unless the user explicitly asks you to apply fixes.

Two rule catalogs, both read before auditing:
- `references/apa7-rules.md` — **formatting**: how the paper looks (layout, title
  page, headings, citation and reference formats).
- `references/apa7-style.md` — **writing style**: how the paper reads (Ch. 1, 4,
  5, 8 of the manual), with section numbers and hard/judgment tags.

Run both passes unless the user asks for only one ("just formatting," "just check
my writing").

## When to use

Any request to check, review, proofread, or format a paper for APA — or any
question about whether citations, references, headings, the title page, or layout
are correct. Assume a **student paper** unless the user says it's professional
(the differences are in `references/apa7-rules.md` §10).

## What it checks

1. Whole-document formatting (margins, font, spacing, alignment, indent, page #s)
2. Title page (student): title, author, affiliation, course, instructor, due date
3. Headings — all five levels, correct format and order, no "Introduction" heading
4. In-text citations (paraphrase vs. quote, et al., ampersand, multiple works,
   secondary sources, group authors)
5. Direct quotations (short vs. 40+-word block quotes, page numbers)
6. Numbers, statistics, and mechanics (numerals vs. words, leading zeros, en dashes)
7. Tables and figures (numbering, labels, titles, notes)
8. Reference list (alphabetical order, hanging indent, entry templates, DOIs)
9. Appendices

**Style pass** (`apa7-style.md`):

10. Scholarly voice and crediting sources: level of citation, patchwriting,
    quote vs. paraphrase, source-by-source march (§A)
11. Continuity, tone, conciseness, jargon, anthropomorphism (§B)
12. Grammar: tense by section, voice, pronouns, that/which, modifiers,
    parallelism (§C)
13. Bias-free language: specificity, labels, age, disability, gender, race and
    ethnicity, sexual orientation, SES (§D)

## Workflow

### Step 1 — Get the file and its format

Confirm the path to the paper. It will usually be **.docx** or **PDF**. If they paste text directly, treat it as content-only
(no visual-layout checks possible — say so).

### Step 1b — Client-information check (clinical papers)

Case conceptualizations, assessment reports, treatment plans, process notes and
practicum write-ups can contain real client information. This skill never audits
those until they are de-identified.
- **Ask first** when the paper type is clinical: "Is this de-identified, or a
  fictional or published case?" Wait for the answer before reading further.
- **Stop if you see identifiers** at any point: a client's real name or initials
  with other details, birth date, exact age plus other specifics, school, employer
  or practicum-site name, address, dates of service, record or case numbers, or
  photos. Say what kind of detail you saw (never repeat it), ask the user to
  de-identify the paper or confirm it is fictional, and audit nothing until they do.
- **Never quote identifying details** in the report, even from a paper the user
  says is fine. Point to the location ("p. 2, para 1") instead.
- Fictional cases, textbook vignettes and published case studies are fine to audit.

### Step 2 — Extract structure

**For .docx** — run the bundled inspector. It reads the Word XML directly (no
dependencies) and reports layout facts plus deterministic layout violations, so
you don't have to guess at margins, spacing, fonts, page numbers, or hanging
indents:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check_docx.py" "<path>" --json
```

Use `--full` instead of `--json` for a readable dump that also lists every
paragraph with its formatting (handy for tracing a specific heading). The JSON's
`structural_findings` are high-confidence layout issues — fold them straight into
your report. The `paragraphs[].text` values give you the full text for the
content-level checks in Step 3.

**For PDF** — extract the text for content checks:

```bash
pdftotext -layout "<path>" - 2>/dev/null   # if poppler is installed
```

If `pdftotext` isn't available, read the PDF with the Read tool (`pages`
parameter) or the `pdf` skill. A PDF shows visual layout when rendered, so you
*can* judge title-page layout, heading styling, and page numbers by reading the
rendered pages — but you can't measure margins or confirm true double-spacing from
extracted text. Note any layout item you couldn't verify as **Check**.

### Step 2b — Confirm layout visually (backup check)

The XML scan can be wrong: Google Docs exports, section-specific headers, styles
inherited from a template, and tab-faked indents all read differently in XML than
on the page. **Before reporting any layout or heading-format finding, confirm it on
a rendered page.**
- **If the paper lives in Google Docs**, a downloaded .docx may be an older
  copy. Ask which version is current. If a Google Drive connector is available,
  you can find the Doc (`search_files`, `title contains '<words>'`) and export it
  with `download_file_content` and `exportMimeType: application/pdf`; the result
  is JSON, so base64-decode its `content` field to a .pdf and render it as below.
  Otherwise ask the user to download it as PDF. The live Doc is the version to audit.
- **The .docx scanner skips tables.** A section that looks empty in the scan may
  hold a table. Check the render before reporting anything as missing.
- If a PDF of the same paper exists, or the user can export one (Word: File >
  Save As > PDF; Google Docs: File > Download > PDF), render the pages:
  `pdftoppm -png -r 80 "<pdf>" <temp folder>/page`. Then look at each PNG with the
  Read tool. Screenshots the user sends also work.
- Don't try to render through Word or Pages with AppleScript: both are sandboxed
  and usually can't reach a temp folder (it hangs or fails).
- If no render is available, report XML-only layout findings as 🔎 **Check**, not
  ❌ Error, and say they came from the file's XML, not from the visible page.
- When the render and the XML disagree, the **render wins**.

### Step 3 — Audit against the rule catalog

Read `references/apa7-rules.md` and walk it **category by category**. For each
rule decide Pass / Fail / Can't-verify. The content-level work (citations,
quotations, numbers, references) is yours to judge from the extracted text; the
`.docx` script has already handled most layout rules.

High-value checks the script can't make for you:
- **Citation ↔ reference cross-check.** Build the set of in-text author-year
  citations and the set of reference entries. Flag citations with no matching
  entry, and entries never cited. This is one of the most common real errors.
- **Reference alphabetical order** and **entry templates** (journal vs. book vs.
  chapter; sentence case for titles, title case + italics for journal names).
- **et al. / ampersand / semicolon** rules in in-text citations.
- **Quotes missing a page number**; passages 40+ words that should be block quotes.
- **Heading level order and wording** (no "Introduction" heading; title case).
- **Number style** (leading zeros, numerals vs. words, en dashes in ranges).

Don't invent violations. If the text doesn't show a rule being broken, it passes.
Precision matters more than volume — a grader-relevant miss beats ten nitpicks.

### Step 3b — Style pass

Read `references/apa7-style.md` and walk sections A–D against the paper's text.
- **Severity follows the tags.** `[hard]`/`[HARD]` items are Warnings or Errors;
  `[judgment]`/`[J]` items are **Suggestions** at most. Items in "Beyond the 2020
  manual" are never flagged as errors — mention them only if clearly relevant.
- **Flag, don't rewrite.** Quote the phrase, name the rule (§ number), and give a
  minimal fix for *that phrase*. Never rewrite paragraphs or redraft the argument —
  it's the user's graded work. Offer a fuller edit only if asked.
- **Patterns over instances.** If the same issue recurs (passive voice, "this
  shows" without a noun, wordy openers), report it once with 2–3 examples and a
  count, not ten separate findings.
- **Cap the noise.** Around 10–15 style findings for a typical paper, ranked by
  how much they'd cost with a grader: bias-free language and plagiarism or
  patchwriting first, then tense/voice consistency, then concision and polish.
- **Respect the genre.** A reflection paper uses first person and personal
  experience legitimately; don't flag "I" there (§4.16, §1.10).

### Step 4 — Report

Produce the report in the template below. Omit categories that have no findings,
or mark them `✓ Looks good`. Lead with a summary so the user sees the big picture
first. Keep each finding tight: location, the problem, the rule, the fix.

After the report, offer to apply fixes: for a **.docx** you can edit the file (or
a copy) to correct layout and mechanics; for a **PDF** you can hand back a
corrected-text or a marked-up list, since PDFs aren't edited in place. Wait for
the user to say go — this is graded work and report-only is the safe default.

## Report template

```
# APA 7 Format and Style Check — <filename>

**Assumed paper type:** Student  (tell me if it's professional)
**Checked:** .docx (layout + content)  /  PDF (content; layout noted)

## Summary
<n> errors · <n> warnings · <n> to verify. One line on overall state.
Title page <✓/✗> · Headings <✓/✗> · In-text citations <✓/✗> ·
Quotations <✓/✗> · Numbers/mechanics <✓/✗> · References <✓/✗> ·
Tables/Figures <✓/✗> · Layout <✓/✗>
Style: Voice/sources <✓/✗> · Clarity/tone <✓/✗> · Grammar <✓/✗> · Bias-free <✓/✗>

## Findings

### <Category>
- ❌ **[Error]** <location> — <what's wrong>.
  **Rule:** <the APA rule.>  **Fix:** <what to change.>
- ⚠️ **[Warning]** …
- 🔎 **[Check]** … (needs the source / the live file / your judgment)

## Style
### <A–D section>
- ⚠️ **[Warning]** <location>: "<quoted phrase>" — <problem>.
  **Rule:** §<n> <name>.  **Fix:** <minimal change to that phrase>.
- 💡 **[Suggestion]** … (judgment-call items; recurring patterns with a count)

## Couldn't verify
<Anything that needs the original file, a visual render, or source access.>
```

## Notes

- **Severity:** Error = a grader will mark it; Warning = likely wrong or
  inconsistent; Check = unverifiable from this input or a judgment call. Rank
  Errors first.
- **Locations:** cite by page/paragraph and quote the offending text so the user
  can find it fast (e.g., *p. 3, para 2: "Seldin (1993, as cited in Pounder,
  2007)"*).
- **Suggestion** (style pass only) = a judgment call from the manual; the user
  decides.
- **Content vs. accuracy:** this skill checks *formatting and style*, not whether a source
  is real or a claim is supported. Say so if the user seems to expect fact- or
  citation-accuracy checking.
