import pytest
import subprocess
import requests
import time
import os

@pytest.fixture(scope="session", autouse=True)
def docker_compose():
    compose_path = os.path.join(os.path.dirname(__file__), "..")
    
    subprocess.run(
        ["docker-compose", "up", "--build", "-d"],
        cwd=compose_path,
        check=True
    )
    
    # Esperar que los servicios estén listos
    services = {
        "inventory": "http://localhost:8001/health",
        "payment": "http://localhost:8002/health",
        "order": "http://localhost:8003/health",
    }
    
    for name, url in services.items():
        for _ in range(30):
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    print(f"\n{name} ready")
                    break
            except:
                time.sleep(2)
        else:
            raise Exception(f"{name} did not start")
    
    yield
    
    subprocess.run(
        ["docker-compose", "down"],
        cwd=compose_path
    )
