import pytest

from update_package_version.replacers.pipfile import (
    PipfilePackage, PipfileParser, PipfileReplacer
)

from . import conf as test_conf

pytestmark = [pytest.mark.replacer, pytest.mark.pipfile]


# noinspection PyMethodMayBeStatic,PyProtectedMember
class PipfilePackagePTest:
    pytestmark = [pytest.mark.parser, pytest.mark.pipfile, pytest.mark.package]

    def test_init(self):
        assert PipfilePackage('sample-package', 'dev-packages')
        assert PipfilePackage('sample', version='*', section='dev-packages')
        assert str(PipfileParser('sample'))


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
    def test_init(self):
        assert PipfileReplacer()

    def test_match(self):
        replacer = PipfileReplacer()
        bla = replacer.match(test_conf.PIPFILE_CONFIG, 'sample-package', '*')
