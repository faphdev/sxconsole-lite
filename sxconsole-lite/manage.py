#!/usr/bin/env python
'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sxconsole.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
