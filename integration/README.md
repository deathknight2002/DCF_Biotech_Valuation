# Terminal UI Biotech Integration

This directory contains patch artifacts for integrating the Dash-based DCF valuation
logic from this repository into the [`deathknight2002/terminal-ui-biotech-GG`](https://github.com/deathknight2002/terminal-ui-biotech-GG)
platform.

## What's included

- **`terminal-ui-biotech-GG.patch`** – applies a full backend + frontend implementation
  that wires discounted cash flow analytics into the Node/Express API and the React
  terminal experience.

The patch introduces a dedicated DCF provider on the backend, exposes production-ready
API endpoints, and updates the Aurora financial modeling workspace to visualise the
data (net sales by region, royalty waterfalls, discounted cash flows and KPI cards).

## Applying the patch

1. Clone the terminal UI repository and check out the desired branch (e.g. `main`).

   ```bash
   git clone https://github.com/deathknight2002/terminal-ui-biotech-GG.git
   cd terminal-ui-biotech-GG
   ```

2. Copy the patch file from this repo into the root of the terminal UI project and
   apply it:

   ```bash
   cp /path/to/DCF_Biotech_Valuation/integration/terminal-ui-biotech-GG.patch .
   git apply terminal-ui-biotech-GG.patch
   ```

3. Install dependencies and rebuild the platform if needed:

   ```bash
   # Backend (Node)
   cd backend
   npm install
   cd ..

   # Frontend terminal workspace
   cd terminal
   npm install
   ```

4. Start the backend and frontend development servers (consult the terminal UI repo
   README for helper scripts). The financial modeling page will now render live data
   from the new `/api/financial` endpoints.

## Highlights of the integration

- **Backend (`backend/src/services/dcf-service.ts`)**
  - In-memory biotech asset configuration derived from the Dash app.
  - Revenue waterfall, royalty calculations, milestone logic and DCF/IRR utilities.
  - REST handlers for listing assets, fetching a model, and computing ad-hoc NPV/DCF
    results.
- **API router (`backend/src/routes/financial-modeling.ts`)**
  - Production endpoints wired to the new service layer.
- **Terminal UI (`terminal/src/pages/FinancialModelingPage.tsx`)**
  - React Query wiring for live backend data with graceful fallbacks.
  - Visual dashboards for net sales, royalties, discounted cash flows and summary
    metrics using the Aurora glassmorphism style.
- **Styling (`terminal/src/App.css`)**
  - Aurora-themed controls, tables, charts and KPI cards tailored to the new page.

The integration maintains the sophisticated fallback dataset from the Dash app, so the
UI remains functional even if the backend is offline. Once the patch is applied the
terminal project can immediately showcase the DCF pipeline end-to-end.
