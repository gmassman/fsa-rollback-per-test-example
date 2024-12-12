def test_get_alice(test_client, userA):
    resp = test_client.get("/username/1")
    assert resp.json["name"] == userA.name


def test_get_bob(test_client, userB):
    resp = test_client.get("/username/1")
    assert resp.json["name"] == userB.name


def test_get_small_device(test_client, small_device):
    resp = test_client.get("/device/memory/1")
    assert resp.json["memory"] == small_device.memory


def test_get_large_device(test_client, large_device):
    resp = test_client.get("/device/memory/1")
    assert resp.json["memory"] == large_device.memory
