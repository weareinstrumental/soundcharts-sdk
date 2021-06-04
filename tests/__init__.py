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
