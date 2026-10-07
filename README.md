# DevStart

**Interactive Developer Onboarding Lab + Benchmark.** DevStart teaches API integration by letting developers encounter realistic failures and recover from them while the system measures onboarding friction.

## Included in v1
- six deterministic onboarding scenarios: authentication, malformed JSON, validation, 404 recovery, rate limiting, and transient-server resilience
- explicit HTTP status, stable error code, response headers, recovery guidance, and success state
- per-session attempt history
- completion, first-try success, recovery rate, and attempts-per-completion metrics
- friction ranking by scenario
- polished browser lab + typed FastAPI endpoints
- tests, Docker, and read-only CI

## Quick start
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://localhost:8000`.

## Why it matters
A documentation page can look complete while still leaving developers stuck. DevStart models the moment after the error: does the developer understand what happened, know what to change, and succeed on the next attempt?

## Interview story
> “I built DevStart because developer onboarding should be measurable. The lab intentionally causes common API failures, teaches the recovery contract, and records completion and recovery metrics so an API team can see exactly where new developers struggle.”

## Evidence boundary
The benchmark uses local deterministic scenarios rather than real users or production APIs. A production version would add real tutorial content, persistent anonymized sessions, consent-aware analytics, version comparison, language-specific examples, and controlled user testing.

## Continuous integration
The Verify workflow runs the test suite and Python compilation on Python 3.12 for pushes to main and pull requests. It has read-only repository permissions. Run the tests locally with `python -m pytest`.

