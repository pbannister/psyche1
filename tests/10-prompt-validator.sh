#!/bin/sh
#
# Prompt-validator test: the adversarial corpus.
#
# Tier: tool-gated (python3 and git, through tests/09). Builds a throwaway copy
# of the repository, commits it to a scratch git repository, injects one
# malformed fixture at a time, and asserts that tests/09-prompt-contract.sh
# rejects each one for the expected reason. This tests the validator itself,
# not only the clean corpus.
set -eu

DIRECTORY_SCRIPT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPOSITORY_ROOT=$(CDPATH= cd -- "$DIRECTORY_SCRIPT/.." && pwd)
SCRIPT_CHECK="$REPOSITORY_ROOT/tests/09-prompt-contract.sh"

. "$DIRECTORY_SCRIPT/lib/test_helpers.sh"
skip_unless_tool python3
skip_unless_tool git

DIRECTORY_TEST=$(mktemp -d)
trap 'rm -rf "$DIRECTORY_TEST"' EXIT HUP INT TERM
DIRECTORY_ROOT="$DIRECTORY_TEST/root"

fail() {
    echo "10-prompt-validator: $1" >&2
    exit 1
}

# reset: a clean, committed copy of the repository to mutate. Committing it
# lets the validator's tracked-root and tool-config checks run.
reset() {
    rm -rf "$DIRECTORY_ROOT"
    mkdir -p "$DIRECTORY_ROOT"
    (cd "$REPOSITORY_ROOT" && tar --exclude=./.git --exclude=./site.out \
        --exclude=./dataflow.out --exclude=./logs -cf - .) \
        | (cd "$DIRECTORY_ROOT" && tar -xf -)
    git -C "$DIRECTORY_ROOT" init -q
    git -C "$DIRECTORY_ROOT" add -A
}

FILE_TASK="$DIRECTORY_ROOT/prompts/tasks/01-site-build-implement.md"
FILE_WORKFLOW="$DIRECTORY_ROOT/prompts/02-workflow.md"
FILE_FEATURE="$DIRECTORY_ROOT/prompts/features/01-site-build.md"
FILE_FEATURE_02="$DIRECTORY_ROOT/prompts/features/02-project-pages.md"
FILE_EPISODE="$DIRECTORY_ROOT/prompts/episodes/01-episode-template.md"
FILE_PHASES="$DIRECTORY_ROOT/PHASES.md"

count_case=0
count_accept=0

expect_reject() {
    name_case=$1
    text_expect=$2
    count_case=$((count_case + 1))
    git -C "$DIRECTORY_ROOT" add -A >/dev/null 2>&1 || true
    if output_case=$(sh "$SCRIPT_CHECK" "$DIRECTORY_ROOT" 2>&1); then
        fail "the validator accepted '$name_case'"
    fi
    printf '%s\n' "$output_case" | grep -qF "$text_expect" \
        || fail "the validator rejected '$name_case' for the wrong reason: $output_case"
}

expect_accept() {
    name_case=$1
    count_accept=$((count_accept + 1))
    git -C "$DIRECTORY_ROOT" add -A >/dev/null 2>&1 || true
    if ! output_case=$(sh "$SCRIPT_CHECK" "$DIRECTORY_ROOT" 2>&1); then
        fail "the validator rejected '$name_case': $output_case"
    fi
}

# Baseline: the clean corpus validates.
reset
if ! output_clean=$(sh "$SCRIPT_CHECK" "$DIRECTORY_ROOT" 2>&1); then
    fail "the clean corpus did not validate: $output_clean"
fi

# --- task structure ---
reset; sed -i '/^## TASK-OUTPUT$/d' "$FILE_TASK"
expect_reject 'task missing TASK-OUTPUT' 'missing ## TASK-OUTPUT'

reset; sed -i '1i ## TASK-OUTPUT' "$FILE_TASK"
expect_reject 'task sections out of order' 'must precede TASK-OUTPUT'

reset; sed -i '/^OUTPUT:/d' "$FILE_TASK"
expect_reject 'task missing the OUTPUT line' 'OUTPUT: restatement'

reset; sed -i '/^- Run:/d' "$FILE_TASK"
expect_reject 'TASK-VERIFY without a Run line' "TASK-VERIFY has no 'Run:' line"

reset; sed -i 's/^- Expected: .*/- Expected: looks good./' "$FILE_TASK"
expect_reject 'a judgmental Expected line' 'must describe an observable result'

# --- scope table and operation lines ---
reset; sed -i '/^| create |/d' "$FILE_TASK"
expect_reject 'TASK-FILES without rows' "TASK-FILES has no '| operation |"

reset; sed -i 's/^| create |/| frobnicate |/' "$FILE_TASK"
expect_reject 'unknown operation in TASK-FILES' 'unknown operation'

reset; sed -i 's#`scripts/site-build.sh`#`/etc/passwd`#' "$FILE_TASK"
expect_reject 'absolute path in TASK-FILES' 'not repository-relative'

reset; sed -i 's#`scripts/site-build.sh`#`../outside.sh`#' "$FILE_TASK"
expect_reject 'parent escape in TASK-FILES' 'not repository-relative'

reset; sed -i '/^|---|---|$/a | create | `scripts/undeclared.sh` |' "$FILE_TASK"
expect_reject 'TASK-FILES row without an operation line' 'has no operation line in TASK-DESCRIPTION'

reset; sed -i '/^## TASK-DESCRIPTION$/a - Modify: `scripts/undeclared.sh`' "$FILE_TASK"
expect_reject 'operation on an undeclared path' 'operation on undeclared path'

reset; sed -i 's/^- Create: `scripts\/site-build.sh`$/- Modify: `scripts\/site-build.sh`/' "$FILE_TASK"
expect_reject 'verb disagrees between sections' "but 'modify' in TASK-DESCRIPTION"

# --- traceability ---
reset; sed -i '/^## TASK-ACCEPTANCE$/a - `NOPE-R999`' "$FILE_TASK"
expect_reject 'unknown acceptance identifier' 'unknown identifier'

reset; sed -i '/^## TASK-ACCEPTANCE$/a - `PROJECT-PAGES-R001`' "$FILE_TASK"
expect_reject 'acceptance from a feature not in TASK-FEATURES' 'not in TASK-FEATURES'

# Feature 02 depends on feature 01, so a task that lists 02 may claim a
# requirement owned by 01: dependencies apply transitively.
reset; sed -i 's#`prompts/features/01-site-build.md`#`prompts/features/02-project-pages.md`#' "$FILE_TASK"
expect_accept 'acceptance reachable through a feature dependency'

reset; sed -i 's#`01-site-build.md`#`99-missing.md`#' "$FILE_FEATURE_02"
expect_reject 'unresolved feature dependency' 'feature dependency does not resolve'

reset; sed -i '/^## Requirements$/a - A new unnamed requirement.' "$FILE_FEATURE"
expect_reject 'requirement without an identifier' 'requirement without an identifier'

# --- mandatory sections and feature references ---
reset; sed -i '/^## TASK-FILES$/d; /^| create |/d' "$FILE_TASK"
expect_reject 'task missing TASK-FILES' 'missing ## TASK-FILES'

reset; sed -i '/^## TASK-VERIFY$/d; /^- Run:/d; /^- Expected:/d' "$FILE_TASK"
expect_reject 'task missing TASK-VERIFY' 'missing ## TASK-VERIFY'

reset; sed -i '/^## TASK-FEATURES$/d; /^\- `prompts\/features\/01-site-build.md`$/d' "$FILE_TASK"
expect_reject 'TASK-ACCEPTANCE without TASK-FEATURES' 'has TASK-ACCEPTANCE but no TASK-FEATURES'

reset; sed -i '/^## TASK-FEATURES$/d; /^\- `prompts\/features\/01-site-build.md`$/d; /^## TASK-ACCEPTANCE$/d; /^- `SITE-BUILD-R/d' "$FILE_TASK"
expect_reject 'feature referenced but no TASK-FEATURES' 'references a feature but has no TASK-FEATURES'

reset; sed -i '/^## TASK-ACCEPTANCE$/d; /^- `SITE-BUILD-R/d' "$FILE_TASK"
expect_reject 'TASK-FEATURES without TASK-ACCEPTANCE' 'has TASK-FEATURES but no TASK-ACCEPTANCE'

reset; sed -i 's#`prompts/features/01-site-build.md`#`prompts/03-conventions.md`#' "$FILE_TASK"
expect_reject 'TASK-FEATURES lists a non-feature' 'TASK-FEATURES must list feature files'

reset; sed -i 's#`prompts/features/01-site-build.md`#`prompts/features/99-missing.md`#' "$FILE_TASK"
expect_reject 'TASK-FEATURES lists a missing feature' 'TASK-FEATURES names a missing feature'

# --- corpus and registry ---
reset; cp "$FILE_FEATURE" "$DIRECTORY_ROOT/prompts/features/01-dup.md"
expect_reject 'duplicate feature number' 'duplicate feature number'

reset; printf '%s\n' 'See `prompts/does-not-exist.md`.' >> "$FILE_WORKFLOW"
expect_reject 'unresolved prompt reference' 'reference does not exist'

reset; printf '# Temporary rule file\n' > "$DIRECTORY_ROOT/prompts/common/04-temp.md"
expect_reject 'unregistered universal rule file' 'not in the contract section 2 registry'

reset; printf '%s\n' '- Change only what the task requires.' >> "$FILE_WORKFLOW"
expect_reject 'duplicated authoritative rule' 'duplicated in'

# --- episodes and phases ---
reset; sed -i '/^## EPISODE-ACCEPTANCE$/d' "$FILE_EPISODE"
expect_reject 'episode missing acceptance' 'missing ## EPISODE-ACCEPTANCE'

# The fixture rewrites whatever the current phase line is, so it works in a
# project at any phase rather than only in one that has not started.
reset; sed -i 's/^Current: .*/Current: phase 1 — in-progress/' "$FILE_PHASES"
expect_reject 'invalid phase state' 'invalid phase state'

# --- root structure and portable tool configuration ---
reset; mkdir -p "$DIRECTORY_ROOT/.undocumented"
printf '%s\n' 'x' > "$DIRECTORY_ROOT/.undocumented/config.json"
expect_reject 'undeclared tool directory' 'tool directory is not permitted'

reset; mkdir -p "$DIRECTORY_ROOT/.vscode"
printf '%s\n' '{ "path": "/home/someone/sources" }' > "$DIRECTORY_ROOT/.vscode/settings.json"
expect_reject 'absolute home path in tool configuration' 'absolute home path'

# --- the coding-agent entry point ---
reset; rm "$DIRECTORY_ROOT/AGENTS.md"
expect_reject 'missing agent entry point' 'AGENTS.md is missing'

reset; printf '# Agent Entry Point\n\nRun `make test`.\n' > "$DIRECTORY_ROOT/AGENTS.md"
expect_reject 'agent entry point without pointers' 'AGENTS.md does not point at prompts/01-contract.md'

reset; printf '%s\n' '- Change only what the task requires.' >> "$DIRECTORY_ROOT/AGENTS.md"
expect_reject 'rule restated in the agent entry point' 'duplicated in AGENTS.md'

# --- unattended scripts ---
reset; printf '#!/bin/sh\nread -p "Continue? " answer\n' > "$DIRECTORY_ROOT/scripts/prompt-user.sh"
expect_reject 'script that blocks on standard input' 'blocks on standard input'

# --- concurrent work isolation ---
reset; printf '%s\n' 'Each writer works in its own git worktree.' >> "$FILE_FEATURE"
expect_reject 'duplicated concurrent-work rule' 'duplicated in'

echo "10-prompt-validator: ok ($count_case rejected, $count_accept accepted)"
exit 0
