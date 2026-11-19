# PsyD Claude Skills

Four small skills for Claude Code, made by a first-year PsyD student for anyone in a clinical or counseling psychology program. They came out of a real first semester: papers that needed APA checks, AI policies that needed honest disclosures, and readings that needed actual reading.

**The ethics line:** these skills help you think, check and disclose. They never write your graded work or handle client information. They don't invent citations, and they always leave room for you to disclose how you used them.

## Install

You need [Claude Code](https://claude.com/claude-code). In a terminal:

```bash
claude plugin marketplace add Seabaggin/psyd-claude-skills
```

```bash
claude plugin install psyd-skills@psyd-claude-skills
```

Restart Claude Code, and the skills turn on by themselves when your request matches. You can also call one by name, for example `/psyd-skills:apa7`.

To remove it later:

```bash
claude plugin uninstall psyd-skills@psyd-claude-skills
```

## The skills

### apa7: check a paper against APA 7

Reads your .docx, PDF or pasted text and gives you a sorted report: title page, headings, citations, quotations, numbers, tables, references, page layout, and a second pass on writing style and bias-free language. For a .docx it measures margins, fonts, spacing and hanging indents directly from the file.

- **Triggers when** you ask it to check, proofread or "APA-ify" a paper, or ask whether something is cited or formatted right.
- **What it won't do:** change your file. It reports, quotes the spot, names the rule and suggests a minimal fix. It edits only if you ask. It also doesn't check whether a source is real or a claim is true. That part stays with you.
- **Clinical papers:** for a case conceptualization, assessment report or anything similar, it first asks whether the paper is de-identified, and it stops if it spots identifying client details.
- **Needs:** Python 3 for the .docx layout check (already on most Macs; on Windows, install it from python.org). Pasted text and PDFs work without it.

### ai-disclosure: say how you used AI, honestly

Drafts the two-to-four-sentence AI-use statement many programs now ask for, based on what Claude actually helped with in your conversation, and the APA reference for Claude.

- **Triggers when** you say "AI disclosure," "add the AI statement," or ask how to word your AI use for an assignment.
- **What it won't do:** hide or shrink help that happened, or invent help that didn't. If the help went past your course's policy, it tells you first so you can decide. It asks for your syllabus's AI policy, because your course's rules are the ones that count.

### reading-coach: get ready to read, then get pushed on what you read

Two modes. **Pre-read** gives you just enough to read actively: where the paper or chapter sits, terms you can't get from context, the study design, the statistics you'll meet, and two questions to hold while reading. **Post-read** checks your own notes and asks you hard questions about claims, samples, inference and what it would change with a client.

- **Triggers when** you say "pre-read," "prime me for X," "post-read," "pressure-test me on X," or share your notes on something you just read.
- **What it won't do:** summarize, preview findings, or fill gaps you didn't work on. If your notes are thin, it says so and asks you to try again. Without the PDF or text it won't guess at a reading's details; it asks for the text first, or marks anything specific as unconfirmed.

### synthesize-reading: turn your highlights into a short study note

After you've read and highlighted something (in Zotero, a PDF reader, Readwise, or pasted in), it turns your highlights and margin notes into a short note you'll actually use later: a TL;DR card, key points with readable numbers and page numbers, and one block per chapter for textbooks. Notes are sized by how much the source matters to your work. Your margin notes are quoted word for word.

- **Triggers when** you ask to synthesize a reading or "turn my highlights into a note."
- **What it won't do:** work without your highlights (no reading, no note), write graded reading responses or discussion posts, or invent page numbers. It reads your PDFs and never moves or edits them.

## Good to know

- **Some skills use free command-line tools when they're installed:** `pdftotext`, `pdftoppm` and `pdffonts` come from Poppler (`brew install poppler` on a Mac). Without them, Claude reads PDFs another way.
- **Your course's rules come first.** Every syllabus has its own AI policy and rubric. When a skill and your syllabus disagree, the syllabus wins.
- **Keep client information out of Claude entirely.** None of these skills need it, and none should ever see it.
- **Disclose.** If you used any of these on a submission, the `ai-disclosure` skill will help you say so.

## License

MIT. See [LICENSE](LICENSE).
