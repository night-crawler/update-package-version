import typing as t
from pathlib import Path

from update_package_version.base import (
    BaseReplacementResult, BaseReplacerMatchBundle
)

from .config import FilePattern, OriginConfig


class FileSearchResult:
    def __init__(self, file_pattern: FilePattern, matched_path: Path):
        self.file_pattern = file_pattern
        self.matched_path = matched_path


class FileSearch:
    def __init__(self, origin_config: OriginConfig):
        self.origin_config = origin_config

    def find_files(self) -> t.List[FileSearchResult]:
        """
        Searches for all file locations that match a given file patterns glob-mask.
        Returns a list of FileSearchResult's descendingly sorted by parts count (the longest path first).
        :return: A list of FileSearchResult instances
        """
        results = []
        for file_pattern in self.origin_config.file_patterns:
            for matched_path in file_pattern.glob:
                if matched_path.is_file():
                    results.append(FileSearchResult(file_pattern, matched_path))

        return list(sorted(
            results,
            key=lambda sr: len(sr.matched_path.parts), reverse=True
        ))

    def find(self, package_name: str, version='*') -> t.List[BaseReplacerMatchBundle]:
        matches = []
        for file_search_result in self.find_files():
            matches += file_search_result.file_pattern.replacer.match(
                file_search_result.matched_path,
                package_name,
                version
            )
        return matches

    def replace(
            self,
            package_name: str,
            src_version: str,
            trg_version: str) -> t.List[BaseReplacementResult]:
        replacements = []

        for file_search_result in self.find_files():
            replacements += file_search_result.file_pattern.replacer.replace(
                file_search_result.matched_path,
                package_name,
                src_version, trg_version
            )
        return replacements
