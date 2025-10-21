#!/usr/bin/env python3
"""Installation wizard for zsh-llm-suggestions."""

import logging
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, cast

try:
    import questionary

    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False

from . import __version__

logger = logging.getLogger(__name__)


def get_install_dir() -> Path:
    """Get installation directory."""
    return Path.home() / ".local" / "share" / "zsh-llm-suggestions"


def get_shell_config() -> Optional[Path]:
    """Detect shell config file."""
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        return Path.home() / ".zshrc"
    if "bash" in shell:
        return Path.home() / ".bashrc"
    return None


def ask_confirmation(message: str, default: bool = False) -> bool:
    """Ask for user confirmation with questionary if available, otherwise input().

    Args:
        message: The question to ask
        default: Default answer (True for yes, False for no)

    Returns:
        Boolean answer from user
    """
    if HAS_QUESTIONARY:
        return cast(bool, questionary.confirm(message, default=default).ask())
    # Fallback to input()
    default_str = "Y/n" if default else "y/N"
    response = input(f"{message} [{default_str}]: ")
    if not response:  # User pressed enter without typing
        return default
    return response.lower() in ["y", "yes"]


def create_backup(config_file: Path) -> Optional[Path]:
    """Create a timestamped backup of the config file.

    Args:
        config_file: Path to the config file to backup

    Returns:
        Path to the backup file, or None if backup failed
    """
    if not config_file or not config_file.exists():
        return None

    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = config_file.parent / f"{config_file.name}.backup.{timestamp}"
        backup_path.write_text(config_file.read_text())
        logger.debug(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.warning(f"Failed to create backup of {config_file}: {e}", exc_info=True)
        print(f"⚠️  Warning: Could not create backup: {e}")
        return None


def atomic_write_config(config_file: Path, content: str) -> None:
    """Atomically write content to config file using temp file + rename.

    Args:
        config_file: Path to the config file
        content: String content to write

    Raises:
        Exception: If write or rename fails
    """
    # Write to temporary file in same directory (ensures same filesystem)
    fd, temp_path = tempfile.mkstemp(
        dir=config_file.parent, prefix=f".{config_file.name}.tmp.", text=True
    )

    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)

        # Atomic replace (POSIX guarantees atomicity)
        Path(temp_path).replace(config_file)
    except Exception:
        # Clean up temp file on failure
        try:
            Path(temp_path).unlink()
        except OSError:
            pass
        raise


def has_block_markers(config_content: str, block_name: str) -> bool:
    """Check if config has block markers for a given block name.

    Args:
        config_content: String content of config file
        block_name: Name of the block (e.g., 'zsh-llm-suggestions')

    Returns:
        True if both BEGIN and END markers are present
    """
    begin_marker = f"# BEGIN {block_name}"
    end_marker = f"# END {block_name}"
    return begin_marker in config_content and end_marker in config_content


def remove_block(config_content: str, block_name: str) -> str:
    """Remove a block between BEGIN and END markers.

    Args:
        config_content: String content of config file
        block_name: Name of the block to remove

    Returns:
        Updated config content with block removed
    """
    lines = config_content.split("\n")
    new_lines = []
    in_block = False
    begin_marker = f"# BEGIN {block_name}"
    end_marker = f"# END {block_name}"

    for line in lines:
        if line.strip() == begin_marker:
            in_block = True
            continue
        if line.strip() == end_marker:
            in_block = False
            continue

        if not in_block:
            new_lines.append(line)

    return "\n".join(new_lines)


def install() -> None:
    """Interactive installer - copy zsh script and update shell config."""
    print(f"zsh-llm-suggestions {__version__} installer")
    print("=" * 50)
    print()

    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)

    # Find and copy zsh script from installed package data
    try:
        import importlib.resources

        script_content = (
            importlib.resources.files("zsh_llm_suggestions.data")
            .joinpath("zsh-llm-suggestions.zsh")
            .read_text()
        )
    except Exception as e:
        print(f"❌ Error reading installed zsh script: {e}")
        print("   Make sure the package is installed correctly.")
        sys.exit(1)

    script_path = install_dir / "zsh-llm-suggestions.zsh"
    script_path.write_text(script_content)

    print(f"✅ Installed zsh script to: {script_path}")
    print()

    # Offer to update shell config
    config_file = get_shell_config()
    if config_file and config_file.exists():
        source_line = f"source {script_path}"

        try:
            config_content = config_file.read_text()
        except Exception as e:
            print(f"❌ Error reading {config_file}: {e}")
            print("   Please manually add this line to your shell config:")
            print(f"   {source_line}")
            source_added = False
        else:
            # Check if already configured (either with or without block markers)
            if (
                has_block_markers(config_content, "zsh-llm-suggestions")
                or source_line in config_content
            ):
                print(f"✅ Already configured in {config_file}")
                source_added = True
            else:
                if ask_confirmation(f"Add source line to {config_file}?", default=False):
                    # Create backup before modifying
                    backup_path = create_backup(config_file)
                    if backup_path:
                        print(f"📋 Created backup: {backup_path}")

                    try:
                        # Add source line with block markers for easy removal
                        new_content = config_content.rstrip("\n") + "\n\n"
                        new_content += "# BEGIN zsh-llm-suggestions\n"
                        new_content += f"{source_line}\n"
                        new_content += "# END zsh-llm-suggestions\n"

                        atomic_write_config(config_file, new_content)
                        print(f"✅ Added to {config_file}")
                        source_added = True
                    except Exception as e:
                        print(f"❌ Error updating {config_file}: {e}")
                        if backup_path:
                            print(f"   Backup available at: {backup_path}")
                        source_added = False
                else:
                    print()
                    print("⚠️  Please manually add this line to your shell config:")
                    print(f"   {source_line}")
                    source_added = False

        # Offer to configure key bindings
        if source_added:
            print()
            try:
                config_content = config_file.read_text()  # Re-read to get updated content
            except Exception as e:
                print(f"❌ Error reading {config_file}: {e}")
                config_content = ""

            key_bindings = [
                "bindkey '^o' zsh_llm_suggestions_openai",
                "bindkey '^xo' zsh_llm_suggestions_openai_explain",
                "bindkey '^p' zsh_llm_suggestions_github_copilot",
                "bindkey '^xp' zsh_llm_suggestions_github_copilot_explain",
            ]

            # Check if key bindings already exist (either with or without block markers)
            if has_block_markers(config_content, "zsh-llm-suggestions-keybindings") or all(
                binding in config_content for binding in key_bindings
            ):
                print("✅ Key bindings already configured")
            else:
                if ask_confirmation(f"Configure key bindings in {config_file}?", default=False):
                    # Create backup before modifying
                    backup_path = create_backup(config_file)
                    if backup_path:
                        print(f"📋 Created backup: {backup_path}")

                    try:
                        # Add key bindings with block markers for easy removal
                        new_content = config_content.rstrip("\n") + "\n\n"
                        new_content += "# BEGIN zsh-llm-suggestions-keybindings\n"
                        for binding in key_bindings:
                            new_content += f"{binding}\n"
                        new_content += "# END zsh-llm-suggestions-keybindings\n"

                        atomic_write_config(config_file, new_content)
                        print("✅ Configured key bindings:")
                        print("   • Ctrl+O - OpenAI suggestions")
                        print("   • Ctrl+X then O - OpenAI explanations")
                        print("   • Ctrl+P - Copilot suggestions")
                        print("   • Ctrl+X then P - Copilot explanations")
                    except Exception as e:
                        print(f"❌ Error updating {config_file}: {e}")
                        if backup_path:
                            print(f"   Backup available at: {backup_path}")
                else:
                    print()
                    print("⚠️  Please manually add key bindings to your shell config:")
                    for binding in key_bindings:
                        print(f"   {binding}")

            print()
            print("💡 Restart your shell or run:")
            print(f"   source {config_file}")
    else:
        print("⚠️  Could not detect shell config file.")
        print("   Please manually add this line to your ~/.zshrc or ~/.bashrc:")
        print(f"   source {script_path}")

    print()
    print("🎉 Installation complete!")
    print()
    print("Commands now available:")
    print("  - zsh-llm-openai (called by Ctrl+O)")
    print("  - zsh-llm-copilot (called by Ctrl+P)")
    print("  - zsh-llm-uninstall (to remove)")
    print("  - zsh-llm-status (check installation)")


def uninstall() -> None:
    """Remove installation."""
    print(f"zsh-llm-suggestions {__version__} uninstaller")
    print("=" * 50)
    print()

    install_dir = get_install_dir()

    if not install_dir.exists():
        print("ℹ️  No installation found.")
        return

    # Remove zsh script
    script_path = install_dir / "zsh-llm-suggestions.zsh"
    if script_path.exists():
        script_path.unlink()
        print(f"✅ Removed: {script_path}")

    # Try to remove directory if empty
    try:
        install_dir.rmdir()
        print(f"✅ Removed directory: {install_dir}")
    except OSError:
        print(f"ℹ️  Directory not empty: {install_dir}")

    # Offer to remove from shell config
    config_file = get_shell_config()
    if config_file and config_file.exists():
        source_line = f"source {script_path}"

        try:
            config_content = config_file.read_text()
        except Exception as e:
            print(f"❌ Error reading {config_file}: {e}")
            config_content = ""

        # Check if source line exists (either with block markers or standalone)
        if (
            has_block_markers(config_content, "zsh-llm-suggestions")
            or source_line in config_content
        ):
            if ask_confirmation(f"Remove source line from {config_file}?", default=False):
                # Create backup before modifying
                backup_path = create_backup(config_file)
                if backup_path:
                    print(f"📋 Created backup: {backup_path}")

                try:
                    # Try block-based removal first
                    if has_block_markers(config_content, "zsh-llm-suggestions"):
                        new_content = remove_block(config_content, "zsh-llm-suggestions")
                    else:
                        # Fallback: Remove the source line and the comment above it
                        lines = config_content.split("\n")
                        new_lines = []
                        skip_next = False
                        for _i, line in enumerate(lines):
                            if (
                                line.strip() == "# zsh-llm-suggestions"
                                and _i + 1 < len(lines)
                                and source_line in lines[_i + 1]
                            ):
                                skip_next = True
                                continue
                            if skip_next:
                                skip_next = False
                                continue
                            if source_line not in line:
                                new_lines.append(line)
                        new_content = "\n".join(new_lines)

                    atomic_write_config(config_file, new_content)
                    print(f"✅ Removed from {config_file}")
                except Exception as e:
                    print(f"❌ Error updating {config_file}: {e}")
                    if backup_path:
                        print(f"   Backup available at: {backup_path}")

        # Offer to remove key bindings
        try:
            config_content = config_file.read_text()  # Re-read to get updated content
        except Exception as e:
            print(f"❌ Error reading {config_file}: {e}")
            config_content = ""

        key_bindings = [
            "bindkey '^o' zsh_llm_suggestions_openai",
            "bindkey '^xo' zsh_llm_suggestions_openai_explain",
            "bindkey '^p' zsh_llm_suggestions_github_copilot",
            "bindkey '^xp' zsh_llm_suggestions_github_copilot_explain",
        ]

        # Check if any key bindings exist (either with block markers or standalone)
        if has_block_markers(config_content, "zsh-llm-suggestions-keybindings") or any(
            binding in config_content for binding in key_bindings
        ):
            if ask_confirmation(f"Remove key bindings from {config_file}?", default=False):
                # Create backup before modifying
                backup_path = create_backup(config_file)
                if backup_path:
                    print(f"📋 Created backup: {backup_path}")

                try:
                    # Try block-based removal first
                    if has_block_markers(config_content, "zsh-llm-suggestions-keybindings"):
                        new_content = remove_block(
                            config_content, "zsh-llm-suggestions-keybindings"
                        )
                    else:
                        # Fallback: Remove key bindings and the comment line
                        lines = config_content.split("\n")
                        new_lines = []
                        in_binding_block = False

                        for _i, line in enumerate(lines):
                            # Check if this is the start of the key bindings block
                            if line.strip() == "# zsh-llm-suggestions key bindings":
                                in_binding_block = True
                                continue

                            # Skip lines that are key bindings
                            if any(binding in line for binding in key_bindings):
                                continue

                            # If we were in a binding block and hit a non-binding line, we're done
                            if in_binding_block and line.strip() != "":
                                in_binding_block = False

                            new_lines.append(line)
                        new_content = "\n".join(new_lines)

                    atomic_write_config(config_file, new_content)
                    print(f"✅ Removed key bindings from {config_file}")
                except Exception as e:
                    print(f"❌ Error updating {config_file}: {e}")
                    if backup_path:
                        print(f"   Backup available at: {backup_path}")

    print()
    print("✅ Uninstallation complete!")
    print()
    print("To completely remove zsh-llm-suggestions:")
    print("  uv tool uninstall zsh-llm-suggestions")


def status() -> None:
    """Show installation status and version."""
    print(f"zsh-llm-suggestions {__version__}")
    print("=" * 50)
    print()

    print("Command status:")
    import shutil

    if shutil.which("zsh-llm-openai"):
        print("  ✅ zsh-llm-openai available")
    else:
        print("  ❌ zsh-llm-openai not found")

    if shutil.which("zsh-llm-copilot"):
        print("  ✅ zsh-llm-copilot available")
    else:
        print("  ❌ zsh-llm-copilot not found")

    print()

    install_dir = get_install_dir()
    script_path = install_dir / "zsh-llm-suggestions.zsh"

    print("Installation status:")
    if script_path.exists():
        print(f"  ✅ zsh script: {script_path}")
    else:
        print(f"  ❌ zsh script not found at {script_path}")

    print()

    config_file = get_shell_config()
    if config_file and config_file.exists():
        config_content = config_file.read_text()
        if str(script_path) in config_content:
            print(f"  ✅ Configured in {config_file}")
        else:
            print(f"  ⚠️  Not configured in {config_file}")

    print()
    print("Installation method:")
    import importlib.util

    spec = importlib.util.find_spec("zsh_llm_suggestions")
    if spec and spec.origin:
        print(f"  📦 Installed as package: {Path(spec.origin).parent}")
    else:
        print("  ⚠️  Package not found in Python path")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "install":
            install()
        elif command == "uninstall":
            uninstall()
        elif command == "status":
            status()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: install, uninstall, status")
            sys.exit(1)
    else:
        status()
