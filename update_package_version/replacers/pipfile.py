import re
import typing as t
from pathlib import Path
from pprint import pprint

import toml
from semver import VersionInfo

from update_package_version.base import (
    BaseReplacementResult, BaseReplacer, BaseReplacerMatchBundle
)
from update_package_version.constants import VERSION_SIGNS_RX


class PipfilePackage:
    VERSION_RX = re.compile(
        fr'(?P<sign>{VERSION_SIGNS_RX})?'
        r'(?P<version>[\-\d.*]+)?'
    )

    def __init__(self, name: str, section: str, version: t.Optional[str] = '==0.0.0'):
        assert name
        assert section
        parsed = self._parse_version(version)
        self.sign = parsed['sign']
        self.version = parsed['version']
        self.raw_version = version
        self.section = section
        self.name = name

    @staticmethod
    def _parse_version(version):
        if isinstance(version, dict):
            return {'sign': '==', 'version': version.get('tag')}

        for match in PipfilePackage.VERSION_RX.finditer(version):
            return match.groupdict()

    @property
    def version_info(self) -> VersionInfo:
        return VersionInfo.parse(self.raw_version)

    def __str__(self):
        return f'PipfilePackage({self.name}, section=\'{self.section}\', version=\'{self.raw_version}\')'

    def __repr__(self):
        return self.__str__()


class PipfileReplacerMatchBundle(BaseReplacerMatchBundle):
    def __init__(self):
        pass


class PipfileParser:
    def __init__(self, path: t.Union[str, Path]):
        self.path = Path(path)
        self._data: t.Dict[str, t.Dict[str, t.Any]] = None

    def _parse(self):
        if self._data is not None:
            return self._data

        self._data = toml.load(self.path.open('r'))
        return self._data

    def _wrap_packages(self, section: str) -> t.Dict[str, PipfilePackage]:
        _packages = {}
        for package_name, version_info in self._parse().get(section, {}).items():
            _packages[package_name] = (PipfilePackage(
                package_name, section=section, version=version_info
            ))
        return _packages

    @property
    def packages(self) -> t.ValuesView[PipfilePackage]:
        return self._wrap_packages('packages').values()

    @property
    def dev_packages(self) -> t.ValuesView[PipfilePackage]:
        return self._wrap_packages('dev-packages').values()

    def filter(self, package_name: str, version: str = '*') -> t.List[PipfilePackage]:
        p1 = self._wrap_packages('packages').get(package_name, None)
        p2 = self._wrap_packages('dev-packages').get(package_name, None)

        results = []
        for package in [p1, p2]:
            if not package:
                continue
            if version == '*':
                results.append(package)
                continue
            if package.version == version:
                results.append(package)

        return results

    def update_version(self, package_name: str, version: str):
        self._data


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
