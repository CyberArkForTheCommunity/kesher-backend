#!/usr/bin/env python
import argparse
from pathlib import Path
from build_lambda_asset import BuildLambdaAsset
from create_requirements_txt import create_requirements_txt
import pathlib


def build():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-deps", nargs="?", const=True, default=False, help="Skip consume dependencies")
    parser.add_argument("--dev", nargs="?", const=True, default=False, help="Include development dependencies")
    args = parser.parse_args()

    do_build(consume_dependencies=not args.skip_deps, include_dev=args.dev)


def do_build(consume_dependencies=True, include_dev=False):
    build_dir = Path(pathlib.Path(__file__).parent.absolute()) / '.build'

    Path(build_dir).mkdir(parents=True, exist_ok=True)

    email_lambda_runtime_deps = ['pandas', 'aws-lambda-powertools', 'pydantic', 'aws-lambda-context']
    requirements_txt: Path = build_dir/'email_functions_service_requirements.txt'
    create_requirements_txt(runtime_dependencies=email_lambda_runtime_deps, target=requirements_txt)
    BuildLambdaAsset(include_paths=['cdk/kesher_service_cdk/service_stack/email_services/functions'], 
                     build_dir=build_dir/'email_services', 
                     consume_dependencies=consume_dependencies,
                     requirements_txt=requirements_txt).build()


    requirements_txt: Path = build_dir/'service_requirements.txt'
    create_requirements_txt(dev_dependencies=['ptvsd'] if include_dev else [], target=requirements_txt)
    BuildLambdaAsset(include_paths=['service'], build_dir=build_dir/'service', consume_dependencies=consume_dependencies,
                     requirements_txt=requirements_txt).build()



if __name__ == "__main__":
    build()
