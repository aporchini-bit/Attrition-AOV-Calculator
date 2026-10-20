# ROPS Attrition & AOV Calculator

Models renewal attrition/AOV for Salesforce contracts. Pulls contract and asset
data live from org62 — no manual SOQL or CSV exports.

The whole tool is one self-contained file: **`dist/rops-calculator.py`**. The
HTML and server are bundled inside it, so there are no other files to keep
next to it.

## Download the tool

1. Open the repo on GitHub:
   **https://github.com/aporchini-bit/Attrition-AOV-Calculator**
2. Click the green **`<> Code`** button → **Download ZIP**.
3. You'll get a file named **`Attrition-AOV-Calculator-main.zip`** in your
   Downloads.
4. **Unzip it** (double-click on Mac; right-click → *Extract All…* on Windows).
   You'll end up with a folder named **`Attrition-AOV-Calculator-main`**.
5. Keep that whole folder together — don't move individual files out of it.

### What's inside the folder

After unzipping you'll see these items. You only ever **double-click one
launcher** — everything else supports it.

| Item | What it is | Do you touch it? |
|------|------------|------------------|
| **`start.command`** | Mac launcher — **double-click this on a Mac** | ✅ Mac users |
| **`windows/`** → **`start.bat`** | Windows launcher — **double-click this on Windows** (inside the `windows` folder) | ✅ Windows users |
| `dist/rops-calculator.py` | The actual tool (one bundled file the launchers run) | No — runs automatically |
| `windows/python-embed/` | A built-in copy of Python for Windows (so you don't install anything) | No |
| `windows/SETUP.md` | Only needed if Windows shows a "Setup needed" message | Only if prompted |
| `README.md` | This file | Reading it now |
| `rops-calculator-config.json.example` | A sample of the saved-session file format | No |
| `src/` | The editable source code (for maintainers only) | No |
| `.gitignore` | Housekeeping for Git | No |

**Short version:** on a Mac, double-click **`start.command`**. On Windows, open
the **`windows`** folder and double-click **`start.bat`**. That's it.

## Run it

> **Important:** don't open the bundle in a browser or a text editor — it's a
> program you *run*. It then serves the calculator at `http://localhost:8766`.

### Mac

1. Download and unzip the folder (see **Download the tool** above).
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

1. Download and unzip the folder (see **Download the tool** above).
   Everything needed to run it is already included — nothing to install.
2. **Open the `windows` folder and double-click `start.bat`.** A window opens
   and your browser opens to the calculator. Leave that window open while you
   use the tool.
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

## Two tools, one page

A tab bar at the top switches between two calculators that share the same saved
Salesforce session:

- **Attrition & AOV** — model renewal attrition/AOV for a contract (the default tab).
- **FCV** — Full Cancellation Value calculator (see below).

The session-ID box sits above the tabs, so you set it once and both tools use it.
You can deep-link to a tab with `#attrition` or `#fcv` in the URL.

## Using the Attrition & AOV tab

1. Paste one or more contract numbers, record IDs, or URLs — fetches live from
   Salesforce.
2. If you entered more than one contract, pick which one to model.
3. Explore renewal scenarios: adjust quantities, reprice lines, cancel
   products. Any price edited **below** the current rate is flagged for
   required Deal Desk review. Save named scenarios to compare (and delete them
   with the ✕ on each scenario chip).
4. Use **Undo last change** / **Reset modifications** to step back or start over.
5. Optionally compare against an actual quote in the last step.

## FCV — Full Cancellation Value

The **FCV** section (below the quote comparison) calculates Full Cancellation Value
for KMOD RevRec decisions.

**Case lookup (optional):** enter a Salesforce Case number and click **Look up case**
to pre-fill the effective date, currency, contract end date, contract AOV, and the
reduction AOV (from the Case's Attrition Amount). Review and adjust the pre-filled
values before calculating — e.g. for a reduction, use the reduced line's own end date
if it differs from the contract end. If a field can't be found (some older contracts
store a 0 AOV), it's left blank for you to enter. Needs a valid saved session.

You can also skip the lookup and enter everything manually. Pick a mode and enter the
values:

- **Full cancellation** — AOV, effective date, end date. FCV = (AOV ÷ 360) × days
  remaining.
- **Reduction / Swap** — the removed line's annualized value (or Attrition Amount),
  effective date, and the line's own end date. FCV = (AOV ÷ 12) × months, where
  months = (end − effective) ÷ 30. Usage products can derive their annual AOV from a
  multi-year lump sum. For a swap, enter only the removed side.
- **DPP fee reduction** — the Asset Line Item's Sales Price, Quantity, start and end
  dates. FCV = Sales Price × Qty × months (anchored to the effective date). A
  future-dated line is treated as not active and excluded.

Pick a **currency**; non-USD amounts are converted to USD using Org62's live
`CurrencyType` rate (so it needs a valid saved session), and the result flags when the
USD FCV exceeds **$100,000** (RevRec approval required). If the rate lookup fails, a
manual rate field appears as a fallback.

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
