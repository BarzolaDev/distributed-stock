from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

def test_rate_limit():
    counter = {"count": 0}

    def mock_incr(key):
        counter["count"] += 1
        return counter["count"]

    def mock_expire(key, ttl):
        pass

    mock_redis = MagicMock()
    mock_redis.incr = mock_incr
    mock_redis.expire = mock_expire

    with patch("middleware.rate_limiter.r", mock_redis):
        client = TestClient(app)
        
        for i in range(10):
            response = client.get("/health")
            assert response.status_code == 200

        response = client.get("/health")
        assert response.status_code == 429
