# ROPS Attrition & AOV Calculator

Models renewal attrition/AOV for Salesforce contracts. Pulls contract and asset
data live from org62 — no manual SOQL or CSV exports.

The whole tool is one self-contained file: **`dist/rops-calculator.py`**. The
HTML and server are bundled inside it, so there are no other files to keep
next to it.

## Run it

> **Important:** don't open the bundle in a browser or a text editor — it's a
> program you *run*. It then serves the calculator at `http://localhost:8766`.

### Mac

1. **Download this folder** (clone the repo, or download it as a zip and unzip).
2. **Double-click `start.command`.** macOS already has Python 3 built in —
   nothing to install.
   - If macOS says *"start.command" can't be opened because it is from an
     unidentified developer* or *Apple could not verify…*, click **Done**,
     then open **System Settings → Privacy & Security**, scroll to Security
     and click **Open Anyway**, then double-click `start.command` again.
3. A terminal window opens and your browser opens to the calculator. Leave
   that window open while you use the tool.

**Prefer the terminal?** You can also just run the one file directly:

```bash
python3 dist/rops-calculator.py
```

### Windows

1. **Download this folder** (clone the repo, or download it as a zip and
   unzip). Everything needed to run it is already included — nothing to
   install.
2. **Double-click `windows/start.bat`.** A window opens and your browser opens
   to the calculator. Leave that window open while you use the tool.
   - If `start.bat` shows a "Setup needed" message, see `windows/SETUP.md`
     (that only happens if the `python-embed` folder got dropped during
     download).

### If port 8766 is already in use

Run it on a different port (any launcher or the direct command honors this):

```bash
ROPS_PORT=8790 python3 dist/rops-calculator.py
```

## First-time setup: your Salesforce session ID

The tool authenticates to org62 with **your own** Salesforce session ID. It's
per-person and per-machine, and it expires (typically after a few hours).

1. **Get your session ID (the `sid`):**
   - Log into **org62** in your browser.
   - Easiest: use the **Salesforce Inspector** extension and copy the Session
     ID it shows for the current org, **or**
   - In Chrome DevTools → **Application → Cookies**, pick the row for
     **`https://org62.my.salesforce.com`** (not `lightning.force.com`) and copy
     the full value of the cookie named **`sid`** (it starts with `00D…` and
     contains a `!` — copy all of it).
2. On the calculator page (Step 1), **paste the session ID and click Save.**
3. Click **Test session** to confirm it works:
   - **"Session is valid"** → you're set.
   - **`INVALID_SESSION_ID`** → the token is wrong-domain, truncated, or
     expired. Re-copy the `sid` from **org62.my.salesforce.com** (not
     Lightning) and save again.
   - **API-disabled errors** → your Salesforce profile may lack API access;
     ask an admin.

The saved session ID is remembered on your machine until it expires, when
you'll paste a fresh one the same way.

## Using it

1. Paste one or more contract numbers, record IDs, or URLs — fetches live from
   Salesforce.
2. If you entered more than one contract, pick which one to model.
3. Explore renewal scenarios: adjust quantities, reprice lines, cancel
   products. Any price edited **below** the current rate is flagged for
   required Deal Desk review. Save named scenarios to compare (and delete them
   with the ✕ on each scenario chip).
4. Use **Undo last change** / **Reset modifications** to step back or start over.
5. Optionally compare against an actual quote in the last step.

## For maintainers

- **Edit the source** in `src/`, not the bundle:
  - `src/rops-calculator.html` — the UI
  - `src/rops-calculator-server.py` — the backend/API
- **Rebuild the single file** after any change (from the repo root):

  ```bash
  python3 src/build-bundle.py
  ```

  This regenerates `dist/rops-calculator.py` from the two source files. Commit
  the regenerated bundle alongside your source changes.

## Notes

- The server runs only on your machine (`localhost`) — nothing is shared
  between teammates. Each person needs their own session ID and sees only what
  their own Salesforce login is permitted to see.
- Your session ID is stored in `rops-calculator-config.json` (created next to
  the bundle, or in your home folder if that isn't writable). It's gitignored —
  it never gets committed or shared.
