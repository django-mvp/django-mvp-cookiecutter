"""What the template produces, asserted without installing anything.

These run in a second and cover the failures that are cheap to make and
expensive to find: a placeholder that never got substituted, a file that should
not have been generated, a name derived wrongly. Whether the generated package
actually installs and passes its own suite is a separate question, answered by
the workflow in .github/workflows/ci.yml, which does exactly that.
"""

import json
import subprocess
from pathlib import Path

import pytest
from cookiecutter.exceptions import FailedHookException
from cookiecutter.main import cookiecutter

TEMPLATE = Path(__file__).resolve().parent.parent

TEXT_SUFFIXES = {".py", ".toml", ".md", ".yml", ".yaml", ".html", ".cfg", ".txt"}


def generate(output_dir: Path, **context) -> Path:
    """Generate a package and return its directory."""
    return Path(
        cookiecutter(
            str(TEMPLATE),
            no_input=True,
            output_dir=str(output_dir),
            extra_context=context,
        )
    )


def text_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in TEXT_SUFFIXES
    ]


@pytest.fixture(scope="module")
def generated(tmp_path_factory) -> Path:
    """One package generated with the defaults, shared across the read-only tests."""
    return generate(tmp_path_factory.mktemp("default"))


class TestGeneratedLayout:
    """The files a package cannot work without."""

    @pytest.mark.parametrize(
        "relative_path",
        [
            "pyproject.toml",
            "README.md",
            "CONSTITUTION.md",
            "AGENTS.md",
            "CONTEXT.md",
            "GOALS.md",
            "CHANGELOG.md",
            "LICENSE",
            "manage.py",
            "codecov.yml",
            "ruff-base.toml",
            ".gitignore",
            ".pre-commit-config.yaml",
            "docs/ROADMAP.md",
            "docs/adr/README.md",
            "docs/agents/domain.md",
            "docs/agents/issue-tracker.md",
            "docs/agents/triage-labels.md",
            ".github/dependabot.yml",
            ".github/workflows/build.yml",
            ".github/workflows/tests.yml",
            ".github/workflows/prepare-release.yml",
            ".github/workflows/tag-release.yml",
            ".github/workflows/publish.yml",
            ".github/workflows/auto-merge-dependabot.yml",
            "demo/settings.py",
            "demo/urls.py",
            "demo/views.py",
            "demo/menus.py",
            "demo/apps.py",
            "demo/wsgi.py",
            "demo/management/commands/seed_demo.py",
            "demo/templates/base.html",
            "demo/templates/demo/overview.html",
            "tests/conftest.py",
            "tests/settings.py",
            "tests/test_app.py",
            "tests/test_demo.py",
        ],
    )
    def test_it_is_generated(self, generated: Path, relative_path: str) -> None:
        assert (generated / relative_path).is_file()

    def test_the_package_directory_is_named_for_the_import_name(
        self, generated: Path
    ) -> None:
        assert (generated / "mvp_example" / "apps.py").is_file()

    def test_the_cotton_namespace_matches_the_import_name(
        self, generated: Path
    ) -> None:
        """The directory name is the first segment of every tag this ships.

        Cotton renders a component it cannot resolve as empty output rather
        than raising, so a mismatch here breaks every tag with no error.
        """
        namespace = generated / "mvp_example" / "templates" / "cotton" / "mvp_example"
        assert namespace.is_dir()

    def test_the_demo_project_is_not_packaged(self, generated: Path) -> None:
        """`demo/` is a place to look at the package, not something to ship.

        Asserted as an exact list rather than as the absence of the word
        "demo": a second entry added here reaches every install, and the
        difference between one entry and two is the whole point.
        """
        import tomllib

        pyproject = tomllib.loads((generated / "pyproject.toml").read_text())
        assert pyproject["tool"]["poetry"]["packages"] == [{"include": "mvp_example"}]


class TestNothingIsLeftUnrendered:
    """The failure that survives every other check by looking like content."""

    def test_no_placeholder_survives(self, generated: Path) -> None:
        offenders = [
            str(path.relative_to(generated))
            for path in text_files(generated)
            if "cookiecutter." in path.read_text(encoding="utf-8")
        ]
        assert offenders == []

    def test_no_unsubstituted_date_survives(self, generated: Path) -> None:
        offenders = [
            str(path.relative_to(generated))
            for path in text_files(generated)
            if "__GENERATED_DATE__" in path.read_text(encoding="utf-8")
        ]
        assert offenders == []

    def test_the_constitution_is_dated(self, generated: Path) -> None:
        from datetime import date

        footer = (generated / "CONSTITUTION.md").read_text().strip().splitlines()[-1]
        assert date.today().isoformat() in footer

    def test_github_expressions_survived(self, generated: Path) -> None:
        """A `${{ }}` expression rendered away is a workflow that silently misfires.

        It stays valid YAML and the job still runs — with an empty secret.
        """
        workflow = (generated / ".github/workflows/tag-release.yml").read_text()
        assert "${{ secrets.RELEASE_TOKEN }}" in workflow

    def test_django_template_syntax_survived(self, generated: Path) -> None:
        component = (
            generated / "mvp_example/templates/cotton/mvp_example/example.html"
        ).read_text()
        assert "{{ slot }}" in component
        assert "{{ attrs }}" in component


class TestImportNameIsDerived:
    @pytest.mark.parametrize(
        ("distribution_name", "expected"),
        [
            ("django-mvp-charts", "mvp_charts"),
            ("django-mvp-compliance", "mvp_compliance"),
            ("django-accounts-center", "accounts_center"),
            ("daisy-cotton", "daisy_cotton"),
        ],
    )
    def test_the_default_drops_the_django_prefix(
        self, tmp_path: Path, distribution_name: str, expected: str
    ) -> None:
        generated = generate(tmp_path, distribution_name=distribution_name)
        assert (generated / expected / "apps.py").is_file()

    def test_an_override_wins(self, tmp_path: Path) -> None:
        """django-accounts-center imports as `dac`, which nothing could derive."""
        generated = generate(
            tmp_path, distribution_name="django-accounts-center", import_name="dac"
        )
        assert (generated / "dac" / "apps.py").is_file()


class TestBrowserTests:
    def test_they_are_absent_by_default(self, generated: Path) -> None:
        assert not (generated / "tests/test_browser.py").exists()
        assert (
            "install-playwright"
            not in (generated / ".github/workflows/tests.yml").read_text()
        )
        assert "playwright" not in (generated / "pyproject.toml").read_text()

    def test_asking_for_them_wires_the_whole_chain(self, tmp_path: Path) -> None:
        """The test file alone is not enough, and it fails quietly without the rest.

        Without the CI input there is no browser, without the dependency there
        is no playwright, and without the async-unsafe setting the database
        never builds. Any one missing turns these into skips, which a checks
        page cannot tell from passes.
        """
        generated = generate(tmp_path, browser_tests="yes")

        assert (generated / "tests/test_browser.py").is_file()
        assert (
            "install-playwright: true"
            in (generated / ".github/workflows/tests.yml").read_text()
        )

        pyproject = (generated / "pyproject.toml").read_text()
        assert "pytest-playwright" in pyproject
        assert "DJANGO_ALLOW_ASYNC_UNSAFE=1" in pyproject

        assert "def chromium" in (generated / "tests/conftest.py").read_text()

    def test_the_conformance_declaration_follows_the_test_file(
        self, tmp_path: Path
    ) -> None:
        with_browser = generate(tmp_path / "yes", browser_tests="yes")
        without = generate(tmp_path / "no", browser_tests="no")

        assert "tests/test_browser.py" in (with_browser / "pyproject.toml").read_text()
        assert "tests/test_browser.py" not in (without / "pyproject.toml").read_text()


class TestNamesAreValidated:
    @pytest.mark.parametrize(
        "import_name",
        ["9lives", "has-hyphens", "class", "Capitals", "with space"],
    )
    def test_an_unusable_import_name_is_refused(
        self, tmp_path: Path, import_name: str
    ) -> None:
        """Refused before anything is written, not by Django three steps later."""
        with pytest.raises(FailedHookException):
            generate(tmp_path, import_name=import_name)

    def test_an_unusable_distribution_name_is_refused(self, tmp_path: Path) -> None:
        with pytest.raises(FailedHookException):
            generate(tmp_path, distribution_name="-leading-hyphen")

    def test_a_usable_name_is_accepted(self, tmp_path: Path) -> None:
        generated = generate(tmp_path, distribution_name="django-mvp-thing")
        assert generated.is_dir()


class TestGeneratedPythonParses:
    def test_every_module_compiles(self, generated: Path) -> None:
        """A placeholder in the wrong place produces a file Python cannot read.

        Nothing else here would notice: the text is present, the path is right,
        and it only fails when something imports it.
        """
        modules = [str(path) for path in generated.rglob("*.py")]
        result = subprocess.run(
            ["python", "-m", "py_compile", *modules],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr

    def test_the_config_files_parse(self, generated: Path) -> None:
        import tomllib

        import yaml

        tomllib.loads((generated / "pyproject.toml").read_text())
        for path in (generated / ".github").rglob("*.yml"):
            yaml.safe_load(path.read_text())


class TestGeneratedCodeIsAlreadyClean:
    """The generated tree passes its own linters before anyone touches it.

    This is not a nicety. The import name is substituted into expressions whose
    length then decides how the formatter wraps them, so a template that is
    correctly formatted for a short name can be wrongly formatted for a long
    one. The two names below are chosen to sit either side of that: whichever
    way a line wraps, one of them catches it.

    Without this, the first thing a new package does is fail its own lint gate,
    and the fix looks like a bug in the code rather than in the template.
    """

    @pytest.mark.parametrize("import_name", ["dac", "mvp_a_deliberately_long_name"])
    @pytest.mark.parametrize("browser_tests", ["no", "yes"])
    def test_the_formatter_has_nothing_to_say(
        self, tmp_path: Path, import_name: str, browser_tests: str
    ) -> None:
        generated = generate(
            tmp_path / f"{import_name}-{browser_tests}",
            import_name=import_name,
            browser_tests=browser_tests,
        )
        result = subprocess.run(
            ["ruff", "format", "--check", "."],
            cwd=generated,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    @pytest.mark.parametrize("import_name", ["dac", "mvp_a_deliberately_long_name"])
    @pytest.mark.parametrize("browser_tests", ["no", "yes"])
    def test_the_linter_has_nothing_to_say(
        self, tmp_path: Path, import_name: str, browser_tests: str
    ) -> None:
        generated = generate(
            tmp_path / f"lint-{import_name}-{browser_tests}",
            import_name=import_name,
            browser_tests=browser_tests,
        )
        result = subprocess.run(
            ["ruff", "check", "--no-fix", "."],
            cwd=generated,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr


class TestPinsAreConsistent:
    def test_every_shared_reference_uses_the_declared_tag(
        self, generated: Path
    ) -> None:
        """One tag versions the whole toolchain.

        A workflow left on an older tag than the dependency bundle is the
        quietest kind of drift: everything still runs, against two different
        versions of the standard.
        """
        tag = json.loads((TEMPLATE / "cookiecutter.json").read_text())["_shared_tag"]

        referencing = [
            *(generated / ".github/workflows").rglob("*.yml"),
            generated / "pyproject.toml",
        ]
        for path in referencing:
            text = path.read_text()
            if "django-mvp/shared" not in text:
                continue
            for line in text.splitlines():
                if "django-mvp/shared" in line and "@" in line:
                    assert f"@{tag}" in line, f"{path.name}: {line.strip()}"

    def test_the_changelog_has_no_version_heading(self, generated: Path) -> None:
        """A version heading here makes the first push cut a release nobody prepared.

        Tag Release fires on any push to main touching pyproject.toml, and the
        absence of a matching `## [X.Y.Z]` section is the only thing stopping
        it.
        """
        changelog = (generated / "CHANGELOG.md").read_text()
        assert "## [Unreleased]" in changelog
        assert "## [0.0.1]" not in changelog
