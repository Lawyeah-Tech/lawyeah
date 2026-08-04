# Domain System Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single-entry domain template with a validated domain-package system containing one capability guide Skill, independently triggered atomic Skills, explicit relationships, decision-node MCP dependencies, and a tested 22-domain boundary map.

**Architecture:** Keep the domain pack as the installation, version, and uninstall unit. Make `pack.json` the machine-readable source of truth for the guide Skill, atomic Skill inventory, relationships, and MCP decision-node dependencies; package every runtime Skill under `skills/<lawyeah-name>/`. Keep complete boundary analysis and evaluations private while publishing only distilled domain boundaries outside the user release.

**Tech Stack:** Git, Markdown, JSON Schema Draft 2020-12, Python 3 standard library, Agent Skills folders, deterministic ZIP releases.

## Global Constraints

- Runtime paths and stable identifiers use lowercase ASCII `kebab-case`; Chinese is display text only.
- Every published Skill name starts with `lawyeah-` and matches its parent directory.
- A domain package contains exactly one guide Skill and one or more atomic Skills when active.
- The guide Skill describes capability, boundary, and package overview; specific requests may trigger atomic Skills directly.
- Atomic Skills correspond to complete user goals and independently verifiable deliverables, not workflow steps.
- Supported Skill relations are `depends-on`, `related-to`, and `excludes`; fixed before/after chains and composition templates are prohibited.
- Only `depends-on` creates an execution dependency, and it must identify the required business result.
- MCP dependency levels are `required`, `recommended`, and `optional`, declared per atomic Skill decision node.
- Similar Skills in different domains remain independent and do not share runtime methods, knowledge files, assets, or versions.
- Runtime document templates live under the owning atomic Skill's `assets/templates/` path.
- Domain packs use semantic versions; atomic Skills are not independently versioned; MCP contracts are independently versioned.
- Private research and boundary evaluation evidence remain under ignored `research/`; distilled domain boundaries are public but excluded from user releases.
- No concrete atomic legal Skill is authored in this phase.

---

### Task 1: Failing Contracts for the Multi-Skill Pack

**Files:**
- Modify: `tests/test_repository_contract.py`
- Modify: `tests/test_release_builder.py`

**Interfaces:**
- Consumes: the existing repository validator and release builder.
- Produces: failing tests that require multi-Skill active packs, ASCII paths, guide/atomic inventory integrity, relation integrity, decision-node MCP dependencies, and allowlisted `skills/**` archives.

- [x] **Step 1: Add an active multi-Skill pack fixture**

Create a fixture with `pack.json`, `skills/lawyeah-contracts-guide/SKILL.md`, and `skills/lawyeah-contracts-review/SKILL.md`. The manifest declares one guide and one atomic Skill.

- [x] **Step 2: Add validator failure cases**

Test rejection of a missing guide directory, a Skill directory/name mismatch, a relation to an unknown Skill, a cross-directory runtime reference, and a non-ASCII runtime path.

- [x] **Step 3: Update the release expectation**

Require the archive to contain `pack.json` plus allowlisted files below `skills/**`, while excluding pack tests, research, root scaffolding, and credentials.

- [x] **Step 4: Run the tests and verify RED**

Run: `python3 -m unittest tests.test_repository_contract tests.test_release_builder -v`

Expected: FAIL because the current validator requires a root `SKILL.md`, the release manifest does not include `skills/**`, and the new pack schema is absent.

### Task 2: Pack Schema, Validator, Release, and Scaffolding

**Files:**
- Modify: `schemas/pack.schema.json`
- Modify: `schemas/mcp-capabilities.schema.json`
- Create: `schemas/domain-catalog.schema.json`
- Modify: `tooling/validate_repository.py`
- Modify: `tooling/build_release.py`
- Modify: `release-manifest.json`
- Replace: `templates/domain-pack/SKILL.md.tmpl`
- Replace: `templates/domain-pack/agents/openai.yaml.tmpl`
- Replace: `templates/domain-pack/references/ROUTING.md`
- Modify: `templates/domain-pack/pack.json.tmpl`
- Create: `templates/domain-pack/skills/guide/SKILL.md.tmpl`
- Create: `templates/domain-pack/skills/guide/agents/openai.yaml.tmpl`
- Create: `templates/domain-pack/skills/atomic/SKILL.md.tmpl`
- Create: `templates/domain-pack/skills/atomic/agents/openai.yaml.tmpl`

**Interfaces:**
- Consumes: Task 1 tests.
- Produces: `pack.json` schema version 2; a validator that enforces package and Skill invariants; deterministic archives containing every allowlisted runtime Skill; non-runtime guide and atomic scaffolds.

- [x] **Step 1: Implement schema version 2**

Define pack identity, public scope, guide Skill ID, Skill inventory, allowed relationships, MCP contract range, and per-decision-node capability levels. Do not define fixed workflow chains or independent atomic versions.

- [x] **Step 2: Implement validator invariants**

Validate Skill IDs and paths, frontmatter name matching, exactly one guide, at least one atomic Skill for active packs, relation targets, no self-dependencies, `depends-on` required-result text, MCP decision-node uniqueness, ASCII runtime paths, and no cross-Skill relative references.

- [x] **Step 3: Change the release boundary**

Require `pack.json`, allow `skills/**`, and reject any active pack whose validated runtime inventory is incomplete before archiving.

- [x] **Step 4: Replace the old composition/router scaffold**

Remove the root execution Skill and `ROUTING.md` composition table. Add a narrow capability-guide template and a self-contained atomic Skill template. Place runtime document templates under each atomic Skill's `assets/templates/`.

- [x] **Step 5: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_repository_contract tests.test_release_builder -v`

Expected: PASS.

### Task 3: Private Boundary Workbook and Public 22-Domain Map

**Files:**
- Create ignored: `research/architecture/domain-boundary-workbook.md`
- Create ignored: `research/architecture/domain-boundary-evals.json`
- Modify: `catalog/domains.json`
- Create: `docs/architecture/domain-boundaries.md`
- Modify: `tests/test_repository_contract.py`

**Interfaces:**
- Consumes: the approved client-goal and deliverable ownership rule.
- Produces: private positive/negative/cross-domain boundary evidence and a public distilled map with purpose, inclusions, exclusions, primary deliverables, ownership rule, and related domains for all 22 entries.

- [x] **Step 1: Add failing public-boundary validation tests**

Require every domain to contain non-empty `purpose`, `inScope`, `outOfScope`, `primaryDeliverables`, `ownershipRule`, and valid `relatedDomains`. Require reciprocal related-domain declarations and prohibit self-relations.

- [x] **Step 2: Verify the boundary test is RED**

Run: `python3 -m unittest tests.test_repository_contract.RepositoryContractTests.test_current_repository_satisfies_contract -v`

Expected: FAIL because the current catalog contains only a single `scope` string.

- [x] **Step 3: Build the private boundary workbook and evaluation fixture**

Record the full design rationale and at least one `should-own`, `should-not-own`, and `cross-domain` prompt per domain. Keep these files ignored and untracked.

- [x] **Step 4: Publish the distilled boundary map**

Replace the single `scope` field with the approved dimensions, preserve the 8/8/6 priority counts, and write a human-readable cross-domain ownership guide without research citations or intermediate reasoning.

- [x] **Step 5: Run repository contract tests**

Run: `python3 -m unittest tests.test_repository_contract -v`

Expected: PASS and report 22 valid boundary definitions.

### Task 4: Documentation, Governance, and Full Verification

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `docs/architecture/repository.md`
- Modify: `docs/superpowers/plans/2026-08-04-domain-system-architecture.md`

**Interfaces:**
- Consumes: Tasks 1–3 contracts.
- Produces: public documentation aligned with the implemented architecture and fresh verification evidence.

- [x] **Step 1: Update public architecture language**

Document the guide/atomic/package layers, source-of-truth rule, atomicity test, relationship semantics, self-containment, ASCII paths, template asset location, versioning, MCP decision-node dependencies, and private/public/runtime boundary separation.

- [x] **Step 2: Remove obsolete architecture language**

Remove claims that each domain exposes only one top-level Skill and remove every runtime composition-scheme or root routing-table requirement.

- [x] **Step 3: Run full verification**

Run: `python3 -m unittest discover -s tests -v && python3 tooling/validate_repository.py --root . && git diff --check`

Expected: all tests pass, repository validation reports 22 domains with exact priority counts and complete boundary definitions, and no whitespace errors.

- [x] **Step 4: Verify private and release boundaries**

Run: `git check-ignore -v research/architecture/* && test -z "$(git ls-files research/architecture)" && git status --short`

Expected: private workbooks are ignored and untracked; only intended public architecture files are shown.

- [x] **Step 5: Mark supported plan steps complete**

Change `[ ]` to `[x]` only where fresh command output demonstrates completion.
