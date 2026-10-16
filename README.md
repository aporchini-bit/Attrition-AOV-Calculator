# ROPS Attrition & AOV Calculator

Models renewal attrition/AOV for Salesforce contracts. Pulls contract and asset
data live from org62 — no manual SOQL or CSV exports.

## Setup (one time, per person)

1. **Install Python 3** if you don't have it already (macOS usually has it —
   check with `python3 --version` in Terminal).

2. **Download this folder** (clone the repo, or download it as a zip and
   unzip it).

3. **Get a Salesforce session ID** for org62:
   - Open any org62 page in your browser while logged in.
   - Open the Salesforce Inspector browser extension.
   - Copy the **Session ID** it shows for the current org.

4. **Start the server.** In Terminal, from this folder:
   ```bash
   python3 rops-calculator-server.py
   ```
   You should see:
   ```
   ROPS Calculator → http://localhost:8766
   ```

5. **Open the tool**: go to `http://localhost:8766` in your browser.

6. **Paste your session ID** when prompted on the page (Step 1), and save it.
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
