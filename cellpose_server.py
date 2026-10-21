#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Local Cellpose server for eMyHC_Quanti.

Starts a small web server on your own computer that
  * opens the eMyHC_Quanti page at http://127.0.0.1:8765
  * runs Cellpose on your GPU when you click "Segment with Cellpose (local GPU)" in the page.
Images never leave your computer.

Usage (in the Anaconda Prompt, after "conda activate cellpose"):
  python cellpose_server.py
  python cellpose_server.py --model "D:/models/my_finetuned_model"
Keep the window open while you work; press Ctrl+C to stop.
"""
import argparse, glob, json, os, sys, threading, time, webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def cellpose_major_version():
    try:
        from importlib.metadata import version
        return int(version("cellpose").split(".")[0])
    except Exception:
        return 0


def load_model(args, major):
    from cellpose import models
    if args.model:
        return models.CellposeModel(gpu=not args.cpu, pretrained_model=args.model)
    if major >= 4:
        return models.CellposeModel(gpu=not args.cpu)                 # Cellpose-SAM
    return models.CellposeModel(gpu=not args.cpu, model_type="cyto3")


def segment(model, img, major, px_um, args):
    kw = dict(flow_threshold=args.flow, cellprob_threshold=args.cellprob)
    if major >= 4 and not args.model:
        return model.eval(img, **kw)[0]
    diam = (args.diam_um / px_um) if (px_um and args.diam_um) else None
    try:
        return model.eval(img, diameter=diam, channels=[0, 0], **kw)[0]
    except TypeError:
        return model.eval(img, diameter=diam, **kw)[0]


def _quiet(cmd):
    """Run a command without printing anything; return True if it started and exited with 0."""
    import subprocess
    try:
        return subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False


def open_browser(url, port):
    """Open the page in a browser on this machine: Windows, macOS, WSL (Windows browser) or Linux desktop."""
    import platform, shutil, socket
    system = platform.system()
    if system == "Windows":
        try:
            os.startfile(url)
            return
        except Exception:
            pass
    elif system == "Darwin":
        if _quiet(["open", url]):
            return
    else:
        try:
            wsl = "microsoft" in open("/proc/version").read().lower()
        except Exception:
            wsl = False
        if wsl:  # Linux inside Windows: use the Windows browser
            if shutil.which("wslview") and _quiet(["wslview", url]):
                return
            if shutil.which("cmd.exe") and _quiet(["cmd.exe", "/c", "start", "", url]):
                return
            if shutil.which("powershell.exe") and _quiet(["powershell.exe", "-NoProfile", "Start-Process", url]):
                return
        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            for cmd in ("xdg-open", "gio", "sensible-browser"):
                if shutil.which(cmd) and _quiet([cmd, "open", url] if cmd == "gio" else [cmd, url]):
                    return
    host = socket.gethostname()
    print("\nNo browser could be opened on this machine (%s)." % host)
    print("If it has a screen, open %s in any browser." % url)
    print("If it is a remote server, run this on YOUR computer and keep it open:")
    print("    ssh -L %d:127.0.0.1:%d <your-user>@%s" % (port, port, host))
    print("then open %s in your own browser.\n" % url)


def find_page(explicit):
    if explicit:
        for cand in (explicit, os.path.join(HERE, explicit)):
            if os.path.isfile(cand):
                return os.path.abspath(cand)
        here = sorted(set(glob.glob("*.html") + glob.glob(os.path.join(HERE, "*.html"))))
        msg = "Cannot find %s (looked in %s and %s)." % (explicit, os.getcwd(), HERE)
        if here:
            msg += "\nHTML files found:\n  " + "\n  ".join(os.path.basename(p) for p in here)
            msg += '\nUse one of these names, e.g.  python cellpose_server.py --html "%s"' % os.path.basename(here[0])
        sys.exit(msg)
    pages = sorted(glob.glob(os.path.join(HERE, "eMyHC_Quanti*.html"))) or sorted(glob.glob(os.path.join(HERE, "fiber-csa*.html")))
    if not pages:
        sys.exit("Put eMyHC_Quanti.html or fiber-csa.html in the same folder as this script, or use --html <file>.")
    return pages[-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--html", default=None, help="path of the eMyHC_Quanti page (default: newest eMyHC_Quanti*.html next to this script)")
    ap.add_argument("--model", default=None, help="path to a fine-tuned Cellpose model (optional)")
    ap.add_argument("--diam_um", type=float, default=35.0, help="typical fiber diameter in µm (Cellpose 3 models only)")
    ap.add_argument("--flow", type=float, default=0.4)
    ap.add_argument("--cellprob", type=float, default=0.0)
    ap.add_argument("--cpu", action="store_true", help="run on CPU instead of the GPU")
    ap.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    args = ap.parse_args()

    page = find_page(args.html)
    major = cellpose_major_version()
    try:
        import torch
        gpu = bool(torch.cuda.is_available()) and not args.cpu
    except Exception:
        gpu = False
    print("Loading Cellpose (version %s, GPU: %s)..." % (major or "?", "yes" if gpu else "no"))
    model = load_model(args, major)
    model_name = os.path.basename(args.model) if args.model else ("cpsam" if major >= 4 else "cyto3")
    lock = threading.Lock()
    status = {"ok": True, "cellpose": major, "gpu": gpu, "model": model_name}

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=os.path.dirname(page), **k)

        def log_message(self, fmt, *a):
            pass

        def end_headers(self):
            # never let the browser reuse a cached page from another tool or version
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def _cors(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Width, X-Height, X-Pixel-Um")
            self.send_header("Access-Control-Expose-Headers", "X-Dtype, X-Count, X-Seconds, X-Model")
            self.send_header("Access-Control-Allow-Private-Network", "true")

        def do_OPTIONS(self):
            self.send_response(204)
            self._cors()
            self.end_headers()

        def do_GET(self):
            path = self.path.split("?")[0]
            if path == "/api/status":
                body = json.dumps(status).encode()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if path in ("/", "/index.html"):
                # send the browser to this tool's own address, so different tools never share a URL
                self.send_response(302)
                self.send_header("Location", "/" + os.path.basename(page))
                self.end_headers()
                return
            return super().do_GET()

        def do_POST(self):
            if self.path.split("?")[0] != "/api/segment":
                self.send_error(404)
                return
            try:
                w = int(self.headers["X-Width"])
                h = int(self.headers["X-Height"])
                px = float(self.headers.get("X-Pixel-Um") or 0) or None
                n = int(self.headers["Content-Length"])
                raw = self.rfile.read(n)
                img = np.frombuffer(raw, dtype=np.uint8).reshape(h, w)
                t0 = time.time()
                with lock:
                    masks = segment(model, img, major, px, args)
                dt = time.time() - t0
                count = int(masks.max())
                dtype = "uint16" if count < 65536 else "uint32"
                out = masks.astype("<u2" if dtype == "uint16" else "<u4").tobytes()
                print("Segmented %d x %d px: %d fibers in %.1f s" % (w, h, count, dt))
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(out)))
                self.send_header("X-Dtype", dtype)
                self.send_header("X-Count", str(count))
                self.send_header("X-Seconds", "%.1f" % dt)
                self.send_header("X-Model", model_name)
                self.end_headers()
                self.wfile.write(out)
            except Exception as e:
                msg = str(e).encode()
                print("ERROR:", e)
                self.send_response(500)
                self._cors()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(msg)))
                self.end_headers()
                self.wfile.write(msg)

    srv = None
    for port in range(args.port, args.port + 20):
        try:
            srv = HTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            print("Port %d is already in use (another cellpose_server.py is probably still running); trying %d..." % (port, port + 1))
    if srv is None:
        sys.exit("No free port found. Stop the other server (Ctrl+C in its window) and try again.")
    args.port = port
    url = "http://127.0.0.1:%d/%s" % (args.port, os.path.basename(page))
    print("Ready. Open %s in your browser (page: %s). Press Ctrl+C to stop." % (url, os.path.basename(page)))
    if not args.no_browser:
        threading.Timer(1.0, lambda: open_browser(url, args.port)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
