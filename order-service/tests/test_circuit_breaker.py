from services.circuit_breaker import CircuitBreaker
import pytest

def test_circuit_opens_after_threshold():
    cb = CircuitBreaker(name="test", failure_threshold=3)
    
    def failing_func():
        raise Exception("Service down")
    
    for _ in range(3):
        with pytest.raises(Exception):
            cb.call(failing_func)
    
    assert cb.state == "OPEN"

def test_circuit_rejects_when_open():
    cb = CircuitBreaker(name="test", failure_threshold=3)
    cb.state = "OPEN"
    cb.last_failure_time = __import__('time').time()
    
    with pytest.raises(Exception, match="Circuit test is OPEN"):
        cb.call(lambda: None)

def test_circuit_closes_on_success():
    cb = CircuitBreaker(name="test", failure_threshold=3)
    cb.state = "HALF_OPEN"
    cb.last_failure_time = __import__('time').time() - 31
    
    cb.call(lambda: "ok")
    
    assert cb.state == "CLOSED"
    assert cb.failure_count == 0
