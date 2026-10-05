"""Offline tests for the final-render routes: no FFmpeg, no swiftc, no media decoding."""
import importlib.util
import subprocess
from pathlib import Path

import pytest

import render.final as final
import render.swift_edit as swift_edit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("render_final_script", ROOT / "scripts/render_final.py")
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "proj"
    for clip in ("renders/a/attempt-01/a.mp4", "renders/b/attempt-01/b.mp4"):
        (root / clip).parent.mkdir(parents=True, exist_ok=True)
        (root / clip).write_bytes(b"fake")
    (root / "audio").mkdir()
    (root / "audio/bed.wav").write_bytes(b"fake")
    (root / "cuts.txt").write_text("# header\nrenders/a/attempt-01/a.mp4\n\n  renders/b/attempt-01/b.mp4  \n")
    return root


class Recorder:
    def __init__(self, returncode=0, stdout='{"ok":true}\n'):
        self.calls, self.returncode, self.stdout = [], returncode, stdout

    def __call__(self, cmd, **kwargs):
        self.calls.append((list(cmd), kwargs))
        if cmd[0] == "swiftc":
            Path(cmd[cmd.index("-o") + 1]).write_text("binary")
            return subprocess.CompletedProcess(cmd, 0, "", "")
        return subprocess.CompletedProcess(cmd, self.returncode, self.stdout, "boom" if self.returncode else "")


@pytest.fixture
def mac(monkeypatch):
    monkeypatch.setattr(swift_edit, "swift_available", lambda: True)
    monkeypatch.setattr(script, "swift_available", lambda: True)
    monkeypatch.setattr(script, "ffmpeg_available", lambda: False)
    rec = Recorder()
    monkeypatch.setattr(swift_edit.subprocess, "run", rec)
    return rec


def test_repository_tools_exist_and_keep_rendering_identical():
    for name in ("finish_anime", "concat_cuts"):
        assert (ROOT / f"tools/edit/{name}.swift").is_file()
    tool = (ROOT / "tools/edit/finish_anime.swift").read_text()
    for constant in ("EXPOSURE_EV: CGFloat = -0.10", "BLOOM_MIX: CGFloat = 0.16", "GRAIN_AMP: CGFloat = 0.12",
                     "OUT_W = 1280, OUT_H = 720, FPS: Int32 = 24", '"--project-root"', '"--clips-file"'):
        assert constant in tool
    # Provenance is a parameter, never a hard-coded model claim.
    assert '"video_model": "google/veo-3.1-lite"' not in tool and '"--video-model"' in tool


def test_clips_file_parsing_matches_swift_rules(project):
    assert swift_edit.read_clips_file(project / "cuts.txt") == ["renders/a/attempt-01/a.mp4", "renders/b/attempt-01/b.mp4"]
    (project / "empty.txt").write_text("# only comments\n\n")
    with pytest.raises(swift_edit.EditRouteError):
        swift_edit.read_clips_file(project / "empty.txt")


def test_no_ffmpeg_without_clips_file_gives_clear_message(monkeypatch, capsys, project):
    monkeypatch.setattr(final.shutil, "which", lambda name: None)
    monkeypatch.setattr(final, "FFMPEG_BIN", "definitely-not-ffmpeg")
    called = []
    monkeypatch.setattr(script, "render_final", lambda p: called.append(p))
    assert script.main([str(project)]) == 2
    err = capsys.readouterr().err
    assert "FFmpeg not found" in err and "--clips-file" in err and not called


def test_render_final_library_refuses_cleanly_without_ffmpeg(monkeypatch, project):
    (project / "renders/videos").mkdir(parents=True)
    (project / "renders/videos/x.mp4").write_bytes(b"x")
    monkeypatch.setattr(final.shutil, "which", lambda name: None)
    monkeypatch.setattr(final, "FFMPEG_BIN", "definitely-not-ffmpeg")
    monkeypatch.setattr(final.subprocess, "run", lambda *a, **k: pytest.fail("ffmpeg must not be invoked"))
    with pytest.raises(RuntimeError, match="FFmpeg not found"):
        final.render_final(project)


def test_ffmpeg_present_keeps_legacy_route(monkeypatch, project, capsys):
    monkeypatch.setattr(script, "ffmpeg_available", lambda: True)
    monkeypatch.setattr(script, "render_final", lambda p: Path(p) / "final/film.mp4")
    assert script.main([str(project)]) == 0
    assert "final/film.mp4" in capsys.readouterr().out


def test_swift_finish_route_builds_once_and_runs_with_project_paths(mac, project, tmp_path):
    build = tmp_path / "build"
    args = [str(project), "--clips-file", "cuts.txt", "--out", "final/s1.mp4", "--audio", "audio/bed.wav",
            "--letterbox", "2.39", "--tier", "preparation", "--video-model", "google/veo-3.1-lite",
            "--build-dir", str(build)]
    assert script.main(args) == 0
    (compile_cmd, _), (run_cmd, run_kwargs) = mac.calls
    assert compile_cmd[:2] == ["swiftc", "-O"] and compile_cmd[-1] == str(ROOT / "tools/edit/finish_anime.swift")
    assert run_kwargs["cwd"] == project.resolve()
    assert run_cmd[run_cmd.index("--project-root") + 1] == str(project.resolve())
    assert run_cmd[run_cmd.index("--clips-file") + 1] == str((project / "cuts.txt").resolve())
    assert run_cmd[run_cmd.index("--out") + 1] == "final/s1.mp4"
    assert run_cmd[run_cmd.index("--audio") + 1] == "audio/bed.wav"
    assert run_cmd[run_cmd.index("--video-model") + 1] == "google/veo-3.1-lite"
    assert "--model-folder" not in run_cmd and "--seed" not in run_cmd
    # cached binary keyed by source hash: second run does not recompile
    mac.calls.clear()
    assert script.main(args[:5] + ["--out", "final/s2.mp4", "--audio", "audio/bed.wav", "--build-dir", str(build)]) == 0
    assert [c[0][0] for c in mac.calls] != ["swiftc"] and len(mac.calls) == 1


def test_swift_concat_route_passes_ordered_clips(mac, project, tmp_path):
    args = [str(project), "--clips-file", str(project / "cuts.txt"), "--tool", "concat_cuts",
            "--out", "final/cut.mp4", "--audio", "audio/bed.wav", "--build-dir", str(tmp_path / "b")]
    assert script.main(args) == 0
    run_cmd = mac.calls[-1][0]
    assert run_cmd[1:] == [str(project.resolve()), "final/cut.mp4", "audio/bed.wav",
                           "renders/a/attempt-01/a.mp4", "renders/b/attempt-01/b.mp4"]


@pytest.mark.parametrize("extra, message", [
    (["--out", "final/x.mp4"], "--audio is required"),
    (["--out", "final/x.mp4", "--audio", "audio/missing.wav"], "Missing audio"),
    ([], "--out is required"),
])
def test_swift_route_input_errors_never_build_or_run(mac, project, capsys, extra, message):
    assert script.main([str(project), "--clips-file", "cuts.txt", *extra]) == 2
    assert message in capsys.readouterr().err and mac.calls == []


def test_swift_route_refuses_missing_clip_and_existing_output(mac, project, capsys):
    (project / "bad.txt").write_text("renders/nope.mp4\n")
    assert script.main([str(project), "--clips-file", "bad.txt", "--out", "final/x.mp4", "--audio", "audio/bed.wav"]) == 2
    assert "Missing clip" in capsys.readouterr().err
    (project / "final").mkdir()
    (project / "final/x.mp4").write_bytes(b"keep")
    assert script.main([str(project), "--clips-file", "cuts.txt", "--out", "final/x.mp4", "--audio", "audio/bed.wav"]) == 2
    assert "overwrite" in capsys.readouterr().err and mac.calls == []


def test_concat_rejects_finish_only_options(mac, project, capsys):
    assert script.main([str(project), "--clips-file", "cuts.txt", "--tool", "concat_cuts", "--out", "final/x.mp4",
                        "--audio", "audio/bed.wav", "--letterbox", "2.39"]) == 2
    assert "finish_anime only" in capsys.readouterr().err


def test_non_macos_clips_route_is_a_clear_blocker(monkeypatch, project, capsys):
    monkeypatch.setattr(swift_edit.sys, "platform", "linux")
    monkeypatch.setattr(script, "ffmpeg_available", lambda: False)
    monkeypatch.setattr(swift_edit.subprocess, "run", lambda *a, **k: pytest.fail("nothing may run"))
    assert script.main([str(project), "--clips-file", "cuts.txt", "--out", "final/x.mp4", "--audio", "audio/bed.wav"]) == 2
    err = capsys.readouterr().err
    assert "macOS" in err and "FFmpeg is also absent" in err


def test_tool_failure_exit_code_propagates(monkeypatch, mac, project, tmp_path, capsys):
    mac.returncode = 3
    assert script.main([str(project), "--clips-file", "cuts.txt", "--out", "final/x.mp4", "--audio", "audio/bed.wav",
                        "--build-dir", str(tmp_path / "b")]) == 3
    assert "finish_anime failed (exit 3)" in capsys.readouterr().err
