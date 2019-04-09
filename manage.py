#!/usr/bin/env python
import os
import sys

# activating the local virtual env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
activate_this = os.path.abspath(os.path.join(BASE_DIR, 'env', 'bin', 'activate_this.py'))
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djtest.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
