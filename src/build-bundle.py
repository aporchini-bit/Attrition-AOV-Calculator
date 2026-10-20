#!/usr/bin/env python3
"""
Build a single-file, self-contained version of the ROPS Attrition & AOV Calculator.

Reads the editable source (rops-calculator-server.py + rops-calculator.html) and
emits dist/rops-calculator.py — one file a teammate can download and run with:

    python3 rops-calculator.py

The HTML is embedded (base64) and served from memory, so no sibling files are
needed. The session-ID config is stored in the user's home folder so the lone
file works from anywhere (e.g. ~/Downloads).

Regenerate whenever you edit the HTML or the server (from the repo root):

    python3 src/build-bundle.py
"""
import base64
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)          # src/ lives one level under the repo root
SERVER_SRC = os.path.join(HERE, 'rops-calculator-server.py')
HTML_SRC = os.path.join(HERE, 'rops-calculator.html')
OUT_DIR = os.path.join(REPO_ROOT, 'dist')  # bundle stays at repo-root dist/
OUT_FILE = os.path.join(OUT_DIR, 'rops-calculator.py')


def build():
    with open(SERVER_SRC, 'r', encoding='utf-8') as f:
        server = f.read()
    with open(HTML_SRC, 'rb') as f:
        html_bytes = f.read()

    html_b64 = base64.b64encode(html_bytes).decode('ascii')

    # 1) Replace the path-definition block (SCRIPT_DIR / HTML_FILE / CONFIG_FILE)
    #    with a standalone version: embedded HTML + home-dir config.
    path_block_re = re.compile(
        r"SCRIPT_DIR\s*=.*?\nHTML_FILE\s*=.*?\nCONFIG_FILE\s*=.*?\n",
        re.DOTALL,
    )
    if not path_block_re.search(server):
        sys.exit("ERROR: could not find the SCRIPT_DIR/HTML_FILE/CONFIG_FILE block to replace.")

    standalone_paths = (
        "# --- bundled: paths resolved for a standalone single file ---\n"
        "import base64 as _b64\n"
        "_EMBEDDED_HTML = _b64.b64decode(_EMBEDDED_HTML_B64)\n"
        "# Config lives next to this file if writable, else in the home folder,\n"
        "# so the lone .py works from anywhere (e.g. ~/Downloads).\n"
        "def _resolve_config_path():\n"
        "    here = os.path.dirname(os.path.abspath(__file__))\n"
        "    candidate = os.path.join(here, 'rops-calculator-config.json')\n"
        "    try:\n"
        "        if os.path.exists(candidate):\n"
        "            return candidate\n"
        "        # test writability of the folder\n"
        "        testfile = os.path.join(here, '.rops-write-test')\n"
        "        with open(testfile, 'w') as _t:\n"
        "            _t.write('')\n"
        "        os.remove(testfile)\n"
        "        return candidate\n"
        "    except Exception:\n"
        "        return os.path.join(os.path.expanduser('~'), '.rops-calculator-config.json')\n"
        "CONFIG_FILE = _resolve_config_path()\n"
    )
    server = path_block_re.sub(standalone_paths, server, count=1)

    # 2) Replace the on-disk HTML read with serving the embedded bytes.
    serve_block_re = re.compile(
        r"        # Static file serving\n"
        r"        try:\n"
        r"            with open\(HTML_FILE, 'rb'\) as f:\n"
        r"                content = f\.read\(\)\n"
        r"            self\.send_response\(200\)\n"
        r"            self\.send_header\('Content-Type', 'text/html; charset=utf-8'\)\n"
        r"            self\.send_header\('Content-Length', str\(len\(content\)\)\)\n"
        r"            self\.end_headers\(\)\n"
        r"            self\.wfile\.write\(content\)\n"
        r"        except FileNotFoundError:\n"
        r"            self\.send_response\(404\)\n"
        r"            self\.end_headers\(\)\n"
        r"            self\.wfile\.write\(b'rops-calculator\.html not found'\)\n"
    )
    serve_replacement = (
        "        # Static file serving (embedded)\n"
        "        content = _EMBEDDED_HTML\n"
        "        self.send_response(200)\n"
        "        self.send_header('Content-Type', 'text/html; charset=utf-8')\n"
        "        self.send_header('Content-Length', str(len(content)))\n"
        "        self.end_headers()\n"
        "        self.wfile.write(content)\n"
    )
    server, n = serve_block_re.subn(serve_replacement, server)
    if n != 1:
        sys.exit("ERROR: could not find the HTML static-serving block to replace (expected exactly 1, got %d)." % n)

    # 3) Prepend the embedded HTML blob after the module docstring / imports.
    #    Insert the big base64 string right before the PORT definition.
    port_anchor = "\nPORT = int(os.environ.get('ROPS_PORT', '8766'))\n"
    if port_anchor not in server:
        sys.exit("ERROR: could not find the PORT anchor.")
    blob = "\n_EMBEDDED_HTML_B64 = (\n"
    # chunk the base64 into readable lines
    CHUNK = 120
    for i in range(0, len(html_b64), CHUNK):
        blob += '    "%s"\n' % html_b64[i:i + CHUNK]
    blob += ")\n"
    server = server.replace(port_anchor, blob + port_anchor, 1)

    header = (
        "#!/usr/bin/env python3\n"
        "# ============================================================\n"
        "#  ROPS Attrition & AOV Calculator  —  SINGLE-FILE BUILD\n"
        "#  Do not edit this file directly. It is generated by\n"
        "#  build-bundle.py from rops-calculator-server.py + .html.\n"
        "#  Run with:  python3 rops-calculator.py\n"
        "# ============================================================\n"
    )
    # Drop the original shebang line from the server source to avoid duplication.
    server = re.sub(r"^#![^\n]*\n", "", server, count=1)
    output = header + server

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output)

    print("Built %s (%d bytes, HTML embedded: %d bytes)" % (OUT_FILE, len(output), len(html_bytes)))


if __name__ == '__main__':
    build()
