import importlib

DEFAULT_REPLACER_MODULE_PATH = 'update_package_version.replacers'


def import_from(module: str, name: str):
    return getattr(
        importlib.import_module(module, [name]),
        name
    )
