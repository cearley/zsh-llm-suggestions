# Release Process

This document outlines the steps for creating a new release of zsh-llm-suggestions.

## 🎯 Quick Release (Recommended)

The easiest way to create a release is to use our **automated workflow**:

### Automatic Release (Primary Method)

1. **Update version** in `src/zsh_llm_suggestions/__init__.py`:
   ```python
   __version__ = "0.2.3"  # Change to your new version
   ```

2. **Commit and push** to master:
   ```bash
   git add src/zsh_llm_suggestions/__init__.py
   git commit -m "Bump version to 0.2.3"
   git push origin master
   ```

3. **Done!** 🎉
   - CI runs automatically
   - If CI passes: GitHub Actions creates tag and release
   - If CI fails: Fix the issue, push again (no need to bump version again!)
   - Release notes are auto-generated from commits

**That's it!** No manual tagging or release creation needed.

### What if CI fails?

No problem! The workflow is smart:

```bash
# Scenario: CI fails after version bump
git add src/zsh_llm_suggestions/__init__.py some_code.py
git commit -m "Bump version to 0.2.3 + new feature"
git push
→ CI runs... FAILS ❌
→ No release created (good!)

# Fix the code, push again (version already bumped)
git add some_code.py
git commit -m "Fix bug in new feature"
git push
→ CI runs... PASSES ✅
→ Release v0.2.3 created! 🎉
```

The workflow compares the version in `__init__.py` with the latest tag, not just the files changed in the current commit.

### Manual Release (Backup Method)

If you need more control or the automatic workflow fails:

1. Go to **Actions** tab on GitHub
2. Select **Manual Release** workflow
3. Click **Run workflow**
4. Enter the version number (e.g., `0.2.3`)
5. Optionally check "Update __init__.py" if you haven't updated it yet
6. Click **Run workflow**

The workflow will create the tag and GitHub release for you.

---

## Prerequisites

Before any release:

- [ ] All changes committed to the `master` branch
- [ ] All tests passing (`uv run pytest`)
- [ ] Manual testing completed (`./test-environment.sh`)
- [ ] README.md updated with any new features or changes
- [ ] CLAUDE.md updated if development workflow changed
- [ ] CI/CD passing on GitHub Actions
- [ ] No critical bugs or security issues pending

## Version Source of Truth

**Version is defined in ONE place only:**
- `src/zsh_llm_suggestions/__init__.py`: `__version__ = "X.Y.Z"`

The `pyproject.toml` reads dynamically from `__init__.py`:
```toml
[project]
dynamic = ["version"]  # Don't hardcode version here!

[tool.hatch.version]
path = "src/zsh_llm_suggestions/__init__.py"
```

**You only need to update `__init__.py`** - everything else (pyproject.toml, git tags, releases) is automatic!

**Do NOT edit `pyproject.toml`** to change the version - it won't work!

## Automated Workflows

### Auto-Release Workflow

**File**: `.github/workflows/auto-release.yml`

**Triggers**: After CI workflow completes successfully on master

**Safety**: Only releases when:
- ✅ CI workflow passes all tests
- ✅ Version in `__init__.py` differs from latest tag

**What it does**:
1. Waits for CI to complete successfully
2. Compares current version with latest tag
3. If version changed: creates git tag (e.g., `v0.2.3`)
4. Creates GitHub release with auto-generated notes
5. Includes installation instructions in release

**Smart behavior**: If CI fails on first push, just fix the code and push again - the release will still trigger!

**When to use**: For most releases - just bump the version and push!

**Important**: If CI fails, the release workflow will not run. Fix CI issues before releasing.

### Manual Release Workflow

**File**: `.github/workflows/manual-release.yml`

**Triggers**: Manual workflow dispatch

**Inputs**:
- `version`: Version to release (without v prefix)
- `update_version_file`: Optionally update `__init__.py`

**What it does**:
1. Validates version format
2. Optionally updates `__init__.py` and commits
3. Creates annotated git tag
4. Creates GitHub release with auto-generated notes

**When to use**:
- Hotfixes that need immediate release
- When automatic workflow fails
- When you need more control over the process

## Traditional Manual Release (Legacy)

If you prefer the old manual process or need to release without GitHub Actions:

### 1. Update Version

Update version in `src/zsh_llm_suggestions/__init__.py`:
```python
__version__ = "0.2.3"
```

### 2. Commit Changes

```bash
git add src/zsh_llm_suggestions/__init__.py
git commit -m "Bump version to 0.2.3"
git push origin master
```

### 3. Create Git Tag

```bash
# Format: v<major>.<minor>.<patch>
git tag -a v0.2.3 -m "Release v0.2.3: Brief description"
git push origin v0.2.3
```

**Tag Naming Convention:**
- Use semantic versioning: `v<major>.<minor>.<patch>`
- Include a brief description in the tag message

### 4. Create GitHub Release

Using GitHub CLI:

```bash
gh release create v0.2.3 \
  --title "v0.2.3: Brief description" \
  --generate-notes \
  --latest
```

Or use the GitHub web interface at:
`https://github.com/cearley/zsh-llm-suggestions/releases/new`

---

## Verifying a Release

After any release (automatic or manual), verify it works:

```bash
# Test installation from the new release
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@v0.2.3

# Verify commands are available
command -v zsh-llm-openai
command -v zsh-llm-install

# Test the installer
zsh-llm-status
```

## Installation Behavior

Users installing without a version specifier get the latest code from master:

```bash
uv tool install git+https://github.com/cearley/zsh-llm-suggestions
```

To install a specific version, specify the tag:

```bash
uv tool install git+https://github.com/cearley/zsh-llm-suggestions@v0.2.3
```

---

## Semantic Versioning Guide

This project follows [Semantic Versioning](https://semver.org/):

- **Major version (X.0.0)**: Breaking changes that require user action
  - Example: `v0.9.0` → `v1.0.0` - Changed command names or removed features
- **Minor version (0.X.0)**: New features, backward compatible
  - Example: `v0.1.0` → `v0.2.0` - Added new commands or features
- **Patch version (0.0.X)**: Bug fixes, backward compatible
  - Example: `v0.2.0` → `v0.2.1` - Fixed bug in installer

**Version Bumping Guide:**
- Bug fixes only → Bump patch (0.2.2 → 0.2.3)
- New features + bug fixes → Bump minor (0.2.3 → 0.3.0)
- Breaking changes → Bump major (0.9.0 → 1.0.0)

## Hotfix Process

For urgent bug fixes that need immediate release:

**Quick Hotfix (Recommended):**
1. Fix the bug on master branch
2. Bump version in `__init__.py` to patch version (e.g., 0.2.2 → 0.2.3)
3. Commit and push
4. Auto-release workflow creates the release automatically

**Or use Manual Release workflow:**
1. Fix the bug on master branch
2. Go to Actions → Manual Release
3. Enter the patch version number
4. Run workflow

**Traditional Hotfix Branch (if needed):**
1. Create hotfix branch from tag: `git checkout -b hotfix/v0.2.3 v0.2.2`
2. Make the fix and commit
3. Merge to master: `git checkout master && git merge hotfix/v0.2.3`
4. Use automatic or manual release workflow
5. Delete hotfix branch: `git branch -d hotfix/v0.2.3`

## Post-Release Tasks

After publishing a release:

- [ ] Announce the release (if applicable)
- [ ] Update any related documentation or wikis
- [ ] Close related issues/PRs
- [ ] Update project boards or milestones

## Troubleshooting

### Auto-release workflow didn't trigger

**Symptoms**: Pushed version bump but no release was created

**Common causes**:
1. **CI workflow failed** - Auto-release only runs after CI succeeds
   - Check the CI workflow status first
   - Fix any failing tests, then push the fix
   - Release will trigger once CI passes
2. **Version already released** - The version in `__init__.py` matches the latest tag
   - Check: https://github.com/cearley/zsh-llm-suggestions/releases
   - If you want a new release, bump the version number
3. **Not on master branch** - Workflow only runs on master
   - Ensure you pushed to `master` branch

**Solutions**:
1. Check **Actions** tab for CI workflow status
2. If CI passed, check Auto Release workflow status
3. Verify the version in `__init__.py` differs from the latest tag
4. Use **Manual Release** workflow as backup if needed

### Tag already exists

**Symptoms**: Workflow fails with "tag already exists" error

**Solutions**:

Option 1 - Use existing tag (recommended):
- The release already exists, no action needed
- Check: https://github.com/cearley/zsh-llm-suggestions/releases

Option 2 - Delete and recreate tag (⚠️ use with caution):
```bash
# Delete local tag
git tag -d v0.2.3

# Delete remote tag
git push origin :refs/tags/v0.2.3

# Delete GitHub release (if exists)
gh release delete v0.2.3 --yes

# Now push version change again to trigger auto-release
```

**⚠️ Warning:** Only delete published tags/releases if absolutely necessary. It can break existing installations.

### Version mismatch

**Symptoms**: Manual workflow warns about version mismatch

**Solution**: Enable "Update __init__.py" checkbox in manual workflow, or manually update `__init__.py` before running the workflow.

### Workflow permissions error

**Symptoms**: "Resource not accessible by integration" error

**Solution**: Verify workflow has `contents: write` permission (already configured in workflow files).

### Release notes wrong or incomplete

You can edit release notes after publication:

```bash
# Using GitHub CLI
gh release edit v0.2.3 --notes "Updated release notes..."

# Or edit via web interface at:
# https://github.com/cearley/zsh-llm-suggestions/releases
```

### Need to re-run release workflow

If the workflow partially failed:

1. Delete the tag (see "Tag already exists" above)
2. Delete the partial release: `gh release delete v0.2.3 --yes`
3. Re-push the commit or run manual workflow again

## Related Documentation

- [README.md](README.md) - User-facing installation and usage
- [CLAUDE.md](CLAUDE.md) - AI-assisted development guidelines
- [SECURITY_AUDIT.md](SECURITY_AUDIT.md) - Security considerations
