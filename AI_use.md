# Use of Generative AI

This file accompanies the paper *Momentum-Driven Growth–Value Style Rotation* (MDPI *Investment*, manuscript investment-4633668) by Zibo Wang, Weiqi Zhang and Eugene Pinsky. It describes how a generative AI tool was used. It supplements the "Use of Generative AI" subsection in the paper's Data and Methodology section.

## Tool

- **Tool:** Claude (Opus 5.5), Anthropic
- **Interface:** claude.ai
- **Period of use:** September–November 2026

## How the tool was used

We worked with Claude in three interactive sessions. The Python scripts in `replication_code/` were developed in sessions 2 and 3, not from separate prompts written to generate code. In each session we gave the tool the manuscript, the reviewer reports (during the revision) and the data files in this repository, and made high-level requests. The tool then wrote and ran the scripts and corrected them in further iterations. We reviewed the code, its output and the text.

This is a summary of our instructions, not their verbatim text:

1. **Manuscript preparation (September 2026).** Review the manuscript and prepare it for submission: expand the literature review (with references), revise the title and abstract, separate the Introduction and Literature Review, and add a Limitations section. No analysis code was written in this session.
2. **Before submission (October 2026).** Review the manuscript and the analysis code, and correct any errors. Extend the empirical analysis with additional tests, tables, robustness checks and references, using only the data in this repository.
3. **Revision (November 2026).** Revise the manuscript in response to the reviewer reports, including any additional analyses, tables, figures and references needed to address the reviewers' comments.

The tool was also used to help derive and check formulas and to draft and edit the manuscript text.

## Tables and figures

All tables (Tables 1–20) and figures (Figures 1–7) in the paper are produced by the scripts in `replication_code/` from the data in this repository (see `replication_code/README.md`). None was generated directly by the AI tool. The scripts are deterministic, so every reported number can be reproduced by running them, without using the AI tool.

## Responsibility

The AI tool proposed and implemented additional analyses. The authors reviewed, selected and approved all analyses and results reported, and take full responsibility for the content of the paper.

## Screenshots of the chat sessions

The folder `AI_screenshots/` contains screenshots of the two chat sessions in which the scripts and analyses were developed (sessions 2 and 3). For each session, the screenshots show the opening instructions, representative exchanges in which code was written, run and corrected, and examples of the authors' follow-up (S2_05: author corrections before submission; S3_04: the authors asking which additional data to obtain for the revision). Session 1 involved only text and references, not code, so it is described above but not shown. Session 3 took place in a chat that began with work on an unrelated paper; its screenshots start at the request for this paper. Personal contact details and material unrelated to this paper have been masked.

| Session | Date | Purpose | Files |
|---|---|---|---|
| 1 | 21 September 2026 | Manuscript text and references (no code) | — |
| 2 | 1 October 2026 | Reviewing and extending the analysis before submission | `AI_screenshots/S2_*.png` |
| 3 | November 2026 | Revision in response to the reviewer reports | `AI_screenshots/S3_*.png` |

## Session transcripts

The complete session transcripts are available to the journal's editorial office on request from the corresponding author (Eugene Pinsky, epinsky@bu.edu).
