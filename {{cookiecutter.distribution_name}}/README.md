# {{ cookiecutter.distribution_name }}

{{ cookiecutter.description }}

<!--
  The README is this package's charter, and it is read in two places: on the
  repository page and on the package index. Write it for someone deciding
  whether to install this, who has not read anything else here.

  Every link is absolute. A relative link resolves on GitHub and 404s on PyPI,
  which is where the person deciding is most likely to be standing.

  Badges go here once the repository is public — the dynamic ones read the
  GitHub API anonymously and render as "404" or "invalid" against a private
  repository, which looks worse than having none.

  Sections, in this order:
    1. One sentence, above. What it does, for whom.
    2. Scope & philosophy — below. What it is and is not, and the principles
       that settle a close call.
    3. Installation.
    4. Quickstart — the smallest thing that works, end to end.
    5. The public surface, in full. For a package this small, list it.
    6. Anything genuinely surprising: what it deliberately does not do, what it
       leaves to the host project, and the failure modes that are quiet.

  Keep the CHANGELOG out of it. Link to it instead.
-->

## Scope & philosophy

<!--
  What this package is for, what it stays out of, and how a close call gets
  settled. Three short paragraphs at most.

  The useful sentences are the exclusions: "it renders markup and nothing else
  — no models, no views, no URLs" saves a reader the ten minutes they would
  otherwise spend finding out. Then the tension-breaker: when two reasonable
  designs conflict, which value wins here.

  This section and GOALS.md do different jobs. This one says what the package
  *is*; GOALS.md says what it is trying to become good at.
-->

## Installation

```bash
pip install {{ cookiecutter.distribution_name }}
```

Then add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    # ...
    "mvp",
    "{{ cookiecutter.import_name }}",
]
```

This package requires [django-mvp](https://github.com/django-mvp/django-mvp).
It renders inside django-mvp's layout and reads its colours from the theme
django-mvp supplies, so it does nothing useful on its own.

## Quickstart

<!--
  The smallest complete example: what goes in the view, what goes in the
  template, and what appears on the page. Real code that runs, not a sketch.
  If the example needs three files, show three files.
-->

## Public surface

<!--
  Everything a host project can touch: components and their attributes,
  settings, template tags, models, views. Being able to list it exhaustively is
  a feature of a package this size, and the list is what makes an addition to
  it a deliberate decision rather than a side effect.
-->

## Contributing

Standards for this repository live in
[CONSTITUTION.md](https://github.com/{{ cookiecutter._github_owner }}/{{ cookiecutter.distribution_name }}/blob/main/CONSTITUTION.md),
and the vocabulary to use in issues and commits lives in
[CONTEXT.md](https://github.com/{{ cookiecutter._github_owner }}/{{ cookiecutter.distribution_name }}/blob/main/CONTEXT.md).

```bash
poetry install
poetry run pytest
poetry run pre-commit install
```

`demo/` is a Django project on django-mvp's application shell, for looking at
this package in a browser while working on it:

```bash
poetry run python manage.py migrate
poetry run python manage.py seed_demo
poetry run python manage.py runserver
```

## License

MIT. See [LICENSE](https://github.com/{{ cookiecutter._github_owner }}/{{ cookiecutter.distribution_name }}/blob/main/LICENSE).
