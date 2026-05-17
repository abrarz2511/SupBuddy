I want to create an App and an agent that helps track the status of shipments of a logistics company. The shipment is recieved in a shipping port, crosses customs, delivered to the delivery center, delivered to the regional hub and then finally to the end customer. At each location, the shipment is recieved, and then the status is updated with time. 
The backend monitoring service (SLA RUles engine) will be responsible for pulling tracking data on a schedule, normalizing milestone events, and applying deterministic SLA rules. The SLA rules will be defined as a set of conditions and actions. The conditions will be evaluated against the tracking data, and the actions will be taken if the conditions are met. If the conditions are met, the SLA engine will be updating the status of the shipment. If any high level issue is found (the timing difference between expected and real is huge, the shipment is not received, customs did not clear the shipment etc.) the SLA engine will alert the Freight Exception Analyst Agent.

The first agent will be the Freight Exception Analyst Agent. This agent will analyze shipment tracking exceptions detected by the backend monitoring service. It will determine the likely cause, risk priority, confidence level, supporting evidence, and recommended next action for missing, stale, or late shipment milestone updates.




For sub-process 1 (alert and analyze): 

### Agent 1: Freight Exception Analyst Agent

Analyzes shipment tracking exceptions detected by the backend monitoring service. Determines the likely cause, risk priority, confidence level, supporting evidence, and recommended next action for missing, stale, or late shipment milestone updates.

Analyst agent:

1. Receive structured alert context from backend.
2. Review shipment timeline, SLA breach, next milestones, and business impact.
3. Check external signals such as weather, traffic, port status, and customs status.
4. Compare against historical patterns.
5. Produce likely cause, risk priority, confidence, evidence, and recommended next step.
6. Return structured output to backend for storage and notification.

Backend API needed: 

getShipmentContext
saveAlertAnalysis
sendNotification

### Backend

The backend will consist of FastAPI.

Backend service:

1. Pull tracking data on a schedule.
2. Normalize milestone events.
3. Apply deterministic SLA rules.
4. Detect missing, stale, or late updates.
5. Deduplicate against open alerts.
6. Trigger analyst agent only for meaningful issues.
7. Store alert with backend rule reason.
8. Receive agent analysis and update alert with priority, likely cause, confidence, and evidence.
9. Send notification to the user.
10. Track alert lifecycle until resolved.

Services:

- Tracking service
    - objects that return true or false, time recieved (to signify that package is recieved, approved at customs etc.)
- Schedule service
    - Get a predetermined schedule that the SLA engine will compare against (a schedule that has expected time of arrival, which port, distribution center etc.)
- SLA Rules engine
    - Detect missing, late, or risky updates (compare expected return time from the predetermined schedule with the actual time, calculate if it is too late, anything is missing, anything should cause anything is missing or anything is causes risk to the predetermined schedule using SLA rules)
- Database service
    - Create a database to store the exceptions and there priority scores
- Agent getaway: Call the watsonx ‘Freight Exception Analyst Agent’ if the SLA rules engine finds anything to alert the agent
- Context tools for agent:
    - Weather lookup
    - traffic lookup
    - local disruption/ news lookup
    - port delay lookup
    - shipment history lookup
- Frontend API: The frontend API can call the backend services