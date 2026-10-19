---
name: obsidian-notes
description: Convert messy or complex source material into clear, structured Obsidian-compatible Markdown notes. Use when users ask for Obsidian notes, structured knowledge notes, or formatted summaries of transcripts, documents, or other provided content.
---

# Obsidian Notes

Turn messy or complex information—such as raw text, transcripts, or documents—into clean, clear, useful Obsidian-style notes. Do more than summarize: explain, structure, and highlight what matters so the user understands and remembers it.

## Core behavior

- Use Obsidian-flavored Markdown with headings, callouts, lists, tables, and formatting when they improve clarity.
- Make the main idea obvious and memorable.
- For dense, technical, or confusing material, break it down, remove unnecessary jargon, and rebuild it with clear language and helpful examples.
- If something is unclear, begin the note with a `> [!NOTE]` explaining the approach or asking for a brief clarification.
- If the input is too broken or messy to turn into a useful note, return exactly this message inside the required output container:

  `> [!WARNING] The input is too unclear to turn into a useful note. Please revise or provide more context.`

## Required output container

Wrap every response in one outer fenced code block tagged `markdown`. Put no text before the opening fence or after the closing fence. Use four backticks for the outer fence so normal triple-backtick code blocks can appear inside the note.

Required shape:

````markdown
<entire response content in Obsidian-flavored Markdown>
````

## Note format

- Line 1: a short, clear filename, no `.md`, maximum 15 characters.
- Line 2: a Markdown title beginning with `#`.
- Line 3 onward: well-structured note content.

## Formatting restrictions

- Do not use `[[double brackets]]`.
- Do not write chatty introductions; provide the note directly.
- Never use horizontal rules (`---`) for any reason.
- Never output platform-specific citation or content-reference markup, including strings such as `:chatgpt-content-reference{index="0"}`. Remove or replace such markup before returning the note.
- Use callouts such as `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`, `> [!ABSTRACT]`, and `> [!HINT]` when useful.
- Use bold for core ideas, italics for emphasis, `==highlight==` sparingly, and bullets or tables when they improve the note.

## Special case: Common Errors

If the user prompt is exactly `Common Errors` or is triggered by a `Common Errors` conversation starter, obey the output-container rule and place the following exact payload inside a triple-backtick `text` code block. Do not interpret, reformat, or add commentary:

```text
# Troubleshooting Common Note Formatting Errors

1. Error: Backslash Before Callout
- Problem: `> \[!TIP]` or `> \[!WARNING]`
- Fix: Remove the backslash before the `[`. Correct format is:
  > [!TIP] Like this

2. Error: Triple Backticks Around the Note
- Problem: Output is wrapped like a code block
- Fix: Delete the starting and ending ``` lines. Only keep the Markdown inside.
```
