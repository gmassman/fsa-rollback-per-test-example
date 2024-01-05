from app import db, User

def test_get_alice(test_client, userA):
    resp = test_client.get("/username/1")
    assert resp.json["name"] == userA.name


def test_get_bob(test_client, userB):
    resp = test_client.get("/username/1")
    assert resp.json["name"] == userB.name
