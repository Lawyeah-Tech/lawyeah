# Lawyeah Repository Initialization Implementation Plan

> 历史实施计划（2026-08-04）。不代表当前公开仓库：律师安装目录是 `领域/` 和 `合同/`，已无 `tests/`、`tooling/` 和发布工作流。

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Initialize the public Lawyeah monorepo with a validated 22-domain catalog, progressive-disclosure pack template, static release packaging contract, and repository governance.

**Architecture:** Keep each published legal domain self-contained and host-discoverable through one top-level `SKILL.md`. Maintain development validation and static package generation in the public source repository, exclude those files from user release assets, and keep private research outside the repository. Build platform-neutral domain sources into static archives without installing executables or embedding MCP credentials.

**Tech Stack:** Git, Markdown, JSON Schema Draft 2020-12, Python 3 standard library, GitHub Actions.

## Global Constraints

- The repository is public and licensed under Apache-2.0.
- The repository contains exactly 22 planned Mainland China legal-business domain packs: P0 8, P1 8, P2 6.
- No cross-domain runtime Skill is published; every eventual domain pack is self-contained and professionally specialized.
- Each domain pack exposes one top-level `SKILL.md` and loads bundled resources progressively.
- Customer installations contain static Skill files only; no updater, installer daemon, or background executable is installed.
- Static platform packages differ only in host metadata, MCP connection declaration, and path layout; professional content remains canonical.
- MCP credentials, tokens, endpoints, and unconfirmed tool parameters are not stored in the repository.
- MCP capability dependence uses `required`, `recommended`, and `optional` classifications.
- Reinstallation replaces an official pack directory atomically; official pack files are not merged with user edits.
- Private research, raw retrieval evidence, credentials, generated archives, caches, and local state remain untracked.
- Release archives use an allowlist and exclude repository tooling, tests, plans, and CI configuration.

---

### Task 1: Executable Repository Contracts

**Files:**
- Create: `tests/test_repository_contract.py`
- Create: `tests/test_release_builder.py`
- Create: `tooling/validate_repository.py`
- Create: `tooling/build_release.py`

**Interfaces:**
- Consumes: repository-root JSON files and a domain-pack directory supplied through command-line arguments.
- Produces: `validate_repository.py --root PATH -> exit 0/1`; `build_release.py --root PATH --pack PACK_ID --output PATH -> deterministic ZIP and SHA-256 sidecar`.

- [x] **Step 1: Write the failing repository validation test**

```python
def test_current_repository_satisfies_contract(self):
    result = subprocess.run(
        [sys.executable, "tooling/validate_repository.py", "--root", str(ROOT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
```

- [x] **Step 2: Write the failing release-boundary tests**

```python
def test_release_contains_only_allowlisted_runtime_files(self):
    result = run_builder(self.repo, "review-draft-contracts", self.output)
    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
    with zipfile.ZipFile(self.output) as archive:
        self.assertEqual(
            archive.namelist(),
            [
                "review-draft-contracts/SKILL.md",
                "review-draft-contracts/pack.json",
                "review-draft-contracts/references/workflow.md",
            ],
        )

def test_rebuilding_same_pack_is_byte_identical(self):
    first = hashlib.sha256(self.output.read_bytes()).hexdigest()
    run_builder(self.repo, "review-draft-contracts", self.second_output)
    second = hashlib.sha256(self.second_output.read_bytes()).hexdigest()
    self.assertEqual(first, second)
```

- [x] **Step 3: Run tests and verify the expected red state**

Run: `python3 -m unittest discover -s tests -v`

Expected: FAIL because `tooling/validate_repository.py` and `tooling/build_release.py` do not exist.

- [x] **Step 4: Implement repository validation**

Implement `validate_repository.py` with Python standard-library JSON parsing and observable validation for:

```text
required root files
catalog schema version and catalog version
exactly 22 unique domain IDs and Chinese names
priority counts P0=8, P1=8, P2=6
allowed lifecycle states planned|active|deprecated
active pack presence and required SKILL.md/pack.json files
release allowlist required entries
parseable JSON Schema files
```

- [x] **Step 5: Implement deterministic allowlist packaging**

Implement `build_release.py` so it:

```text
rejects path traversal and unknown/inactive pack IDs
requires SKILL.md and pack.json
includes only exact paths or recursively allowlisted prefixes
sorts archive paths
uses a fixed ZIP timestamp and permissions
writes <archive>.sha256 beside the archive
never includes research, tests, tooling, CI, credentials, caches, or local state
```

- [x] **Step 6: Run the focused tests**

Run: `python3 -m unittest tests.test_release_builder -v`

Expected: release behavior passes; repository contract remains red until Task 2 adds the required data files.

### Task 2: Governance, Catalog, and Schemas

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `NOTICE`
- Create: `CONTRIBUTING.md`
- Create: `SECURITY.md`
- Create: `.gitignore`
- Create: `.gitattributes`
- Create: `release-manifest.json`
- Create: `catalog/domains.json`
- Create: `catalog/bundles.json`
- Create: `catalog/platforms.json`
- Create: `schemas/pack.schema.json`
- Create: `schemas/mcp-capabilities.schema.json`
- Create: `schemas/adapter.schema.json`
- Create: `docs/architecture/repository.md`

**Interfaces:**
- Consumes: the 22-domain decisions, Apache-2.0 policy, static-install policy, and MCP dependency levels.
- Produces: human-readable governance and machine-readable contracts consumed by `validate_repository.py` and future CI builders.

- [x] **Step 1: Add the exact 22-domain catalog**

Use verb-led, lowercase, hyphenated stable IDs. Record Chinese display name, P0/P1/P2 priority, Mainland China jurisdiction, scope summary, and `planned` lifecycle state. Do not assign pack versions before a real pack exists.

- [x] **Step 2: Add bundle and platform catalogs**

Define only deterministic bundles: `full` selects P0/P1/P2, and `p0` selects P0. Record the confirmed static targets WorkBuddy, Kimi, Codex, Claude, Qwen Code, Qoder, TRAE, Comate, and generic Agent Skills without inventing platform manifests.

- [x] **Step 3: Add schemas and the release allowlist**

The pack schema requires Apache-2.0, semantic pack versioning, one `SKILL.md` entry point, Mainland China jurisdiction, an MCP contract version range, and the three capability dependency arrays. The release manifest includes only `SKILL.md`, `pack.json`, `agents/`, `references/`, `scripts/`, and `assets/` from one active pack.

- [x] **Step 4: Add repository and distribution documentation**

Document the source/release boundary, private research boundary, progressive disclosure layout, static installation, reinstall replacement, one-time MCP authorization, version layers, and absence of embedded credentials or local updaters.

- [x] **Step 5: Run repository validation**

Run: `python3 tooling/validate_repository.py --root .`

Expected: PASS with a summary containing 22 domains, P0=8, P1=8, P2=6.

### Task 3: Progressive-Disclosure Domain Pack Template

**Files:**
- Create: `templates/domain-pack/SKILL.md.tmpl`
- Create: `templates/domain-pack/pack.json.tmpl`
- Create: `templates/domain-pack/agents/openai.yaml.tmpl`
- Create: `templates/domain-pack/references/ROUTING.md`

**Interfaces:**
- Consumes: pack schema and Agent Skill requirements.
- Produces: a non-publishable scaffolding template for future domain pack initialization; actual skills must still be initialized and validated with the skill-creator workflow.

- [x] **Step 1: Add a concise top-level Skill template**

Keep YAML frontmatter limited to `name` and `description`. The body contains intake, task routing, selective reference loading, MCP availability checks, output contract, and quality gate sections without legal conclusions.

- [x] **Step 2: Add the pack manifest template**

Use explicit template tokens for pack identity and version. Default capability arrays are empty, preventing unconfirmed MCP tools from entering a release.

- [x] **Step 3: Add UI metadata and routing guidance templates**

Keep UI values templated and state that generated `agents/openai.yaml` must match the completed Skill. Explain that every referenced workflow or knowledge file must be linked directly from the top-level Skill to avoid multi-hop reference chains.

- [x] **Step 4: Validate templates are excluded from releases**

Run: `python3 -m unittest tests.test_release_builder -v`

Expected: PASS because the builder packages only one selected active pack and never repository templates.

### Task 4: CI and End-to-End Verification

**Files:**
- Create: `.github/workflows/validate.yml`
- Modify: `docs/superpowers/plans/2026-08-04-lawyeah-repository-initialization.md`

**Interfaces:**
- Consumes: all repository contracts and tests.
- Produces: repeatable validation on pushes and pull requests.

- [x] **Step 1: Add dependency-free CI**

Run Python 3.11 with:

```bash
python -m unittest discover -s tests -v
python tooling/validate_repository.py --root .
```

- [x] **Step 2: Run the complete verification suite**

Run: `python3 -m unittest discover -s tests -v && python3 tooling/validate_repository.py --root .`

Expected: all tests pass and validation reports 22 domains with the exact priority counts.

- [x] **Step 3: Verify archive exclusion behavior**

Run: `git archive --format=tar HEAD 2>/dev/null | tar -tf -` after the first commit exists; before a commit exists, use `git check-attr export-ignore -- tooling tests templates .github docs/superpowers` and the release-builder integration test.

Expected: development-only paths have `export-ignore: set`, and release-builder tests prove that runtime archives contain allowlisted pack files only.

- [x] **Step 4: Inspect repository state**

Run: `git status --short && git diff --check && git diff --stat`

Expected: only initialization files are present, no credentials or generated archives are tracked, and no whitespace errors are reported.

- [x] **Step 5: Mark this plan complete**

Change completed checkboxes from `[ ]` to `[x]` only for steps supported by fresh command output.
