import re
import typing as t
from pathlib import Path

from update_package_version.replacers.base import BaseReplacer


DEFAULT_PYTHON_MATCH_PATTERNS = [
    r'(?P<{package}>)==(?P<version>[\-\d\.]+)',

    r'(?P<{package}>)\.git@(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$',
]


def match_dict(rx, line):
    return [m.groupdict() for m in rx.finditer(line)]


class RegexReplacer(BaseReplacer):
    def __init__(self, match_patterns: t.Optional[t.List[str]] = None, **opts):
        self.match_patterns = match_patterns or [] # DEFAULT_PYTHON_MATCH_PATTERNS
        self.opts = opts

    def test(self, file_path: t.Union[str, Path], package_name: str, version: str):
        path = Path(file_path)
        
        interpolated_rx_list = [
            re.compile(p.format(package=re.escape(package_name)))
            for p in self.match_patterns
        ]

        results = []
        
        for i, line in enumerate(path.read_text().splitlines()):
            for rx in interpolated_rx_list:
                for match in rx.finditer(line):
                    results.append({
                        'path': path,
                        'line': i,
                        'match_dict': match.groupdict()
                    })

        return results
