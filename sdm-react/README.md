System Dynamics Modeler (React)

Overview
- React port of the provided `FrontEnd.html` with similar features:
  - Systems and components (Stock, Flow, Converter, Dataset, Calculator, Reference)
  - Drag, select, and connect components on a grid canvas
  - Scenarios with per‑scenario overrides
  - Dataset pivot modal (via PivotTable.js) + CSV import/export
  - Calculator editor modal (equation text)
  - Run Simulation to view resolved model JSON
  - Clear workspace
  - Hierarchical systems and scenarios (tree with add/rename/delete)
  - Canvas shows only active system’s components
  - Autosave to localStorage + Export/Import full model JSON
  - Select connections (click a line) and press Delete to remove
  - Visual cues: dashed Reference nodes; selected connections highlighted
  - Zoom controls (buttons at bottom center)
  - Double-click nodes to open editors (data table/pivot or calculator)
  - Global Components tree: create cross-system References via “Ref here”

Getting Started
1) Install deps:
   - `cd sdm-react`
   - `npm install` (or `pnpm i` / `yarn`)
2) Run dev server:
   - `npm run dev`
   - Open the printed local URL (e.g. http://localhost:5173)

Notes
- Tailwind is loaded via CDN for simplicity.
- Pivot UI uses jQuery + PivotTable via CDN. Requires internet.
- Reference creation: select a component, then click Reference in a system to create a Reference of the selection. If none selected, it uses the first component in that system.

Build
- `npm run build` then `npm run preview`
