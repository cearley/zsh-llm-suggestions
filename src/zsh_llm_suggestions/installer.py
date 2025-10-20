#!/usr/bin/env python3
"""Installation wizard for zsh-llm-suggestions."""

import os
import sys
from pathlib import Path
from . import __version__

def get_install_dir():
    """Get installation directory."""
    return Path.home() / ".local" / "share" / "zsh-llm-suggestions"

def get_shell_config():
    """Detect shell config file."""
    shell = os.environ.get('SHELL', '')
    if 'zsh' in shell:
        return Path.home() / ".zshrc"
    elif 'bash' in shell:
        return Path.home() / ".bashrc"
    return None

def install():
    """Interactive installer - copy zsh script and update shell config."""
    print(f"zsh-llm-suggestions {__version__} installer")
    print("=" * 50)
    print()

    install_dir = get_install_dir()
    install_dir.mkdir(parents=True, exist_ok=True)

    # Find and copy zsh script from installed package data
    try:
        if sys.version_info >= (3, 9):
            import importlib.resources
            script_content = importlib.resources.files('zsh_llm_suggestions.data').joinpath('zsh-llm-suggestions.zsh').read_text()
        else:
            import pkg_resources
            script_content = pkg_resources.resource_string('zsh_llm_suggestions.data', 'zsh-llm-suggestions.zsh').decode('utf-8')
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
        source_line = f'source {script_path}'
        config_content = config_file.read_text()

        # Add source line
        if source_line in config_content:
            print(f"✅ Already configured in {config_file}")
            source_added = True
        else:
            response = input(f"Add source line to {config_file}? [y/N]: ")
            if response.lower() in ['y', 'yes']:
                with config_file.open('a') as f:
                    f.write(f'\n# zsh-llm-suggestions\n{source_line}\n')
                print(f"✅ Added to {config_file}")
                source_added = True
            else:
                print()
                print("⚠️  Please manually add this line to your shell config:")
                print(f"   {source_line}")
                source_added = False

        # Offer to configure key bindings
        if source_added:
            print()
            config_content = config_file.read_text()  # Re-read to get updated content
            key_bindings = [
                "bindkey '^o' zsh_llm_suggestions_openai",
                "bindkey '^[^o' zsh_llm_suggestions_openai_explain",
                "bindkey '^p' zsh_llm_suggestions_github_copilot",
                "bindkey '^[^p' zsh_llm_suggestions_github_copilot_explain"
            ]

            # Check if key bindings already exist
            bindings_exist = all(binding in config_content for binding in key_bindings)

            if bindings_exist:
                print("✅ Key bindings already configured")
            else:
                response = input(f"Configure key bindings in {config_file}? [y/N]: ")
                if response.lower() in ['y', 'yes']:
                    with config_file.open('a') as f:
                        f.write('\n# zsh-llm-suggestions key bindings\n')
                        for binding in key_bindings:
                            f.write(f'{binding}\n')
                    print("✅ Configured key bindings:")
                    print("   • Ctrl+O - OpenAI suggestions")
                    print("   • Ctrl+Alt+O - OpenAI explanations")
                    print("   • Ctrl+P - Copilot suggestions")
                    print("   • Ctrl+Alt+P - Copilot explanations")
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
        print(f"   Please manually add this line to your ~/.zshrc or ~/.bashrc:")
        print(f"   source {script_path}")

    print()
    print("🎉 Installation complete!")
    print()
    print("Commands now available:")
    print("  - zsh-llm-openai (called by Ctrl+O)")
    print("  - zsh-llm-copilot (called by Ctrl+P)")
    print("  - zsh-llm-uninstall (to remove)")
    print("  - zsh-llm-status (check installation)")

def uninstall():
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
        source_line = f'source {script_path}'
        config_content = config_file.read_text()

        if source_line in config_content:
            response = input(f"Remove source line from {config_file}? [y/N]: ")
            if response.lower() in ['y', 'yes']:
                # Remove the source line and the comment above it
                lines = config_content.split('\n')
                new_lines = []
                skip_next = False
                for i, line in enumerate(lines):
                    if line.strip() == '# zsh-llm-suggestions' and i + 1 < len(lines) and source_line in lines[i + 1]:
                        skip_next = True
                        continue
                    if skip_next:
                        skip_next = False
                        continue
                    if source_line not in line:
                        new_lines.append(line)

                config_file.write_text('\n'.join(new_lines))
                print(f"✅ Removed from {config_file}")

        # Offer to remove key bindings
        config_content = config_file.read_text()  # Re-read to get updated content
        key_bindings = [
            "bindkey '^o' zsh_llm_suggestions_openai",
            "bindkey '^[^o' zsh_llm_suggestions_openai_explain",
            "bindkey '^p' zsh_llm_suggestions_github_copilot",
            "bindkey '^[^p' zsh_llm_suggestions_github_copilot_explain"
        ]

        # Check if any key bindings exist
        bindings_exist = any(binding in config_content for binding in key_bindings)

        if bindings_exist:
            response = input(f"Remove key bindings from {config_file}? [y/N]: ")
            if response.lower() in ['y', 'yes']:
                # Remove key bindings and the comment line
                lines = config_content.split('\n')
                new_lines = []
                in_binding_block = False

                for i, line in enumerate(lines):
                    # Check if this is the start of the key bindings block
                    if line.strip() == '# zsh-llm-suggestions key bindings':
                        in_binding_block = True
                        continue

                    # Skip lines that are key bindings
                    if any(binding in line for binding in key_bindings):
                        continue

                    # If we were in a binding block and hit a non-binding line, we're done
                    if in_binding_block and line.strip() != '':
                        in_binding_block = False

                    new_lines.append(line)

                config_file.write_text('\n'.join(new_lines))
                print(f"✅ Removed key bindings from {config_file}")

    print()
    print("✅ Uninstallation complete!")
    print()
    print("To completely remove zsh-llm-suggestions:")
    print("  uv tool uninstall zsh-llm-suggestions")

def status():
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

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'install':
            install()
        elif command == 'uninstall':
            uninstall()
        elif command == 'status':
            status()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: install, uninstall, status")
            sys.exit(1)
    else:
        status()
