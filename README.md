# django-mvp-cookiecutter

A [cookiecutter](https://github.com/cookiecutter/cookiecutter) template for
packages that extend [django-mvp](https://github.com/django-mvp/django-mvp).

It generates a package that installs, tests green, and runs in a browser on the
first try — with the CI, release flow, linting, coverage gating and
documentation structure already in place.

## Use it

```bash
uvx cookiecutter gh:django-mvp/django-mvp-cookiecutter
```

`uvx` runs it without installing anything globally.

Then:

```bash
cd <your-package>
uv sync
uv run pytest
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

The suite passes and the demo project runs before you have written anything.

## What it asks

| Prompt | Example | Notes |
|---|---|---|
| `distribution_name` | `django-mvp-charts` | The package name and the repository name |
| `import_name` | `mvp_charts` | The directory Python imports and the Django app label. Defaulted from the distribution name; override it when the default reads badly |
| `description` | `Charts for django-mvp projects` | One sentence. Lands in the package metadata, the README, and the demo project |
| `verbose_name` | `Charts` | How the app names itself in the admin and in menus. Defaulted from the import name |
| `browser_tests` | `no` | Choose `yes` if this package's behaviour can only be measured in a real browser — a resolved height, a computed colour, a script that runs |

That is the whole list, deliberately. Everything else is fixed, because a
choice offered here is a way for two packages to end up different for no
reason. If something fixed is wrong for your package, change it after
generating — it is your repository at that point.

## What you get

```
<distribution-name>/
├── <import_name>/          the package: app config and Cotton components
├── demo/                   a Django project on django-mvp's shell, not distributed
├── tests/                  suite inheriting the demo's settings
├── docs/
│   ├── adr/                decision records, with the format documented
│   ├── agents/             issue tracker, labels, domain docs
│   └── ROADMAP.md
├── .github/workflows/      build, tests, and the three-step release flow
├── AGENTS.md CONTEXT.md GOALS.md CONSTITUTION.md README.md CHANGELOG.md
└── pyproject.toml uv.lock codecov.yml ruff-base.toml .pre-commit-config.yaml
```

`CONSTITUTION.md` arrives filled in: the standards apply to every package built
this way, and articles XII onward are yours to write.

`AGENTS.md`, `CONTEXT.md`, `GOALS.md`, `docs/ROADMAP.md` and `README.md` arrive
as shells — the headings and the house style, with a note in each section
saying what belongs there and what does not. They are written to be usable by a
coding agent as well as by a person: an agent reading `GOALS.md` should be able
to tell a goal from a task without being told.

Replace the guidance blocks as you fill each file in, and delete them when the
section is real.

## Keeping up with the standard

The generated package pins the shared workflows and the shared tooling bundle
to one release tag. Two things keep that honest:

- **On every push**, CI generates a package, installs it, and runs its tests,
  its linters and its build. The claim this repository makes is about what
  comes out of it, so that is what gets tested.
- **Weekly**, a separate job fails when the pinned toolchain tag or the
  django-mvp floor has fallen behind the latest release. Dependabot cannot read
  a pin that lives inside a template, so without this the repository would go
  stale silently. It does not run on pull requests: an upstream release that
  landed yesterday has nothing to do with the change under review.

## License

MIT.
