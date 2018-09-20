import pytest

from pathlib import Path
from uuid import uuid4

from update_package_version.cli import UpdatePackageVersionCLI

pytestmark = pytest.mark.cli


@pytest.fixture
def cli():
    return UpdatePackageVersionCLI()


# noinspection PyMethodMayBeStatic
class UpdatePackageVersionCLITest:
    def test_init(self, cli: UpdatePackageVersionCLI):
        assert cli
        with pytest.raises(FileNotFoundError):
            UpdatePackageVersionCLI(config_file_path=Path('/tmp') / f'{uuid4().hex}.tmp')

    def test_print_settings(self, cli: UpdatePackageVersionCLI):
        assert cli.print_settings()

    def test_copy_sample(self, cli: UpdatePackageVersionCLI):
        cli._user_config_file_path = Path('/tmp') / f'{uuid4().hex}.tmp'
        cli.copy_sample()

        with pytest.raises(FileExistsError):
            cli.copy_sample()
