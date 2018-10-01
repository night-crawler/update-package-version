from pathlib import Path
from tempfile import gettempdir

DATA_DIR = Path(__file__).absolute().parent / 'data'
CONFIG_0 = DATA_DIR / 'config_0.yml'
CORRUPTED_LIST_CONFIG = DATA_DIR / 'corrupted_list_config.yml'
CORRUPTED_ORIGIN_CONFIG = DATA_DIR / 'corrupted_origin_config.yml'

PIPFILE_CONFIG = Path(DATA_DIR / 'dir1/dir2/dir3/dir4' / 'Pipfile')

TMP_DIR = Path(gettempdir())
TMP_CONFIG_PREFIX = 'update-package-version-test-'
TMP_CONFIG_SUFFIX = '.yml'

SAMPLE_REQUIREMENTS_TXT_FILE = Path(DATA_DIR / 'dir1/dir2/dir3/dir4' / 'requirements4.txt')
