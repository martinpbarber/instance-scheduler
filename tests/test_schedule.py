import context
import unittest

import logging

import pytz
import datetime

from scheduler import Day, Schedule

DEFAULT_START = datetime.time(hour=10,minute=0)
DEFAULT_STOP = datetime.time(hour=22,minute=0)
DEFAULT_ZONE = pytz.timezone('UTC')
DEFAULT_DAYS = set([
    Day.Mon,
    Day.Tue,
    Day.Wed,
    Day.Thu,
    Day.Fri,
    Day.Sat,
    Day.Sun
])
DEFAULT_SCHEDULE_STRING = '10:00;22:00;UTC;Mon,Tue,Wed,Thu,Fri,Sat,Sun'

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
        sch = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertTrue(sch)
        self.assertEqual(sch.start_time, DEFAULT_START)
        self.assertEqual(sch.stop_time, DEFAULT_STOP)
        self.assertEqual(sch.time_zone, DEFAULT_ZONE)
        self.assertEqual(sch.days, DEFAULT_DAYS)

    def test_create_empty_start(self):
        '''

        '''
        sch = Schedule(None, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertTrue(sch)
        self.assertEqual(sch.start_time, None)
        self.assertEqual(sch.stop_time, DEFAULT_STOP)
        self.assertEqual(sch.time_zone, DEFAULT_ZONE)
        self.assertEqual(sch.days, DEFAULT_DAYS)

    def test_create_empty_stop(self):
        '''

        '''
        sch = Schedule(DEFAULT_START, None, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertTrue(sch)
        self.assertEqual(sch.start_time, DEFAULT_START)
        self.assertEqual(sch.stop_time, None)
        self.assertEqual(sch.time_zone, DEFAULT_ZONE)
        self.assertEqual(sch.days, DEFAULT_DAYS)

    def test_evaluate_None(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 0, 0)

        sch = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, None)

    def test_evaluate_True(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 12, 0)

        sch = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, True)

    def test_evaluate_False(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 23, 0)

        sch = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, False)

    def test_no_start_evaluate_None(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 0, 0)

        sch = Schedule(None, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, None)

    def test_no_start_evaluate_False(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 23, 0)

        sch = Schedule(None, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, False)

    def test_no_stop_evaluate_None(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 0, 0)

        sch = Schedule(DEFAULT_START, None, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, None)

    def test_no_stop_evaluate_True(self):
        '''

        '''
        timestamp = datetime.datetime(2018, 4, 23, 12, 0)

        sch = Schedule(DEFAULT_START, None, DEFAULT_ZONE, DEFAULT_DAYS)
        target = sch.evaluate(timestamp)
        self.assertEqual(target, True)

    def test_create_from_string(self):
        '''

        '''
        sch = Schedule.from_string(DEFAULT_SCHEDULE_STRING)
        self.assertTrue(sch)
        self.assertEqual(sch.start_time, DEFAULT_START)
        self.assertEqual(sch.stop_time, DEFAULT_STOP)
        self.assertEqual(sch.time_zone, DEFAULT_ZONE)
        self.assertEqual(sch.days, DEFAULT_DAYS)

    ######################################################################
    # Test Failure
    ######################################################################
    def test_invalid_start_type(self):
        '''

        '''
        start = '10:00'

        with self.assertRaises(TypeError) as cm:
            sch = Schedule(start, DEFAULT_STOP, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertRegex(cm.exception.args[0], 'start_time must be a datetime.time object')

    def test_invalid_stop_type(self):
        '''

        '''
        stop = '22:00'

        with self.assertRaises(TypeError) as cm:
            sch = Schedule(DEFAULT_START, stop, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertRegex(cm.exception.args[0], 'stop_time must be a datetime.time object')

    def test_empty_start_stop(self):
        '''

        '''
        with self.assertRaises(ValueError) as cm:
            sch = Schedule(None, None, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertRegex(cm.exception.args[0], 'start_time or stop_time must be set')

    def test_invalid_start_stop(self):
        '''

        '''
        with self.assertRaises(ValueError) as cm:
            sch = Schedule(DEFAULT_START, DEFAULT_START, DEFAULT_ZONE, DEFAULT_DAYS)
        self.assertRegex(cm.exception.args[0], 'stop_time ".*" must be after start_time ".*"')

    def test_invalid_zone_type(self):
        '''

        '''
        zone = 'UTC'

        with self.assertRaises(TypeError) as cm:
            sch = Schedule(DEFAULT_START, DEFAULT_STOP, zone, DEFAULT_DAYS)
        self.assertRegex(cm.exception.args[0], 'time_zone must be a datetime.tzinfo object')

    def test_invalid_days_type(self):
        '''

        '''
        days = ['mon','tue','wed','thu','fri']

        with self.assertRaises(TypeError) as cm:
            sch = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, days)
        self.assertRegex(cm.exception.args[0], 'days must be a set of scheduler.Day')

    def test_invalid_days_value(self):
        '''

        '''
        days = set(['mon','tue','wed','thu','fri'])

        with self.assertRaises(TypeError) as cm:
            sch = Schedule(DEFAULT_START, DEFAULT_STOP, DEFAULT_ZONE, days)
        self.assertRegex(cm.exception.args[0], 'days must be a set of scheduler.Day')

if __name__ == '__main__':
    unittest.main()
