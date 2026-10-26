#!/usr/bin/env python
"""Django CLI. Le projet s'exécute exclusivement sous Python 3.12."""
import os
import sys


def main():
    if sys.version_info[:2] != (3, 12):
        raise SystemExit("Python 3.12 requis. Utilisez Docker Compose ou py -3.12.")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
