This module adds a "magic" __main__.py that turns a zip file of dependencies
into something that can be appended to Python script.

Example:

pip install --target ./deps/ -r myscript.reqs magicmain
PYTHONPATH=./deps/ ./myscript.py    # Check that it works
(cd deps/ ; zip -r ../deps.zip .)
cat zips.zip >> myscript.py
./myscript.py                       # Should work!
