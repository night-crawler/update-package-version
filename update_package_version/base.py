import typing as t
from pathlib import Path

from update_package_version.utils import (
    DEFAULT_REPLACER_MODULE_PATH, import_from
)


class BaseReplacementResult:
    pass


class BaseReplacerMatchBundle:
    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        raise NotImplementedError()

    def __bool__(self):
        raise NotImplementedError()

    @property
    def additional_info(self):
        raise NotImplementedError()


class BaseReplacer:
    def match(
            self,
            path: t.Union[str, Path],
            package_name: str,
            version: str
    ) -> t.List[BaseReplacerMatchBundle]:
        raise NotImplementedError()

    def replace(
        self,
        file_path: t.Union[str, Path],
        package_name: str,
        src_version: str,
        trg_version: str
    ) -> t.List[BaseReplacementResult]:
        raise NotImplementedError()


def import_replacer(dpath: str) -> t.Type[BaseReplacer]:
    path_parts = dpath.rsplit('.', 1)
    if len(path_parts) == 2:
        mod_path, replacer_class_name = path_parts
    else:
        mod_path, replacer_class_name = DEFAULT_REPLACER_MODULE_PATH, dpath

    return import_from(mod_path, replacer_class_name)
