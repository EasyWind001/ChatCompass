# README Synchronization Requirement

## 🌐 Bilingual README Maintenance

ChatCompass maintains two README files:
- **README.md** - Chinese version (primary)
- **README_EN.md** - English version

## ⚠️ Critical Rule: Always Keep Both READMEs in Sync

### When to Update Both READMEs

**You MUST update both README.md and README_EN.md in the following situations:**

1. **Before each version release/push** ✅
   - All version numbers must be consistent
   - All feature descriptions must be synchronized
   - All test statistics must match

2. **When adding new features** ✅
   - Feature descriptions
   - Usage examples
   - Configuration instructions

3. **When updating project information** ✅
   - Version numbers
   - Test statistics (test count, pass rate, coverage)
   - Dependencies
   - Installation steps

4. **When modifying documentation links** ✅
   - Internal links
   - External links
   - Anchor links

5. **When updating examples or code snippets** ✅
   - Command examples
   - Configuration examples
   - Code samples

### Synchronization Checklist

Before committing changes, verify:

- [ ] Both README.md and README_EN.md have been updated
- [ ] Version numbers are consistent (badges and content)
- [ ] Test statistics match (test count, pass rate, coverage)
- [ ] Feature lists are synchronized
- [ ] All links are valid in both files
- [ ] Examples and code snippets are consistent
- [ ] Formatting (tables, lists, headings) is aligned

### Version Information to Sync

Always keep these consistent across both READMEs:

1. **Version Badge**: `[![Version](https://img.shields.io/badge/Version-vX.X.X-orange.svg)]`
2. **Test Statistics Badge**: `[![Tests](https://img.shields.io/badge/Tests-XX%20Passed-brightgreen.svg)]`
3. **Latest Features Section**: Version numbers and feature descriptions
4. **Changelog Section**: Version dates and changes
5. **Test Coverage Section**: Test counts, pass rates, coverage percentages
6. **Quick Start Examples**: Version numbers in code examples

### Common Mistakes to Avoid

❌ **DO NOT:**
- Update only README.md and forget README_EN.md
- Update only README_EN.md and forget README.md
- Have different version numbers in the two files
- Have different test statistics
- Have different feature lists
- Have broken links in one file but working links in the other

✅ **DO:**
- Always update both files together in the same commit
- Verify consistency before committing
- Test all links in both files
- Keep formatting and structure aligned
- Add translation notes if direct translation is not possible

### Workflow

1. **Make changes to README.md** (Chinese version)
2. **Immediately translate and update README_EN.md**
3. **Verify both files are synchronized**
4. **Test all links in both files**
5. **Commit both files together**

### Example Commit Message

```
docs: update READMEs for v1.2.6 release

- Update version badges to v1.2.6
- Update test statistics (66 tests, 98.5% pass rate)
- Add Delete feature description
- Sync all links and examples
- Both README.md and README_EN.md updated
```

## 🚨 Pre-Push Checklist

Before pushing to GitHub:

```bash
# 1. Check both files exist and are up to date
git status README.md README_EN.md

# 2. Verify version numbers match
grep -E "Version-v[0-9]+\.[0-9]+\.[0-9]+" README.md README_EN.md

# 3. Verify test statistics match
grep -E "Tests-[0-9]+" README.md README_EN.md

# 4. Check both files are staged
git diff --cached README.md
git diff --cached README_EN.md
```

## 📝 Translation Guidelines

When translating from Chinese (README.md) to English (README_EN.md):

1. **Preserve Technical Terms**: Keep command names, file paths, code as-is
2. **Adapt Cultural References**: Translate idioms and cultural references appropriately
3. **Maintain Structure**: Keep the same section order and hierarchy
4. **Keep Links Identical**: Use the same file paths for internal links
5. **Match Formatting**: Preserve tables, lists, and code blocks formatting

## 🔍 Validation Tools

Use these commands to help verify synchronization:

```bash
# Check if both files exist
ls -la README.md README_EN.md

# Compare line counts (should be similar)
wc -l README.md README_EN.md

# Search for version numbers
grep "v1\.[0-9]\.[0-9]" README.md README_EN.md

# Search for test counts
grep -i "test" README.md README_EN.md | grep -E "[0-9]+"
```

## 🎯 Enforcement

This rule is **ALWAYS ACTIVE** and **MANDATORY**.

- AI assistants MUST check and update both READMEs
- Code reviewers MUST verify synchronization
- Pre-commit hooks SHOULD validate consistency
- CI/CD pipelines SHOULD enforce this rule

**Failure to maintain synchronization is considered a blocking issue.**
