import typing as t
from pathlib import Path

from yaml import safe_dump, safe_load

DEFAULTS = {
    'file_patterns': [
        {'Pipfile': 'PipfileReplacer'},
        {'requirements.txt': 'RegexReplacer'},
        {'requirements/*.txt': 'RegexReplacer'}
    ],

    'max_depth': 3,

    'match_patterns': [
        r'^\s*{package}==(?P<major>\d+)$',
    ]
}


class OriginConfig:
    def __init__(
            self,
            root: str,
            *,
            name: str,
            max_depth: int = 3,
            match_patterns: t.List[str],
            file_patterns: t.List[str],
            on_update: t.Optional[t.List[str]] = None
    ):
        if not root:
            raise ValueError('Origin\'s root directory must not be a non-empty string')

        self.root = Path(root)
        self.name = name
        self.max_depth = max_depth
        self.match_patterns = match_patterns or []
        self.file_patterns = file_patterns or []
        self.on_update = on_update or []

    def __str__(self):
        return f'Origin <{self.root}>'

    def is_valid(self):
        return self.root.exists() and self.root.is_file()


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
                max_depth=origin_bundle.get('max-depth'),
                match_patterns=origin_bundle.get('match-patterns'),
                file_patterns=origin_bundle.get('file-patterns'),
                on_update=origin_bundle.get('on-update'),
                defaults=self._conf.get('defaults') or DEFAULTS
            ))
        return result

    @staticmethod
    def configure_origin(
            root: str,
            *,
            name: t.Optional[str] = None,
            max_depth: t.Optional[int] = 3,
            match_patterns: t.Optional[t.List[str]] = None,
            file_patterns: t.Optional[t.List[str]] = None,
            on_update: t.Optional[t.List[str]] = None,

            defaults: t.Optional[t.Dict[str, t.Any]] = None
    ) -> OriginConfig:

        _defaults = defaults or DEFAULTS

        return OriginConfig(
            root,
            name=name,
            max_depth=max_depth or _defaults.get('max_depth'),
            match_patterns=match_patterns or _defaults.get('match_patterns'),
            file_patterns=file_patterns or _defaults.get('file_patterns'),
            on_update=on_update or _defaults.get('on_update'),
        )
