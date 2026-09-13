"""Start Django and open its local page once it is ready."""

from pathlib import Path
import subprocess
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen
import webbrowser


ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8000"


def open_when_ready(server):
    while server.poll() is None:
        try:
            with urlopen(URL, timeout=1):
                pass
        except (URLError, OSError):
            time.sleep(0.3)
        else:
            webbrowser.open(URL)
            return


def main():
    server = subprocess.Popen(
        [sys.executable, str(ROOT / "Back" / "manage.py"), "runserver", "8000"],
        cwd=ROOT,
    )
    threading.Thread(target=open_when_ready, args=(server,), daemon=True).start()
    try:
        return server.wait()
    except KeyboardInterrupt:
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.terminate()
            server.wait()
        return 0


if __name__ == "__main__":
    sys.exit(main())
