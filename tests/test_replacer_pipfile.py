import pytest

from pathlib import Path
from shutil import rmtree
from tempfile import NamedTemporaryFile

from update_package_version.replacers.pipfile import (
    PipfilePackage, PipfileParser, PipfileReplacer
)

from . import conf as test_conf

pytestmark = [pytest.mark.replacer, pytest.mark.pipfile]


@pytest.fixture
def sample_repo_package() -> PipfilePackage:
    version = {
        'git': 'https://secret-token@github.com/some-user/sample-package.git',
        'editable': True,
        'ref': '0.2.0'
    }
    return PipfilePackage('sample-package', 'dev-packages', version=version)


@pytest.fixture
def sample_regular_package() -> PipfilePackage:
    version = '>=1.2.3'
    return PipfilePackage('sample-package', 'dev-packages', version=version)


@pytest.fixture
def sample_pipfile() -> str:
    temp_requirements_file = NamedTemporaryFile(
        prefix=test_conf.TMP_CONFIG_PREFIX,
        suffix='.tmp',
        delete=False
    )
    temp_requirements_file.file.write(
        test_conf.PIPFILE_CONFIG.read_bytes()
    )
    temp_requirements_file.close()
    return temp_requirements_file.name


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PipfilePackagePTest:
    pytestmark = [pytest.mark.parser, pytest.mark.pipfile, pytest.mark.package]

    def test_init(self):
        assert PipfilePackage('sample-package', 'dev-packages')
        assert PipfilePackage('sample', version='*', section='dev-packages')
        assert PipfilePackage('sample-package', section='packages', version='*').version == '*'

    def test_is_repo(self, sample_repo_package: PipfilePackage, sample_regular_package: PipfilePackage):
        assert sample_repo_package.is_repo
        assert not sample_regular_package.is_repo

    def test_get_version(self, sample_repo_package: PipfilePackage):
        assert sample_repo_package.get_version() == sample_repo_package.raw_version

    def test_update_version(self, sample_repo_package: PipfilePackage, sample_regular_package: PipfilePackage):
        updated_version = sample_repo_package.set_version('2.2.2')
        assert updated_version['ref'] == '2.2.2'
        assert sample_repo_package.version == '2.2.2'

        updated_version = sample_regular_package.set_version('3.3.3')
        assert updated_version == '>=3.3.3'
        assert sample_regular_package.version == '3.3.3'


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PipfileParserTest:
    pytestmark = [pytest.mark.parser, pytest.mark.pipfile]

    def test_parse(self):
        parser = PipfileParser(test_conf.PIPFILE_CONFIG)
        assert parser._parse()

    def test_packages(self):
        parser = PipfileParser(test_conf.PIPFILE_CONFIG)
        assert parser.packages
        assert parser.dev_packages

    def test_filter(self):
        parser = PipfileParser(test_conf.PIPFILE_CONFIG)
        assert parser.filter('sample-package', '*')
        assert len(parser.filter('sample-package', '*')) == 2

        assert len(parser.filter('drf-metadata', '*')) == 1
        assert not parser.filter('drf-metadata', '1.1.1.1.1')


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PipfileReplacerTest:
    pytestmark = [pytest.mark.parser, pytest.mark.pipfile, pytest.mark.replacer]

    def test_init(self):
        assert PipfileReplacer()

    def test_match(self):
        replacer = PipfileReplacer()
        bundles = replacer.match(test_conf.PIPFILE_CONFIG, 'sample-package', '*')
        assert len(bundles) == 1
        assert len(bundles[0].matches) == 2

    def test_pipfile_replace(self, sample_pipfile: str):
        replacer = PipfileReplacer()
        replacements = replacer.replace(sample_pipfile, 'drf-metadata', '*', '1.1.1')
        assert len(replacements) == 1

        replacements = replacer.replace(sample_pipfile, 'sample-package', '*', '1.1.1')
        assert len(replacements) == 2

        replacements = replacer.replace(sample_pipfile, 'graypy', '*', '1.1.1')
        assert len(replacements) == 1
        assert replacements[0].right == '==1.1.1'

    def teardown(self):
        pattern = test_conf.TMP_DIR.glob(f'{test_conf.TMP_CONFIG_PREFIX}*')
        for path in pattern:
            if path.is_file():
                path.unlink()
            else:
                rmtree(path)
