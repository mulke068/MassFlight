# massFlight (minimal)

This workspace contains a small PyQt5 example.

How to run

From PowerShell, run:

```powershell
& "C:/Program Files/Python313/python.exe" g:/testprog/massFlight/gui.py
```

Notes

- `Mhome.MainWindow` is a plain `QMainWindow` and does not create a `QApplication` itself. `gui.py` is responsible for creating the `QApplication` before constructing/ showing the window.
- If you have `Msphere`-related code to run instead, call that from `gui.py` after creating the `QApplication`.
