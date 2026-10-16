# Windows one-time setup (about 2 minutes)

You only need to do this once. After this, everyone just double-clicks
`start.bat` to open the calculator — no terminal, no typing commands.

1. Download the Python "embeddable" package (a small, install-free copy of
   Python — about 10 MB, needs no admin rights):

   https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip

2. Right-click the downloaded zip → **Extract All...**

3. Rename the extracted folder to exactly: `python-embed`

4. Move that `python-embed` folder into this `windows` folder, so you end up
   with:

   ```
   windows/
     start.bat
     SETUP.md
     python-embed/
       python.exe
       ...
   ```

5. Double-click `start.bat`. A black window opens (leave it open) and your
   browser opens to the calculator automatically.

That's it — from now on, just double-click `start.bat` whenever you want to
use the tool. Close the black window when you're done.
