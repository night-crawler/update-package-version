import typing as t
from pathlib import Path

import fire

from .config import ConfigParser, OriginConfig


class UpdatePackageVersionCLI:
    def __init__(
        self,
        config_file_path: str = None,
        config_file_name: str = '.update_package_version.yml',
        dry_run: bool = False,
    ):
        self._user_home_path = Path.home()
        self._cwd = Path.cwd()

        self._param_config_file_path = config_file_path and Path(config_file_path)
        self._cwd_config_file_path = self._cwd / config_file_name
        self._user_config_file_path = self._user_home_path / config_file_name

        if self._param_config_file_path and not self._param_config_file_path.exists():
            raise FileNotFoundError(f'Specified configuration file does not exist: {config_file_path}')

        # param -> CWD -> user home
        self._config_file_path = None
        for path in [self._param_config_file_path, self._cwd_config_file_path, self._user_config_file_path]:
            if path and path.exists():
                self._config_file_path = path
                break

        self._data_dir = Path(__file__).parent / 'data'
        self._sample_config_file = self._data_dir / 'sample__update-package-version.yml'

        self._dry_run = dry_run

    def print_settings(self):
        """
        Prints all collected runtime information.
        """
        return [
            f'HOME: {self._user_home_path}',
            f'CWD: {self._cwd}',
            f'Internal data dir: {self._data_dir}',
            f'Default config file: {self._sample_config_file}',
            f'Config file path: {self._config_file_path}',
            f'Dry run: {self._dry_run}'
        ]

    def copy_sample(self):
        """
        Copies the sample configuration file to user's home directory.
        """
        if self._user_config_file_path.exists():
            raise FileExistsError(f'Configuration file exists: {self._user_config_file_path}')

        self._user_config_file_path.write_bytes(
            self._sample_config_file.read_bytes()
        )

    def _get_origins(self) -> t.List[OriginConfig]:
        """
        Reads origins from a config file if possible, otherwise it assumes we're using defaults with CWD.
        :return: A list of OriginConfig instances
        """
        if self._config_file_path:
            return ConfigParser(self._config_file_path).origins

        return [ConfigParser.configure_origin(f'{self._cwd}')]

    def bump(self, *args, trg: str, src: str='*'):
        if len(args) != 1:
            raise ValueError('You must specify exactly one package to update')

        origins = self._get_origins()
        print(origins[0])
        print(self._config_file_path, args, src, trg)


def main():
    fire.Fire(UpdatePackageVersionCLI)
