# Changelog

All notable changes to this template are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

A version here describes the template, not the packages it generates. Those
start at `0.0.1` whatever version generated them.

## [Unreleased]

### Changed

- This repository builds and develops with uv instead of Poetry. Contributors
  run `uv sync` and `uv run pytest`, and CI installs from `uv.lock`.
- A generated package builds and develops with uv too. Its `pyproject.toml`
  uses `[dependency-groups]` and `[tool.uv.sources]` with hatchling as the
  build backend, its source distribution lists only the package, the readme
  and the licence, and it arrives with a `uv.lock` already written.
- Generated workflows call the shared workflows at v0.6.0, which adds Django
  6.1 to the test matrix. The generated package declares the Django 6.1
  classifier.
- Dependabot in a generated package watches `uv.lock` rather than the pip
  ecosystem.

### Added

- The template. It generates a package that installs, passes its own tests,
  passes its own linters, and runs in a browser without an edit.
- Five prompts, and no more: the distribution name, the import name, a
  description, the app's display name, and whether the package needs tests that
  run in a real browser. Everything else is fixed, because a choice offered
  here is a way for two packages to differ for no reason.
- A demo Django project on django-mvp's application shell, with three sign-in
  accounts seeded by a management command, so a generated package can be looked
  at in a browser before it does anything.
- `CONSTITUTION.md` filled in with the standards that apply to every package
  built this way, and `AGENTS.md`, `CONTEXT.md`, `GOALS.md`, `docs/ROADMAP.md`
  and `README.md` as shells — headings, house style, and a note in each section
  saying what belongs there.
- CI that generates a package, installs it, and runs its suite and its linters
  on every push. The template's claim is about what comes out of it, so that is
  what gets tested.
- `scripts/check_pins.py`, run weekly, which fails when the pinned toolchain
  tag or the django-mvp floor has fallen behind. Dependabot cannot read a pin
  that lives inside a template, so this is what stops this repository quietly
  going stale.
