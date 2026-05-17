# Backend API Basic Test Plan

## Goal

Verify the core SupBuddy backend API works for common shipment, schedule,
alert, and health-check workflows.

## Prerequisites

- PostgreSQL is running.
- `.env` is configured with a valid `DATABASE_URL`.
- Dependencies are installed with `pip install -r requirements.txt`.
- The API is running with:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 1. Health and Startup

- Call `GET /health`.
- Expected: response status is `200` and body contains `{"status": "healthy"}`.
- Open `GET /docs`.
- Expected: Swagger UI loads without errors.
- Call `GET /openapi.json`.
- Expected: OpenAPI schema is returned.

## 2. Shipment Workflow

- Create a shipment with `POST /api/v1/shipments/`.
- Expected: response status is `201` and includes shipment ID, tracking number,
  origin, destination, and current status.
- List shipments with `GET /api/v1/shipments/`.
- Expected: created shipment appears in the response.
- Get the shipment by tracking number using
  `GET /api/v1/shipments/tracking/{tracking_number}`.
- Expected: correct shipment details are returned.
- Update the shipment with `PATCH /api/v1/shipments/tracking/{tracking_number}`.
- Expected: status/location fields are updated.

## 3. Milestone Workflow

- Add a milestone with `POST /api/v1/shipments/{shipment_id}/milestones`.
- Expected: response status is `201` and milestone data is returned.
- Get milestones with `GET /api/v1/shipments/{shipment_id}/milestones`.
- Expected: milestone list includes the new milestone.

## 4. Schedule Workflow

- Create a schedule with
  `POST /api/v1/schedules/shipments/{shipment_id}/schedules`.
- Expected: response status is `201` and schedule data is returned.
- Get schedules with
  `GET /api/v1/schedules/shipments/{shipment_id}/schedules`.
- Expected: created schedule appears in the response.
- Check adherence with
  `GET /api/v1/schedules/shipments/{shipment_id}/schedules/adherence`.
- Expected: response contains schedule adherence results.

## 5. Alerts

- Call `GET /api/v1/alerts/`.
- Expected: response status is `200` and returns a list.
- Filter alerts with query parameters such as `status`, `priority`, and `limit`.
- Expected: response status is `200` and filters are accepted.
- If an alert exists, call `GET /api/v1/alerts/{alert_id}`.
- Expected: alert details are returned.

## 6. Error Handling

- Request a missing shipment by tracking number.
- Expected: response status is `404`.
- Request an endpoint with an invalid UUID.
- Expected: response status is `422`.
- Create a shipment with missing required fields.
- Expected: response status is `422`.
- Create a duplicate shipment tracking number.
- Expected: response status is `400`.

## 7. Basic Verification Commands

Run these checks before considering the backend API ready:

```bash
python -m flake8 app
python -c "from main import app; app.openapi(); print('openapi ok')"
python -m pytest tests/ -v
```

