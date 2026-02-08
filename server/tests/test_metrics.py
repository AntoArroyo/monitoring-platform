def test_latest_metrics(client):
    res = client.get("/metrics/latest")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_timeseries(client):
    res = client.get("/metrics/timeseries?metric_name=cpu_percent&minutes=60")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

    if data:
        assert "timestamp" in data[0]
        assert "value" in data[0]
