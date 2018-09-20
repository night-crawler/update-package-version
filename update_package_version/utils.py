import importlib

DEFAULT_REPLACER_MODULE_PATH = 'update_package_version.replacers'


def import_from(module: str, name: str):
    return getattr(
        importlib.import_module(module, [name]),
        name
    )


def import_replacer(dpath: str):
    path_parts = dpath.rsplit('.', 1)
    if len(path_parts) == 2:
        mod_path, replacer_class_name = path_parts
    else:
        mod_path, replacer_class_name = DEFAULT_REPLACER_MODULE_PATH, dpath

    return import_from(mod_path, replacer_class_name)
