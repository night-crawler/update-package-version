import pytest

from tempfile import NamedTemporaryFile, gettempdir
from uuid import uuid4

from update_package_version.config import ConfigParser
from update_package_version.constants import DEFAULT_PYTHON_CONFIG

from . import conf as test_conf

pytestmark = pytest.mark.config


@pytest.fixture
def parser() -> ConfigParser:
    temp_config_file = NamedTemporaryFile(
        prefix=test_conf.TMP_CONFIG_PREFIX,
        suffix=test_conf.TMP_CONFIG_SUFFIX,
        delete=False
    )
    temp_config_file.file.write(test_conf.CONFIG_0.read_bytes())
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
            ConfigParser(test_conf.TMP_DIR / f'{uuid4().hex}.tmp')

        with pytest.raises(ValueError):
            ConfigParser(test_conf.CORRUPTED_LIST_CONFIG)

    def test_origins__raises_on_a_wring_type(self):
        with pytest.raises(ValueError):
            assert ConfigParser(test_conf.CORRUPTED_ORIGIN_CONFIG).origins

    def test_origins(self):
        parser = ConfigParser(test_conf.CONFIG_0)
        assert parser.origins

    def test_configure_origin(self):
        o = ConfigParser.configure_origin(test_conf.DATA_DIR)
        assert len(o.file_patterns) == len(DEFAULT_PYTHON_CONFIG['file_patterns'])
        assert o.on_update == []
        assert o.name is None

    def teardown(self):
        pattern = test_conf.TMP_DIR.glob(
            f'{test_conf.TMP_CONFIG_PREFIX}*{test_conf.TMP_CONFIG_SUFFIX}'
        )
        for file in pattern:
            file.unlink()
