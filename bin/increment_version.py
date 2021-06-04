#!/usr/bin/env python

import sys
import re

if len(sys.argv) < 2:
    print('No previous tag provided')
    exit(1)

tag = sys.argv[1]
if len(sys.argv) > 2:
    operation = sys.argv[2]
else:
    operation = 'patch'

if operation not in ('major', 'minor', 'patch'):
    print('Unsupported operation: {}'.format(operation))
    exit(1)

tag = tag.strip('v')
version = re.match(r'^([0-9\.]+)$', tag)
numbers = version.group(1).split('.')
index = ['major', 'minor', 'patch'].index(operation)

if len(numbers) < (index+1):
    print("No {} version found in {}".format(operation, version))
    exit(1)

# increment the relevant number
numbers[index] = '%d' % (int(numbers[index]) + 1)

# (re)set any following numbers to zero
for i in range(index+1, len(numbers)):
    numbers[int(i)] = '0'

# output the final version
print('.'.join(numbers))