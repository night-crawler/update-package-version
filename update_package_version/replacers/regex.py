import re
import typing as t
from pathlib import Path

from update_package_version.replacers.base import BaseReplacer

VERSION_SIGNS = '|'.join(re.escape(s) for s in ['==', '<=', '>=', '<', '>'])
PYTHON_REGULAR_PACKAGE_RX = \
    r'(?P<package>{package})' \
    fr'(?P<sign>{VERSION_SIGNS})' \
    r'(?P<version>[\-\d\.]+)'
PYTHON_GIT_RX = r'(?P<package>{package})\.git@(?P<version>[\-\d\.]+)'


DEFAULT_PYTHON_MATCH_PATTERNS = [
    PYTHON_REGULAR_PACKAGE_RX,
    PYTHON_GIT_RX
]


class RegexReplacerMatch:
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
        self.matches = matches
        self.line_num = line_num
        self.line = line
        self.path = path

        self.lookup_package_name = lookup_package_name
        self.lookup_package_version = lookup_package_version

    def __str__(self):
        return f'Match <.../{self.path.parts[-1]}:{self.line_num} :: ' \
               f'{self.lookup_package_name}@{self.lookup_package_version}>'

    def __repr__(self):
        return self.__str__()

    def __bool__(self):
        """
        Tries to be truthy in case there are some matches.
        If it has a version specified (but not an asterisk sign, which allows any version),
        then it compares against it. In this case, at least one match should have the same version.
        :return:
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
                results.append(RegexReplacerMatch(
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
    ) -> t.List[RegexReplacerMatch]:
        return list(filter(None, self._match_all(
            file_path, self.match_patterns,
            package_name, version
        )))
