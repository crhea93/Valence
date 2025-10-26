#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    # Check environment variables to determine which settings to use
    if os.getenv("DJANGO_LOCAL"):
        settings_module = "cognitiveAffectiveMaps.settings_local"
    elif os.getenv("DJANGO_DEVELOPMENT"):
        settings_module = "cognitiveAffectiveMaps.settings_dev"
    else:
        settings_module = "cognitiveAffectiveMaps.settings"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
