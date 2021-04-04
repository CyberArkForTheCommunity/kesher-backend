#!/usr/bin/env python
# pylint: disable = print-used
import os
from stack_utils import environment
from kesher_service_cdk.service_stack.constants import BASE_NAME

# pylint: disable=invalid-name
project_path = os.path.abspath(os.path.dirname(__file__))
environment.destroy(project_path=project_path, base_stack_name=BASE_NAME)
