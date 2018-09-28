import re

VERSION_SIGNS = '|'.join(re.escape(s) for s in ['==', '<=', '>=', '<', '>'])
PYTHON_REGULAR_PACKAGE_RX = \
    r'(?P<package>{package})' \
    fr'(?P<sign>{VERSION_SIGNS})?' \
    r'(?P<version>[\-\d\.]+)?'
PYTHON_GIT_RX = r'(?P<package>{package})\.git@(?P<version>[\-\d\.]+)'
PYTHON_EXCLUDE_GIT_RX = r'^\s*\-e.+git.+'
DEFAULT_PYTHON_MATCH_PATTERNS = [
    PYTHON_REGULAR_PACKAGE_RX,
    PYTHON_GIT_RX
]

DEFAULT_PYTHON_CONFIG = {
    'file_patterns': [
        # {
        #     'pattern': 'Pipfile',
        #     'replacer': 'PipfileReplacer'
        # },
        {
            'pattern': '**/requirements.txt',
            'replacer': 'RegexReplacer'
        },
        {
            'pattern': '**/requirements/*.txt',
            'replacer': 'RegexReplacer'
        }
    ],
}
