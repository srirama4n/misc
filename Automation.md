How they line up with the flow
Creating an agent (steps 1–3)
The user types "move anything over $5,000 on payday." Chat API → Kafka → Orchestrator → Supervisor → Personal Agent Builder. None of the automation service's endpoints are involved yet.
The builder calls list_templates through MCP → GET /v1/templates, then validate_agent → POST /v1/agents/validate, and shows the review card.
The user taps Create. The app calls POST /v1/confirmations and gets a token, which goes back into chat as a structured confirm. The builder calls create_agent through MCP → POST /v1/agents with that token. The service saves the agent and grant in MongoDB and publishes agent-control to Kafka, so the Flink trigger job starts watching.
Running the agent (steps 4–10)
Steps 4–6 use no REST at all. The payroll event → Flink → trigger-fired on Kafka → the service starts the run → the preview task goes to the Orchestrator over Kafka.
Steps 7–8: the grant endpoints come in. The sub-agent calls the preview tool through MCP, carrying the grant token. The MCP grant check verifies the token's signature with keys from GET /.well-known/jwks.json (cached), then loads the grant from Redis, or from GET /v1/grants/{grantId} on a cache miss.
Step 9: approval. The push opens the app, which calls GET /v1/approvals/{approvalId} to show the card, then POST /v1/approvals/{approvalId}/approve with the cvams step-up token, or /deny.
Step 10: execute. The service sends the execute task over Kafka, and the grant check runs again (same two endpoints). The reply comes back on automation-replies, and the run is marked done.
Outside the main flow
Agents tab: GET /v1/customers/{customerId}/agents, GET /v1/agents/{agentId}, PATCH to pause or resume (publishes agent-control so Flink stops or starts matching), and DELETE (revokes the grant, so the grant check blocks anything still in flight).
Activity feed: GET /v1/customers/{customerId}/activity.
Builder management: "pause my payday agent" in chat reaches the same PATCH, DELETE and list endpoints through MCP tools.
Operations: POST /v1/admin/agents/pause-all during an incident, with progress at GET /v1/admin/jobs/{jobId}. POST /v1/admin/templates publishes a newly reviewed template, which then appears in GET /v1/templates.
The rule of thumb: REST is used wherever a person or an agent needs an immediate answer (the app, the builder, the grant check, ops). Kafka carries everything event-driven: triggers in, control messages and tasks out, replies back.
To test the integration next
Builder ↔ service: run the MCP server locally and point the three agent tools at your standalone service, so you exercise the real MCP path instead of curl.
Grant check: point the MCP interceptor at your /.well-known/jwks.json and /v1/grants/{grantId}, then try a tool outside the grant to confirm it's blocked.
The fake Orchestrator in standalone stands in for steps 7–8 and 10. That's the edge to replace with the real Orchestrator topic once the Orchestrator team confirms the topic name and channel=automation routing.
