import pytest


@pytest.mark.asyncio
async def test_health_check_return_200(client):
    response = await client.get("/health")

    # assert expevted outcome
    data = response.json()
    assert data["app"] == "swiftlogistics core engine"
    assert data["status"] == "healthy"
