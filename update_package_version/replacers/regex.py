import re
import typing as t
from pathlib import Path
from shutil import move
from tempfile import NamedTemporaryFile

from update_package_version.constants import DEFAULT_PYTHON_MATCH_PATTERNS
from update_package_version.replacers.base import (
    BaseReplacer, BaseReplacerMatchBundle
)


class RegexReplacerMatchBundle(BaseReplacerMatchBundle):
    def __init__(
            self,
            *,
            rx: t.Pattern,
            path: Path,
            line_num: int,
            line: str,
            matches: t.List[t.Match[t.AnyStr]],
            lookup_package_name: str,
            lookup_package_version: str,
    ):
        self.rx = rx

        # we expect here to get a natural order of matches that complies with text occurrences as they go
        self.matches = matches
        self.line_num = line_num
        self.line = line
        self.path = Path(path)

        self.lookup_package_name = lookup_package_name
        self.lookup_package_version = lookup_package_version

    def __str__(self):
        return f'Match <.../{self.path.parts[-1]}:{self.line_num} :: ' \
               f'{self.lookup_package_name}@{self.lookup_package_version}>'

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        """
        If a match has a version specified (but not an asterisk sign, which allows any version),
        then it compares against it. In this case, at least one match must have the same version.
        :return: True in case there are some matches, False otherwise.
        """
        # print(self, self.matches)
        for match in self.matches:
            if not self.lookup_package_version:
                return True
            if self.lookup_package_version == '*':
                return True

            gd = match.groupdict()
            if gd.get('version') == self.lookup_package_version:
                return True

        return False


class RegexReplacer(BaseReplacer):
    def __init__(self, match_patterns: t.Optional[t.List[t.Pattern]] = None, **opts):
        self.match_patterns = match_patterns or DEFAULT_PYTHON_MATCH_PATTERNS
        self._validate_match_patterns(self.match_patterns)
        self.opts = opts

    @staticmethod
    def _validate_match_patterns(match_patterns: t.List[str]):
        for p in match_patterns:
            try:
                rx = re.compile(p.format(package='sample-package'))
            except Exception as e:
                raise RuntimeError(f'Cannot compile regex pattern: {p}')

            if 'version' not in rx.groupindex:
                # raise ValueError(f'Pattern {p} does not contain a named group with version')
                pass

    @staticmethod
    def _match_all(
            file_path: t.Union[str, Path],
            patterns: t.List[str],
            package_name: str,
            version: str
    ):
        path = Path(file_path)

        interpolated_rx_list = [
            re.compile(p.format(package=re.escape(package_name)))
            for p in patterns
        ]

        results = []

        for i, line in enumerate(path.read_text().splitlines()):
            # we don't need empty lines
            if not line or not line.strip():
                continue

            for rx in interpolated_rx_list:
                results.append(RegexReplacerMatchBundle(
                    rx=rx,
                    matches=[match for match in rx.finditer(line)],
                    line_num=i,
                    line=line,
                    lookup_package_name=package_name,
                    lookup_package_version=version,
                    path=file_path
                ))

        return results

    def match(
            self,
            file_path: t.Union[str, Path],
            package_name: str,
            version: str
    ) -> t.List[RegexReplacerMatchBundle]:
        return list(filter(None, self._match_all(
            file_path, self.match_patterns,
            package_name, version
        )))

    def _prepare_replace_map(
            self,
            file_path: t.Union[str, Path],
            package_name: str,
            src_version: str,
            trg_version: str
    ) -> t.Dict[int, str]:
        replace_map = {}

        match_bundles = self.match(file_path, package_name, src_version)
        for match_bundle in match_bundles:
            line = match_bundle.line
            # have to reverse matches since we don't want to mess up the lower span string indexes
            for match in reversed(match_bundle.matches):
                match_span, version_span = match.span(), match.span('version')
                no_version = version_span == (-1, -1)

                if no_version:
                    l, r = line[:match_span[1]], line[match_span[1]:]
                    line = f'{l}=={trg_version}{r}'
                    continue

                # we don't get <sign> named group involved at the moment
                l, r = line[:version_span[0]], line[version_span[1]:]
                line = f'{l}{trg_version}{r}'

            replace_map[match_bundle.line_num] = line

        return replace_map

    def replace(
        self,
        file_path: t.Union[str, Path],
        package_name: str,
        src_version: str,
        trg_version: str
    ):
        file_path = Path(file_path)
        replace_map = self._prepare_replace_map(file_path, package_name, src_version, trg_version)
        tmp_file = NamedTemporaryFile(prefix=file_path.name, suffix='.replace', delete=False)

        for i, line in enumerate(file_path.read_text().splitlines()):
            if i in replace_map:
                tmp_file.write(replace_map[i].encode())
                continue
            tmp_file.write(line.encode())

        tmp_file.close()
        move(tmp_file.name, file_path)

        return len(replace_map)
