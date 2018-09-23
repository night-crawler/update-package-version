import pytest

from pathlib import Path

from update_package_version.replacers.regex import (
    PYTHON_REGULAR_PACKAGE_RX, RegexReplacer
)

pytestmark = [pytest.mark.replacer, pytest.mark.regex]


DATA_DIR = Path(__file__).absolute().parent / 'data'
SAMPLE_FILE = DATA_DIR/'dir1/dir2/dir3/dir4'/'requirements4.txt'


# noinspection PyMethodMayBeStatic,PyProtectedMember
class RegexReplacerTest:
    def test_match_all(self):
        matches = RegexReplacer._match_all(
            SAMPLE_FILE, [PYTHON_REGULAR_PACKAGE_RX],
            'sample-package', '*'
        )
        assert matches, 'There are should be matches'
        assert all(matches), 'All matches should be truthy'
        assert all(m.line for m in matches), 'There are should be no empty lines'

    def test__validate(self):
        with pytest.raises(RuntimeError):
            # this regex should fail
            RegexReplacer._validate_match_patterns([r'(?P<{package}>)==(?P<version>[\-\d\.]+)'])

        # no named group
        # RegexReplacer._validate_match_patterns([r'{package}==(?P<version>[\-\d\.]+)'])

    def test_match(self):
        rr = RegexReplacer(
            [PYTHON_REGULAR_PACKAGE_RX],
        )
        assert len(rr.match(SAMPLE_FILE, 'sample-package', '0.0.1')) == 1
