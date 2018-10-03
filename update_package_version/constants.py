import re

VERSION_SIGNS = ['==', '<=', '>=', '<', '>']
VERSION_SIGNS_RX = '|'.join(re.escape(s) for s in VERSION_SIGNS)
PYTHON_REQUIREMENTS_PACKAGE_RX = \
    r'(?P<package>{package})' \
    fr'(?P<sign>{VERSION_SIGNS_RX})?' \
    r'(?P<version>[\-\d\.]+)?'
PYTHON_REQUIREMENTS_GIT_RX = r'(?P<package>{package})\.git@(?P<version>[\-\d\.]+)'
PYTHON_EXCLUDE_GIT_RX = r'^\s*\-e.+git.+'
PYTHON_EXCLUDE_HASH_COMMENT = r'^\s*#.+'
PYTHON_REQUIREMENTS_MATCH_PATTERNS = [
    PYTHON_REQUIREMENTS_PACKAGE_RX,
    PYTHON_REQUIREMENTS_GIT_RX
]

DEFAULT_PYTHON_CONFIG = {
    'file_patterns': [
        {
            'pattern': '**/Pipfile',
            'replacer': 'PipfileReplacer'
        },
        {
            'pattern': '**/requirements.txt',
            'replacer': 'RegexReplacer',
            'match-patterns': [PYTHON_REQUIREMENTS_PACKAGE_RX],
            'exclude-patterns': [PYTHON_REQUIREMENTS_GIT_RX, PYTHON_EXCLUDE_HASH_COMMENT]
        },
        {
            'pattern': '**/requirements.txt',
            'replacer': 'RegexReplacer',
            'match-patterns': [PYTHON_REQUIREMENTS_GIT_RX],
            'exclude-patterns': [PYTHON_EXCLUDE_HASH_COMMENT]
        },

        {
            'pattern': '**/requirements/*.txt',
            'replacer': 'RegexReplacer',
            'match-patterns': [PYTHON_REQUIREMENTS_PACKAGE_RX],
            'exclude-patterns': [PYTHON_REQUIREMENTS_GIT_RX, PYTHON_EXCLUDE_HASH_COMMENT]
        },
        {
            'pattern': '**/requirements/*.txt',
            'replacer': 'RegexReplacer',
            'match-patterns': [PYTHON_REQUIREMENTS_GIT_RX],
            'exclude-patterns': [PYTHON_EXCLUDE_HASH_COMMENT]
        },
    ],
}
