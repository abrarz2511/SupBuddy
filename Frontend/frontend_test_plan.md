# Frontend Test Plan

## Goal

Verify the SupBuddy React frontend works for the main dashboard and shipment
management workflows, correctly handles API states, and remains usable across
desktop and mobile viewports.

## Prerequisites

- Node.js 18+ is installed.
- Frontend dependencies are installed:

```bash
cd Frontend
npm install
```

- The backend API is running on `http://localhost:8000`.
- Frontend environment configuration points to the backend:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_REFRESH_INTERVAL=30000
VITE_ENABLE_AUTO_REFRESH=true
```

- The frontend dev server is running:

```bash
npm run dev
```

- Open the app at `http://localhost:3000`.

## 1. Static Verification

- Run `npm run build`.
- Expected: TypeScript compiles and Vite creates a production build without
  errors.
- Run `npm run lint`.
- Expected: ESLint completes with zero warnings and zero errors.
- Start `npm run preview` after a successful build.
- Expected: the production build loads and behaves the same as the dev server
  for the core routes.

## 2. App Startup and Routing

- Open `/`.
- Expected: the SupBuddy Dashboard page loads without a blank screen or console
  runtime errors.
- Open `/manage-shipments`.
- Expected: the Manage Shipments page loads.
- Open `/manage-shipments?action=create`.
- Expected: the Manage Shipments page loads with the Create New Shipment dialog
  open.
- Open an unknown route such as `/not-a-real-route`.
- Expected: the app redirects to `/`.
- Use the dashboard quick actions.
- Expected: Create New Shipment navigates to `/manage-shipments?action=create`,
  and Manage Shipments navigates to `/manage-shipments`.

## 3. Dashboard Data States

- Load the dashboard while the backend has active shipments.
- Expected: Active Shipments shows the correct active count and shipment cards.
- Load the dashboard while the backend has active alerts.
- Expected: Active Alerts shows the correct alert count and alert cards.
- Click the refresh icon.
- Expected: shipments and alerts are refetched without duplicating cards or
  resetting the route.
- Load the dashboard with no active shipments.
- Expected: the No Active Shipments empty state appears with a Create Shipment
  action.
- Load the dashboard with no active alerts.
- Expected: the No Active Alerts empty state appears.
- Stop the backend or point `VITE_API_BASE_URL` to an invalid URL.
- Expected: shipment and alert sections show clear error messages and the rest
  of the page remains usable.
- If more than 10 active shipments exist, load the dashboard.
- Expected: only the first 10 are shown and View All Shipments navigates to
  `/manage-shipments`.
- If more than 5 active alerts exist, load the dashboard.
- Expected: only the first 5 are shown and View All Alerts is visible. The
  current app does not define an `/alerts` route yet, so record this as a known
  navigation gap until that page exists.

## 4. Manage Shipments List

- Open `/manage-shipments` with existing shipment data.
- Expected: the All Shipments tab displays the total count and shipment cards.
- Search by tracking number.
- Expected: only matching shipments remain visible.
- Search by origin.
- Expected: only matching shipments remain visible.
- Search by destination.
- Expected: only matching shipments remain visible.
- Search for a value that does not match any shipment.
- Expected: No Shipments Found appears.
- Clear the search field.
- Expected: the shipment list returns to the unfiltered page data.
- If the backend returns multiple pages, use Previous and Next.
- Expected: page text updates correctly, Previous is disabled on page 1, and
  Next is disabled on the last page.
- Click Active, Delivered, and With Alerts tabs.
- Expected: each tab changes selection and shows the current placeholder content.
  Treat the placeholders as known incomplete functionality, not a regression.
- Click the Filters button.
- Expected: no filtering occurs in the current implementation. Record this as a
  known incomplete control until filter behavior is implemented.

## 5. Create Shipment Dialog

- Open the dialog from the Manage Shipments page.
- Expected: the dialog title is Create New Shipment and all fields are visible.
- Verify the Create Shipment button with an empty form.
- Expected: the button is disabled.
- Fill tracking number, origin, destination, and customer ID, leaving current
  location empty.
- Expected: the current implementation enables Create Shipment. Record whether
  current location should be required by product/API requirements.
- Select each available initial status.
- Expected: the selected status is displayed and no console errors occur.
- Submit a valid new shipment.
- Expected: the button changes to Creating while the request is pending, the
  dialog closes on success, the form resets, and the new shipment appears after
  refetch.
- Submit a duplicate or invalid shipment.
- Expected: the dialog remains open and the console logs the failure. Record the
  missing user-facing error state as a UX gap if no visible message appears.
- Cancel the dialog after entering values.
- Expected: the dialog closes. Reopening currently preserves unsaved values;
  verify whether that is desired behavior.

## 6. Card and Status Rendering

- Review shipment cards for each supported shipment status.
- Expected: status badges use the expected labels and colors, and card text does
  not overflow.
- Review alert cards for critical, high, medium, and low priorities.
- Expected: priority indicators are visually distinct and readable.
- Click a shipment card from the dashboard or Manage Shipments page.
- Expected: the app attempts to navigate to `/shipments/{tracking_number}`. The
  current app does not define this route yet, so record this as a known
  navigation gap until a shipment detail page exists.
- Click an alert card from the dashboard.
- Expected: the app attempts to navigate to `/alerts/{alert_id}`. The current app
  does not define this route yet, so record this as a known navigation gap until
  an alert detail page exists.

## 7. API Integration

- Confirm dashboard shipment requests call `GET /api/v1/shipments/active`.
- Confirm Manage Shipments requests call `GET /api/v1/shipments` with `page` and
  `page_size` query parameters.
- Confirm create shipment calls `POST /api/v1/shipments`.
- Confirm dashboard alert requests call `GET /api/v1/alerts` with active statuses
  and a limit.
- Expected: API responses are rendered correctly, loading states appear during
  pending requests, and API errors do not crash the app.
- Verify auth token behavior if an `auth_token` exists in local storage.
- Expected: API requests include the configured authorization header.

## 8. Responsive Layout

Test these viewport sizes:

- Mobile: 375 x 667
- Large mobile: 414 x 896
- Tablet: 768 x 1024
- Desktop: 1440 x 900

For each viewport:

- Open `/`.
- Expected: dashboard header, refresh button, shipment section, alerts section,
  and quick actions remain visible and do not overlap.
- Open `/manage-shipments`.
- Expected: search, tabs, create button, cards, and pagination remain usable.
- Open the Create New Shipment dialog.
- Expected: all fields and dialog actions are reachable without horizontal
  scrolling.

## 9. Accessibility and Keyboard Checks

- Navigate the dashboard with the keyboard.
- Expected: refresh and action buttons are reachable and visibly focused.
- Navigate Manage Shipments with the keyboard.
- Expected: back, create, refresh, search, tabs, pagination, and dialog controls
  are reachable in a logical order.
- Open and close the Create New Shipment dialog by keyboard.
- Expected: focus is trapped inside the dialog while open and returns to a
  sensible control after close.
- Check icon-only buttons.
- Expected: each icon-only button has an accessible name. Add labels if screen
  reader tooling reports unlabeled buttons.
- Check color contrast for priority badges, status badges, buttons, and error
  messages.
- Expected: text meets WCAG AA contrast.

## 10. Browser Smoke Matrix

Run the core startup, dashboard, and create shipment checks in:

- Chrome latest
- Edge latest
- Firefox latest

Expected: layout, routing, forms, and API-backed rendering behave consistently.

## 11. Regression Checklist

Run this checklist before considering frontend changes ready:

```bash
cd Frontend
npm run lint
npm run build
npm run dev
```

- `/` loads successfully.
- `/manage-shipments` loads successfully.
- Dashboard loading, empty, error, and populated states are verified.
- Shipment search and pagination are verified.
- Create Shipment success and failure paths are verified.
- Mobile and desktop layouts are checked.
- Browser console has no unexpected runtime errors.

## 12. Recommended Automation

- Add Vitest and React Testing Library for component and hook tests.
- Add tests for `Dashboard` loading, error, empty, and populated states.
- Add tests for `ManageShipments` search, pagination, create dialog validation,
  and submit behavior.
- Mock API calls with MSW so tests cover realistic request and error flows.
- Add Playwright for end-to-end route, responsive, and create shipment flows.
- Add an accessibility check with axe in either component tests or Playwright.
