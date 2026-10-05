import pytest

from comfyui.client import ComfyUIClient


def test_queue_requires_legacy_opt_in_without_network(monkeypatch):
    with ComfyUIClient("http://invalid.invalid") as client:
        monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: pytest.fail("Must not submit"))
        with pytest.raises(ValueError, match="explicit opt-in"):
            client.queue({})


def test_openrouter_is_paid_even_without_api_flag(monkeypatch):
    with ComfyUIClient("http://invalid.invalid", legacy_opt_in=True) as client:
        monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: pytest.fail("Must not submit"))
        with pytest.raises(ValueError, match="Paid OpenRouter"):
            client.queue({"real_fixture_node": {"class_type": "OpenRouterImageGenerate", "is_api_node": False, "inputs": {}}})


def test_generation_post_is_never_automatically_retried():
    with ComfyUIClient("http://invalid.invalid") as client:
        methods = client.session.get_adapter("http://invalid.invalid").max_retries.allowed_methods
        assert "GET" in methods
        assert "POST" not in methods


def test_hosted_node_blocks_legacy_client(monkeypatch):
    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return {"PartnerTestFixture": {"is_api_node": True}}

    with ComfyUIClient("http://invalid.invalid", legacy_opt_in=True) as client:
        monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: Response())
        monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: pytest.fail("Must not submit"))
        with pytest.raises(ValueError, match="explicit job consent"):
            client.queue({"fixture_node": {"class_type": "PartnerTestFixture", "inputs": {}}})
