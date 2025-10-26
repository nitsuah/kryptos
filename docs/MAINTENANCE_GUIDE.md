# Maintenance Guide

**Purpose:** Keep the kryptos codebase clean, relevant, well-tested, and maintainable.

**Audience:** Human developers and AI agents working on this project.

**Last Updated:** October 26, 2025

---

## Table of Contents

1. [Philosophy](#philosophy) 2. [Maintenance Cadence](#maintenance-cadence) 3. [Documentation
Management](#documentation-management) 4. [Scripts Management](#scripts-management) 5. [Tests Management](#tests-
management) 6. [Code Review Checklist](#code-review-checklist) 7. [Definition of Done](#definition-of-done) 8. [Audit
Procedures](#audit-procedures) 9. [AI Agent Prompts](#ai-agent-prompts)

---

## Philosophy

### Core Principles

1. **Tests are Sacred**
   - Tests preserve knowledge about what SHOULD work
   - Understand deeply before modifying or deleting
   - When in doubt, keep the test (disk space is cheap, regressions are expensive)
   - If a test seems bad, improve it rather than delete it

2. **Documentation Decays**
   - Outdated docs are worse than no docs
   - Prune regularly (quarterly at minimum)
   - Consolidate aggressively (one good doc > three mediocre docs)
   - Mark historical context as such

3. **Scripts are Temporary**
   - Working scripts should become tests
   - Reusable logic should become src/kryptos APIs
   - One-off debugging scripts should be deleted
   - Development tools should be documented and kept

4. **Coverage Matters (But Isn't Everything)**
   - 100% coverage ≠ good tests
   - Critical paths need >90% coverage
   - Test behavior, not implementation
   - Integration tests catch more bugs than unit tests

5. **Knowledge Preservation**
   - Keep context (why decisions were made)
   - Delete clutter (outdated code, obsolete docs)
   - Document assumptions (what we believe to be true)
   - Record learnings (what we discovered)

6. **Code Cleanliness Over Cleverness**
   - Docs explain WHAT and WHY (architecture, integrations, philosophy)
   - Code shows HOW (implementation details)
   - Type hints ARE documentation (parameters, returns)
   - No redundancy: code doesn't repeat what docs explain
   - Minimal logging: errors/warnings only, not progress narratives
   - Surgical cleanup: manual file-by-file preserves functionality

---

## Automation & Pre-Commit Hooks

### Philosophy on Automation

**Automate safely:**
- Formatting (black, isort) - safe, deterministic
- Linting (ruff, pylint) - catches bugs, enforces style
- Type checking (mypy) - catches type errors
- Simple cleanups (trailing whitespace, unused imports)

**Don't automate:**
- Docstring removal - breaks code structure
- Comment removal - loses context
- Log statement removal - manual judgment needed
- Complex refactoring - requires understanding

### Lessons Learned: Code Cleanup

**What DOESN'T work:**
- ❌ `astor` - reformats code, renames classes, breaks imports
- ❌ `docformatter` - argument errors, unreliable
- ❌ PowerShell regex on Python - breaks indentation
- ❌ AST manipulation without source preservation
- ❌ Batch removal of comments/logs without context

**What DOES work:**
- ✅ Manual file-by-file cleanup (surgical, preserves functionality)
- ✅ Black/isort for formatting only
- ✅ Ruff for linting and safe auto-fixes
- ✅ grep/semantic search to find patterns, manual review to remove
- ✅ Test after each file to ensure nothing breaks

**Cleanup Workflow:** 1. Search for patterns (verbose docstrings, log.info calls, etc.) 2. Review each file individually
3. Make targeted edits 4. Run imports/tests to verify 5. Commit per-file or per-module 6. Document what was removed and
why

### Pre-Commit Hook Setup

Recommended `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.14
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--ignore-missing-imports]
```

Install: `pip install pre-commit && pre-commit install`

Run manually: `pre-commit run --all-files`

### What Pre-Commit Should NOT Do

- Don't auto-remove docstrings (needs manual review)
- Don't auto-remove comments (context matters)
- Don't auto-remove log statements (errors should stay)
- Don't run slow tests (use CI for full test suite)
- Don't modify line counts aggressively (breaks git blame)

---

## Maintenance Cadence

### Weekly
- [ ] Review new tests for quality (are they testing behavior or implementation?)
- [ ] Check for new scripts (should they be integrated or deleted?)
- [ ] Update TODO.md with current priorities

### Monthly
- [ ] Quick audit of docs/ (any new files? outdated info?)
- [ ] Quick audit of scripts/ (any scripts ready for integration?)
- [ ] Review test coverage trends (improving or declining?)
- [ ] Check for stale branches

### Quarterly (Full Audit)
- [ ] Documentation audit (see [Documentation Management](#documentation-management))
- [ ] Scripts audit (see [Scripts Management](#scripts-management))
- [ ] Tests audit (see [Tests Management](#tests-management))
- [ ] Coverage analysis (identify gaps in critical paths)
- [ ] Update technical debt plan
- [ ] Review and update this maintenance guide

---

## Documentation Management

### When to Create New Documentation

**Do create docs for:**
- Architecture decisions (why, not just what)
- API reference (how to use core functionality)
- Non-obvious algorithms (mathematical explanations)
- Historical context (why we tried X and chose Y)
- Setup/installation procedures
- Contributing guidelines

**Don't create docs for:**
- Obvious code (the code itself is documentation)
- Temporary solutions (use code comments instead)
- Personal notes (keep in your own notes, not the repo)
- Duplicate information (consolidate existing docs instead)

### When to Update vs Consolidate

**Update existing doc when:**
- Small corrections or additions
- Fixing outdated information
- Adding missing details
- Clarifying unclear sections

**Consolidate multiple docs when:**
- Multiple docs cover same topic
- Docs have significant overlap
- Navigating between docs is confusing
- Total pages > 2x the information content

### When to Delete Documentation

**Delete docs that are:**
- Completely outdated (describes code that no longer exists)
- Superseded by better documentation
- No longer relevant (describes abandoned approaches)
- Empty or stub files never completed

**Keep docs that:**
- Explain historical decisions (mark as "Historical Context")
- Document dead ends (so we don't repeat mistakes)
- Preserve unique insights (even if code changed)

### Documentation Audit Checklist

For each document in `docs/`:

1. **Relevance Check**
   - [ ] Does it describe current code/architecture?
   - [ ] Is the information still accurate?
   - [ ] Would a new contributor find this helpful?

2. **Consolidation Check**
   - [ ] Does another doc cover this topic better?
   - [ ] Could this be merged with related docs?
   - [ ] Is there significant duplication?

3. **Quality Check**
   - [ ] Is it well-organized?
   - [ ] Are examples up-to-date?
   - [ ] Is it discoverable (linked from index)?

4. **Action Decision**
   - [ ] Keep as-is
   - [ ] Update (list what needs updating)
   - [ ] Consolidate with: [doc name]
   - [ ] Mark as historical
   - [ ] Delete (reason: ___)

### Documentation Structure

```
docs/
├── DOCUMENTATION_INDEX.md      # Map of all docs with descriptions
├── MAINTENANCE_GUIDE.md        # This file
├── CONTRIBUTING.md             # How to contribute (links to MAINTENANCE_GUIDE)
├── TECHDEBT_PLAN.md           # Current technical debt backlog
├── architecture/               # System design docs
├── api/                        # API reference
├── algorithms/                 # Mathematical/cryptographic explanations
├── historical/                 # Context about past decisions
├── audits/                     # Audit results and findings
│   └── [TOPIC]_AUDIT_YYYY-MM-DD.md
└── guides/                     # How-to guides
```

---

## Scripts Management

### Scripts Directory Philosophy

**`scripts/` should contain:**
- Active development tools (used regularly)
- One-off analysis scripts (clearly marked as such)
- Documented utilities (with README explaining purpose)

**`scripts/` should NOT contain:**
- Working test code (belongs in `tests/`)
- Reusable functionality (belongs in `src/kryptos/`)
- Debugging code from weeks ago (delete it)
- Broken or incomplete scripts (fix or delete)

### Script Lifecycle

```
1. Create script for development/debugging
   ↓
2. Script proves useful
   ├─→ Extract reusable logic → src/kryptos/ (as API)
   ├─→ Convert to test → tests/
   └─→ Keep as dev tool → document in scripts/README.md
   ↓
3. Delete script once functionality is integrated
```

### Integrating Scripts into Core

When a script has reusable functionality:

1. **Identify the reusable parts**
   - Pure functions (deterministic, no side effects)
   - Algorithms or calculations
   - Data processing utilities

2. **Design the API**
   - Look at similar code in `src/kryptos/`
   - Follow existing patterns (logging, config, error handling)
   - Make it generic (not specific to your use case)

3. **Add to appropriate module**
   - Cipher code → `src/kryptos/k4/`
   - Utilities → `src/kryptos/utils/`
   - Analysis → `src/kryptos/k4/analysis/`

4. **Add proper infrastructure**
   - Type hints
   - Docstrings (Google style)
   - Error handling
   - Logging (use existing logger)
   - Configuration (if needed)

5. **Write tests**
   - Unit tests for the API
   - Integration tests if needed
   - Edge cases

6. **Delete the script**
   - Once functionality is in tests AND core code
   - Document the deletion (in commit message)

### Converting Scripts to Tests

When a script validates something:

1. **Understand what it's testing**
   - What behavior is being validated?
   - What are the success criteria?
   - What are the edge cases?

2. **Design the test**
   - Use pytest fixtures for setup
   - Make assertions explicit
   - Add parametrize for variations
   - Include docstring explaining what and why

3. **Make it reproducible**
   - Remove randomness (or seed it)
   - Remove file I/O if possible (use in-memory)
   - Remove dependencies on external state

4. **Add to test suite**
   - Choose appropriate test file
   - Follow naming conventions
   - Add markers if needed (@pytest.mark.slow, etc.)

5. **Verify and delete**
   - Run new test to confirm it works
   - Run old script to confirm same behavior
   - Delete script once test is verified

### Scripts Audit Checklist

For each script in `scripts/`:

1. **Functionality Check**
   - [ ] Does it still work?
   - [ ] What does it do? (can you explain in 1 sentence?)
   - [ ] When was it last used?

2. **Integration Check**
   - [ ] Should this be a test? (tests validating behavior)
   - [ ] Should this be in src/? (reusable functionality)
   - [ ] Should this be kept as dev tool? (active use)

3. **Quality Check**
   - [ ] Is it documented? (comments, docstrings, or README)
   - [ ] Does it follow project conventions?
   - [ ] Are there hard-coded paths/values?

4. **Action Decision**
   - [ ] Convert to test in `tests/`
   - [ ] Extract API to `src/kryptos/`
   - [ ] Keep and document (add to scripts/README.md)
   - [ ] Delete (reason: ___)

---

## Tests Management

### Test Quality Principles

**Good tests:**
- Test behavior, not implementation
- Have clear, descriptive names
- Test one thing per test function
- Are fast (unless marked @slow)
- Are deterministic (same input → same output)
- Have clear assertions with messages
- Are independent (don't rely on other tests)

**Bad tests:**
- Test implementation details (breaks when refactoring)
- Have vague names (test_thing_works)
- Test multiple unrelated things
- Take forever to run
- Are flaky (pass/fail randomly)
- Have unclear assertions
- Require tests to run in specific order

### Test Categories

1. **Unit Tests** - Test individual functions/classes
   - Fast (<1ms per test)
   - No I/O, no network, no file system
   - Mock external dependencies
   - Goal: 80%+ coverage of critical logic

2. **Integration Tests** - Test components working together
   - Slower (1-100ms per test)
   - May use file system or test databases
   - Minimal mocking
   - Goal: Cover critical user paths

3. **End-to-End Tests** - Test full workflows
   - Slowest (>100ms per test)
   - Use real components
   - No mocking
   - Goal: Validate key scenarios work

4. **Property-Based Tests** - Test invariants with generated data
   - Use hypothesis or similar
   - Find edge cases automatically
   - Goal: Validate algorithmic properties

5. **Regression Tests** - Prevent specific bugs from returning
   - Tests for bugs we've fixed
   - Should include bug description in docstring
   - Goal: Never repeat the same bug

### When to Add Tests

**Always add tests for:**
- New features (behavior should be validated)
- Bug fixes (prevent regression)
- Critical paths (encryption, key recovery, scoring)
- Public APIs (contract with users)
- Complex algorithms (correctness is non-obvious)

**Consider tests for:**
- Refactored code (if coverage dropped)
- Edge cases (empty input, huge input, invalid input)
- Performance regressions (if critical path)

**Don't add tests for:**
- Trivial getters/setters
- Framework code (if well-tested upstream)
- Temporary debugging code

### When to Modify Tests

**Update tests when:**
- Behavior intentionally changed
- Test is flaky (make it deterministic)
- Test is unclear (improve naming/assertions)
- Test is slow (optimize or mark @slow)

**Replace tests when:**
- Current test is testing wrong thing
- Current test is too coupled to implementation
- Better testing approach discovered

**Delete tests only when:**
- Functionality no longer exists
- Test is completely redundant (another test covers it better)
- Test is testing framework, not our code
- **AND you're certain it won't catch regressions**

### Test Deletion Protocol

**BEFORE deleting any test:**

1. **Understand what it tests**
   - Read the test code carefully
   - Run the test (does it pass?)
   - Break the code it tests (does it fail appropriately?)

2. **Search for redundancy**
   - Are there other tests covering this?
   - Is the behavior tested elsewhere?
   - Could this catch a regression others miss?

3. **Check history**
   - When was it added? (git log)
   - Why was it added? (commit message)
   - Was it fixing a specific bug?

4. **Validate with coverage**
   - Run coverage with this test
   - Run coverage without this test
   - What lines are no longer covered?

5. **Document decision**
   - Write clear commit message explaining why
   - If replacing, mention replacement test
   - If deleting, explain why it's redundant

**RED FLAGS (don't delete):**
- Test was added to fix a specific bug
- Test is the only one testing a module
- Test covers edge cases
- Test validates critical security/correctness
- You're not sure what it's testing (figure it out first)

### Tests Audit Checklist

For each test file in `tests/`:

1. **Relevance Check**
   - [ ] Does it test current functionality?
   - [ ] Is the tested code still in the codebase?
   - [ ] Does it pass consistently?

2. **Effectiveness Check**
   - [ ] Does it catch real bugs? (try breaking the code)
   - [ ] Is it testing behavior or implementation?
   - [ ] Are assertions clear and meaningful?

3. **Quality Check**
   - [ ] Is the test name descriptive?
   - [ ] Is it fast enough? (unit tests should be <10ms)
   - [ ] Is it deterministic?
   - [ ] Is it well-organized?

4. **Coverage Check**
   - [ ] What lines does it cover?
   - [ ] Are there gaps in critical paths?
   - [ ] Is there redundant coverage?

5. **Action Decision**
   - [ ] Keep as-is
   - [ ] Improve (list improvements)
   - [ ] Replace with better test
   - [ ] Mark as slow (@pytest.mark.slow)
   - [ ] Delete (reason: ___, verified redundant)

---

## Code Review Checklist

### For New Features

- [ ] Tests added for new functionality
- [ ] Documentation updated (if API changed)
- [ ] Type hints added
- [ ] Docstrings written (Google style)
- [ ] Error handling in place
- [ ] Logging added (for debugging)
- [ ] No hard-coded values (use config)
- [ ] No temporary debugging code
- [ ] Follows existing code patterns

### For Bug Fixes

- [ ] Test added to prevent regression
- [ ] Root cause understood (not just symptom fixed)
- [ ] Similar bugs searched for (fix all instances)
- [ ] Commit message explains the bug
- [ ] Related documentation updated

### For Refactoring

- [ ] Tests still pass (behavior unchanged)
- [ ] Coverage didn't decrease
- [ ] Performance didn't degrade significantly
- [ ] API contracts preserved (backward compatible)
- [ ] Commit message explains why (not just what)

### For Documentation

- [ ] Information is accurate
- [ ] Examples work (test them)
- [ ] Links aren't broken
- [ ] Follows documentation structure
- [ ] Added to documentation index

---

## Definition of Done

A task is "done" when:

### For New Features
1. Code is written and reviewed 2. Tests are written and passing (>80% coverage for new code) 3. Documentation is
updated (API docs, guides, etc.) 4. Integration tests pass 5. No new linting errors 6. Committed with clear message 7.
Deployed/merged to appropriate branch

### For Bug Fixes
1. Bug is reproduced 2. Root cause identified 3. Fix implemented 4. Regression test added 5. All tests pass 6. Commit
message explains bug and fix 7. Related issues closed

### For Refactoring
1. Tests pass (behavior unchanged) 2. Coverage maintained or improved 3. Performance maintained or improved 4. Code is
clearer/simpler 5. Documentation updated if needed 6. Reviewed by someone who knows the code

### For Documentation
1. Information verified as accurate 2. Examples tested 3. Links checked 4. Added to index/navigation 5. Reviewed for
clarity 6. Committed with descriptive message

---

## Audit Procedures

### Quarterly Full Audit

Follow this process every 3 months (or after major changes):

#### Week 1: Data Collection

**Day 1-2: Documentation Audit**
- Review every file in `docs/`
- Create `docs/audits/DOCS_AUDIT_YYYY-MM-DD.md`
- Categorize docs: Keep / Update / Consolidate / Delete
- Update or create `docs/DOCUMENTATION_INDEX.md`

**Day 3-4: Scripts Audit**
- Review every file in `scripts/`
- Create `docs/audits/SCRIPTS_AUDIT_YYYY-MM-DD.md`
- Categorize scripts: Test / Integrate / Keep / Delete
- Update or create `scripts/README.md`

**Day 5: Tests Overview**
- Run full test suite with coverage
- Generate coverage report: `pytest --cov=src/kryptos --cov-report=html`
- List all test files and counts
- Identify patterns (what's well-tested, what's not)

#### Week 2: Deep Analysis

**Day 1-3: Tests Deep Dive**
- Review test files systematically
- Create `docs/audits/TESTS_AUDIT_YYYY-MM-DD.md`
- For each test: assess relevance, effectiveness, quality
- Identify: keep / improve / replace / delete
- **Important:** Don't delete tests during review, just mark them

**Day 4: Coverage Analysis**
- Identify critical paths with <80% coverage
- Identify trivial code with >95% coverage (maybe over-tested?)
- Create `docs/audits/COVERAGE_ANALYSIS_YYYY-MM-DD.md`
- Prioritize coverage improvements by risk

**Day 5: Synthesis**
- Create/update `docs/TECHDEBT_PLAN.md`
- Categorize findings: Critical / High / Medium / Low
- Estimate effort for each item
- Create prioritized backlog

#### Week 3: Execution

**Prioritize:** 1. Delete clearly obsolete docs/scripts 2. Consolidate redundant documentation 3. Convert working
scripts to tests 4. Integrate reusable script code to src/ 5. Add high-priority missing tests 6. Improve low-quality
tests 7. Delete redundant tests (carefully!)

#### Week 4: Documentation

**Deliverables:**
- All audit documents in `docs/audits/`
- Updated `TECHDEBT_PLAN.md`
- Updated `DOCUMENTATION_INDEX.md`
- Updated `scripts/README.md`
- Summary report in project communication channel

---

## AI Agent Prompts

### For Documentation Audit

```
Review the documentation in docs/ following the Maintenance Guide audit procedures.

For each markdown file:
1. Check if it describes current code/architecture
2. Look for outdated information
3. Check for duplicates or consolidation opportunities
4. Assess if it would help a new contributor

Create docs/audits/DOCS_AUDIT_YYYY-MM-DD.md with findings:
- Keep (reason)
- Update (what needs updating)
- Consolidate (with what other doc)
- Delete (reason)

Then create/update docs/DOCUMENTATION_INDEX.md as an organized map of all docs.
```

### For Scripts Audit

```
Review all scripts in scripts/ following the Maintenance Guide audit procedures.

For each script:
1. Determine what it does (1-sentence description)
2. Check if it still works (try running it if safe)
3. Decide: Convert to test / Extract to src/ / Keep as tool / Delete

Create docs/audits/SCRIPTS_AUDIT_YYYY-MM-DD.md with findings.

For scripts marked "Convert to test":
- List which test file it should go in
- Note what behavior it's validating

For scripts marked "Extract to src/":
- List which module it should go in
- Note what API should be exposed

Create/update scripts/README.md explaining remaining scripts.
```

### For Tests Audit

```
Review all tests in tests/ following the Maintenance Guide audit procedures.

THIS IS THE MOST CRITICAL AUDIT - BE THOROUGH.

For each test file:
1. What functionality does it test?
2. Does that functionality still exist?
3. Is it testing behavior or implementation?
4. Are there redundant tests covering the same thing?
5. Are there gaps in test coverage?

Create docs/audits/TESTS_AUDIT_YYYY-MM-DD.md with findings:
- Keep (passes quality checks)
- Improve (list specific improvements)
- Replace (with what better test)
- Delete (ONLY if redundant and you're certain)

CRITICAL: For any test marked "Delete", you must:
- Explain what it tests
- Show which other test covers it
- Verify with coverage that deleting won't lose coverage
- Include all this justification in the audit doc

DO NOT delete tests during the audit. Only mark them for deletion.
```

### For Coverage Analysis

```
Analyze test coverage following the Maintenance Guide procedures.

1. Run: pytest --cov=src/kryptos --cov-report=html --cov-report=term
2. Review the HTML report in htmlcov/index.html
3. Identify modules/files with <80% coverage
4. Focus on critical paths: encryption, key recovery, scoring algorithms

Create docs/audits/COVERAGE_ANALYSIS_YYYY-MM-DD.md with:
- Current overall coverage percentage
- Critical paths with low coverage (prioritize fixing these)
- Non-critical paths with low coverage (lower priority)
- Over-tested areas (>95% coverage of trivial code)
- Recommended new tests to add (with priority)

Prioritize by risk: crypto logic > algorithms > infrastructure > utilities
```

### For Technical Debt Planning

```
Synthesize all audit findings into a technical debt plan.

Review:
- docs/audits/DOCS_AUDIT_YYYY-MM-DD.md
- docs/audits/SCRIPTS_AUDIT_YYYY-MM-DD.md
- docs/audits/TESTS_AUDIT_YYYY-MM-DD.md
- docs/audits/COVERAGE_ANALYSIS_YYYY-MM-DD.md

Create/update docs/TECHDEBT_PLAN.md with:
- Critical items (must fix: security, correctness)
- High priority (should fix soon: coverage gaps, clarity)
- Medium priority (nice to have: refactoring, optimization)
- Low priority (cosmetic: style, naming)

For each item:
- Description
- Category (docs/scripts/tests/code)
- Priority (critical/high/medium/low)
- Effort estimate (hours)
- Risk if not fixed

Create prioritized backlog sorted by: priority, then risk, then effort.
```

---

## Maintenance Tips

### For AI Agents

1. **Always read the Maintenance Guide first** when asked to audit or clean up 2. **Follow the checklists** - they
ensure consistent quality 3. **Document your reasoning** - explain why decisions were made 4. **Be conservative with
deletions** - when in doubt, keep it 5. **Ask questions** - if unsure about a test/doc/script, ask the human

### For Humans

1. **Trust the process** - the checklists work 2. **Review AI decisions** - especially test deletions 3. **Update this
guide** - as you learn better patterns 4. **Run audits regularly** - don't let debt accumulate 5. **Teach the AI** - if
it makes mistakes, update the prompts

---

## Version History

- **v1.1** (2025-10-26): Added automation & cleanup principles
  - Documented what works/doesn't work for automated cleanup
  - Added pre-commit hook recommendations
  - Added "Code Cleanliness Over Cleverness" principle
  - Emphasized surgical manual cleanup over batch automation

- **v1.0** (2025-01-27): Initial version based on K1/K2/K3 validation experience
  - Established core principles
  - Created audit procedures
  - Added AI agent prompts
  - Defined deletion protocols

---

**Next Review Date:** January 26, 2026 (3 months)

**Maintainer:** Project team

**Questions?** Open an issue or discuss in project communication channel.
