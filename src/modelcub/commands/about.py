import platform
import shutil
from .. import __version__

def run(args):
    print(f"ModelCub {__version__}")
    print(f"Python {platform.python_version()} on {platform.system()} {platform.release()}")
    # Optional libs: report if present (no hard deps)
    for pkg in ("ultralytics", "torch", "numpy", "opencv-python"):
        name = pkg.replace("-", "_")
        try:
            mod = __import__(name)
            ver = getattr(mod, "__version__", "installed")
            print(f"{pkg}: {ver}")
        except Exception:
            print(f"{pkg}: not installed")
    path = shutil.which("modelcub")
    if path:
        print(f"CLI path: {path}")
    return 0
