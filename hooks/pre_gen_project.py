"""Reject names that would produce a package nobody can install or import.

Both checks fail before anything is written. A distribution name Python's
packaging tools will not accept, or a directory name that is not a legal
module name, surfaces here as one line rather than as a confusing error from
Poetry or from Django's app registry several minutes later.
"""

import keyword
import re
import sys

DISTRIBUTION = "{{ cookiecutter.distribution_name }}"
IMPORT_NAME = "{{ cookiecutter.import_name }}"

# PEP 503: letters, digits, and runs of ., - or _ between them.
DISTRIBUTION_PATTERN = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$")


def fail(message: str) -> None:
    sys.stderr.write(f"\nERROR: {message}\n\n")
    sys.exit(1)


if not DISTRIBUTION_PATTERN.match(DISTRIBUTION):
    fail(
        f"'{DISTRIBUTION}' is not a usable distribution name. It has to start "
        "and end with a letter or a digit, and may otherwise hold letters, "
        "digits, dots, hyphens and underscores."
    )

if not IMPORT_NAME.isidentifier() or keyword.iskeyword(IMPORT_NAME):
    fail(
        f"'{IMPORT_NAME}' is not a usable import name. It becomes a directory "
        "Python imports and a Django app label, so it has to be a legal "
        "identifier: letters, digits and underscores, not starting with a "
        "digit."
    )

if IMPORT_NAME != IMPORT_NAME.lower():
    fail(
        f"'{IMPORT_NAME}' has capitals in it. An import name is lower case, "
        "because the directory name is the import path on a case-sensitive "
        "filesystem and the app label everywhere else."
    )
