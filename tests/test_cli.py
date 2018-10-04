import pytest

from pathlib import Path
from shutil import copytree, rmtree
from uuid import uuid4

from tests.conf import TMP_DIR, DATA_DIR, TMP_CONFIG_PREFIX
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
        assert all(cli.print_settings())

    def test_copy_sample(self, cli: UpdatePackageVersionCLI):
        cli._user_config_file_path = Path('/tmp') / f'{uuid4().hex}.tmp'
        assert all(cli.copy_sample())

        with pytest.raises(FileExistsError):
            all(cli.copy_sample())

    def test_find(self, cli: UpdatePackageVersionCLI):
        assert all(cli.find('sample-package'))

    def test_update(self):
        tmp_dir = TMP_DIR / f'{TMP_CONFIG_PREFIX}{uuid4().hex}'
        copytree(DATA_DIR, tmp_dir)
        assert tmp_dir.exists()

        cli = UpdatePackageVersionCLI(cwd=tmp_dir)
        assert all(cli.update('sample-package', trg='1.1.1', src='*'))

    def teardown(self):
        pattern = TMP_DIR.glob(f'{TMP_CONFIG_PREFIX}*')
        for path in pattern:
            if path.is_file():
                path.unlink()
            else:
                rmtree(path)
