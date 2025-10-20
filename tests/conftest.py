# Ensure certain modules are imported before tests run to avoid issues with patched __import__
# This helps prevent recursion when tests patch builtins.__import__ and then import importlib.
import importlib  # noqa: F401
import importlib.util  # Preload submodule to avoid patched __import__ creating MagicMocks

# Add src to path for imports
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))
