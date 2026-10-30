from fastapi.testclient import TestClient

import main


class FakeCursor:
    def fetchall(self):
        return [("Ada", "Hello")]


class FakeConnection:
    def __init__(self, executed):
        self.executed = executed

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, query, parameters=None):
        self.executed.append((query, parameters))
        return FakeCursor()


def test_health_and_greeting(monkeypatch):
    monkeypatch.setattr(main, "connect", lambda: FakeConnection([]))

    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok"}
        assert client.get("/").json() == {"message": main.settings.greeting}


def test_list_messages(monkeypatch):
    monkeypatch.setattr(main, "connect", lambda: FakeConnection([]))

    with TestClient(main.app) as client:
        response = client.get("/messages")

    assert response.status_code == 200
    assert response.json() == [{"author": "Ada", "text": "Hello"}]


def test_add_message(monkeypatch):
    executed = []
    monkeypatch.setattr(main, "connect", lambda: FakeConnection(executed))

    with TestClient(main.app) as client:
        response = client.post("/messages", json={"author": "Ada", "text": "Hello"})

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert executed[-1][1] == ("Ada", "Hello")