SHELL := /bin/sh
.DEFAULT_GOAL := help

UV ?= uv
NPM ?= npm
CARGO ?= cargo
PYTHON ?= $(UV) run python
DESKTOP_DIR := apps/desktop
TAURI_DIR := $(DESKTOP_DIR)/src-tauri
ACCEPTANCE_ROOT ?= $(CURDIR)/.osca/desktop-acceptance
ACCEPTANCE_STATE_ROOT ?= $(ACCEPTANCE_ROOT)/state
ACCEPTANCE_PROFILE ?= $(ACCEPTANCE_ROOT)/profile
ACCEPTANCE_EVIDENCE ?= $(ACCEPTANCE_ROOT)/evidence

.PHONY: help tools setup sync frontend-install run run-clean acceptance-prepare acceptance-reset acceptance-seed acceptance-run acceptance-check acceptance-info build package frontend-build test test-python test-desktop test-frontend test-rust lint typecheck format-check check clean clean-desktop clean-python clean-all status

help: ## Show available targets.
	@printf '%s\n' 'OSCA developer and desktop commands'
	@printf '%s\n' ''
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@printf '%s\n' ''
	@printf '%s\n' 'Common flows:'
	@printf '%s\n' '  make setup              Install locked Python and desktop dependencies'
	@printf '%s\n' '  make run                Launch the desktop app in development mode'
	@printf '%s\n' '  make run-clean          Rebuild deterministic acceptance data and launch the app'
	@printf '%s\n' '  make acceptance-check   Run automated D5-D8 acceptance baseline'
	@printf '%s\n' '  make build              Build the native desktop package'
	@printf '%s\n' '  make check              Run the canonical contributor validation'

tools: ## Verify required contributor tools and Linux native libraries.
	@command -v $(UV) >/dev/null 2>&1 || { echo 'Missing uv'; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo 'Missing Node.js 22'; exit 1; }
	@command -v $(NPM) >/dev/null 2>&1 || { echo 'Missing npm'; exit 1; }
	@command -v $(CARGO) >/dev/null 2>&1 || { echo 'Missing cargo'; exit 1; }
	@command -v rustc >/dev/null 2>&1 || { echo 'Missing rustc'; exit 1; }
	@if [ "$$(uname -s)" = "Linux" ]; then \
		command -v pkg-config >/dev/null 2>&1 || { echo 'Missing pkg-config'; exit 1; }; \
		pkg-config --exists webkit2gtk-4.1 || { \
			echo 'Missing Linux Tauri libraries. Install libwebkit2gtk-4.1-dev, libappindicator3-dev, librsvg2-dev, and patchelf.'; \
			exit 1; \
		}; \
	fi
	@printf 'uv: '; $(UV) --version
	@printf 'node: '; node --version
	@printf 'npm: '; $(NPM) --version
	@printf 'rustc: '; rustc --version
	@printf 'cargo: '; $(CARGO) --version

setup: tools sync frontend-install ## Install all locked dependencies needed to build and run the desktop app.

sync: ## Install the locked Python environment.
	$(UV) sync --locked

frontend-install: ## Install locked desktop frontend dependencies.
	cd $(DESKTOP_DIR) && $(NPM) ci

run: setup ## Launch the Tauri desktop app in development mode.
	$(PYTHON) scripts/run_desktop.py

run-clean: ## Rebuild deterministic acceptance data and launch the short human-review smoke test.
	$(MAKE) acceptance-seed
	$(MAKE) acceptance-run

acceptance-prepare: setup ## Create isolated state and evidence directories for desktop acceptance.
	@mkdir -p "$(ACCEPTANCE_STATE_ROOT)" "$(ACCEPTANCE_EVIDENCE)"
	@printf '%s\n' 'Desktop acceptance environment prepared:'
	@printf '  state:    %s\n' "$(ACCEPTANCE_STATE_ROOT)"
	@printf '  profile:  %s\n' "$(ACCEPTANCE_PROFILE)"
	@printf '  evidence: %s\n' "$(ACCEPTANCE_EVIDENCE)"


acceptance-reset: ## Remove and recreate the isolated acceptance root; does not touch normal OSCA profiles.
	$(PYTHON) scripts/prepare_desktop_acceptance.py --root "$(ACCEPTANCE_ROOT)" --reset

acceptance-seed: acceptance-reset ## Exercise D5-D7 API workflow and retain a deterministic profile/manifest.

acceptance-run: acceptance-prepare ## Launch the app with the deterministic desktop acceptance profile.
	OSCA_DESKTOP_STATE_ROOT="$(ACCEPTANCE_STATE_ROOT)" $(PYTHON) scripts/run_desktop.py

acceptance-check: test-desktop acceptance-info ## Run automated D5-D8 desktop acceptance baseline and print evidence metadata.

acceptance-info: ## Print paths and source identity to record in manual-test evidence.
	@printf 'source commit: '; git rev-parse HEAD
	@printf 'branch: '; git branch --show-current
	@printf 'architecture: '; uname -m
	@printf 'system: '; uname -s
	@printf 'state root: %s\n' "$(ACCEPTANCE_STATE_ROOT)"
	@printf 'profile root: %s\n' "$(ACCEPTANCE_PROFILE)"
	@printf 'evidence root: %s\n' "$(ACCEPTANCE_EVIDENCE)"
	@$(UV) --version
	@node --version
	@$(NPM) --version
	@rustc --version
	@$(CARGO) --version

build: setup ## Build the native desktop application package for the current platform.
	@if [ "$$(uname -s)" = "Darwin" ]; then \
		cd $(DESKTOP_DIR) && $(NPM) run tauri -- build --bundles app; \
	elif [ "$$(uname -s)" = "Linux" ]; then \
		cd $(DESKTOP_DIR) && $(NPM) run tauri -- build --bundles deb; \
	else \
		cd $(DESKTOP_DIR) && $(NPM) run tauri -- build; \
	fi
	@printf '%s\n' 'Native package output:'
	@find "$(TAURI_DIR)/target/release/bundle" -maxdepth 3 -type f 2>/dev/null || true

package: build ## Alias for the native desktop package build.

frontend-build: frontend-install ## Type-check and build the React frontend only.
	cd $(DESKTOP_DIR) && $(NPM) run build

test: test-python test-frontend test-rust ## Run Python, frontend, and Rust desktop tests.

test-python: sync ## Run the complete Python test suite.
	$(UV) run pytest

test-desktop: sync frontend-install ## Run focused D1-D8 desktop API, acceptance, launcher, packaging, Makefile, and frontend tests.
	$(UV) run pytest tests/test_d1_desktop_api.py tests/test_d2_desktop_api.py tests/test_d3_desktop_*.py tests/test_d4_*.py tests/test_d5_*.py tests/test_d6_*.py tests/test_d7_*.py tests/test_d8_*.py tests/test_desktop_acceptance_prepare.py tests/test_desktop_launcher.py tests/test_desktop_packaging.py tests/test_makefile.py
	cd $(DESKTOP_DIR) && $(NPM) test

test-frontend: frontend-install ## Run desktop frontend tests.
	cd $(DESKTOP_DIR) && $(NPM) test

test-rust: ## Run Tauri broker tests.
	cd $(TAURI_DIR) && $(CARGO) test --all-targets --all-features

lint: sync frontend-install ## Run Python lint, TypeScript checks, and Rust Clippy.
	$(UV) run ruff check .
	cd $(DESKTOP_DIR) && $(NPM) run check
	cd $(TAURI_DIR) && $(CARGO) clippy --all-targets --all-features -- -D warnings

typecheck: sync ## Run strict Python and TypeScript type checks.
	$(UV) run mypy src tests
	cd $(DESKTOP_DIR) && $(NPM) run check

format-check: ## Verify Python and Rust formatting without modifying files.
	$(UV) run ruff format --check .
	cd $(TAURI_DIR) && $(CARGO) fmt --check

check: setup ## Run the canonical full contributor validation used by CI.
	$(PYTHON) scripts/contributor_check.py

clean: clean-desktop clean-python ## Remove generated build and test outputs while preserving installed dependencies.

clean-desktop: ## Remove generated frontend and Rust/Tauri build outputs.
	rm -rf "$(DESKTOP_DIR)/dist" "$(TAURI_DIR)/target" "$(TAURI_DIR)/gen"

clean-python: ## Remove Python caches, test caches, coverage, and package outputs.
	find src tests scripts -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage build dist *.egg-info

clean-all: clean ## Also remove installed local dependencies and isolated acceptance state.
	rm -rf .venv "$(DESKTOP_DIR)/node_modules" "$(ACCEPTANCE_ROOT)"

status: ## Show branch, commit, worktree state, and build paths.
	@git status --short --branch
	@printf 'commit: '; git rev-parse HEAD
	@printf 'desktop bundle root: %s\n' "$(TAURI_DIR)/target/release/bundle"
