"""What the template produces, asserted without installing anything."""

# Whether a generated package installs and passes its own suite is answered by
# .github/workflows/ci.yml, which does exactly that.

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
    return generate(tmp_path_factory.mktemp("default"))


class TestGeneratedLayout:
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
            "docs/contributing/standards/testing.md",
            "docs/contributing/standards/code-documentation.md",
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
            "tests/test_smoke.py",
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
        # Cotton renders a tag it cannot resolve as empty output, so a mismatch
        # breaks every tag with no error.
        namespace = generated / "mvp_example" / "templates" / "cotton" / "mvp_example"
        assert namespace.is_dir()

    def test_the_demo_project_is_not_packaged(self, generated: Path) -> None:
        # An exact list: a second entry here reaches every install.
        import tomllib

        pyproject = tomllib.loads((generated / "pyproject.toml").read_text())
        assert pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == [
            "mvp_example"
        ]

    def test_the_package_is_born_locked(self, generated: Path) -> None:
        # The shared build installs with `uv sync --locked`, which needs a lock.
        assert (generated / "uv.lock").is_file()
        assert not (generated / "poetry.lock").exists()

    def test_the_source_distribution_lists_only_what_ships(
        self, generated: Path
    ) -> None:
        # Anchored entries, so `/README.md` cannot also match `tests/README.md`.
        import tomllib

        pyproject = tomllib.loads((generated / "pyproject.toml").read_text())
        sdist = pyproject["tool"]["hatch"]["build"]["targets"]["sdist"]
        assert sdist["include"] == ["/mvp_example", "/README.md", "/LICENSE"]


class TestNothingIsLeftUnrendered:
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
        # An expression rendered away still runs, with an empty secret.
        workflow = (generated / ".github/workflows/tag-release.yml").read_text()
        assert "${{ secrets.RELEASE_TOKEN }}" in workflow

    def test_the_standards_documents_are_copied_unrendered(
        self, generated: Path
    ) -> None:
        for name in ("testing.md", "code-documentation.md"):
            relative_path = Path("docs/contributing/standards") / name
            source = TEMPLATE / "{{cookiecutter.distribution_name}}" / relative_path
            assert (generated / relative_path).read_text() == source.read_text()

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
        # django-accounts-center imports as `dac`, which nothing could derive.
        generated = generate(
            tmp_path, distribution_name="django-accounts-center", import_name="dac"
        )
        assert (generated / "dac" / "apps.py").is_file()


class TestBrowserTests:
    def test_they_are_absent_by_default(self, generated: Path) -> None:
        assert (
            "TestOverviewPageInABrowser"
            not in (generated / "tests/test_demo.py").read_text()
        )
        assert (
            "install-playwright"
            not in (generated / ".github/workflows/tests.yml").read_text()
        )
        assert "playwright" not in (generated / "pyproject.toml").read_text()

    def test_asking_for_them_wires_the_whole_chain(self, tmp_path: Path) -> None:
        # Any one link missing turns these tests into skips, which a checks page
        # cannot tell from passes.
        generated = generate(tmp_path, browser_tests="yes")

        assert (
            "TestOverviewPageInABrowser"
            in (generated / "tests/test_demo.py").read_text()
        )
        assert (
            "install-playwright: true"
            in (generated / ".github/workflows/tests.yml").read_text()
        )

        pyproject = (generated / "pyproject.toml").read_text()
        assert "pytest-playwright" in pyproject
        assert "DJANGO_ALLOW_ASYNC_UNSAFE=1" in pyproject

        assert "def chromium" in (generated / "tests/conftest.py").read_text()


class TestNoPrivateToolConfig:
    def test_pyproject_configures_only_public_tools(self, tmp_path: Path) -> None:
        # A table for a tool nobody can look up gets copied blindly or deleted.
        import tomllib

        for browser_tests in ("no", "yes"):
            generated = generate(tmp_path / browser_tests, browser_tests=browser_tests)
            tables = tomllib.loads((generated / "pyproject.toml").read_text())["tool"]
            assert sorted(tables) == [
                "coverage",
                "deptry",
                "django-stubs",
                "djlint",
                "hatch",
                "mypy",
                "pytest",
                "ruff",
                "uv",
            ]


class TestNamesAreValidated:
    @pytest.mark.parametrize(
        "import_name",
        ["9lives", "has-hyphens", "class", "Capitals", "with space"],
    )
    def test_an_unusable_import_name_is_refused(
        self, tmp_path: Path, import_name: str
    ) -> None:
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
        # A misplaced placeholder only fails when something imports the file.
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
    # The import name's length decides how the formatter wraps lines. These two
    # names sit either side of that, so one of them catches a wrong wrap.

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
        # A workflow on an older tag than the bundle still runs, against two
        # versions of the toolchain.
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
        # Tag Release fires on any push touching pyproject.toml, and only the
        # absence of a matching version section stops it.
        changelog = (generated / "CHANGELOG.md").read_text()
        assert "## [Unreleased]" in changelog
        assert "## [0.0.1]" not in changelog
