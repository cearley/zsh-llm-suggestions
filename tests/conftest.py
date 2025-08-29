# Ensure certain modules are imported before tests run to avoid issues with patched __import__
# This helps prevent recursion when tests patch builtins.__import__ and then import importlib.
import importlib  # noqa: F401
import importlib.util  # Preload submodule to avoid patched __import__ creating MagicMocks
