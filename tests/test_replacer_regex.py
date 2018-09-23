from tempfile import NamedTemporaryFile

import pytest
from . import conf as test_conf

from update_package_version.replacers.regex import (
    PYTHON_REGULAR_PACKAGE_RX, RegexReplacer
)

pytestmark = [pytest.mark.replacer, pytest.mark.regex]


@pytest.fixture
def sample_requirements_txt_file() -> str:
    temp_requirements_file = NamedTemporaryFile(
        prefix=test_conf.TMP_CONFIG_PREFIX,
        suffix='.txt',
        delete=False
    )
    temp_requirements_file.file.write(
        test_conf.SAMPLE_REQUIREMENTS_TXT_FILE.read_text()
    )
    temp_requirements_file.file.flush()
    return temp_requirements_file.file.name


# noinspection PyMethodMayBeStatic,PyProtectedMember
class RegexReplacerTest:
    def test_match_all(self):
        matches = RegexReplacer._match_all(
            test_conf.SAMPLE_REQUIREMENTS_TXT_FILE, [PYTHON_REGULAR_PACKAGE_RX],
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
        assert len(rr.match(test_conf.SAMPLE_REQUIREMENTS_TXT_FILE, 'sample-package', '0.0.1')) == 1

    def replace(self, sample_requirements_txt_file: str):
        rr = RegexReplacer([PYTHON_REGULAR_PACKAGE_RX])
        res = rr.replace(
            sample_requirements_txt_file, 'sample-package', '*', '1.0.0'
        )

    def teardown(self):
        pattern = test_conf.TMP_DIR.glob(f'{test_conf.TMP_CONFIG_PREFIX}')
        for file in pattern:
            file.unlink()

