import fire
from pathlib import Path


class UpdatePackageVersionCLI:
    def __init__(
        self,
        config_file_path: str = None,
        config_file_name: str = '.update_package_version.yml',
        max_depth: int = 8,
        dry_run: bool = False,
    ):
        self._user_home_path = Path.home()
        self._cwd = Path.cwd()

        self._param_config_file_path = config_file_path and Path(config_file_path)
        self._cwd_config_file_path = self._cwd / config_file_name
        self._user_config_file_path = self._user_home_path / config_file_name

        if self._param_config_file_path and not self._param_config_file_path.exists():
            raise FileNotFoundError(f'Specified configuration file does not exist: {config_file_path}')

        # param, CWD, user home
        self._config_file_path = \
            self._param_config_file_path or \
            self._cwd_config_file_path or \
            self._user_config_file_path

        self._data_dir = Path(__file__).parent / 'data'
        self._sample_config_file = self._data_dir / 'sample__update-package-version.yml'

        self._max_depth = max_depth
        self._dry_run = dry_run

    def print_settings(self):
        """
        Prints all collected runtime information.
        """
        return [
            f'HOME: {self._user_home_path}',
            f'CWD: {self._cwd}',
            f'Internal data dir: {self._data_dir} - exists: {self._data_dir.exists()}',
            f'Default config file: {self._sample_config_file} - exists: {self._sample_config_file.exists()}',
            f'Config file path: {self._config_file_path} - exists: {self._config_file_path.exists()}',
            f'Default max depth: {self._max_depth}',
            f'Dry run: {self._dry_run}'
        ]

    def copy_sample(self):
        """
        Copies the sample configuration file to user home directory.
        """
        if self._user_config_file_path.exists():
            raise FileExistsError(f'Configuration file exists: {self._user_config_file_path}')

        self._user_config_file_path.write_bytes(
            self._sample_config_file.read_bytes()
        )


def main():
    fire.Fire(UpdatePackageVersionCLI)
