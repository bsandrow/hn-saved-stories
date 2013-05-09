
import logging
import sys

just_message = logging.Formatter("%(message)s")

stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(just_message)

logger = logging.getLogger('blah')
logger.addHandler(stdout)
logger.setLevel(logging.ERROR)
