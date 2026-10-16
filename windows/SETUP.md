# Windows — nothing to set up

Good news: this folder already includes everything needed to run the tool.
Just double-click `start.bat`. No download, no install, no terminal.

## If start.bat shows a "Setup needed" message

That means the `python-embed` folder didn't come through when you downloaded
or copied this project (some zip tools or file-size limits can drop it). To
fix it:

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

5. Double-click `start.bat` again.
