# ROPS Attrition & AOV Calculator

Models renewal attrition/AOV for Salesforce contracts. Pulls contract and asset
data live from org62 — no manual SOQL or CSV exports.

## Setup (one time, per person)

**Important:** never open `rops-calculator.html` directly by double-clicking
it. It has to be loaded through the local server at `http://localhost:8766`
— opening the file directly (`file:///...`) will show CORS/network errors
and none of the Fetch buttons will work.

### Mac

1. **Download this folder** (clone the repo, or download it as a zip and
   unzip it).
2. **Double-click `start.command`.** macOS already has Python 3 built in —
   nothing to install. If macOS warns about an unidentified developer the
   first time, right-click the file → **Open** instead of double-clicking.
3. A terminal window opens and your browser opens to the calculator
   automatically. Leave that window open while you use the tool.

### Windows

1. **Download this folder** (clone the repo, or download it as a zip and
   unzip it).
2. **One-time only:** follow `windows/SETUP.md` (about 2 minutes) — it has
   you download a small, install-free copy of Python once. No admin rights
   needed.
3. From then on, just **double-click `windows/start.bat`** whenever you want
   to use the tool. A window opens and your browser opens to the calculator
   automatically.

### Either way, once it's open

1. **Get a Salesforce session ID** for org62:
   - Open any org62 page in your browser while logged in.
   - Open the Salesforce Inspector browser extension.
   - Copy the **Session ID** it shows for the current org.
2. **Paste your session ID** when prompted on the page (Step 1), and save it.
   It's remembered on your machine after that — until it expires (typically a
   few hours), at which point you'll paste a fresh one the same way.

## Using it

1. Paste one or more contract numbers, record IDs, or URLs — fetches live
   from Salesforce.
2. If you entered more than one contract, pick which one to model.
3. Explore renewal scenarios: adjust quantities, reprice lines, cancel
   products. Any price edited **below** the current rate is flagged for
   required Deal Desk review.
4. Use **Undo last change** / **Reset modifications** to step back or start
   over.
5. Optionally compare against an actual quote in the last step.

## Notes

- The server runs only on your machine (`localhost`) — nothing is shared
  between teammates. Each person needs their own session ID and sees only
  what their own Salesforce login is permitted to see.
- `rops-calculator-config.json` (holding your session ID) is created
  automatically the first time you save one, and is gitignored — it never
  gets committed or shared.
