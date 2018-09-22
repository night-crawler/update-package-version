import typing as t
from pathlib import Path

from .config import OriginConfig


class FileSearch:
    def __init__(self, origin_config: OriginConfig):
        self.origin_config = origin_config

        # file_patterns looks like a list of pattern-replacer mappings:
        # [ {pattern: replacer}, ... ]
        self.glob_patterns = [
            origin_config.root.glob([*file_pattern.keys()][0])
            for file_pattern
            in self.origin_config.file_patterns
        ]

    def find_files(self) -> t.List[Path]:
        """
        Searches for all file locations that match a given file patterns glob-mask.
        Returns a file path list sorted descendingly by parts count (the longest path first).
        :return:
        """
        results = []
        for pattern in self.glob_patterns:
            for matched_node in pattern:
                if matched_node.is_file():
                    results.append(matched_node)

        return list(sorted(results, key=lambda r: len(r.parts), reverse=True))

    def find_matches(self):
        pass
