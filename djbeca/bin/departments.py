#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys

import django


django.setup()

from djimix.people.departments import department as dept_name
from djtools.utils.workday import department_detail
from djbeca.core.models import Proposal

# env
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djbeca.settings.shell')


# set up command-line options
desc = "Use --test flag to execute without database modifications."

# RawTextHelpFormatter method allows for new lines in help text
parser = argparse.ArgumentParser(
    description=desc, formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    '--test',
    action='store_true',
    help="Dry run?",
    dest='test',
)


def main():
    """Update department field to conform to workday infrastructure."""
    proposals = Proposal.objects.all().order_by('department')
    for obj in proposals:
        code = obj.department.strip()
        dept = department_detail(code)
        if dept:
            if test:
                print(dept['code'], dept['name'], dept['id'])
            else:
                obj.department = dept['id']
                obj.save()
        else:
            if test:
                name = dept_name(code)
                print(
                    'fail: {0}|{1}|{2}|{3}|{4}'.format(
                        code, name, obj.user.username, obj.created_at, obj.id,
                    ),
                )
            else:
                obj.department = ''
                obj.save()


if __name__ == '__main__':
    args = parser.parse_args()
    test = args.test

    if test:
        print(args)

    sys.exit(main())
