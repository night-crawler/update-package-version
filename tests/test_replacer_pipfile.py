import pytest

from tempfile import NamedTemporaryFile
from update_package_version.replacers.pipfile import PipfileReplacer

from . import conf as test_conf

pytestmark = [pytest.mark.replacer, pytest.mark.pipfile]


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
    def test_init(self):
        replacer = PipfileReplacer()
        print(replacer)

    def test_match(self):
        replacer = PipfileReplacer()
        bla = replacer.match(test_conf.PIPFILE_CONFIG, 'sample-package', '*')
