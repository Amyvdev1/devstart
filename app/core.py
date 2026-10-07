from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    objective: str
    method: str
    endpoint: str
    concept: str
    hint: str
    success_message: str


SCENARIOS = [
    Scenario("missing-api-key", "Authenticate your first request", "Supply the required API key header.", "GET", "/v1/me", "authentication", "Use x-api-key: devstart-demo", "Authentication succeeded."),
    Scenario("malformed-json", "Recover from malformed JSON", "Send a syntactically valid JSON object.", "POST", "/v1/orders", "request-shape", "Use a JSON object such as {\"product_id\":\"sku_123\"}.", "The JSON body is valid."),
    Scenario("missing-product-id", "Create your first order", "Include a non-empty product_id field.", "POST", "/v1/orders", "validation", "Try product_id: sku_123", "Order payload passed validation."),
    Scenario("invalid-resource-id", "Handle a missing resource", "Request a known order identifier.", "GET", "/v1/orders/{id}", "resource-lookup", "The demo resource is ord_demo_1.", "Known resource located."),
    Scenario("rate-limit", "Recover from a 429", "Choose a safe retry delay based on retry guidance.", "POST", "/v1/orders", "rate-limits", "Use retry_after_seconds >= 2.", "Retry policy is safe."),
    Scenario("server-error", "Handle a transient server failure", "Choose a bounded retry strategy instead of retrying forever.", "POST", "/v1/orders", "resilience", "Use max_retries between 1 and 3 and exponential_backoff=true.", "Transient failure strategy is bounded and recoverable."),
]

SCENARIO_MAP = {s.id: s for s in SCENARIOS}


def list_scenarios() -> list[dict[str, Any]]:
    return [asdict(s) for s in SCENARIOS]


def evaluate_attempt(scenario_id: str, *, headers: dict[str, str] | None = None,
                     body: Any = None, path_params: dict[str, str] | None = None) -> dict[str, Any]:
    if scenario_id not in SCENARIO_MAP:
        raise KeyError(f"Unknown scenario: {scenario_id}")
    headers = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
    path_params = path_params or {}

    if scenario_id == "missing-api-key":
        ok = headers.get("x-api-key") == "devstart-demo"
        return _result(ok, 200 if ok else 401, "Authenticated successfully." if ok else "API key is missing or invalid.",
                       None if ok else "Add x-api-key: devstart-demo and retry.", "AUTHENTICATION_FAILED" if not ok else None)

    if scenario_id == "malformed-json":
        ok = isinstance(body, dict)
        return _result(ok, 200 if ok else 400, "JSON body parsed successfully." if ok else "Request body is not a valid JSON object.",
                       None if ok else "Send a JSON object and set Content-Type: application/json.", "MALFORMED_JSON" if not ok else None)

    if scenario_id == "missing-product-id":
        data = body if isinstance(body, dict) else {}
        value = data.get("product_id")
        ok = isinstance(value, str) and bool(value.strip())
        return _result(ok, 201 if ok else 422, "Order payload is valid." if ok else "product_id is required.",
                       None if ok else "Add a non-empty product_id field to the JSON body.", "VALIDATION_ERROR" if not ok else None)

    if scenario_id == "invalid-resource-id":
        resource_id = path_params.get("id") or ((body or {}).get("id") if isinstance(body, dict) else None)
        ok = resource_id == "ord_demo_1"
        return _result(ok, 200 if ok else 404, "Order ord_demo_1 found." if ok else "The requested order does not exist.",
                       None if ok else "Use the known demo ID ord_demo_1 and make 404 a recoverable application state.", "NOT_FOUND" if not ok else None)

    if scenario_id == "rate-limit":
        data = body if isinstance(body, dict) else {}
        delay = data.get("retry_after_seconds", 0)
        ok = isinstance(delay, (int, float)) and 2 <= delay <= 60
        return _result(ok, 200 if ok else 429, "Retry policy is safe." if ok else "Retry is too aggressive or unbounded.",
                       None if ok else "Respect Retry-After and wait between 2 and 60 seconds in this demo.", "RATE_LIMITED" if not ok else None,
                       response_headers={"Retry-After":"2","X-RateLimit-Remaining":"0"} if not ok else {})

    if scenario_id == "server-error":
        data = body if isinstance(body, dict) else {}
        retries = data.get("max_retries")
        backoff = data.get("exponential_backoff")
        ok = type(retries) is int and 1 <= retries <= 3 and backoff is True
        return _result(ok, 200 if ok else 503, "Transient failure recovery is bounded." if ok else "Retry strategy is unsafe or incomplete.",
                       None if ok else "Use 1–3 retries with exponential_backoff=true, then surface a recoverable failure.", "UPSTREAM_UNAVAILABLE" if not ok else None)

    raise AssertionError("unreachable")


def _result(success: bool, status: int, message: str, next_action: str | None,
            error_code: str | None = None, response_headers: dict[str, str] | None = None) -> dict[str, Any]:
    return {
        "success": success,
        "status": status,
        "message": message,
        "error_code": error_code,
        "next_action": next_action,
        "response_headers": response_headers or {},
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def benchmark_summary(attempts: list[dict[str, Any]], total_scenarios: int | None = None) -> dict[str, Any]:
    total_scenarios = total_scenarios or len(SCENARIOS)
    if not attempts:
        return {"attempts":0,"unique_scenarios":0,"completed":0,"completion_rate":0.0,"first_try_success_rate":0.0,"recovery_rate":0.0,"avg_attempts_per_completed":0.0,"friction":[]}
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for row in attempts:
        by_scenario.setdefault(str(row.get("scenario_id")), []).append(row)
    completed = {k:v for k,v in by_scenario.items() if any(x.get("success") for x in v)}
    first_try = sum(1 for rows in completed.values() if rows and rows[0].get("success"))
    recovered = sum(1 for rows in completed.values() if rows and not rows[0].get("success") and any(x.get("success") for x in rows[1:]))
    total_failed_first = sum(1 for rows in by_scenario.values() if rows and not rows[0].get("success"))
    friction = sorted([
        {"scenario_id":sid,"title":SCENARIO_MAP.get(sid, Scenario(sid,sid,"","","","","","")).title,"attempts":len(rows),"errors":sum(1 for x in rows if not x.get("success")),"completed":any(x.get("success") for x in rows)}
        for sid,rows in by_scenario.items()
    ], key=lambda x:(-x["errors"],-x["attempts"],x["scenario_id"]))
    return {
        "attempts": len(attempts),
        "unique_scenarios": len(by_scenario),
        "completed": len(completed),
        "completion_rate": round(len(completed)/total_scenarios*100,1),
        "first_try_success_rate": round(first_try/max(1,len(completed))*100,1),
        "recovery_rate": round(recovered/max(1,total_failed_first)*100,1),
        "avg_attempts_per_completed": round(sum(len(v) for v in completed.values())/max(1,len(completed)),2),
        "friction": friction,
    }
