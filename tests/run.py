import os
import os.path
import sys
import unittest

sys.path.append(os.path.join(os.getcwd()))
sys.path.append(os.path.join(os.getcwd(), 'src'))

from tests import env

from xmlrunner import XMLTestRunner

if len(sys.argv) > 1:
    pattern = sys.argv[1]
else:
    pattern = "test_*.py"

tests = unittest.TestLoader().discover("tests", pattern=pattern)
ret = not XMLTestRunner(output=".test-reports/unittest/", verbosity=2).run(tests).wasSuccessful()
sys.exit(ret)
