import os
import subprocess
import typing as t

if t.TYPE_CHECKING:
    from update_package_version.config import OriginConfig
    from update_package_version.base import BaseReplacementResult


class ExecResult:
    def __init__(self, proc: subprocess.Popen, outs: str, errs: str):
        self.proc = proc
        self.outs = outs
        self.errs = errs

    def __str__(self):
        combined = '\n'.join(filter(None, [self.outs, self.errs]))
        return f'Return code {self.proc.returncode}\n{combined}'

    def __bool__(self):
        return self.proc.returncode == 0


class ShellRunner:
    def __init__(self, origin: 'OriginConfig'):
        self.origin = origin

    def __call__(self, *, replacement: 'BaseReplacementResult', env: t.Optional[t.Dict[str, str]] = None):
        if not self.origin.on_update:
            return []

        results = []
        env = env or os.environ.copy()
        env['UPV_PATH'] = replacement.path
        for command in self.origin.on_update:
            results.append(self.run_single_cmd(command, env, self.origin.root))

        return results

    @staticmethod
    def parse_env(env_output: str):
        pass

    @staticmethod
    def run_single_cmd(command: str, env: t.Dict, cwd: t.Optional[str]=None) -> ExecResult:
        env = env or os.environ

        # TODO: run command, capture env, return env
        # sentinel = uuid4().hex
        # _command = f'{command} && echo {sentinel} && env'
        proc = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            env=env,
            cwd=cwd,
        )

        outs, errs = proc.communicate()
        outs, errs = outs or b'', errs or b''
        outs, errs = outs.decode(), errs.decode()

        return ExecResult(proc, outs, errs)
