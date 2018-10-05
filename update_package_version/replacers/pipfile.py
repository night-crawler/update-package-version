import re
import typing as t
from pathlib import Path

import toml

from update_package_version.base import (
    BaseReplacementResult, BaseReplacer, BaseReplacerMatchBundle
)
from update_package_version.constants import VERSION_SIGNS_RX


class PipfilePackageReplacement(BaseReplacementResult):
    def __init__(
            self, *,
            left: str, right: str,
            path: Path,
    ):
        # must not trim spaces here
        self.left = left
        self.right = right
        self.path = path

    def __str__(self):
        return f'{self.path} {self.left} -> {self.right}'

    def __repr__(self):
        return self.__str__()


class PipfilePackage:
    VERSION_RX = re.compile(
        fr'(?P<sign>{VERSION_SIGNS_RX})?'
        r'(?P<version>[\-\d.*]+)?'
    )

    def __init__(
            self,
            name: str,
            section: str,
            version: t.Optional[t.Union[str, dict]] = '==0.0.0'
    ):
        assert name
        assert section in ['dev-packages', 'packages']
        parsed = self._parse_version(version)
        self.sign = parsed['sign']
        self.version = parsed['version']
        self.raw_version = version
        self.section = section
        self.name = name

    def __str__(self):
        return f'PipfilePackage({self.name}, section=\'{self.section}\', version=\'{self.raw_version}\')'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _parse_version(version):
        if isinstance(version, dict):
            return {'sign': '==', 'version': version.get('ref')}

        for match in PipfilePackage.VERSION_RX.finditer(version):
            return match.groupdict()

    @property
    def is_repo(self) -> bool:
        return isinstance(self.raw_version, dict)

    def get_version(self) -> t.Union[dict, str]:
        if self.is_repo:
            version_bundle: dict = self.raw_version.copy()
            version_bundle.update({
                'ref': self.version,
            })
            return version_bundle

        sign = self.sign or '=='
        return f'{sign}{self.version}'

    def set_version(self, new_version: str):
        self.version = new_version
        return self.get_version()


class PipfileReplacerMatchBundle(BaseReplacerMatchBundle):
    def __init__(
            self, *,
            replacer: 'PipfileReplacer',
            path: Path,
            matches: t.List[t.Any],
            lookup_package_name: str,
            lookup_package_version: str,
    ):
        self.replacer = replacer

        self.matches = matches
        self.path = Path(path)

        self.lookup_package_name = lookup_package_name
        self.lookup_package_version = lookup_package_version

    def __str__(self):
        return f'Match <{self.path} :: ' \
               f'{self.lookup_package_name}@{self.lookup_package_version}>'

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        return bool(self.matches)

    @property
    def additional_info(self):
        lines = []
        for m in self.matches:
            lines.append(f'{m}')
        return lines


class PipfileParser:
    def __init__(self, path: t.Union[str, Path]):
        self.path = Path(path)
        self._data: t.Dict[str, t.Dict[str, t.Any]] = None
        self._parse()

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

    def update_version(
            self,
            package_name: str,
            src_version: str,
            trg_version: str,
    ) -> t.List[PipfilePackageReplacement]:
        replacements = []
        for package in self.filter(package_name, src_version):
            old_version = package.version

            new_version = package.set_version(trg_version)
            self._data[package.section][package.name] = new_version
            replacements.append(PipfilePackageReplacement(
                left=old_version,
                right=new_version,
                path=self.path
            ))
        return replacements

    def save(self):
        toml.dump(self._data, self.path.open('w'))


class PipfileReplacer(BaseReplacer):
    def __init__(self, **opts):
        pass

    def match(
            self,
            path: t.Union[str, Path],
            package_name: str,
            version: str) -> t.List[PipfileReplacerMatchBundle]:
        match_bundles = []
        parser = PipfileParser(path)

        pipfile_packages = parser.filter(package_name, version)
        if not pipfile_packages:
            return []

        match_bundles.append(PipfileReplacerMatchBundle(
            replacer=self,
            path=path,
            matches=pipfile_packages,
            lookup_package_name=package_name,
            lookup_package_version=version
        ))

        return match_bundles

    def replace(
            self,
            file_path: t.Union[str, Path],
            package_name: str, src_version: str,
            trg_version: str
    ) -> t.List[PipfilePackageReplacement]:
        parser = PipfileParser(file_path)
        replacements = parser.update_version(
            package_name, src_version, trg_version
        )
        parser.save()
        return replacements

    def __str__(self):
        return f'PipfileReplacer'
