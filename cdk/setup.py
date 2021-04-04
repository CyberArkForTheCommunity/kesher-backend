from setuptools import setup, find_packages
from os import getenv


def get_micro():
    build_number: str = getenv("BUILD_NUMBER", "0")
    branch_name: str = getenv("BRANCH_NAME", "None")
    micro = build_number
    if branch_name != "master" and not branch_name.startswith("release"):
        micro = f"dev{build_number}+{''.join(e for e in branch_name if e.isalnum()).lower()}"
    return micro


setup(
    name="kesher-service-cdk",
    version=f"1.0.{get_micro()}",
    description="AWS CDK stack for kesher service",
    url="https://github.com/CyberArkForTheCommunity/kesher-backend",
    author="Kesher",
    author_email="Kesher@kesher.com",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    classifiers=[
        "Development Status :: 1 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    install_requires=[
        "aws-cdk.aws-iam>=1.96.0",
        "aws-cdk.aws-kms>=1.96.0",
        "aws-cdk.aws-s3>=1.96.0",
        "aws-cdk.core>=1.96.0",
        "aws-cdk.aws-cognito>=1.96.0",
        "aws-cdk.aws_apigateway>=1.96.0",
        "aws-cdk.aws-dynamodb>=1.96.0"
    ],
    python_requires=">=3.8",
)
