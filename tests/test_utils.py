import pytest

from update_package_version.base import import_replacer
from update_package_version.utils import import_from

pytestmark = pytest.mark.config


# noinspection PyMethodMayBeStatic
class UtilsTest:
    def test__import_from(self):
        cli_class = import_from('update_package_version.cli', 'UpdatePackageVersionCLI')
        assert cli_class

    def test__import_replacer(self):
        assert import_replacer('PipfileReplacer')
