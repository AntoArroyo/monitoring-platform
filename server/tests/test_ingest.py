from datetime import datetime

def test_ingest_metrics(client):
    payload = {
        "agent_id": "test-pi-01",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": 12.5,
            "ram_percent": 45.0,
            "disk_percent": 67.0,
            "uptime_seconds": 1234
        },
        "raspberry_pi": {
            "cpu_temp_c": 55.2
        }
    }

    res = client.post("/api/v1/ingest", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ingested"
