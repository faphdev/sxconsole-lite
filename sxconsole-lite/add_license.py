#! /usr/bin/env python

'''
Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: see LICENSE.md for more details.
'''

import subprocess


license = (
    'Copyright (c) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>\n'
    'License: see LICENSE.md for more details.\n')


def __main__():
    files = subprocess.check_output(['git', 'ls-files', '*.py']).splitlines()
    for name in files:
        process_file(name)


def process_file(name):
    with open(name) as f:
        content = f.read()
    if content and license not in content:
        add_header(name, content)
        print 'Added license header to', name


def add_header(name, content):
    lines = content.splitlines(True)  # keepends=True
    position, new_string = get_header_position(lines)

    if new_string:
        new_license = "'''\n{}'''\n\n".format(license)
    else:
        new_license = license + '\n* * *\n\n'

    lines.insert(position, new_license)
    with open(name, 'w') as f:
        f.write(''.join(lines).lstrip())


def get_header_position(lines):
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        elif line in ('"""', "'''"):
            return i + 1, False
        else:
            return i, True
    else:
        return len(lines) - 1, True


if __name__ == '__main__':
    __main__()
