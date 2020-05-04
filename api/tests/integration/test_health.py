class TestHealth:
    def test_health(self, client):
        res = client.get("/api/health")
        data = res.get_json()

        assert data["code"] == 200
        assert set(["status", "version", "broker"]).issubset(data["data"])
