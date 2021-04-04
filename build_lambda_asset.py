import os
import platform
import shutil
from pathlib import Path
from typing import List
import docker
from docker.types import Mount
from datetime import datetime
import hashlib

from aws_cdk import aws_lambda
from aws_cdk.core import BundlingOptions, DockerVolume, DockerVolumeConsistency


# pylint: disable=print-used
def timeit(method):

    def timed(*args, **kw):
        t_start = datetime.now()
        result = method(*args, **kw)
        t_end = datetime.now()
        print(f'{method.__name__} - Total time = {(t_end - t_start).total_seconds()} seconds')
        return result

    return timed


class BuildLambdaAsset:

    def __init__(self, include_paths: List[str], build_dir: Path, cache_dir: Path = None, requirements_txt: Path = Path('requirements.txt'),
                 consume_dependencies: bool = None, verbose: bool = False) -> None:
        self._include_paths = include_paths
        self._build_dir: Path = build_dir
        self._cache_dir: Path = cache_dir if cache_dir is not None else Path.home() / ".everest-pip-cache"
        self._requirements_txt: Path = requirements_txt
        self._req_md5_file: Path = Path(str(requirements_txt) + '.md5')
        self._consume_dependencies = consume_dependencies
        self._verbose = verbose

    @timeit
    def build(self):
        md5_sum: str = None
        if self._consume_dependencies is None:
            prev_md5_sum: str = self._req_md5_file.read_text() if self._req_md5_file.is_file() else ''
            md5_sum = hashlib.md5(self._requirements_txt.read_bytes()).hexdigest()
            self._consume_dependencies = prev_md5_sum != md5_sum
        self._clean_build_target()
        self._copy_resources()
        if self._consume_dependencies:
            self._consume()
        if md5_sum is not None:
            self._req_md5_file.write_text(md5_sum)

    def _clean_build_target(self):
        if self._consume_dependencies:
            if self._req_md5_file.is_file():
                self._req_md5_file.unlink()
            shutil.rmtree(self._build_dir, ignore_errors=True)
            self._build_dir.mkdir(parents=True, exist_ok=True)
            self._cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            for include_path in self._include_paths:
                shutil.rmtree(self._build_dir / os.path.basename(os.path.normpath(include_path)), ignore_errors=True)

    def _copy_resources(self):
        print('Copying \'include\' resources:')
        for include_path in self._include_paths:
            print(f'    -  {(Path.cwd() / include_path).resolve()}')
            shutil.copytree(include_path, (self._build_dir / os.path.basename(os.path.normpath(include_path))).as_posix())
        shutil.copy(self._requirements_txt.as_posix(), (self._build_dir / 'requirements.txt').as_posix())

    def _consume(self) -> None:
        if platform.system().lower() == 'linux':
            self._consume_natively()
        else:
            self._consume_using_docker()

    @timeit
    def _consume_natively(self) -> None:
        """
        Build lambda dependencies natively on linux. Should be the same architecture though.
        """
        print('Installing lambda runtime dependencies on Linux')
        if os.system(f"python -m pip install --target {self._build_dir} --requirement {self._requirements_txt}") != 0:
            raise Exception('Cloud not resolve lambda runtime dependencies')
        print('Finish to install lambda runtime dependencies')

    @timeit
    def _consume_using_docker(self) -> None:
        """
        Build lambda dependencies in a container as-close-as-possible to the actual runtime environment.
        """
        print('Installing dependencies [running in Docker]...')
        client = docker.from_env()
        client.images.pull(repository='amazon/aws-sam-cli-build-image-python3.8', tag='latest')
        # pylint: disable=bad-option-value
        container = client.containers.run(
            image='amazon/aws-sam-cli-build-image-python3.8:latest',
            command="/bin/sh -c 'python3.8 -m pip install --target /var/task/ --requirement /var/task/requirements.txt && "
            "find /var/task -name \\*.so -exec strip \\{\\} \\;'",
            auto_remove=True,
            mounts=[
                Mount(target="/var/task", source=self._build_dir.as_posix(), type="bind", consistency="delegated"),
                Mount(target="/root/.cache", source=self._cache_dir.as_posix(), type="bind", consistency="delegated"),
                Mount(target="/root/.netrc", source=f"{str(Path.home())}/.netrc", type="bind", consistency="delegated", read_only=True)
            ],
            user=0,
            detach=True,
        )
        try:
            if self._verbose:
                for log in container.logs(stream=True, follow=True):
                    print(log.decode('utf-8'), end='')
            else:
                container.wait()
        finally:  # handle Ctrl-C or other interruptions: kill the container
            try:
                container.kill()
            except (docker.errors.NotFound, docker.errors.APIError):
                pass  # container has already exited, was already deleted, etc.
