import pytest

from pathlib import Path
from tempfile import NamedTemporaryFile, gettempdir
from uuid import uuid4

from update_package_version.config import DEFAULTS, ConfigParser

pytestmark = pytest.mark.config


DATA_DIR = Path(__file__).absolute().parent / 'data'
CONFIG_0 = DATA_DIR / 'config_0.yml'
CORRUPTED_LIST_CONFIG = DATA_DIR / 'corrupted_list_config.yml'
CORRUPTED_ORIGIN_CONFIG = DATA_DIR / 'corrupted_origin_config.yml'

TMP_DIR = Path(gettempdir())
TMP_CONFIG_PREFIX = 'update-package-version-test-'
TMP_CONFIG_SUFFIX = '.yml'


@pytest.fixture
def parser() -> ConfigParser:
    temp_config_file = NamedTemporaryFile(prefix=TMP_CONFIG_PREFIX, suffix=TMP_CONFIG_SUFFIX, delete=False)
    temp_config_file.file.write(CONFIG_0.read_bytes())
    temp_config_file.file.flush()

    return ConfigParser(temp_config_file.name)


# noinspection PyMethodMayBeStatic,PyProtectedMember
class ConfigParserTest:
    def test_init(self):
        with pytest.raises(ValueError):
            ConfigParser('')

        # directory
        with pytest.raises(ValueError):
            ConfigParser(gettempdir())

        with pytest.raises(FileNotFoundError):
            ConfigParser(TMP_DIR / f'{uuid4().hex}.tmp')

        with pytest.raises(ValueError):
            ConfigParser(CORRUPTED_LIST_CONFIG)

    def test_origins__raises_on_a_wring_type(self):
        with pytest.raises(ValueError):
            assert ConfigParser(CORRUPTED_ORIGIN_CONFIG).origins

    def test_origins(self):
        parser = ConfigParser(CONFIG_0)
        assert parser.origins

    def test_configure_origin(self):
        o = ConfigParser.configure_origin(DATA_DIR)
        assert len(o.file_patterns) == len(DEFAULTS['file_patterns'])
        assert o.on_update == []
        assert o.name is None

    def teardown(self):
        pattern = TMP_DIR.glob(f'{TMP_CONFIG_PREFIX}*{TMP_CONFIG_SUFFIX}')
        for file in pattern:
            file.unlink()
