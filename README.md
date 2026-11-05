# HockeyIQ Kenya

*An analytics platform for the Kenya Hockey Union.*

An end-to-end sports analytics pipeline built on real, live-scraped data
from the [Kenya Hockey Union](https://www.kenyahockeyunion.org/) website
— covering **all 8 competitions running in the 2026 season**: Premier
League (Men/Women), Super League (Men/Women), and all four National
League zones (East/Central/West/South).

The project goes beyond a simple scrape-and-report exercise. Existing
Kenyan hockey resources (results/standings sites like HockeyKE and
similar) already cover the descriptive layer well — this project is
deliberately an **analytical layer on top of that same underlying
data**: validated predictive modeling (Elo and Pythagorean expectation,
checked against real outcomes and against each other), honest
measurement of how complete the underlying data actually is, and
playing-style analysis that goes beyond league position — not a
competing results tracker, an addition to that landscape. It builds a
**restart-safe analytics platform** with 20+ analytical modules,
progressing from foundational league tables through to composite
metrics the project author designed independently (Player Influence
Index, Dominance Index, Team Power Rankings) and unsupervised learning
(K-Means clustering of playing styles).

## What this project demonstrates

- **Web scraping at scale**: Selenium + BeautifulSoup, handling
  JavaScript-rendered content, inconsistent page structures across
  competitions, and gracefully handling missing data (e.g. scoreless
  matches with no event timeline) rather than crashing on it.
- **Data engineering discipline**: a restart-safe notebook architecture
  where every analytical module depends only on objects rebuilt from
  saved CSVs — not on variables left over from earlier cells — so the
  project can be paused and resumed at any point.
- **Original analytics design**: composite metrics designed and
  justified from first principles (not textbook formulas), including
  a Team Power Ranking, a Player Influence Index, and a Goal Scoring
  Consistency classification — each with documented reasoning for why
  the weights were chosen.
- **Statistical & ML techniques**: standard deviation-based consistency
  scoring, K-Means clustering for team similarity, and quadrant analysis
  comparing underlying performance to results.
- **Communication**: every module follows a Business Question →
  Analysis → Visualization → Executive Report structure aimed at a
  non-technical (coaching staff) audience, not just a code dump.
- **Interactive tools, not just static charts**: a live Team Comparison
  Tool (pick any two teams, get an instant side-by-side breakdown), and
  a Predicted Final Table that projects each competition's remaining
  fixtures using **two independent models side by side** — the
  project's validated Elo rating and Pythagorean expectation — flagging
  where the two models agree or disagree, rather than presenting a
  single unvalidated forecast.
- **International coverage**: Kenya's senior national team results
  (Africa Cup of Nations, Junior Africa Cup), scraped separately from
  FIH's Tournament Management System, including full match-level
  detail (scorers, goal type, cards for both teams) and a "How Kenya
  Concedes" breakdown alongside the existing scoring breakdown.
- **FIH World Ranking, live from FIH's own site**: Kenya's current
  world rank and points (Men's and Women's, tracked separately),
  match-by-match rank movement history, and Kenya's honest computed
  position among African Hockey Federation nations — deliberately not
  presented as an official "African Ranking," since no such
  separately-published ranking exists.
- **Head-to-Head Lookup, Notable Trends, and Season Records**: pick any
  two teams for their real history against each other; an
  automatically-detected feed of genuinely specific patterns (goal
  droughts, perfect home records, extended unbeaten runs) rather than
  manually curated commentary; and a curated highlight card pulling the
  best record-holder from each category into one place.
- **International Goal Timeline and prediction confidence bars**: a
  lightweight, honest visual of real recorded goal minutes for
  international matches (not continuous match tracking, since that data
  doesn't exist), and a visual confidence indicator on the Predicted
  Final Table showing how strongly Elo and Pythagorean agree, rather
  than a plain checkmark.
- **Fully automated**: a GitHub Actions workflow re-scrapes, re-runs
  the full analytical pipeline, and republishes the live dashboard
  automatically every week — no manual notebook runs required to keep
  the dashboard current.

## Project structure

```
hockeyiq-kenya/
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── domestic-weekly.yml        # weekly automated scrape (01→02→03→04) + rebuild + publish to GitHub Pages
├── notebooks/
│   ├── 01_scraping.ipynb            # Selenium/BeautifulSoup scraper → raw CSVs
│   ├── 02_league_analytics.ipynb    # League table, results, first-pass team/player stats
│   ├── 03_advanced_analytics.ipynb  # Modules 11–43: tactical profiling, clustering, coach/scout/federation intelligence, Elo, Pythagorean, dashboard
│   ├── 04_international.ipynb       # Africa Cup of Nations / Junior Africa Cup results, FIH World Rankings (FIH TMS + FIH ranking pages)
│   └── 05_worldcup_live.ipynb       # Standalone FIH World Cup 2026 tracker (tournament over; kept for the record, no longer scheduled)
├── data/
│   ├── raw/         # scraped, unprocessed match & event data
│   └── processed/   # cleaned datasets consumed by later notebooks
├── reports/
│   └── dashboard.html   # standalone executive dashboard — open directly in any browser
└── scripts/          # helper scripts (e.g. weekly LinkedIn digest)
```

The live site is deployed by the workflow directly from `reports/dashboard.html`
(GitHub Pages source = "GitHub Actions"); there is no `docs/` folder to keep in sync.

Each notebook is self-contained: it reads its inputs from `data/`,
writes its outputs back to `data/`, and can be run independently as
long as the notebook before it has been run at least once.

## Pipeline

```
01_scraping.ipynb
   scrapes kenyahockeyunion.org
   → data/raw/matches_2026.csv, data/raw/events_2026.csv
        │
        ▼
02_league_analytics.ipynb
   builds league table, results dataset, first-pass team/player stats
   → data/processed/*.csv  (incl. performance_metrics.csv)
        │
        ▼
03_advanced_analytics.ipynb
   Modules 11–30: tactical intelligence, dominance/efficiency metrics,
   clustering, executive reports, Player Influence Index, goal
   consistency, home/away stability
   → data/processed/*.csv (final analytical tables)
```

## Data coverage

| Competition | Status |
|---|---|
| Premier League Women (PLW) | ✅ Onboarded |
| Premier League Men (PLM) | ✅ Onboarded |
| Super League Men (SLM) | ✅ Onboarded |
| Super League Women (SLW) | ✅ Onboarded |
| National League Men — East Zone (NLM-EZ) | ✅ Onboarded |
| National League Men — Central Zone (NLM-CZ) | ✅ Onboarded |
| National League Men — West Zone (NLM-WZ) | ✅ Onboarded |
| National League Men — South Zone (NLM-SZ) | ✅ Onboarded |

All 8 URLs in `SEASON_URLS` (`01_scraping.ipynb`) were confirmed
directly against the live site — not guessed — by locating a real team
page in each competition and reading its "Standings" link. KHU changes
this URL's slug format almost every season (e.g. NLM-EZ was
`national-league-men-_-ez-2024-2025` last season and
`national-league-men-_-ez-nlm-ez-2026` this season), so each entry will
need re-verifying the same way once the 2027 season begins. The
discovery loop warns clearly (rather than failing silently) if a URL
stops working, making that easy to catch.

## Important: goal-level data completeness

**Match scorelines (final scores, league tables, Elo ratings) are complete
for every match.** But **goal-by-goal detail — who scored, what minute,
which cards were shown — is only present for a subset of matches.**

This was confirmed directly against the live source site: KHU records a
final score for every match, but only enters full goal-by-goal detail for
some of them. A real match with a 5-0 scoreline was found with zero
embedded event data — nothing to scrape, because KHU's own system never
recorded it. This is a genuine gap in the source site's own record-keeping,
not a scraping bug, and not something a better scraper can recover.

**What this means for using this project's numbers:**
- **Fully reliable, built from scorelines alone:** league tables, Elo
  ratings, Competitive Balance Index, participation counts, Home/Away
  Scoring Stability
- **Reliable only for the matches with full detail, not the whole season:**
  Top Scorers, Player Influence Index, Squad Reliance, Coach Intelligence,
  Scout Intelligence, clutch-goal detection

The exact coverage rate is computed fresh on every run (see the **Data
Integrity Check** near the top of `03_advanced_analytics.ipynb`, and the
"Goal-Level Detail Coverage" stat on the dashboard itself) — check that
number before citing any player-level statistic in a scholarship,
federation, or public submission.

## Who this project is built for

Beyond the core analytics, three modules translate the data into decisions for specific audiences:

- **Coach Intelligence (Module 31):** which teams perform against top-3 opponents specifically (a much harder test than overall record), which squads are dangerously reliant on a single scorer, and who delivers in the last 10 minutes of a match.
- **Scout Intelligence (Module 32):** players who statistically outperform their own competition's average (fair comparisons across very different divisions), and a volume-vs-efficiency quadrant that separates elite finishers from players padding stats on a dominant team.
- **Federation Intelligence (Module 33):** a Competitive Balance Index per competition, participation levels across the 4 National League zones, and discipline load — the kind of league-health view a federation needs that no single team's coach would ever compute.

All three feed a standalone **Executive Dashboard** (`reports/dashboard.html`) — open it directly in any browser, no Jupyter or internet connection required. Charts are embedded as images rather than loaded from a JS library specifically so it never shows broken/blank charts to someone reviewing it offline.

**Predictive Modeling (Module 34):** an Elo rating system processed match-by-match per competition, with margin-of-victory weighting and home-advantage adjustment. Unlike the other modules, this one is validated against outcomes it didn't see coming — a Brier score compares the model's predictions to a naive baseline, and an Elo-to-Points correlation check confirms the ratings broadly agree with the actual league tables. A `predict_match(team_a, team_b, competition)` function returns a win probability for any hypothetical matchup.

## International performance (new)

A separate notebook (`04_international.ipynb`) scrapes Kenya's national-team
results from continental competitions organized by the African Hockey
Federation \u2014 the Africa Cup of Nations and Junior Africa Cup \u2014 from FIH's
Tournament Management System (`tms.fih.ch`), confirmed as the actual source
of this data by direct verification before writing any scraper code.

This data is genuinely richer than the domestic KHU data in one specific
way: it distinguishes **Field Goal vs Penalty Corner vs Penalty Stroke**
for every goal \u2014 exactly the breakdown confirmed absent from the domestic
source (see Module 36). It also includes full lineups, venue, and match
officials.

**Scope, stated honestly:** covers national-team competitions only. The
Africa Cup for Club Champions \u2014 where Kenyan clubs (confirmed: Sikh Union
Nairobi won Bronze in a recent edition) compete \u2014 was investigated but
not confirmed to live on the same platform; it appears to be reported
primarily on africahockey.org's own site, which would need its own
separate scraping reconnaissance. This is a documented next step, not
yet built.

The dashboard's **International** section loads this data automatically
if present, and shows a clear message if `04_international.ipynb`
hasn't been run yet \u2014 the rest of the dashboard works fully without it.

**Data collection scope, a deliberate design choice:** full match detail
(goals, cards, lineups) is collected for Kenya's matches only \u2014 scraping
every match for every team in each tournament would roughly quadruple
scrape time for data mostly irrelevant to a Kenya-focused project. Final
tournament standings are captured for every team, though, since that
table is already sitting on the same page fetched during match discovery
(no extra scraping cost) and gives Kenya's results real context \u2014 e.g.
whether a loss was to a dominant team or a team that barely beat anyone
else. This is a deliberate middle ground, not an oversight.

**Africa Cup for Club Championships:** the earlier open question in this
project \u2014 resolved. Confirmed the data lives on the African Hockey
Federation's own site (`africahockey.org`), not the FIH platform used
for national-team competitions, and confirmed a real structured
medal-history table exists there spanning **1988\u20132026**. This is now
scraped, and it directly confirms **Lakers Hockey Club of Kenya won the
2026 Women's ACCC title**, alongside Kenyan club medals across the
competition's history (Simba Union, Kenya Armed Forces, Post & Telecomm,
Sliders Club, Telkom Kenya). Match-by-match goal/card detail for this
competition is **not** captured \u2014 it exists only in prose news
articles with no guaranteed consistent format, a genuinely harder
scraping problem documented as a limitation, not attempted here.

**Domestic \u2192 international player linkage:** `04_international.ipynb`
also cross-checks whether any domestic KHU goal-scorer or carded player
also appears in Kenya's international squads \u2014 solving a real name-format
mismatch between the two sources (`"Joan Ajao"` domestically vs
`"AJAO Joan"` internationally) rather than assuming a plain string match
would work. **This produces name matches, not confirmed identity
matches** \u2014 two people can share a name \u2014 and is presented that way
throughout, with a manual-verification caveat on every result.

**Advanced match statistics (Possession, Shots, Circle Entries, PC/PS by quarter):**
FIH publishes a separate per-match statistics report as a **PDF document**
(confirmed via direct inspection \u2014 `mime_type: application/pdf`), not
an HTML page like everything else scraped in this project. It's now
scraped using `pdfplumber`. **Confirmed risk, checked before building
this:** every real example found during reconnaissance showed mostly
zero values, consistent with the same "optional, inconsistently
completed" pattern already found in the domestic data \u2014 so this module
reports a **per-category coverage check first** (e.g. Penalty Corners
might be well-populated while Circle Entries is nearly empty on the
very same match, confirmed during testing), rather than assuming the
data is usable and building analysis on top of it blind.

**Testing limitation, stated directly:** every other scraper in this
project was tested against a reconstruction of real diagnostic output
before being delivered. This one could not be fully tested that way \u2014
downloading and parsing an actual PDF file requires network access the
development environment didn't have. The text-parsing logic *was*
tested against the real extracted text of an actual statistics PDF
(and a real bug was caught and fixed that way \u2014 trailing document
footer text being misread as match data), but the PDF-download step
itself has not been exercised end-to-end. Treat its first real run as
the actual test, not a settled feature.

## Team player stats — a second, richer source of domestic scorer data

Confirmed by directly fetching two real team pages before writing any
code (Butali Warriors, Sikh Union Nairobi): each KHU team's own page
carries an **all-time aggregate Players Stats table**, separate from
match timelines and apparently maintained more completely \u2014 real
examples showed players with 10\u201312 goals, far above anything the
timeline-based Top Scorers table (limited by the ~9.5% domestic event
coverage) has ever produced.

`01_scraping.ipynb` now scrapes this directly (discovering every real
team page link rather than guessing URL slugs), and
`03_advanced_analytics.ipynb` (Module 38) surfaces it on the dashboard
as **"All-Time Club Top Scorers"**, clearly labeled and separated from
the season-scoped timeline data so the two are never confused.

**Honest limitations, carried over from source:**
- These are all-time club totals, not scoped to the current season.
- KHU's own system sometimes records the same player twice under
  slightly different name spellings or separate per-season profile
  entries \u2014 confirmed during testing (two "Festus Onyango" rows for
  the same club) and reported as found, not silently merged.

## Visual variety — the right chart for the right question

Charts were audited for whether each one is genuinely the best fit for
its data, not chosen for variety's sake. Rankings and comparisons
(standings, Elo, scorer lists) stay as bars/tables \u2014 a donut would
make ranking *harder* to read, not easier. Three genuine part-of-a-whole
questions had never been charted at all, and now are:

- **Match Outcome Distribution** (donut, one per competition, in League
  Tables) \u2014 Home Win / Away Win / Draw as a share of every match played.
- **Goal Type Breakdown** (donut, International section) \u2014 Field Goal
  vs Penalty Corner vs Penalty Stroke as a share of Kenya's goals.
- **Card Type Composition** (donut grid, one per competition, in
  Federation Intelligence) \u2014 Green/Yellow/Red as a share of all cards
  shown, normalized for the real case-inconsistency confirmed in KHU's
  own data ("Green Card" vs "Yellow card").

## Getting started

```bash
git clone <this-repo-url>
cd hockeyiq-kenya
pip install -r requirements.txt
```

Run the notebooks in order: `01_scraping.ipynb` →
`02_league_analytics.ipynb` → `04_international.ipynb` →
`03_advanced_analytics.ipynb`.

**Note:** `01_scraping.ipynb` uses Selenium with Chrome and requires
Google Chrome installed locally (ChromeDriver is managed automatically
via `webdriver-manager`). Scraping only needs to be re-run when new
matches have been played — the two analytics notebooks work entirely
from the saved CSVs and don't touch the network.

## Automation — this updates itself

A GitHub Actions workflow (`.github/workflows/domestic-weekly.yml`, shown
in the Actions tab as **Domestic pipeline (weekly)**) runs automatically
every Monday at 04:00 UTC. It re-scrapes and re-runs the full pipeline in
order (`01 → 02 → 03 → 04`), commits the refreshed data and dashboard back
to the repository, and publishes the dashboard to GitHub Pages — no manual
notebook runs required. Because every predictive metric (Elo, Pythagorean,
the Predicted Final Table, clustering) is computed fresh from the saved
CSVs each run, **these update automatically too** as new matches are added,
not just the raw match list. It can also be triggered on demand from the
repository's Actions tab (**Domestic pipeline (weekly) → Run workflow**).

**Incremental vs full scrape.** By default `01_scraping.ipynb` scrapes only
matches it has not seen before. To re-scrape the whole season from the first
match (for example to pick up event data KHU has backfilled), set the
environment variable `HOCKEYIQ_FULL_RESCRAPE=1`, or delete
`data/raw/matches_2026.csv` before the run.

**The 2026 FIH World Cup tracker** (`05_worldcup_live.ipynb`) was a separate,
4-hourly workflow during the tournament (15–30 August 2026). The tournament
is over and that workflow has been removed; the notebook is kept so the
tracker can be re-enabled for a future World Cup.

## Data quality safeguards

- **One club, one name.** KHU's site sometimes labels the same club
  differently on team pages and match pages (e.g. "Warriors" vs "Butali
  Warriors"). `02_league_analytics.ipynb` maps known variants to a canonical
  name (`TEAM_ALIASES`), removes any duplicate matches this exposes, and
  prints a *Possible duplicate club* warning when one name in a competition
  is a word-suffix of another, so new cases are caught instead of silently
  splitting a club (and its players) in two.
- **Ties are shown, not hidden.** Streak records list every team sharing
  the record rather than only the first one found.
- **Newest first.** The All Matches table lists the latest match first within
  each competition.
- **Phone-friendly.** On screens narrower than 860 px the navigation becomes a
  scrollable bar, tables scroll sideways, and body text is at least 12 px.

## Sample findings (2026 season, at time of writing)

- **Longest streaks (as of 5 November 2026):** Blazers Hockey Club (Premier
  League Women) hold both records, with 8 consecutive wins and 13 matches
  unbeaten; Kitale Hockey Club (National League Men – West) are next on
  7 wins and 9 unbeaten.
- **Butali Warriors** led the Premier League Men's table in total
  goals (28) but drew close to **Sikh Union Nairobi** (27) on the
  project's Power Ranking, because Sikh Union spread its scoring across
  13 different players versus Butali's 11 — rewarded explicitly by the
  ranking's "Scorers" term.
- Playing-style clustering compares each team **only against its own
  competition**, not the whole league system — a real bug in an
  earlier version compared every team globally instead, which could
  misclassify a genuinely dominant team in a smaller competition as
  "developing" simply because its raw numbers looked modest next to
  the much higher-scoring Premier League. Confirmed fixed and tested
  directly against a real example (Kitale Hockey Club, unbeaten and
  top of its zone, previously misclassified).
- Squad Reliance (which single players a team depends on) now requires
  a minimum of 3 recorded goals before showing a percentage at all —
  and how few teams currently qualify is itself shown on the dashboard
  as a direct, honest measurement of how incomplete KHU's published
  match-event data still is, not just a scouting statistic.

*(Exact figures update automatically every week via the GitHub Actions
workflow described below — see Module 28/29 in
`03_advanced_analytics.ipynb` for the underlying computation.)*

## Roadmap

Elo ratings, win probability, and set-piece analysis are now built (Modules 34, 36). Natural next steps:

- Season-over-season trend analysis (requires scraping a second season)
- Player-level Elo or influence trajectories over time
- **Not planned:** true penalty-corner conversion rates or shot-location visualizations. Confirmed directly against the source site — KHU's published player statistics track only Goal, Green Card, and Yellow Card per player, with no goal-source or shot-location data anywhere in the underlying system. This is a genuine limitation of the data source, not a gap in this project's scraping.

## Data source & disclaimer

All data is scraped from the publicly accessible
[Kenya Hockey Union](https://www.kenyahockeyunion.org/) website. This
is an independent analytics project and is not affiliated with or
endorsed by the Kenya Hockey Union. Metrics such as the Power Ranking,
Dominance Index, and Player Influence Index are original, unofficial
statistics designed for this project — not official league statistics.

## Author

**Agesa A A**
[Optional: LinkedIn / portfolio link / email here]

Licensed under the [MIT License](LICENSE) — free to learn from and build on, with credit.

Feedback and contributions welcome via issues or pull requests.

  were confirmed to return all-zero values across every match tested —
  this data source is real but not currently usable.
