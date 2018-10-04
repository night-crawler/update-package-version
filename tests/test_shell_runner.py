import pytest

from pathlib import Path

from update_package_version.base import BaseReplacementResult
from update_package_version.config import OriginConfig
from update_package_version.shell_runner import ShellRunner

pytestmark = pytest.mark.shell_runner


class TestReplacementResult(BaseReplacementResult):
    def __init__(self, path=Path.cwd()):
        self.path = path


# noinspection PyMethodMayBeStatic,PyProtectedMember
class ShellRunnerTest:
    def test_init(self):
        cwd_origin_config = OriginConfig(str(Path.cwd()), name='', file_patterns=[])
        ShellRunner(cwd_origin_config)

    def test_run(self):
        cwd_origin_config = OriginConfig(
            str(Path.cwd()), name='', file_patterns=[], on_update=[
                'echo'
            ]
        )

        ShellRunner(cwd_origin_config)(replacement=TestReplacementResult())

    def test_run_single_command(self):
        result = ShellRunner.run_single_cmd('echo lol', {'bla': '1'}, '/tmp')
        assert result.proc.returncode == 0
        assert result
        assert result.outs
        assert not result.errs
