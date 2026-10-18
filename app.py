import hashlib
import json
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

app = FastAPI()

EMAIL = "24f1002036@ds.study.iitm.ac.in"
PROTOCOL_VERSION = "2025-03-26"


@app.get("/")
async def health():
    return {"status": "ok", "service": "exam-mcp-server"}


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    # The challenge is intentionally read from the HTTP headers on every call.
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}, status_code=400)

    method = payload.get("method")
    request_id = payload.get("id")

    # Notifications do not receive a JSON-RPC response.
    if method == "notifications/initialized" or (isinstance(method, str) and method.startswith("notifications/")):
        return Response(status_code=202)

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": payload.get("params", {}).get("protocolVersion", PROTOCOL_VERSION),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "exam-challenge-mcp", "version": "1.0.0"}
            }
        })

    if method == "ping":
        return JSONResponse({"jsonrpc": "2.0", "id": request_id, "result": {}})

    if method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": [{
                    "name": "solve_challenge",
                    "description": "Compute the exam response from the per-call X-Exam-Challenge HTTP header.",
                    "inputSchema": {"type": "object", "properties": {}}
                }]
            }
        })

    if method == "tools/call":
        params = payload.get("params") or {}
        if params.get("name") != "solve_challenge":
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32602, "message": "Unknown tool"}
            })

        challenge = request.headers.get("x-exam-challenge")
        if not challenge:
            return JSONResponse({
                "jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32602, "message": "Missing X-Exam-Challenge header"}
            })

        normalized_email = EMAIL.strip().lower()
        answer = hashlib.sha256(f"{challenge}:{normalized_email}".encode("utf-8")).hexdigest()[:16]
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"content": [{"type": "text", "text": answer}]}
        })

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": -32601, "message": "Method not found"}
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
