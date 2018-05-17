import context
import unittest

import logging

from scheduler import Schedule

logger = logging.getLogger()
logger.setLevel(logging.WARN)
logger.addHandler(logging.StreamHandler)

class ScheduleTestCase(unittest.TestCase):
    '''
        Unit tests for Schedule object
    '''
    
    ######################################################################
    # Test Success
    ######################################################################

    def test_create(self):
        '''
            Create a schedule object
        '''
        schedule = Schedule()
        self.assertTrue(schedule)


if __name__ == '__main__':
    unittest.main()
