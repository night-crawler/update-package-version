import pytest

from shutil import rmtree
from tempfile import NamedTemporaryFile

from update_package_version.constants import (
    PYTHON_REQUIREMENTS_MATCH_PATTERNS, PYTHON_REQUIREMENTS_PACKAGE_RX
)
from update_package_version.replacers.regex import RegexReplacer

from . import conf as test_conf

pytestmark = [pytest.mark.replacer, pytest.mark.regex]


@pytest.fixture
def sample_requirements_txt_file() -> str:
    temp_requirements_file = NamedTemporaryFile(
        prefix=test_conf.TMP_CONFIG_PREFIX,
        suffix='.txt',
        delete=False
    )
    temp_requirements_file.file.write(
        test_conf.SAMPLE_REQUIREMENTS_TXT_FILE.read_bytes()
    )
    temp_requirements_file.close()
    return temp_requirements_file.name


# noinspection PyMethodMayBeStatic,PyProtectedMember
class RegexReplacerTest:
    def test_match_all(self):
        matches = RegexReplacer([PYTHON_REQUIREMENTS_PACKAGE_RX])._match_all(
            test_conf.SAMPLE_REQUIREMENTS_TXT_FILE,
            'sample-package', '*'
        )
        assert matches, 'There are should be matches'
        assert all(matches), 'All matches should be truthy'
        assert all(m.line for m in matches), 'There are should be no empty lines'

    def test__validate(self):
        with pytest.raises(RuntimeError):
            # this regex should fail
            RegexReplacer._validate_patterns([r'(?P<{package}>)==(?P<version>[\-\d\.]+)'])

        # no named group
        # RegexReplacer._validate_match_patterns([r'{package}==(?P<version>[\-\d\.]+)'])

    def test_match(self):
        rr = RegexReplacer(
            [PYTHON_REQUIREMENTS_PACKAGE_RX],
        )
        assert len(rr.match(test_conf.SAMPLE_REQUIREMENTS_TXT_FILE, 'sample-package', '0.0.1')) == 1

    def test_prepare_replace_map_wildcard(self, sample_requirements_txt_file: str):
        rr = RegexReplacer(
            [PYTHON_REQUIREMENTS_PACKAGE_RX],
            exclude_patterns=[r'^\s*\-e.+']
        )
        match_bundles = rr.match(sample_requirements_txt_file, 'sample-package', '*')
        replace_map = rr._prepare_replace_map(match_bundles, '1.1.1')

        for replacement in replace_map.values():
            assert '1.1.1' in replacement.right
            assert '0.0' not in replacement.right

    def test_prepare_replace_specific(self, sample_requirements_txt_file: str):
        rr = RegexReplacer([PYTHON_REQUIREMENTS_PACKAGE_RX])

        match_bundles = rr.match(sample_requirements_txt_file, 'sample-package', '0.0.2')
        replace_map = rr._prepare_replace_map(match_bundles, '1.1.1')

        assert len(replace_map) == 1

    def test_replace_in_file(self, sample_requirements_txt_file: str):
        rr = RegexReplacer(
            PYTHON_REQUIREMENTS_MATCH_PATTERNS,
        )
        replaced_count = rr.replace(
            sample_requirements_txt_file, 'sample-package', '*', '1.1.1'
        )

        assert replaced_count
        for line in open(sample_requirements_txt_file).readlines():
            if not line.strip():
                continue
            assert '1.1.1' in line
            assert '0.0' not in line

    def teardown(self):
        pattern = test_conf.TMP_DIR.glob(f'{test_conf.TMP_CONFIG_PREFIX}*')
        for path in pattern:
            if path.is_file():
                path.unlink()
            else:
                rmtree(path)
