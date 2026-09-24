"""Fail when this template has fallen behind what it pins.

A template nobody exercises rots quietly: it goes on generating packages that
install and pass, against a version of the toolchain everything else moved off
months ago. Nothing complains, because everything still works.

This turns that into a red build. It checks three things and reports all of
them rather than stopping at the first:

  * the shared workflow and toolchain tag is the latest release
  * the django-mvp floor is the latest published version
  * the year in the generated LICENSE is this year

Run it with no arguments. Exit 0 means there is nothing to bump.
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
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        return json.load(response)


def check_shared_tag() -> str | None:
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
