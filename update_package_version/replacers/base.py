import typing as t
from update_package_version.utils import DEFAULT_REPLACER_MODULE_PATH, import_from


class BaseReplacer:
    def __init__(self, **options):
        raise NotImplementedError()

    def test(self):
        raise NotImplementedError()

    def replace(self):
        raise NotImplementedError()


def import_replacer(dpath: str) -> t.Type[BaseReplacer]:
    path_parts = dpath.rsplit('.', 1)
    if len(path_parts) == 2:
        mod_path, replacer_class_name = path_parts
    else:
        mod_path, replacer_class_name = DEFAULT_REPLACER_MODULE_PATH, dpath

    return import_from(mod_path, replacer_class_name)
