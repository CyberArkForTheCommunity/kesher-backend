import json
from pathlib import Path
from io import TextIOWrapper


# pylint: disable=print-used
def create_requirements_txt(runtime_dependencies: list = None, dev_dependencies: list = None, target: Path = None):
    if dev_dependencies is None:
        dev_dependencies = []

    if target is None:
        target = Path('requirements.txt')

    with open('Pipfile.lock') as json_file:
        data = json.load(json_file)

    with open(target.as_posix(), "w") as f:
        index = 0
        for source in data['_meta']['sources']:  # sets the pypi server path
            if index == 0:
                f.write(f"-i {source['url']}\n")
            else:
                f.write(f"--extra-index-url {source['url']}\n")
            index += 1

        write_dependencies(f, data, "default", runtime_dependencies)
        write_dependencies(f, data, "develop", dev_dependencies)


def write_dependencies(f: TextIOWrapper, data: dict, dependency_type: str, subset_dependencies: list):
    if subset_dependencies is not None:
        diff = list(set(subset_dependencies) - set(data[dependency_type]))
        if len(diff):
            print(f'WARNING: dependencies {diff} were not found in Pipfile.lock in \'{dependency_type}\' section')
    for dependency in data[dependency_type]:
        if subset_dependencies is not None and dependency not in subset_dependencies:
            continue
        dependency_section = data[dependency_type][dependency]
        if "git" in dependency_section:
            git_string = f"git+{dependency_section['git']}@{dependency_section['ref']}#egg={dependency}"
            f.write(f"-e {git_string}\n") if "editable" in dependency_section else f.write(git_string + "\n")

        else:  # not final: maybe there is more flags like 'markers'
            if "markers" in dependency_section:
                f.write(f"{dependency}{dependency_section['version']} ; {dependency_section['markers']}\n")
            else:
                f.write(f"{dependency}{dependency_section['version']}\n")
