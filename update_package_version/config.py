import typing as t
from pathlib import Path

from yaml import safe_dump, safe_load

from update_package_version.base import BaseReplacer, import_replacer
from update_package_version.constants import DEFAULT_PYTHON_CONFIG


class FilePattern:
    r"""
    A data class representing the configuration file structure like:

    .. code-block:: yaml

        pattern: 'requirements.txt'
        replacer: RegexReplacer
        match-patterns:
          - '^(?P<package>{package})==(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$'

    """
    def __init__(
            self,
            root: str,
            *,
            pattern: str,
            replacer_name: str,
            **replacer_options
    ):
        self.root = Path(root)
        self.pattern = pattern
        self.replacer_name = replacer_name
        self.replacer_options = replacer_options

    def __str__(self):
        return f'FilePattern <{self.pattern}@{self.replacer_name} :: {self.replacer_options}>'

    @property
    def glob(self):
        return self.root.glob(self.pattern)

    @property
    def replacer(self) -> BaseReplacer:
        replacer_class: t.Type[BaseReplacer] = import_replacer(self.replacer_name)

        # transform match-patterns to match_patterns
        _replacer_options = {k.replace('-', '_'): v for k, v in self.replacer_options.items()}

        return replacer_class(**_replacer_options)


class OriginConfig:
    r"""
    A data class representing origin configuration settings. Finds its counterpart in a structure like:

    .. code-block:: yaml

        root: '/some/unreal/but/interesting/root/path'
        file-patterns:
          - pattern: 'Pipfile'
            replacer: PipfileReplacer
          - pattern: 'requirements.txt'
            replacer: RegexReplacer
            match-patterns:
              - '^(?P<package>{package})(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$'
          - pattern: 'requirements/*.txt'
            replacer: RegexReplacer
        on-update:
          - command 1
          - command 2
    """
    def __init__(
            self,
            root: str,
            *,
            name: str,
            file_patterns: t.List[t.Dict[str, str]],
            on_update: t.Optional[t.List[str]] = None
    ):
        if not root:
            raise ValueError('Origin\'s root directory must be a non-empty string')

        self.root = Path(root)
        self.name = name
        self.file_patterns = self._initialize_file_patterns(root, file_patterns)
        self.on_update = on_update or []

    def __str__(self):
        return f'Origin <{self.root}>'

    def is_valid(self) -> bool:
        return self.root.exists() and self.root.is_file()

    @staticmethod
    def _initialize_file_patterns(
            root: str,
            file_pattern_bundles: t.List[t.Dict[str, str]]
    ) -> t.List[FilePattern]:
        """
        Convenience method to instantiate FilePatterns
        """
        initialized = []
        for fp in file_pattern_bundles:
            fp = fp.copy()
            if not fp:
                raise ValueError('File patterns must not contain empty sequences')

            pattern = fp.pop('pattern')
            replacer_name = fp.pop('replacer')

            initialized.append(FilePattern(
                root,
                pattern=pattern,
                replacer_name=replacer_name,
                **fp)
            )
        return initialized


class ConfigParser:
    def __init__(self, config_file_path: str):
        if not config_file_path:
            raise ValueError('Path to a configuration file must not be empty')

        self._config_file_path = Path(config_file_path)

        if not self._config_file_path.exists():
            raise FileNotFoundError(f'File`{config_file_path}` not found')

        if not self._config_file_path.is_file():
            raise ValueError(f'Path `{config_file_path}` is not a file')

        self._conf: t.Dict[str, t.Any] = safe_load(self._config_file_path.open('r'))
        if not isinstance(self._conf, dict):
            raise ValueError(f'Configuration file `{config_file_path}` must have a dict-like format')

    @property
    def origins(self) -> t.List[OriginConfig]:
        result = []
        for origin_bundle in self._conf.get('origins', []):
            if not isinstance(origin_bundle, dict):
                raise ValueError(
                    f'Origin must be a dict-like object, got type {type(origin_bundle)}\n'
                    f'{safe_dump(origin_bundle)}'
                )
            root = origin_bundle.pop('root')
            result.append(self.configure_origin(
                root,
                file_patterns=origin_bundle.get('file-patterns'),
                on_update=origin_bundle.get('on-update'),
                defaults=self._conf.get('defaults') or DEFAULT_PYTHON_CONFIG
            ))
        return result

    @staticmethod
    def configure_origin(
            root: str,
            *,
            name: t.Optional[str] = None,
            file_patterns: t.Optional[t.List[t.Dict[str, str]]] = None,
            on_update: t.Optional[t.List[str]] = None,

            defaults: t.Optional[t.Dict[str, t.Any]] = None
    ) -> OriginConfig:

        _defaults = defaults or DEFAULT_PYTHON_CONFIG

        return OriginConfig(
            root,
            name=name,
            file_patterns=file_patterns or _defaults.get('file_patterns'),
            on_update=on_update or _defaults.get('on_update'),
        )
