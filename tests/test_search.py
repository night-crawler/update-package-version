import typing as t
import pytest

from pathlib import Path

from update_package_version.config import ConfigParser
from update_package_version.search import FileSearch

DATA_DIR = Path(__file__).absolute().parent / 'data'

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
    def test_init(self):
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
            file_patterns=[{glob_pattern: 'RegexReplacer'}]
        ))
        files = fs.find_files()
        names = [f.parts[-1] for f in files]
        assert names == expected_names
