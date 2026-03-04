---
agent: "agent"
tools: ["search/codebase", "edit", "search"]
description: "Add a new telemetry/measurement retrieval method with typed output"
---

# Add New Sensor

In this repository, treat "sensor" as a telemetry or measurement retrieval capability.

Your goal is to add a new read method that returns typed metric/state data.

If not provided, ask for:

- Metric name and API source endpoint
- Expected units/type (int/float/enum/datetime)
- Refresh/frequency expectations (if relevant)
- Example response payload

## Implementation Steps

1. Add method to the relevant endpoint module.
2. Add/extend model types for returned metric data.
3. Parse envelope/raw response forms safely.
4. Add tests for normal and edge payloads.
5. Validate with standard checks.

## Requirements

- Return predictable typed values.
- Handle missing metrics gracefully.
- Keep method naming descriptive and consistent.
