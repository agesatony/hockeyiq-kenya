# HockeyIQ Kenya — Full Project Audit

Prepared as part of prepping this project to go live. Covers: what was
reviewed, what was fixed, what was verified, and — importantly — what
could **not** be verified from the environment this audit was performed
in, so nothing here is overstated as "confirmed working" when it wasn't
actually run.

## Scope reviewed

All five pipeline notebooks (`01_scraping` → `05_worldcup_live`), in
execution order, cell by cell (390 cells in `03_advanced_analytics.ipynb`
alone). A prior chat-log export (originally delivered as a `.docx`) was
also reviewed; it documents an earlier debugging session that fixed the
World Cup pool-tab click bug now living in `05_worldcup_live.ipynb`.

## Fixes applied in this pass

### 1. Dead World Cup scraper cells removed from `04_international.ipynb`
`04_international.ipynb` carried its own, older copy of the World Cup
pool-standings scraper — from before the click-targeting fix (filtering
out non-interactive tags/classes like `<title>`, `<meta>`, and the
`pool venue` schedule labels, and preferring a real button/link/tab-role
element) that was applied only in `05_worldcup_live.ipynb`. Confirmed
directly in `04`'s own last recorded output: every pool click failed
(`could not click this pool's tab, skipping`) and it saved an **empty**
`world_cup_standings.csv`. Both notebooks wrote to the same file. If a
scheduled run of `04` executed after `05` had already produced good
data, the dead code would have silently overwritten live World Cup data
with an empty table. The three broken cells were deleted and replaced
with a markdown note pointing at `05` as the sole owner of this data.

### 2. Python-version syntax error fixed
A full syntax scan (every code cell in all 5 notebooks compiled under
Python 3.11) found one real syntax error: an f-string in the dashboard's
"Scoring Pattern" section embedded a backslash escape (`⚠️`,
a warning icon) directly inside an `{expression}` block. That's invalid
on Python < 3.12 (PEP 701 lifted the restriction only in 3.12) — the
notebook would fail to even parse that cell on a typical CI runner unless
Python 3.12+ is used. Fixed by pre-computing the icon as a plain variable
outside the f-string expression (portable on any Python version), and
the CI workflows additionally pin Python 3.12 as a second layer of
protection. This was the **only** syntax error found across all 1,559
cells in the 5 notebooks combined (post-prune count; see below).

### 3. Stale text in Module 21 fixed
The "Validity Statement" cell said predictive modelling "should only be
introduced after additional seasons have been collected" — written
before Module 34 (Elo Ratings & Win Probability) was added later in the
same notebook, which *does* build and independently validate a
predictive model (Brier score vs. a naive baseline). Rewritten to
describe what the notebook actually contains, without contradicting a
module that runs later in the same read-through.

### 4. Module 23 "Key Findings" and closing summary made data-driven
Previously static boilerplate ("clustering identified three distinct
competitive tiers," "correlation analysis confirmed strong
relationships" — with no numbers attached). Rewritten to report real
computed values from the current run: the actual Dominance Index leader
and score, the actual number and size of clusters found, the actual
playing-style breakdown, the actual Gini coefficient and balance rating,
and — added as the lead finding, since it was previously missing
entirely from this section — the actual event-data coverage rate. The
closing "Final Project Summary" now states the real match/team/
competition counts for the run instead of only generic language.

### 5. Coverage caveat added to the "All Scorers" dashboard table
The dashboard's Squad Reliance section already carried an explicit,
well-written callout about the ~1-in-5 event-coverage gap. The "All
Scorers" table (built from the same partial-coverage source) did not
have an equivalent note next to it, even though a viewer could reach
that table without passing through Squad Reliance first. Added a
matching caveat directly above it, and pointed to Module 38's
independent, more-complete all-time club scorer records as an
alternative source for the same question.

### 6. 15 orphaned cells removed from `03_advanced_analytics.ipynb`
The pre-"Module" section (roughly "Cell 123" through "Cell 300",
predating the numbered Module system used from Module 11 onward) reads
as repetitive on a title skim — "Discipline Ranking," "Clean Sheets," and
similar titles each appear 2-3 times. A full static dependency scan
(every cell's assigned variable names checked against every *later*
cell's read names, across the whole notebook) found that **most of this
apparent duplication is not actually duplication** — each occurrence
feeds a different downstream variable, chart, or CSV export than the
others. Only 15 cells turned out to be genuinely orphaned: they compute
a value or chart, save nothing to CSV, and are never read by anything
later. Those 15 were removed and documented in place (see the audit note
inserted at the top of that section in the notebook itself). Net cell
count: `03_advanced_analytics.ipynb` went from 390 → 376 cells.

**Deliberately not touched:** anything that saves a CSV, even if this
notebook doesn't read that CSV back itself (it may be a promised
deliverable used outside the notebook), and anything whose output is
read by a later cell. A deeper refactor of the remaining exploratory
section is possible but needs a real execution run against real data to
verify nothing breaks — seebelow for why that could not be done here.

## What could not be verified from this environment

This matters as much as the fixes above, and is stated plainly rather
than glossed over:

- **No live network egress to the target sites** (`kenyahockeyunion.org`,
  `tms.fih.ch`, `fih.hockey`, `africahockey.org`) from this sandbox's
  shell/Python — direct requests were blocked by the sandbox's network
  policy. Two of the four sites were spot-checked through a different,
  sanctioned fetch path (an AI-summarized page fetch, not a raw-HTML
  fetch) and both were reachable with content structurally consistent
  with what the scrapers expect (real team names, real pool/standings
  tables, matching the notebooks' own last recorded outputs). This is
  **not** the same as confirming the scrapers' actual CSS
  selectors/regex patterns still match the live DOM — that requires
  real HTML, which this environment could not fetch.
- **No Selenium or real Chrome browser available in this sandbox**
  (only Playwright's bundled Chromium, and the `selenium` Python package
  itself was not installed) — so none of the five notebooks could
  actually be executed here, against live sites or otherwise. Every fix
  above was verified by static analysis (AST parsing, dependency
  scanning, `compile()` syntax checks) — real, but not the same
  guarantee as watching a full run succeed.
- **GitHub Actions runners were not exercised** — the workflow YAML was
  validated for syntax correctness only. The runners' own network
  egress, available Chrome version, and `webdriver-manager`'s ability to
  fetch a matching ChromeDriver are all standard for GitHub-hosted
  `ubuntu-latest` runners but were not test-run here.
- **LinkedIn's API was not called** — no credentials exist for this
  project. `scripts/post_to_linkedin.py` was tested with `--dry-run`
  against realistic sample CSVs (output included below) and its failure
  paths (missing credentials, empty data) were exercised, but a real
  authenticated POST to LinkedIn's UGC Posts API has not been made.

```
HockeyIQ Kenya — weekly season update

Current leaders across Kenya Hockey Union's 2026 domestic competitions:
  • PLM: Sikh Union Nairobi (19 pts)
  • PLW: Blazers Hockey Club (18 pts)
  • NLM-EZ: Ulinzi Patriots (17 pts)
Top scorer so far: Mathias Gularire (Sikh Union Nairobi) — 6 goals.
```

**Bottom line:** treat this repo as audited-and-repaired at the code
level, not as "confirmed live." The go-live checklist in README.md's
last unchecked items — a real monitored first run, and LinkedIn
credentials — are the two things only a live run (yours, on GitHub's
infrastructure, which does have real internet access) or your own
LinkedIn login can complete.

## Findings carried over from the original review (still accurate)

These were identified in the first pass over the project and remain true
of the underlying data/methodology — none of them are bugs to fix, they
are honestly-documented properties of the source data that anyone
presenting this project's numbers should keep in mind:

- Only ~19% of matches with a recorded goal have full goal-by-goal event
  detail in the domestic source data (KHU's own site, confirmed directly,
  not a scraping gap). Every player-level metric describes that subset,
  not the full season. The dashboard surfaces this rate on its front page
  and (as of fix #5 above) above every affected table.
- Penalty corner/penalty stroke goal-source tagging does not exist in the
  domestic data model at all (confirmed against KHU's own published
  tables) — only the international FIH TMS data source has it.
- International coverage is 6 confirmed competitions spanning 2017-2025,
  explicitly not a complete history (FIH's own system only reliably
  covers 2013 onward, and several editions in that range aren't added).
- The FIH per-match advanced-statistics PDFs (possession, shots, circle
  entries) were tested against every match scraped and returned all-zero
  values throughout — a real, confirmed limitation of that specific
  report, not a parsing bug.
- The Elo model beats its naive baseline only marginally (Brier score
  0.187 vs. 0.190) given the small per-team sample sizes typical of a
  partial single season — reported honestly as "adds value" rather than
  oversold as strongly predictive.

## Full go-live checklist

See README.md — kept there so it's the single copy that stays current,
rather than duplicated and drifting between two files.
