"""Fail when this template has fallen behind what it pins.

Checks that the shared toolchain tag and the django-mvp floor are the latest
releases, and that the generated LICENSE carries this year. Every problem is
reported, not only the first. Exit 0 means there is nothing to bump.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTEXT = json.loads((ROOT / "cookiecutter.json").read_text())
TEMPLATE_DIR = ROOT / "{{cookiecutter.distribution_name}}"

SHARED_RELEASES = "https://api.github.com/repos/django-mvp/shared/releases/latest"
DJANGO_MVP_PYPI = "https://pypi.org/pypi/django-mvp/json"


def fetch(url: str) -> dict:
    """Fetch a JSON document.

    Args:
        url: The address to read.

    Returns:
        The decoded response body.
    """
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        return json.load(response)


def check_shared_tag() -> str | None:
    """Compare the shared toolchain tag against its latest release.

    Returns:
        What to bump and how, or None when it is current.
    """
    pinned = CONTEXT["_shared_tag"]
    latest = fetch(SHARED_RELEASES)["tag_name"]
    if pinned == latest:
        return None
    return (
        f"The shared toolchain tag is behind: this template pins {pinned}, "
        f"and the latest release is {latest}.\n"
        f"  Set _shared_tag in cookiecutter.json to {latest}, then regenerate "
        "and run the suite — a shared release can change what the workflows "
        "expect."
    )


def check_django_mvp_floor() -> str | None:
    """Compare the django-mvp floor against its latest published version.

    Returns:
        What to bump and how, or None when it is current.
    """
    pinned = CONTEXT["_django_mvp_floor"]
    latest = fetch(DJANGO_MVP_PYPI)["info"]["version"]
    if pinned == latest:
        return None
    return (
        f"The django-mvp floor is behind: this template pins >={pinned}, "
        f"and the latest published version is {latest}.\n"
        "  A new package should start on the current release. Set "
        "_django_mvp_floor in cookiecutter.json, and check the demo project "
        "still renders — the application shell is what moves."
    )


def check_license_year() -> str | None:
    """Compare the generated LICENSE's copyright year against this year.

    Returns:
        What to bump and how, or None when it is current.
    """
    this_year = date.today().year
    text = (TEMPLATE_DIR / "LICENSE").read_text()
    found = re.search(r"Copyright \(c\) (\d{4})", text)
    if found is None:
        return "The generated LICENSE has no copyright year to check."
    if int(found.group(1)) == this_year:
        return None
    return (
        f"The generated LICENSE says {found.group(1)} and it is {this_year}. "
        "Update the year in the template's LICENSE."
    )


def main() -> int:
    """Run every check and print what needs bumping.

    Returns:
        The process exit code: 0 when every pin is current, 1 otherwise.
    """
    problems = []
    for check in (check_shared_tag, check_django_mvp_floor, check_license_year):
        try:
            problem = check()
        except (urllib.error.URLError, KeyError, TimeoutError) as exc:
            problems.append(f"{check.__name__} could not run: {exc}")
        else:
            if problem:
                problems.append(problem)

    if not problems:
        print("Pins are current.")
        return 0

    for problem in problems:
        print(f"\n{problem}")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
