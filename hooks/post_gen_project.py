"""Stamp today's date, remove what the answers ruled out, then say what next.

Cookiecutter writes every file in the template and has no way to skip one, so
anything conditional is generated and then deleted here.
"""

import shutil
import subprocess
from datetime import date
from pathlib import Path

BROWSER_TESTS = "{{ cookiecutter.browser_tests }}" == "yes"
DISTRIBUTION = "{{ cookiecutter.distribution_name }}"

BROWSER_ONLY_FILES = [
    "tests/test_browser.py",
]


def drop(relative_path: str) -> None:
    path = Path(relative_path)
    if path.is_file():
        path.unlink()


if not BROWSER_TESTS:
    for relative_path in BROWSER_ONLY_FILES:
        drop(relative_path)

# Cookiecutter has no date of its own without an extension the person running
# it would have to install, so the placeholder is substituted here instead.
TODAY = date.today().isoformat()
for path in Path(".").rglob("*.md"):
    text = path.read_text(encoding="utf-8")
    if "__GENERATED_DATE__" in text:
        path.write_text(text.replace("__GENERATED_DATE__", TODAY), encoding="utf-8")

# The shared build workflow installs with `uv sync --locked`, which fails when
# there is no lock file, so a new package is born with one.
LOCKED = False
if shutil.which("uv") is not None:
    LOCKED = subprocess.run(["uv", "lock"], check=False).returncode == 0

LOCK_NOTE = (
    "uv.lock is written, but nothing has been committed."
    if LOCKED
    else "uv could not write uv.lock. Install uv, then run `uv lock` before committing."
)

print(  # noqa: T201 - the hook's whole job at this point is to talk to a person
    f"""
{DISTRIBUTION} is written. {LOCK_NOTE}

  cd {DISTRIBUTION}
  uv sync
  uv run pytest
  uv run pre-commit install && uv run pre-commit run --all-files
  uv run python manage.py migrate && uv run python manage.py seed_demo
  uv run python manage.py runserver

The test suite passes on a freshly generated package, so a failure here is
about the environment rather than about the code.

Four things are worth reading before writing any of your own code:

  CONTEXT.md      name the things this package deals in, before the words
                  harden in issues and tests
  GOALS.md        what the package is trying to be good at
  docs/ROADMAP.md the order the work happens in
  CONSTITUTION.md the standards every change is held to

Each one is a shell with notes on how its sections are meant to read. Replace
the notes with the real content, and delete the guidance blocks as you go.
"""
)
