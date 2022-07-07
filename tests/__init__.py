import json
import logging
import os
import warnings

import os.path
import sys

sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd() + "/src"))

from tests import env

warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)

logging.basicConfig(level=logging.INFO)
# reduce logging for this library during tests
logging.getLogger("soundcharts.client").setLevel(logging.INFO)

dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)
