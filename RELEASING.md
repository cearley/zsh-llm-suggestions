# Release Process

This document outlines the steps for creating a new release of zsh-llm-suggestions.

## Prerequisites

- All changes committed to the `master` branch
- All tests passing (`uv run pytest`)
- Manual testing completed (`./test-environment.sh`)
- README.md updated with any new features or changes
- CLAUDE.md updated if development workflow changed

## Release Checklist

### 1. Prepare the Release

Before creating the release, ensure:

- [ ] Version number updated in `src/zsh_llm_suggestions/__init__.py`
- [ ] All changes committed and pushed to master
- [ ] CI/CD passing on GitHub Actions
- [ ] No critical bugs or security issues pending

### 2. Create Git Tag

Create an annotated tag for the release:

```bash
# Format: v<major>.<minor>.<patch>
git tag -a v0.1.0 -m "Release v0.1.0: Add uv tool install support"
```

**Tag Naming Convention:**
- Use semantic versioning: `v<major>.<minor>.<patch>`
- Include a brief description of the main feature/change in the tag message

### 3. Push Commit and Tag

Push both the commit and the tag to GitHub:

```bash
# Push the commit(s)
git push origin master

# Push the tag
git push origin v0.1.0
```

### 4. Create GitHub Release

You can create the release using either the GitHub web interface or the `gh` CLI.

#### Option A: Using GitHub Web Interface

1. Navigate to: `https://github.com/cearley/zsh-llm-suggestions/releases/new`
2. Select the tag you just pushed (e.g., `v0.1.0`)
3. Set the release title (e.g., `v0.1.0: uv tool install support`)
4. Add release notes (see template below)
5. Click "Publish release"

#### Option B: Using GitHub CLI

```bash
gh release create v0.1.0 \
  --title "v0.1.0: uv tool install support" \
  --notes "First release with uv tool install support.

**Installation:**
\`\`\`bash
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@v0.1.0
\`\`\`

**Features:**
- Install via \`uv tool install\` or traditional git clone
- Interactive installer with \`zsh-llm-install\` command
- Dual installation method support
- All existing functionality preserved

**Changes:**
- Restructured to proper Python package in src/
- Added entry points for CLI commands
- Updated CI to test both installation methods
- Comprehensive README updates

**Breaking Changes:**
None - backward compatible with git clone method

See README for full installation and usage instructions."
```

### 5. Verify the Release

After publishing, verify:

```bash
# Test installation from the new release
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@v0.1.0

# Verify commands are available
command -v zsh-llm-openai
command -v zsh-llm-install

# Test the installer
zsh-llm-status
```

### 6. Installation Without Version Specifier

Users installing without a version specifier will get the latest code from the master branch:

```bash
uv tool install git+https://github.com/cearley/zsh-llm-suggestions
```

To install a specific version, users can specify the tag:

```bash
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@v0.2.1
```

## Release Notes Template

Use this template for release notes:

```markdown
# v<version>: <Brief Description>

<Longer description of the release and its significance>

**Installation:**
\`\`\`bash
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@v<version>
\`\`\`

**Features:**
- Feature 1
- Feature 2
- Feature 3

**Changes:**
- Change 1
- Change 2
- Change 3

**Bug Fixes:**
- Fix 1
- Fix 2

**Breaking Changes:**
<List any breaking changes, or state "None">

**Deprecations:**
<List any deprecations, or state "None">

**Upgrade Notes:**
<Any special instructions for upgrading from previous versions>

See [README.md](README.md) for full installation and usage instructions.
```

## Semantic Versioning Guide

This project follows [Semantic Versioning](https://semver.org/):

- **Major version (X.0.0)**: Breaking changes that require user action
- **Minor version (0.X.0)**: New features, backward compatible
- **Patch version (0.0.X)**: Bug fixes, backward compatible

**Examples:**
- `v0.1.0` → `v0.2.0`: Added new commands (backward compatible)
- `v0.1.0` → `v1.0.0`: Changed command names (breaking change)
- `v0.1.0` → `v0.1.1`: Fixed bug in installer (patch)

## Hotfix Process

For urgent bug fixes that need immediate release:

1. Create a hotfix branch from the tag:
   ```bash
   git checkout -b hotfix/v0.1.1 v0.1.0
   ```

2. Make the fix and commit:
   ```bash
   # Make your changes
   git commit -m "Fix critical bug in installer"
   ```

3. Merge back to master:
   ```bash
   git checkout master
   git merge hotfix/v0.1.1
   ```

4. Follow steps 2-6 above to create the patch release

5. Delete the hotfix branch:
   ```bash
   git branch -d hotfix/v0.1.1
   ```

## Post-Release Tasks

After publishing a release:

- [ ] Announce the release (if applicable)
- [ ] Update any related documentation or wikis
- [ ] Close related issues/PRs
- [ ] Update project boards or milestones

## Troubleshooting

### Tag already exists

If you need to recreate a tag:

```bash
# Delete local tag
git tag -d v0.1.0

# Delete remote tag
git push origin :refs/tags/v0.1.0

# Create new tag
git tag -a v0.1.0 -m "Release v0.1.0: Updated description"

# Push new tag
git push origin v0.1.0
```

**⚠️ Warning:** Only do this if the release hasn't been published yet or if it's absolutely necessary. Changing published releases can break existing installations.

### Release published with wrong notes

You can edit release notes after publication:

```bash
# Using GitHub CLI
gh release edit v0.1.0 --notes "Updated release notes..."

# Or edit via web interface
# Navigate to: https://github.com/cearley/zsh-llm-suggestions/releases
```

## Related Documentation

- [README.md](README.md) - User-facing installation and usage
- [CLAUDE.md](CLAUDE.md) - AI-assisted development guidelines
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Security considerations
