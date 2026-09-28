"""The demo project's pages, asserted as rendered."""

# Everything in the demo fails quietly: an unresolvable component renders empty
# and a menu entry whose URL will not resolve is dropped from the tree.

{% if cookiecutter.browser_tests == "yes" %}import pytest
{% endif %}from django.urls import reverse


class TestOverviewPage:
    def test_it_responds(self, client, db) -> None:
        assert client.get(reverse("overview")).status_code == 200

    def test_the_shell_wraps_it(self, overview_page: str) -> None:
        # A template that fails to extend the shell still returns 200.
        assert 'aria-label="Main navigation"' in overview_page

    def test_the_sidebar_links_the_pages_that_exist(self, overview_page: str) -> None:
        sidebar = overview_page.split('aria-label="Main navigation"', 1)[1]
        sidebar = sidebar.split("</ul>", 1)[0]
        assert f'href="{reverse("overview")}"' in sidebar
{%- if cookiecutter.browser_tests == "yes" %}


@pytest.mark.django_db
class TestOverviewPageInABrowser:
    # Only what a real browser can measure belongs here. A check that works on
    # rendered HTML goes in the class above, which cannot skip.

    def test_the_page_loads_without_a_console_error(
        self, chromium, live_server, page
    ) -> None:
        # A script that throws leaves the markup intact and the page broken.
        errors: list[str] = []
        page.on("pageerror", lambda exception: errors.append(str(exception)))

        page.goto(live_server.url + reverse("overview"))

        assert errors == []
{%- endif %}
