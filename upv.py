#!/usr/bin/env python

"""
It's just a convenient development wrapper. Don't use it in production.

    .. note::
        PEP 338 -- Executing modules as scripts
        https://www.python.org/dev/peps/pep-0338/
"""


from update_package_version.cli import main

if __name__ == '__main__':
    main()
