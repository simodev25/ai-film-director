"""Offline local-install repair tests: all process/network paths are mocked.

Run explicitly with the existing comfy-mcp venv Python. No server is started,
no tool request is submitted and no real workflow is run. Ordinary repository
pytest collects these only when that optional installed connector is available.
"""
import asyncio
import ast
import importlib.util
import inspect
import json
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

AVAILABLE = importlib.util.find_spec("comfy_mcp") is not None
if AVAILABLE:
    # No __main__/stdio server lifecycle, and no import-time process/network.
    with patch("subprocess.Popen", side_effect=AssertionError("offline process guard")), \
         patch("subprocess.run", side_effect=AssertionError("offline process guard")), \
         patch("socket.socket", side_effect=AssertionError("offline socket guard")):
        from comfy_mcp import errors, server
        from mcp.server.mcpserver.exceptions import ToolError, UnexpectedToolError


@unittest.skipUnless(AVAILABLE, "Use the existing comfy-mcp venv Python for local repair tests")
class RepairTests(unittest.IsolatedAsyncioTestCase):
    def guard(self):
        # ExitStack also closes guards if a test fails; never leave a real runner.
        from contextlib import ExitStack
        stack = ExitStack()
        for name in ("_run_comfy", "_run_comfy_raw", "_run_comfy_streaming"):
            stack.enter_context(patch.object(server, name, side_effect=AssertionError("offline child guard")))
        self.addCleanup(stack.close)

    async def test_success_object_and_signature_preserved(self):
        sentinel = {"status": "mock-only"}
        async def fake(value: str, flag: bool = False):
            return sentinel
        wrapped = server._run_workflow_error_boundary(fake)
        self.assertEqual(inspect.signature(wrapped), inspect.signature(fake))
        self.assertIs(await wrapped("fixture", flag=True), sentinel)
        self.assertEqual(inspect.signature(server.run_workflow), inspect.signature(server.run_workflow.__wrapped__))

    async def test_expected_error_exposes_only_safe_machine_fields(self):
        exc = errors.ComfyCliError("RAW body Authorization Bearer sentinel stdout", code="prompt_rejected",
                                   returncode=1, no_envelope=False, timed_out=False,
                                   data={"api_key": "never-surface", "prompt": "private creative prompt"})
        async def fake(): raise exc
        with self.assertRaises(ToolError) as caught:
            await server._run_workflow_error_boundary(fake)()
        e = caught.exception
        self.assertEqual(e.code, "prompt_rejected")
        self.assertEqual(e.returncode, 1)
        self.assertEqual(e.no_envelope, False)
        self.assertEqual(e.timed_out, False)
        self.assertNotIn("never-surface", str(e))
        self.assertNotIn("private creative prompt", str(e))
        self.assertNotIn("RAW body", str(e))
        self.assertTrue(e.__suppress_context__)
        self.assertIsNone(e.__cause__)
        # The internal class/catches are untouched.
        self.assertIsInstance(exc, RuntimeError)
        self.assertEqual(exc.data["api_key"], "never-surface")

    async def test_secret_urls_headers_messages_hints_and_env_are_omitted(self):
        secret = "SYNTHETIC_SECRET_87654"
        for message in (
            "Authorization: Bearer " + secret,
            "https://user:" + secret + "@site/path?token=" + secret + "#" + secret,
            "api-key=" + secret + " stdout: " + secret + " stderr: " + secret,
            "prompt failed hint: " + secret + " env PRIVATE_KEY=" + secret,
            "sk-or-" + secret,
        ):
            safe = errors._safe_connector_tool_error(errors.ComfyCliError(message, data={"hint": secret}))
            self.assertNotIn(secret, str(safe))
            self.assertNotIn(secret, json.dumps(safe.data))
        safe = errors._safe_connector_tool_error(errors.ComfyCliError("none", code=secret, returncode=secret))
        self.assertEqual(safe.code, "unrecognized_code")
        self.assertIsNone(safe.returncode)
        self.assertNotIn(secret, str(safe))

    async def test_no_envelope_timeout_returncode_preserved_without_raw_text(self):
        safe = errors._safe_connector_tool_error(errors.ComfyCliError("private stderr", returncode=2,
                                                                        no_envelope=True, timed_out=True))
        self.assertTrue(safe.no_envelope)
        self.assertTrue(safe.timed_out)
        self.assertEqual(safe.returncode, 2)
        self.assertEqual(safe.code, "cli_error")
        self.assertNotIn("private stderr", str(safe))

    async def test_unexpected_exception_message_and_console_trace_stay_safe(self):
        async def fake(): raise TypeError("Bearer SYNTHETIC_PRIVATE_TRACE")
        with self.assertRaises(ToolError) as caught:
            await server._run_workflow_error_boundary(fake)()
        self.assertEqual(caught.exception.safe_metadata["kind"], "unexpected_connector_error")
        self.assertEqual(caught.exception.safe_metadata["exception_type"], "TypeError")
        self.assertNotIn("SYNTHETIC_PRIVATE_TRACE", str(caught.exception))
        import traceback
        displayed = "".join(traceback.format_exception(caught.exception))
        self.assertNotIn("SYNTHETIC_PRIVATE_TRACE", displayed)

    async def test_cancelled_task_is_not_swallowed_or_retried(self):
        async def fake(): raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            await server._run_workflow_error_boundary(fake)()

    async def test_sdk_public_tool_sees_safe_error_not_unexpected_generic(self):
        self.guard()
        gate = AsyncMock(side_effect=errors.ComfyCliError("unanswered confirmation SECRET", code="spend_consent_required"))
        with patch.object(server, "_resolve_workflow_spend_consent", gate):
            with self.assertRaises(ToolError) as caught:
                await server.mcp.call_tool("run_workflow", {"workflow_path": "mock-existing-path.json",
                                                           "wait": False, "confirm_spend": True})
        self.assertNotIsInstance(caught.exception, UnexpectedToolError)
        self.assertIn("spend_consent_required", str(caught.exception))
        self.assertNotIn("SECRET", str(caught.exception))
        gate.assert_awaited_once()

    async def test_consent_exception_before_child_no_retry(self):
        gate = AsyncMock(side_effect=errors.ComfyCliError("confirmation failed PRIVATE"))
        with patch.object(server, "_resolve_workflow_spend_consent", gate), \
             patch.object(server, "_run_comfy") as child, \
             patch.object(server, "_comfy_run_takes_allow_spend") as probe:
            with self.assertRaises(ToolError):
                await server.run_workflow("mock-only.json", wait=False, confirm_spend=True)
            child.assert_not_called()
            probe.assert_not_called()
            gate.assert_awaited_once()

    async def test_mocked_human_decline_still_blocks_before_any_child(self):
        # Exercise the original real consent helper, but never a client/network.
        with patch.object(server, "_client_elicitation_support", return_value=True), \
             patch.object(server, "_elicit_approval", AsyncMock(return_value=False)) as elicit, \
             patch.object(server, "_run_comfy") as child, \
             patch.object(server, "_comfy_run_takes_allow_spend") as probe:
            with self.assertRaises(ToolError):
                await server.run_workflow("mock-only.json", wait=False, confirm_spend=True, ctx=object())
            elicit.assert_awaited_once()
            child.assert_not_called()
            probe.assert_not_called()

    async def test_mocked_accepted_path_preserves_flag_and_single_success(self):
        expected = {"status": "queued", "prompt_id": "MOCK_NOT_A_REAL_JOB"}
        with patch.object(server, "_resolve_workflow_spend_consent", AsyncMock(return_value=True)) as gate, \
             patch.object(server, "_comfy_run_takes_allow_spend", return_value=True), \
             patch.object(server, "_run_comfy", return_value=expected) as child:
            result = await server.run_workflow("mock-only.json", wait=False, confirm_spend=True)
            self.assertIs(result, expected)
            gate.assert_awaited_once()
            self.assertIs(gate.await_args.args[1], True)
            child.assert_called_once_with("run", "--workflow", "mock-only.json", "--allow-spend", timeout=60.0)

    async def test_nonretryable_cli_error_child_only_mock_once(self):
        with patch.object(server, "_resolve_workflow_spend_consent", AsyncMock(return_value=True)), \
             patch.object(server, "_comfy_run_takes_allow_spend", return_value=True), \
             patch.object(server, "_run_comfy", side_effect=errors.ComfyCliError("BODY_SECRET", code="usage_error", returncode=2)) as child:
            with self.assertRaises(ToolError) as caught:
                await server.run_workflow("mock-only.json", wait=False, confirm_spend=True)
            self.assertEqual(caught.exception.code, "usage_error")
            self.assertNotIn("BODY_SECRET", str(caught.exception))
            child.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
