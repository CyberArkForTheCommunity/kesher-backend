# kesher-service

Cloned from the template-business-service at: 2021-04-04 08:36:33  
Last updated at: 2021-04-04 08:36:33


## Prerequisite installation
You should install the following tools before starting to work
1. Install Python 3.7.+
1. Install pipenv for python dependency management 
- zsh shell (MacOS):
   ```shell script
   pip install pipenv
   echo export PIPENV_VENV_IN_PROJECT=true >> ~/.zshrc
    ```
 - bash shell (Linux):
   ```shell script
   pip install pipenv
   echo export PIPENV_VENV_IN_PROJECT=true >> ~/.bashrc
    ```
1. Install AWS SAM
    ```cmd
    brew tap aws/tap
    brew install aws-sam-cli
    ```
1. Node.js download and install from: [https://nodejs.org/en/download](https://nodejs.org/en/download/)
   Then configure [npm proxy](https://ca-il-confluence.il.cyber-ark.com/display/GRnD/Proxy+Configuration+for+Dev+Tools#ProxyConfigurationforDevTools-npm)
1. Install [AWS CDK](https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html)
    ```shell script
    npm install -g aws-cdk
    ```

## Getting started
1. Use "Self-Service" Jenkins job in order to create template job and repository

1. Load your github.com ssh key in order to resolve dependencies next step
    ```shell script
    ssh-add ~/.ssh/id_rsa
    ```

1. Install dependencies
    ```shell script
    pipenv install --dev 
    ```

1. Enter virtual env by:
    ```shell script
    pipenv shell 
    ```

1. Retrieve AWS token for one day, execute the following:
   ```shell script
   saml2aws login
   ```   
   For more info go to https://github.com/Versent/saml2aws


### Deploy
In order to deploy infra-library CloudFormation stack resources for example: KMS, S3
```shell script
python deploy.py
```
Clean deployment, will remove the old stack from CloudFormation
```shell script
python deploy.py --clean
```

### Destroy
In order to delete the CloudFormation stack deployed in the last step:
```shell script
python env_destroy.py
```

### Pylint
Execute lint on your code:
```shell script
pylint <root-package/filename> -E
```