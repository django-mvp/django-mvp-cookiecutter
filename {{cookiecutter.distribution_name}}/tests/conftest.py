"""Shared fixtures for the test suite.

General setup and anything reused across modules lives here. Test modules hold
assertions, not construction boilerplate.

Once this package has models, each one gets exactly one ``factory_boy``
factory in ``tests/factories.py``, and the fixtures here are thin wrappers over
those factories. A one-off variation needs no fixture of its own — call the
factory inline in the test with the field overridden.
"""

{% if cookiecutter.browser_tests == "yes" %}import os

{% endif %}import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler


@pytest.fixture(scope="session")
def render():
    """Compile a Cotton source string and render it.

    No request is involved. A component that reads nothing off one renders
    anywhere a template does, including a page assembled outside the request
    cycle, and this fixture is what holds it to that.
    """
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    """The demo project's overview page, rendered, as a string."""
    return client.get(reverse("overview")).content.decode()
{%- if cookiecutter.browser_tests == "yes" %}


@pytest.fixture(scope="session")
def chromium():
    """A working chromium, or a decision about what its absence means.

    On a contributor's machine a missing browser is a setup step nobody has
    run yet, and skipping says so without blocking unrelated work. In CI it is
    a hole in the suite: a checks page cannot tell a skipped test from a
    passing one, so these would report green while asserting nothing. There,
    the absence fails.
    """
    from playwright.sync_api import Error, sync_playwright

    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except (Error, ImportError) as exc:  # pragma: no cover - environment probe
        unavailable = f"no chromium available to measure the page with: {exc}"
        if os.environ.get("CI"):
            pytest.fail(
                f"{unavailable}\n\nThe tests workflow installs chromium through "
                "the shared workflow's `install-playwright` input. Reaching this "
                "means that input was dropped or its install step did not run.",
                pytrace=False,
            )
        pytest.skip(unavailable)
{%- endif %}
