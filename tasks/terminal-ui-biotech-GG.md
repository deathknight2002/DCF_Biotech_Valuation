# Coding Task: Enhance Terminal UI for Biotech Portfolio Analysis

## Overview
The repository [`deathknight2002/terminal-ui-biotech-GG`](https://github.com/deathknight2002/terminal-ui-biotech-GG) hosts a terminal-based dashboard for exploring biotech investment opportunities. The goal of this task is to improve the user experience by enriching navigation, surfacing key analytics, and ensuring a smooth workflow for analysts who rely on the terminal UI.

## Objectives
1. **Add an onboarding panel** that summarises how to use the application and shows the three most recently accessed biotech assets.
2. **Implement a watchlist workflow** that allows users to save, view, and remove assets of interest during a session.
3. **Expose risk metrics** (e.g., success probabilities, burn rate, runway) directly within the asset detail view.
4. **Improve the data refresh command** so that analysts receive clear status updates and error feedback.

## User Stories
- *As a biotech analyst*, I want to see a concise onboarding message the first time I launch the dashboard so that I understand the available commands.
- *As a frequent user*, I want the application to remember the last three assets I opened during the current session, so that I can quickly revisit them.
- *As an investor*, I need to track assets I care about in a watchlist panel, so that I can compare them side-by-side without re-running searches.
- *As a risk manager*, I want to inspect each asset's probability of success, monthly burn, and estimated runway right inside the detail view, so that I can assess whether to keep it on the watchlist.
- *As a power user*, I want to know when the `refresh` command is running, when it completes, and whether anything failed, so that I can trust the data I'm seeing.

## Functional Requirements
- Display the onboarding panel automatically on launch and provide a keyboard shortcut (documented in the panel) to show it again.
- Persist the list of the three most recently opened assets in memory for the current session; showing them in both the onboarding panel and a dedicated "Recent Assets" widget in the main layout.
- Introduce watchlist commands (`watch <asset_id>`, `unwatch <asset_id>`, `watchlist`) and visualise the watchlist in a sidebar component.
- Extend the asset detail view to query and display risk metrics alongside existing financial information. Mock data helpers may be introduced if necessary, but they should live in a dedicated module.
- Enhance the `refresh` workflow to include:
  - a status indicator while network calls run,
  - a success message when the refresh completes,
  - and graceful error handling with actionable messaging.

## Non-Functional Requirements
- Maintain compatibility with Python 3.10+ and any TUI framework already used in the repository.
- Adhere to existing linting/formatting rules (e.g., `black`, `ruff`, or project-specific tooling).
- Write comprehensive unit tests for new modules and update existing ones to cover the new behaviours.
- Update documentation (README or `docs/`) to explain new commands and features.

## Acceptance Criteria
- On launch, the onboarding panel appears automatically and displays usage instructions plus the three most recent assets (empty state allowed). The panel can be re-opened with the documented shortcut.
- Opening asset detail pages updates both the "Recent Assets" widget and onboarding panel content.
- Watchlist commands manipulate the in-session watchlist and the sidebar immediately reflects changes.
- Asset detail views show risk metrics sourced from the appropriate helper/module.
- Running the refresh command emits progress updates, ends with a success confirmation, and surfaces descriptive errors when failures occur.
- All new functionality is covered by automated tests and existing tests continue to pass.

## Stretch Goals (Optional)
- Persist watchlist and recent assets across application restarts using a lightweight local cache.
- Add sparkline trend indicators to the watchlist entries for quick performance snapshots.
- Provide a command palette or help overlay listing every command and shortcut.

## Getting Started
1. Fork and clone `deathknight2002/terminal-ui-biotech-GG`.
2. Create a feature branch (e.g., `feature/watchlist-workflow`).
3. Implement the changes described above.
4. Run the project's test suite and linting commands.
5. Submit a pull request summarising the new UX improvements.

Good luck and happy hacking!
