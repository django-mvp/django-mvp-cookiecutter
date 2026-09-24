from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class {{ cookiecutter.import_name.title().replace('_', '') }}Config(AppConfig):
    """What a project gets when it adds this package to INSTALLED_APPS.

    The label is set explicitly rather than left to Django's default, which is
    the last segment of the module path. Two installed apps whose paths end in
    the same word collide on that default, and the error names neither of them
    clearly.
    """

    name = "{{ cookiecutter.import_name }}"
    label = "{{ cookiecutter.import_name }}"
    verbose_name = _("{{ cookiecutter.verbose_name }}")
    default_auto_field = "django.db.models.BigAutoField"
