import typing as t
from pathlib import Path
from pprint import pprint

import toml

from update_package_version.replacers.base import BaseReplacer, BaseReplacementResult, BaseReplacerMatchBundle


class PipfileReplacerMatchBundle(BaseReplacerMatchBundle):
    def __init__(self):
        pass


class PipfileParser:
    def __init__(self, path: t.Union[str, Path]):
        self.path = Path(path)
        self._data = None

    def _parse(self):
        self._data = toml.load(self.path.open('r'))

    @property
    def packages(self):
        return []

    @property
    def dev_packages(self):
        return []


class PipfileReplacer(BaseReplacer):
    def __init__(self, **opts):
        pass

    def match(
            self,
            path: t.Union[str, Path],
            package_name: str,
            version: str) -> t.List[PipfileReplacerMatchBundle]:
        parsed = toml.load(path.open('r'))
        pprint(parsed)

        return []

    def replace(
            self,
            file_path: t.Union[str, Path],
            package_name: str, src_version: str,
            trg_version: str
    ) -> t.List[BaseReplacementResult]:
        return []

    def __str__(self):
        return f'bla'
