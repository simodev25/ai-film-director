"""Loopback-only stdlib HTTP server for the read-only project dashboard."""

from __future__ import annotations

import argparse
from email.utils import formatdate
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import mimetypes
from pathlib import Path
import re
import socket
from urllib.parse import unquote, urlsplit

from .catalog import Catalog, contained_file, safe_parts


STATIC_ROOT = Path(__file__).resolve().parent / "static"
MIME_TYPES = {
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".webp": "image/webp", ".gif": "image/gif", ".mp4": "video/mp4",
    ".webm": "video/webm", ".mov": "video/quicktime", ".wav": "audio/wav",
    ".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".m4a": "audio/mp4",
    ".flac": "audio/flac", ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".svg": "image/svg+xml",
}
STATIC_SUFFIXES = {".html", ".js", ".css", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2"}


def validate_host(host):
    if host == "localhost":
        return "127.0.0.1"
    try:
        if ipaddress.ip_address(host).is_loopback:
            return host
    except ValueError:
        pass
    raise ValueError("Dashboard host must be a loopback address (127.0.0.1, ::1 or localhost)")


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "FilmDashboard/1.0"

    def parse_request(self):
        # Runs before method dispatch, including unsupported HTTP methods.
        return super().parse_request() and self._check_request_origin()

    def log_message(self, format, *args):
        # Do not log untrusted URLs (which may contain accidentally pasted secrets).
        pass

    def _headers(self, status, content_type, length, extra=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; media-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.send_header("Cache-Control", (extra or {}).get("Cache-Control", "no-cache"))
        for key, value in (extra or {}).items():
            if key != "Cache-Control":
                self.send_header(key, value)
        self.end_headers()

    def _json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self._headers(status, "application/json; charset=utf-8", len(payload), {"Cache-Control": "no-store"})
        if self.command != "HEAD":
            self.wfile.write(payload)

    def do_GET(self):
        self._dispatch()

    def do_HEAD(self):
        self._dispatch()

    def _readonly(self):
        self._json({"error": "Read-only dashboard"}, 405)

    do_POST = _readonly
    do_PUT = _readonly
    do_PATCH = _readonly
    do_DELETE = _readonly
    do_OPTIONS = _readonly

    def _local_authority(self, authority):
        """Validate literal loopback/localhost and the bound port, without DNS."""
        if not authority or authority != authority.strip() or any(
                char in authority for char in "/\\?#@%\r\n\t ,"):
            return False
        try:
            parsed = urlsplit("http://" + authority)
            hostname = parsed.hostname
            if not hostname or parsed.username is not None or parsed.password is not None:
                return False
            if hostname != "localhost" and not ipaddress.ip_address(hostname).is_loopback:
                return False
            # No explicit port means HTTP's default port, not this server's port.
            return (parsed.port if parsed.port is not None else 80) == self.server.server_port
        except ValueError:
            return False

    def _check_request_origin(self):
        hosts = self.headers.get_all("Host", [])
        valid = len(hosts) == 1 and self._local_authority(hosts[0])
        origins = self.headers.get_all("Origin", [])
        if origins:
            try:
                origin = urlsplit(origins[0])
                valid = valid and not any(char.isspace() for char in origins[0]) and len(origins) == 1 and origin.scheme == "http" and not (
                    origin.path or origin.query or origin.fragment) and self._local_authority(origin.netloc)
            except ValueError:
                valid = False
        try:
            target = urlsplit(self.path)
            if target.netloc or target.scheme:
                valid = valid and target.scheme == "http" and self._local_authority(target.netloc)
        except ValueError:
            valid = False
        if not valid:
            self._json({"error": "Forbidden request origin"}, 403)
        return valid

    def _dispatch(self):
        try:
            path = unquote(urlsplit(self.path).path, errors="strict")
            if path == "/api/projects":
                self._json(self.server.catalog.list_projects())
            elif path.startswith("/api/projects/"):
                project_id = path[len("/api/projects/"):]
                self._json(self.server.catalog.get_project(project_id))
            elif path.startswith("/media/"):
                parts = safe_parts(path[len("/media/"):])
                if len(parts) < 2:
                    raise FileNotFoundError()
                self._file(self.server.catalog.media_file(parts[0], "/".join(parts[1:])), ranges=True)
            elif path.startswith("/api/"):
                raise FileNotFoundError()
            else:
                relative = "index.html" if path == "/" else path.removeprefix("/")
                if relative.startswith("static/"):
                    relative = relative[len("static/"):]
                if Path(relative).suffix.lower() not in STATIC_SUFFIXES:
                    raise FileNotFoundError()
                self._file(contained_file(self.server.static_root, relative))
        except (ValueError, UnicodeError):
            self._json({"error": "Invalid path or request"}, 400)
        except (FileNotFoundError, PermissionError):
            self._json({"error": "Not found"}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            self._json({"error": "Dashboard data unavailable"}, 500)

    def _file(self, path, *, ranges=False):
        # Stream bounded chunks; never load an entire image/video into memory.
        with path.open("rb") as stream:
            import os
            stat = os.fstat(stream.fileno())
            size = stat.st_size
            start, end, status = 0, size - 1, 200
            extra = {"Last-Modified": formatdate(stat.st_mtime, usegmt=True)}
            if ranges:
                extra["Accept-Ranges"] = "bytes"
                requested = self.headers.get("Range")
                if requested:
                    match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested.strip())
                    try:
                        if not match or not any(match.groups()) or size == 0:
                            raise ValueError()
                        left, right = match.groups()
                        if left:
                            start = int(left)
                            end = min(int(right), size - 1) if right else size - 1
                        else:
                            length = int(right)
                            if length <= 0:
                                raise ValueError()
                            start = max(0, size - length)
                        if start >= size or end < start:
                            raise ValueError()
                    except ValueError:
                        self._headers(416, "application/octet-stream", 0,
                                      {"Content-Range": f"bytes */{size}", "Accept-Ranges": "bytes"})
                        return
                    status = 206
                    extra["Content-Range"] = f"bytes {start}-{end}/{size}"
            length = max(0, end - start + 1)
            content_type = MIME_TYPES.get(path.suffix.lower(), mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self._headers(status, content_type, length, extra)
            if self.command == "HEAD":
                return
            stream.seek(start)
            remaining = length
            while remaining:
                chunk = stream.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)


def make_server(projects_root, host="127.0.0.1", port=8765, *, static_root=None, cache_seconds=1.0):
    """Create a server without starting it (also useful for embedding and tests)."""
    host = validate_host(host)
    server_class = ThreadingHTTPServer
    if ":" in host:
        class IPv6Server(ThreadingHTTPServer):
            address_family = socket.AF_INET6
        server_class = IPv6Server
    server = server_class((host, port), DashboardHandler)
    server.catalog = Catalog(projects_root, cache_seconds=cache_seconds)
    server.static_root = Path(static_root) if static_root is not None else STATIC_ROOT
    return server


def serve(projects_root, host="127.0.0.1", port=8765):
    """Serve until interrupted. This is the integration entry point for the CLI."""
    with make_server(projects_root, host, port) as server:
        bound_host, bound_port = server.server_address[:2]
        address = f"[{bound_host}]" if ":" in bound_host else bound_host
        print(f"Read-only dashboard: http://{address}:{bound_port}", flush=True)
        try:
            server.serve_forever(poll_interval=0.25)
        except KeyboardInterrupt:
            pass


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read-only multi-project film dashboard")
    parser.add_argument("--projects-root", type=Path, default=Path("projects"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    try:
        validate_host(args.host)
    except ValueError as error:
        parser.error(str(error))
    serve(args.projects_root, args.host, args.port)


if __name__ == "__main__":
    main()
