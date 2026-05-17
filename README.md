# Agentic Logistics Exception Management

<img width="1672" height="941" alt="264d38d0-2248-41f5-b920-b31f86755de0" src="https://github.com/user-attachments/assets/f468825d-9bfb-4944-a4d5-b9406843aea3" />


An AI-assisted logistics operations platform that helps logistics coordinators detect shipment exceptions, understand likely causes, and act faster. The system combines a full-stack dashboard, deterministic backend monitoring, contextual data tools, and an IBM watsonx Orchestrate analyst agent to turn raw shipment events into clear, prioritized recommendations.

## About the Project

Freight transportation is full of moving parts: port handoffs, vessel milestones, customs updates, trucking legs, local hubs, weather events, traffic disruptions, and customer delivery windows. Coordinators often spend valuable time manually checking tracking portals, reading news, comparing ETAs, and deciding which exceptions need attention first.

This project automates that workflow. It monitors shipment milestones, flags missing, stale, or late updates, enriches each exception with external context, and asks an AI analyst agent to produce an operational risk summary. The result is a simple application where teams can quickly see what is at risk, why it may be happening, and what action should come next.

The project was built for the IBM Bob Hackathon theme: **Turn idea into impact faster**.

## Key Features

### Intelligent Shipment Monitoring

- Pulls shipment tracking data on a schedule.
- Normalizes shipment milestone events across ocean, port, trucking, hub, and final-mile stages.
- Applies deterministic SLA rules to detect delays, stale updates, missing milestones, and late arrivals.
- Creates structured exception records instead of relying on manual review.

### AI-Powered Exception Analysis

- Sends detected shipment issues to a watsonx Orchestrate analyst agent.
- Generates a plain-language explanation of likely causes.
- Assigns a risk priority based on delay severity, business impact, and contextual signals.
- Produces recommended next actions for logistics coordinators.

### Context-Aware Risk Enrichment

- Uses backend tools and APIs to gather external context such as:
  - Weather conditions near route points or destination regions.
  - Traffic incidents affecting truck movement.
  - Local news that may indicate strikes, closures, accidents, or disruptions.
  - Port-related news and operational issues.
- Passes this context into the agent so the analysis reflects current operating conditions.

### Full-Stack Operations Dashboard

- Displays shipments, milestones, alerts, and risk levels in an easy-to-use UI.
- Highlights delayed and high-priority exceptions.
- Shows the AI-generated reason, supporting context, and recommended action.
- Helps coordinators focus on the shipments that need attention first.

### Scalable Backend Architecture

- Backend service designed around scheduled ingestion, normalization, rule evaluation, and agent-triggered analysis.
- API layer supports dashboard queries and shipment exception workflows.
- Alert records store risk priority, reasoning, contextual evidence, and status.
- Designed to support future integrations with real carrier, port, warehouse, and customer systems.

### IBM Bob-Assisted Development

IBM Bob was used as the intelligent development partner for planning, code understanding, implementation support, debugging, refactoring, and documentation. The repository is intended to include exported Bob session reports in `bob_sessions/` for hackathon judging.

### IBM watsonx Orchestrate Integration

IBM watsonx Orchestrate powers the analyst agent that receives shipment exception context and returns structured operational analysis. The agent is designed to help automate decision support rather than replace the coordinator.



## Example Workflow

1. A scheduled backend job pulls the latest shipment tracking updates.
2. Events are normalized into a common shipment milestone format.
3. SLA rules detect a stale port departure update or late truck pickup.
4. The backend gathers contextual signals such as weather, traffic, and port news.
5. The exception and context are sent to the analyst agent.
6. The agent returns a risk priority, likely cause, and recommended next step.
7. The dashboard displays the alert for the logistics coordinator.
8. The coordinator reviews the recommendation and takes action.

## Tech Stack

- **Frontend:** React / TypeScript
- **Backend:** FastAPI / Python
- **Agent Layer:** IBM watsonx Orchestrate
- **Development Partner:** IBM Bob IDE
- **Data Layer:** Shipment records, milestone events, contextual signals, and alert history

## Planned Modules

```text
frontend/
  Operations dashboard
  Shipment cards
  Alert views
  Risk and status components

backend/
  Shipment ingestion jobs
  Milestone normalization
  SLA rule engine
  Context collection tools
  Agent orchestration client
  Alert persistence APIs


bob_sessions/
  Exported IBM Bob task histories
  Session screenshots for hackathon judging
```

## Why It Matters

Logistics teams lose time when they have to manually determine whether a shipment delay is routine, risky, or urgent. This project reduces that effort by combining deterministic monitoring with AI-supported reasoning. Coordinators get faster visibility, better prioritization, and clearer next steps, while the system keeps the human operator in control.

## Demo Scenarios

- A shipment misses a port departure milestone and the system finds related port congestion news.
- A truck delivery ETA slips because of severe weather near the destination.
- A shipment has no tracking update for several hours and is escalated as a stale update risk.
- Multiple shipments are delayed, and the dashboard ranks them by urgency.

## Hackathon Notes

This project is designed to showcase IBM Bob as a core development partner while using optional IBM watsonx technologies for the agentic workflow. IBM Bob supports repository understanding, planning, implementation, documentation, tests, refactoring, and debugging. IBM watsonx Orchestrate supports the creation and deployment of intelligent agents that automate business workflows, while IBM watsonx.ai can provide foundation-model capabilities for natural language reasoning and intelligent responses.

## Future Enhancements

- Real carrier and freight-forwarder API integrations.
- Predictive ETA scoring using historical shipment data.
- Human-in-the-loop approval workflows for customer notifications.
- Multi-agent collaboration for customs, carrier, and warehouse exception handling.

## Project Goal

Help logistics coordinators work smarter and faster by transforming shipment tracking noise into prioritized, explainable, and actionable exception intelligence.
