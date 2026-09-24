"""What can only be measured in a real browser.

A rendered page is a string. Anything that depends on the browser resolving
it — a computed height, an element that moves when the window does, a script
that runs — is invisible to an assertion against markup, and a class name is
never evidence about the box it produces.

Keep this file for those questions only. A test that could be written against
rendered HTML belongs in the suite that runs without a browser, where it is
faster and cannot skip.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestOverviewPageInABrowser:
    def test_the_page_loads_without_a_console_error(
        self, chromium, live_server, page
    ) -> None:
        """A script that throws leaves the markup intact and the page broken.

        Nothing on the server side notices, and neither does a test that reads
        the response body.
        """
        errors: list[str] = []
        page.on("pageerror", lambda exception: errors.append(str(exception)))

        page.goto(live_server.url + reverse("overview"))

        assert errors == []
