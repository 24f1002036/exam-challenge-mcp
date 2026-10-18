# Exam Challenge MCP Server

## Deploy on Render

1. Create a GitHub repository and upload `app.py`, `requirements.txt`, and `render.yaml`.
2. In Render, choose **New + → Web Service**, connect that repository, and deploy.
3. Wait until the service is live. The MCP endpoint is `https://YOUR-SERVICE.onrender.com/mcp`.
4. Use that exact HTTPS URL for the grader.

The server implements JSON-RPC MCP `initialize`, `notifications/initialized`, `tools/list`, and `tools/call`. It exposes exactly one tool: `solve_challenge`. The tool has no required input properties and reads `X-Exam-Challenge` from the incoming HTTP request headers for every call.

A free hosting service may sleep when idle. Open the service root URL shortly before grading and verify it responds with `{"status":"ok","service":"exam-mcp-server"}`.
