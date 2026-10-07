from app.core import benchmark_summary, evaluate_attempt, list_scenarios

def test_all_scenarios_are_exposed(): assert len(list_scenarios()) >= 6

def test_auth_recovery():
    assert evaluate_attempt('missing-api-key')['status']==401
    assert evaluate_attempt('missing-api-key',headers={'x-api-key':'devstart-demo'})['success'] is True

def test_rate_limit_requires_safe_delay():
    assert not evaluate_attempt('rate-limit',body={'retry_after_seconds':1})['success']
    assert evaluate_attempt('rate-limit',body={'retry_after_seconds':2})['success']

def test_server_error_requires_bounded_backoff():
    assert not evaluate_attempt('server-error',body={'max_retries':10,'exponential_backoff':True})['success']
    assert evaluate_attempt('server-error',body={'max_retries':3,'exponential_backoff':True})['success']

def test_benchmark_tracks_recovery():
    rows=[{'scenario_id':'missing-api-key','success':False},{'scenario_id':'missing-api-key','success':True},{'scenario_id':'rate-limit','success':True}]
    b=benchmark_summary(rows,total_scenarios=2)
    assert b['completion_rate']==100.0 and b['recovery_rate']==100.0

def test_boolean_is_not_a_retry_count():
    assert not evaluate_attempt('server-error',body={'max_retries':True,'exponential_backoff':True})['success']
