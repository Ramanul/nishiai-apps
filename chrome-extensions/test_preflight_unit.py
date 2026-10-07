"""Unit tests for the preflight probe classification (Arena P0 follow-up:
the false-green regression guard must itself be tested)."""
from __future__ import annotations

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_preflight import classify_probe  # noqa: E402


def test_ready_when_http_succeeded():
    assert classify_probe(True, "", False) == "ready"


def test_ready_even_if_stderr_has_noise():
    assert classify_probe(True, "some warning text", False) == "ready"


def test_policy_block_classified_from_stderr():
    err = "Failed to load Chrome DLL: An Application Control policy has blocked this file. (0x11C7)"
    assert classify_probe(False, err, False) == "blocked-by-policy"
    assert classify_probe(False, "APPLICATION CONTROL blocked", False) == "blocked-by-policy"


def test_failed_launch_without_policy_text_is_probe_error():
    # the false-green case: process failed, but the policy text is absent
    assert classify_probe(False, "", False) == "probe-error"
    assert classify_probe(False, "some other crash", False) == "probe-error"


def test_missing_stdout_marker_is_never_ready():
    # returncode 0 with empty output (the Edge --dump-dom trap) cannot be ready
    assert classify_probe(False, "", False) == "probe-error"


def test_timeout_is_probe_error():
    assert classify_probe(False, "", True) == "probe-error"
    assert classify_probe(True, "", True) == "ready"  # success before deadline still wins
