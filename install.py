try:
    from scripts.io.util import load_classes_from_directory
except Exception:
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))
    from scripts.io.util import load_classes_from_directory

import traceback

import launch
from modules import shared

from scripts.use_cases.installer import Installer

if shared.opts.data.get("face_editor_additional_components", None) is not None:
    for cls in load_classes_from_directory(Installer, True):
        try:
            cls().install()
        except Exception as e:
            print(traceback.format_exc())
            print(f"Face Editor: {e}")

launch.run_pip(
    "install lark-parser",
    "requirements for Face Editor",
)
