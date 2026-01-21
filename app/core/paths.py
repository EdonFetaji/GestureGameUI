import os, sys

def asset_path(filename: str) -> str:
    # When bundled by PyInstaller
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
        return os.path.join(base, "app", "assets", filename)

    # Normal run from source
    here = os.path.dirname(os.path.abspath(__file__))  # app/core
    return os.path.join(here, "..", "assets", filename)