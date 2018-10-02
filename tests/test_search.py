import pytest

import typing as t
from shutil import copytree, rmtree
from uuid import uuid4

from tests.conf import DATA_DIR, TMP_CONFIG_PREFIX, TMP_DIR

from update_package_version.config import ConfigParser
from update_package_version.constants import (
    PYTHON_EXCLUDE_GIT_RX, PYTHON_EXCLUDE_HASH_COMMENT,
    PYTHON_REQUIREMENTS_PACKAGE_RX
)
from update_package_version.search import FileSearch

pytestmark = pytest.mark.search

"""
    DATA_DIR
    ├── config_0.yml
    ├── corrupted_list_config.yml
    ├── corrupted_origin_config.yml
    └── dir1
        ├── dir2
        │   ├── dir3
        │   │   ├── dir4
        │   │   │   ├── requirements0.txt  <- it's a directory actually
        │   │   │   └── requirements4.txt
        │   │   └── requirements3.txt
        │   └── requirements2.txt
        └── requirements1.txt

"""


# noinspection PyMethodMayBeStatic
class FileSearchTest:
    def test_file_search_init(self):
        assert FileSearch(ConfigParser.configure_origin(DATA_DIR))

    @pytest.mark.parametrize('glob_pattern,expected_names', [
        (  # directories are unavailable
                '**/requirements0.txt',
                []
        ),
        (  # supports recursive glob
                '**/requirements*.txt',
                ['requirements4.txt', 'requirements3.txt', 'requirements2.txt', 'requirements1.txt']
        ),
        (  # supports glob patterns and special symbols
                './**/dir[1-2]/requirements*.txt',
                ['requirements2.txt', 'requirements1.txt']
        ),
        (  # supports less broad clauses
                './**/dir1/requirements*.txt',
                ['requirements1.txt']
        ),
        (  # can find them on any level
                './**/dir4/requirements*.txt',
                ['requirements4.txt']
        ),
        (  # first level is still accessible
                './**/dir1/requirements*.txt',
                ['requirements1.txt']
        ),
        (  # 0-level is still accessible
                './**/config_0.yml',
                ['config_0.yml']
        ),
    ])
    def test_find_files(self, glob_pattern: str, expected_names: t.List[str]):
        fs = FileSearch(ConfigParser.configure_origin(
            DATA_DIR,
            file_patterns=[{
                'pattern': glob_pattern,
                'replacer': 'RegexReplacer',
            }]
        ))
        files = fs.find_files()
        names = [f.matched_path.parts[-1] for f in files]
        assert names == expected_names

    def test_find_regex(self):
        fs = FileSearch(ConfigParser.configure_origin(
            DATA_DIR,
            file_patterns=[{
                'pattern': '**/requirements*.txt',
                'replacer': 'RegexReplacer',
                'match-patterns': [PYTHON_REQUIREMENTS_PACKAGE_RX]
            }]
        ))

        assert fs.find('sample-package', version='*')

    def test_search_replace_regex(self):
        tmp_dir = TMP_DIR / f'{TMP_CONFIG_PREFIX}{uuid4().hex}'
        copytree(DATA_DIR, tmp_dir)
        assert tmp_dir.exists()

        fs = FileSearch(ConfigParser.configure_origin(
            tmp_dir,
            file_patterns=[{
                'pattern': '**/requirements*.txt',
                'replacer': 'RegexReplacer',
                'match-patterns': [PYTHON_REQUIREMENTS_PACKAGE_RX],
                'exclude-patterns': [PYTHON_EXCLUDE_GIT_RX, PYTHON_EXCLUDE_HASH_COMMENT]
            }]
        ))

        replacement_results = fs.replace('sample-package', '*', '1.1.1')
        assert replacement_results

        for res in replacement_results:
            assert '1.1.1' in str(res)
            assert '#' not in str(res)
            assert '.git' not in str(res)

    def teardown(self):
        pattern = TMP_DIR.glob(f'{TMP_CONFIG_PREFIX}*')
        for path in pattern:
            if path.is_file():
                path.unlink()
            else:
                rmtree(path)
