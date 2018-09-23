import pytest
import re
import typing as t
from pathlib import Path

from update_package_version.replacers.regex import RegexReplacer


pytestmark = [pytest.mark.replacer, pytest.mark.regex]


DATA_DIR = Path(__file__).absolute().parent / 'data'
SAMPLE_FILE = DATA_DIR/'dir1/dir2/dir3/dir4'/'requirements4.txt'


# noinspection PyMethodMayBeStatic,PyProtectedMember
class RegexReplacerTest:
    def test_match_all(self):
        signs = '|'.join(re.escape(s) for s in ['==', '<=', '>=', '<', '>'])
        match_pattern = \
            r'(?P<package>{package})' \
            fr'(?P<sign>{signs})' \
            r'(?P<version>[\-\d\.]+)'

        matches = RegexReplacer._match_all(
            SAMPLE_FILE, [match_pattern],
            'sample-package', '*'
        )
        assert matches, 'There are should be matches'
        assert all(matches), 'All matches should be truthy'
        assert all(m.line for m in matches), 'There should be no empty lines'

    def test__validate(self):
        with pytest.raises(RuntimeError):
            # this regex should fail
            RegexReplacer._validate_match_patterns([r'(?P<{package}>)==(?P<version>[\-\d\.]+)'])

        # no named group
        # RegexReplacer._validate_match_patterns([r'{package}==(?P<version>[\-\d\.]+)'])
